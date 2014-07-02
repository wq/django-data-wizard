from celery import task, current_task
from xlrd import colname
from collections import namedtuple, Counter, OrderedDict
from wq.db.patterns.models import Identifier, Relationship, RelationshipType
import swapper
from .models import MetaColumn, UnknownItem, SkippedRecord, Range
from django.conf import settings
import datetime
from .signals import import_complete, new_metadata

from wq.db.rest.models import get_ct, get_object_id

import wq.db.contrib.vera.models

Site = swapper.load_model('vera', 'Site')
Event = swapper.load_model('vera', 'Event')
Report = swapper.load_model('vera', 'Report')
ReportStatus = swapper.load_model('vera', 'ReportStatus')
Parameter = swapper.load_model('vera', 'Parameter')
Result = swapper.load_model('vera', 'Result')

META_CLASSES = {
    'site': Site,
    'event': Event,
    'report': Report,
    'parameter': Parameter,
    'result': Result,
}

EVENT_KEY = [val for val, cls in Event.get_natural_key_info()]
EventKey = namedtuple('EventKey', EVENT_KEY)

CONTENT_TYPES = {
    Parameter: get_ct(Parameter),
    MetaColumn: get_ct(MetaColumn),
    UnknownItem: get_ct(UnknownItem),
}

DATE_FIELDS = {
    'DateTimeField': datetime.datetime,
    'DateField': datetime.date,
}

if hasattr(settings, 'WQ_DEFAULT_REPORT_STATUS'):
    DEFAULT_STATUS = settings.WQ_DEFAULT_REPORT_STATUS
else:
    DEFAULT_STATUS = None

PRIORITY = {
    'parameter': 1,
    'meta column': 2,
    'unknown item': 3,
}


@task
def auto_import(instance, user):
    """
    Walk through all the steps necessary to interpret and import data from an
    IO.  Meant to be called asynchronously.  Automatically suspends import if
    any additional input is needed from the user.
    """
    # Preload IO to catch any load errors early
    status = {
        'message': "Loading Data...",
        'current': 1,
        'total': 4,
    }
    current_task.update_state(state='PROGRESS', meta=status)
    table = instance.load_io()

    # Parse columns
    status.update(
        message="Parsing Columns...",
        current=2,
    )
    current_task.update_state(state='PROGRESS', meta=status)
    result = read_columns(instance, user)
    if result['unknown_count']:
        result['action'] = "columns"
        result['message'] = "Input Needed"
        return result

    # Parse row identifiers
    status.update(
        message="Parsing Identifiers...",
        current=3,
    )
    current_task.update_state(state='PROGRESS', meta=status)
    result = read_row_identifiers(instance, user)
    if result['unknown_count']:
        result['action'] = "ids"
        result['message'] = "Input Needed"
        return result

    status.update(
        message="Importing Data...",
        current=4,
    )

    # The rest is the same as import_data
    return do_import(instance, user)


def get_choices(instance):
    def make_list(cls, name):
        rows = cls.objects.all()
        ct = CONTENT_TYPES[cls]
        result = [{
            'url': '%s/%s' % (ct.urlbase, get_object_id(row)),
            'label': unicode(row)
        } for row in rows]
        result.insert(0, {
            'url': '%s/new' % ct.urlbase,
            'label': "New %s" % name,
        })
        return {
            'name': name,
            'choices': result
        }

    return [
        make_list(MetaColumn, "Metadata Column"),
        make_list(Parameter, "Parameter")
    ]


@task
def read_columns(instance, user=None):
    matched = get_columns(instance)
    unknown_count = 0
    for info in matched:
        if info['type'] == 'unknown':
            unknown_count += 1
            # Add some useful context items for client
            info['unknown'] = True
            info['types'] = get_choices(instance)

    return {
        'columns': matched,
        'unknown_count': unknown_count,
    }


# FIXME: These functions might make more sense as methods on IoModel
def get_columns(instance):
    if instance.already_parsed():
        return load_columns(instance)
    else:
        return parse_columns(instance)


def get_meta_columns(instance):
    matched = get_columns(instance)
    cols = OrderedDict()
    for col in matched:
        if 'colnum' not in col or not col['type']:
            continue
        if col['type'] in ('parameter_value', 'unknown'):
            continue
        if col['type'] in ('event', 'report', 'result'):
            continue
        cols.setdefault(col['type'], [])
        cols[col['type']].append(col)
    return cols


def load_columns(instance):
    rels = instance.relationships.filter(type__name='Contains Column')
    table = instance.load_io()

    matched = []
    for rel in rels:
        item = rel.right
        info = {
            'match': unicode(item),
            'rel_id': rel.pk,
        }
        if isinstance(item, UnknownItem):
            info['type'] = "unknown"
            info['value'] = item.name
        elif isinstance(item, Parameter):
            info['type'] = "parameter_value"
            info['parameter_id'] = get_object_id(item)
        elif isinstance(item, MetaColumn):
            info['type'] = item.type
            info['field_name'] = item.name

        if rel.range_set.filter(type='list').exists():
            col = rel.range_set.get(type='list').start_column
            info['name'] = table.field_map.keys()[col].replace('\n', ' - ')
            info['column'] = colname(col)
            info['colnum'] = col

        elif rel.range_set.filter(type='value').exists():
            info['name'] = get_range_value(table, rel.range_set.get(
                type='head'
            ))
            info['value'] = get_range_value(table, rel.range_set.get(
                type='value'
            ))
        matched.append(info)
    matched.sort(key=lambda info: info.get('colnum', -1))
    return matched


def get_range_value(table, rng):
    if rng.start_row == rng.end_row and rng.start_column == rng.end_column:
        return table.extra_data.get(rng.start_row, {}).get(rng.start_column)

    val = u""
    for r in range(rng.start_row, rng.end_row + 1):
        for c in range(rng.start_column, rng.end_column + 1):
            val += unicode(table.extra_data.get(r, {}).get(c, ""))
    return val


def parse_columns(instance):
    table = instance.load_io()
    if table.tabular:
        for r in table.extra_data:
            row = table.extra_data[r]
            for c in row:
                if c + 1 in row and c - 1 not in row:
                    parse_column(
                        instance,
                        name=row[c],
                        head=[r, c, r, c],
                        body=[r, c + 1, r, c + 1],
                        body_type='value'
                    )

    for i, name in enumerate(table.field_map.keys()):
        if table.tabular:
            header_row = table.header_row
            start_row = table.start_row
        else:
            header_row = -1
            start_row = 0
        name = table.clean_field_name(name)
        parse_column(
            instance,
            name=name,
            head=[header_row, i, start_row - 1, i],
            body=[start_row, i, start_row + len(table), i],
            body_type='list'
        )

    return load_columns(instance)


def parse_column(instance, name, head, body, body_type):
    matches = list(Identifier.objects.filter_by_identifier(name))
    if len(matches) > 0:
        matches.sort(
            key=lambda ident: PRIORITY.get(ident.content_type.name, 0)
        )
        column = matches[0].content_object
        ctype = matches[0].content_type
    else:
        column = UnknownItem.objects.find(name)
        ctype = CONTENT_TYPES[UnknownItem]

    reltype, is_new = RelationshipType.objects.get_or_create(
        from_type=get_ct(instance),
        to_type=ctype,
        name='Contains Column',
        inverse_name='Column In'
    )
    rel = instance.relationships.create(
        type=reltype,
        to_content_type=ctype,
        to_object_id=column.pk,
    )
    Range.objects.create(
        relationship=rel,
        type='head',
        start_row=head[0],
        start_column=head[1],
        end_row=head[2],
        end_column=head[3]
    )
    Range.objects.create(
        relationship=rel,
        type=body_type,
        start_row=body[0],
        start_column=body[1],
        end_row=body[2],
        end_column=body[3]
    )


@task
def update_columns(instance, user, post):
    matched = get_columns(instance)
    for col in matched:
        if col['type'] != 'unknown':
            continue
        val = post.get('rel_%s' % col['rel_id'], None)
        if not val:
            continue

        vtype, vid = val.split('/')
        if vtype == 'parameters':
            cls = Parameter
        elif vtype == 'metacolumns':
            cls = MetaColumn
        else:
            continue

        if vid == 'new':
            obj = cls.objects.find(col['value'])
            obj.contenttype = CONTENT_TYPES[Parameter]
            obj.save()
            ident = obj.primary_identifier
        else:
            obj = cls.objects.get_by_identifier(vid)
            ident = obj.identifiers.create(
                name=col['value']
            )

        reltype, is_new = RelationshipType.objects.get_or_create(
            from_type=get_ct(instance),
            to_type=CONTENT_TYPES[cls],
            name='Contains Column',
            inverse_name='Column In'
        )
        rel = instance.relationships.get(pk=col['rel_id'])
        rel.type = reltype
        rel.right = obj
        rel.save()

        new_metadata.send(
            sender=update_columns,
            instance=instance,
            object=obj,
            identifier=ident,
        )

    return read_columns(instance)


@task
def read_row_identifiers(instance, user):
    coltypes = get_meta_columns(instance)
    ids = {}
    for mtype in coltypes:
        ids[mtype] = Counter()

    for row in instance.load_io():
        for mtype, cols in coltypes.items():
            counter = ids[mtype]
            meta = OrderedDict()
            for col in cols:
                meta[col['field_name']] = row[col['colnum']]
            key = tuple(meta.items())
            counter[key] += 1

    idgroups = []
    unknown_ids = 0
    for mtype in ids:
        cls = META_CLASSES[mtype]
        idinfo = {
            'type_id': mtype,
            'type_label': mtype.capitalize(),
            'ids': []
        }
        for key, count in ids[mtype].items():
            meta = OrderedDict(key)
            try:
                obj = cls.objects.get_by_natural_key(meta['id'])
            except cls.DoesNotExist:
                obj = None

            info = {
                'value': meta['id'],
                'count': count,
                'meta': [{
                    'name': k,
                    'value': v
                } for k, v in meta.items() if k != 'id']
            }
            if obj is not None:
                info['match'] = unicode(obj)
                # FIXME: Confirm that metadata hasn't changed
            else:
                info['ident_id'] = unknown_ids
                unknown_ids += 1
                info['unknown'] = True
                choices = instance.get_id_choices(cls)
                info['choices'] = [{
                    'id': get_object_id(obj),
                    'label': unicode(obj),
                } for obj in choices]
                info['choices'].insert(0, {
                    'id': 'new',
                    'label': "New %s" % idinfo['type_label'],
                })

            idinfo['ids'].append(info)
        idinfo['ids'].sort(key=lambda info: info['value'])
        idgroups.append(idinfo)
    return {
        'unknown_count': unknown_ids,
        'types': idgroups,
    }


@task
def update_row_identifiers(instance, user, post):
    coltypes = get_meta_columns(instance)
    unknown_count = int(post.get('unknown_count', 0))
    for i in range(0, unknown_count):
        ident_value = post.get('ident_%s_value' % i, None)
        ident_type = post.get('ident_%s_type' % i, None)
        ident_id = post.get('ident_%s_id' % i, None)
        if ident_value and ident_type and ident_id:
            if ident_type not in coltypes:
                raise Exception("Unexpected type %s!" % ident_type)
            cls = META_CLASSES[ident_type]
            if ident_id == 'new':
                # Create new object (with primary identifier)
                obj = cls.objects.find(ident_value)
                ident = obj.primary_identifier

                # Set additional metadata fields on new object
                for col in coltypes[ident_type]:
                    if col['field_name'] == "id":
                        continue

                    formname = 'ident_%s_%s' % (i, col['field_name'])
                    val = post.get(formname, None)
                    if not val:
                        continue

                    setattr(obj, col['field_name'], val)

                    # If present, also apply "name" attribute to identifier
                    if col['field_name'] == "name":
                        ident.name = val
                        ident.slug = ident_value
                        ident.save()
                obj.save()
            else:
                # Add new identifier to existing object for future reference
                obj = cls.objects.get_by_identifier(ident_id)
                name = post.get('ident_%s_name' % i, None)
                if not name:
                    name = ident_value
                ident = obj.identifiers.create(name=name, slug=ident_value)

                # FIXME: Update existing metadata?

            new_metadata.send(
                sender=update_row_identifiers,
                instance=instance,
                object=obj,
                identifier=ident,
            )

    return read_row_identifiers(instance, user)


@task
def reset(instance, user):
    instance.relationships.all().delete()


@task
def import_data(instance, user):
    """
    Import all parseable data from the dataset instance's IO class.
    """
    return do_import(instance, user)


def do_import(instance, user):

    # (Re-)Load data and column information
    table = instance.load_io()
    matched = get_columns(instance)

    # Set global defaults for metadata values
    if not user.is_authenticated():
        user = None
    instance_globals = {
        # Metadata fields
        'event_meta': {},
        'report_meta': {
            'user': user,
            'status_id': DEFAULT_STATUS,
        },
        # result_meta, parameter_meta, and site_meta are defined on a
        # case-by-case basis; see create_record() below

        # Result values indexed by parameter (for "horizontal" tables)
        'param_vals': {}
    }

    # Set default to None for any event key fields that are not required
    for field_name in EVENT_KEY:
        info = Event._meta.get_field_by_name(field_name)
        field = info[0]
        if field.null:
            instance_globals['event_meta'][field_name] = None

    # Set any global defaults defined within data themselves (usually as extra
    # cells above the headers in a spreadsheet)
    for col in matched:
        if 'value' in col:
            save_value(col, col['value'], instance_globals)

    # Loop through table rows and add each record
    rows = len(table)
    errors = []
    skipped = []

    if table.tabular:
        def rownum(i):
            return i + table.start_row
    else:
        def rownum(i):
            return i

    for i, row in enumerate(table):
        # Update state (for status() on view)
        current_task.update_state(state='PROGRESS', meta={
            'current': i + 1,
            'total': rows,
            'skipped': skipped
        })

        # Create report, capturing any errors
        skipreason = None
        try:
            report = create_report(row, instance_globals, matched)
        except Exception as e:
            # Log error in database
            skipreason = repr(e)
            skipped.append({'row': rownum(i) + 1, 'reason': skipreason})
            report, is_new = SkippedRecord.objects.get_or_create(
                reason=skipreason
            )

        # Record relationship between data source and resulting report (or
        # skipped record), including specific cell range.
        rel = instance.create_relationship(
            report,
            'Contains Row',
            'Row In'
        )
        Range.objects.create(
            relationship=rel,
            type='row',
            start_row=rownum(i),
            start_column=0,
            end_row=rownum(i),
            end_column=len(row) - 1
        )

    # Send completion signal (in case any server handlers are registered)
    status = {
        'current': i + 1,
        'total': rows,
        'skipped': skipped
    }
    import_complete.send(sender=import_data, instance=instance, status=status)

    # Return status (thereby updating task state for status() on view)
    return status


def create_report(row, instance_globals, matched):
    """
    Create actual report instance from parsed values.
    """

    # Copy global values to record hash
    record = {
        key: instance_globals[key].copy()
        for key in instance_globals
    }

    # In some spreadsheets (i.e. "horizontal" tables), multiple columns
    # indicate parameter names and each row only contains result values.  In
    # others (i.e. "vertical" tables), each row lists both the parameter name
    # and the value.  See http://wq.io/docs/dbio#horizontal-vs-vertical

    # Parse metadata & "horizontal" table parameter values
    for col in matched:
        if 'colnum' in col:
            save_value(col, row[col['colnum']], record)

    # Handle "vertical" table values (parsed as metadata by save_value())
    if 'result_meta' in record and 'parameter_meta' in record:
        # FIXME: handle other parameter & result metadata
        parameter_id = record['parameter_meta']['id']
        result_value = record['result_meta']['value']
        record['param_vals'][parameter_id] = result_value

    if 'site_meta' in record:
        # FIXME: Handle other site metadata
        site_id = record['site_meta']['id']
        record['event_meta']['site'] = site_id

    # Ensure complete Event natural key (http://wq.io/docs/erav#natural-key)
    missing = set(EVENT_KEY) - set(record['event_meta'].keys())
    if missing:
        raise Exception(
            'Incomplete Record - missing %s' % ", ".join(missing)
        )

    # Create report instance
    report = Report.objects.create_report(
        EventKey(**record['event_meta']),
        record['param_vals'],
        **record['report_meta']
    )
    return report


def save_value(col, val, obj):
    """
    For each cell in each row, use parsed col(umn) information to determine how
    to apply the cell val(ue) to the obj(ect hash).
    """
    if col['type'] == "parameter_value":
        # Parameter value in a "horizontal" table
        save_parameter_value(col, val, obj)
    elif col['type'] != "unknown":
        # Metadata value in either a "horizontal" or "vertical" table
        save_metadata_value(col, val, obj)


def save_parameter_value(col, val, obj):
    """
    This column was identified as a parameter; update param_vals with the
    cell value from this row.
    """
    parameter_id = col['parameter_id']
    vals = obj['param_vals']

    # Hack: if there are two (or more) columns pointing to the same
    # parameter, join both values together with a space.
    if parameter_id in vals:
        val = "%s %s" % (vals[parameter_id], val)

    vals[parameter_id] = val


def save_metadata_value(col, val, obj):
    """
    This column was identified as a metadata field; update the metadata
    for the related object with the cell value from this row.
    """

    # Skip empty values
    if val is None or val == '' or not col['type']:
        return

    # Assign metadata property based on meta_field (MetaColumn.name).
    meta_key = '%s_meta' % col['type']
    meta_cls = META_CLASSES[col['type']]
    meta_field = col['field_name']

    # Event and report metadata are defined whether this is a "horizontal" or
    # "vertical" table.  On the other hand, parameter/result meta are unique to
    # "vertical" tables and are thus not included by default.  In either case,
    # site metadata is also not expected.
    if meta_key not in obj:
        # This is one of parameter, result, or site meta.
        obj[meta_key] = {}

    # A meta_field value of '[field].[part]' indicates a value is split across
    # multiple columns.  For example, a spreadsheet could contain two columns
    # (date and time) that would be merged into a single "observed" field on a
    # custom Event class.  There would then be two MetaColumns values, with
    # names of "observed.date" and "observed.time" respectively.
    if '.' in meta_field:
        meta_field, part = meta_field.split('.')
    else:
        part = None

    # Determine Django field type (for metadata models only)
    if col['type'] == 'result':
        meta_datatype = None
    else:
        meta_datatype = meta_cls._meta.get_field_by_name(
            meta_field,
        )[0].get_internal_type()

    # Automatically parse date values as such
    if (meta_datatype in DATE_FIELDS and isinstance(val, basestring)
            and part != 'time'):
        from dateutil.parser import parse
        val = parse(val)
        if meta_datatype == 'DateField':
            val = val.date()

    # If field is already set by an earlier column, this value might be the
    # second half of a date/time pair.
    if obj[meta_key].get(meta_field, None) is not None:
        if not part:
            raise Exception(
                'Multiple columns found for %s' % meta_field
            )
        if part not in ('date', 'time'):
            raise Exception(
                'Unexpected multi-column field name: %s.%s!' % (
                    meta_field, part
                )
            )
        other_val = obj[meta_key][meta_field]
        val = process_date_part(val, other_val, part)

    # Save value to parsed record
    obj[meta_key][meta_field] = val


def process_date_part(new_val, old_val, part):
    """
    Combine separate date & time columns into a single value.
    """

    if part == 'date':
        date, time = new_val, old_val
    else:
        date, time = old_val, new_val

    # Date should already be a valid date (see parse in save_metadata_value)
    if not isinstance(date, datetime.date):
        raise Exception("Expected date but got %s!" % date)

    # Try some extra hacks to convert time values
    if not isinstance(time, datetime.time):
        if (isinstance(time, float)
                and time >= 100 and time <= 2400):
            # "Numeric" time (hour * 100 + minutes)
            time = str(time)
        elif isinstance(time, basestring) and ":" in time:
            # Take out semicolon for isdigit() code below
            time = time.replace(":", "")

        # FIXME: what about seconds?
        if time.isdigit() and len(time) in (3, 4):
            if len(time) == 3:
                # 300 -> time(3, 0)
                time = datetime.time(
                    int(time[0]),
                    int(time[1:])
                )
            else:
                # 1200 -> time(12, 0)
                time = datetime.time(
                    int(time[0:2]),
                    int(time[2:])
                )
        else:
            # Meh, it was worth a shot
            raise Exception("Expected time but got %s!" % time)
    return datetime.datetime.combine(date, time)
