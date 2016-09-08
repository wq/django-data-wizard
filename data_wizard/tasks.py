from celery import task, current_task
from xlrd import colname
from collections import namedtuple, Counter, OrderedDict
import swapper
from .models import Identifier
from django.conf import settings
from django.utils.six import string_types
import datetime
from .signals import import_complete, new_metadata
import json

from django.contrib.contenttypes.models import ContentType
from wq.db.rest.models import get_ct

import vera.models  # noqa

Site = swapper.load_model('vera', 'Site')
Event = swapper.load_model('vera', 'Event')
Report = swapper.load_model('vera', 'Report')
ReportStatus = swapper.load_model('vera', 'ReportStatus')
Parameter = swapper.load_model('vera', 'Parameter')
Result = swapper.load_model('vera', 'Result')


EVENT_KEY = [val for val, cls in Event.get_natural_key_info()]
EventKey = namedtuple('EventKey', EVENT_KEY)


DATE_FIELDS = {
    'DateTimeField': datetime.datetime,
    'DateField': datetime.date,
}

if hasattr(settings, 'WQ_DEFAULT_REPORT_STATUS'):
    DEFAULT_STATUS = settings.WQ_DEFAULT_REPORT_STATUS
else:
    DEFAULT_STATUS = None

PRIORITY = {
    'instance': 1,
    'meta': 2,
    'unresolved': 3,
    'unknown': 4,
}


def ctid(ct):
    return '%s.%s' % (ct.app_label, ct.model)


def metaname(cls):
    return ctid(get_ct(cls)) + '_meta'


@task
def auto_import(run, user):
    """
    Walk through all the steps necessary to interpret and import data from an
    IO.  Meant to be called asynchronously.  Automatically suspends import if
    any additional input is needed from the user.
    """
    run.add_event('auto_import')
    # Preload IO to catch any load errors early
    status = {
        'message': "Loading Data...",
        'stage': 'meta',
        'current': 1,
        'total': 4,
    }
    current_task.update_state(state='PROGRESS', meta=status)
    run.load_io()

    # Parse columns
    status.update(
        message="Parsing Columns...",
        current=2,
    )
    current_task.update_state(state='PROGRESS', meta=status)
    result = read_columns(run, user)
    if result['unknown_count']:
        result['action'] = "columns"
        result['message'] = "Input Needed"
        current_task.update_state(state='SUCCESS', meta=result)
        return result

    # Parse row identifiers
    status.update(
        message="Parsing Identifiers...",
        current=3,
    )
    current_task.update_state(state='PROGRESS', meta=status)
    result = read_row_identifiers(run, user)
    if result['unknown_count']:
        result['action'] = "ids"
        result['message'] = "Input Needed"
        current_task.update_state(state='SUCCESS', meta=result)
        return result

    status.update(
        message="Importing Data...",
        current=4,
    )

    # The rest is the same as import_data
    return do_import(run, user)


def get_choices(run):
    def make_list(cls, name):
        rows = cls.objects.all()
        ct = get_ct(cls)
        result = [{
            'id': '%s/new' % ctid(ct),
            'label': "New %s" % name,
        }]
        result += [{
            'id': '%s/%s' % (ctid(ct), row.pk),
            'label': str(row),
        } for row in rows]
        return {
            'name': name,
            'choices': result
        }

    meta_choices = set()
    for m in Identifier.objects.filter(resolved=True, field__isnull=False):
        assert(m.type == 'meta')
        mid = '%s:%s' % (ctid(m.content_type), m.field)
        mlabel = ('%s %s' % (m.content_type.name, m.field)).title()
        meta_choices.add((mid, mlabel))
    meta_choices = sorted(meta_choices, key=lambda d: d[1])
    choices = [
        {
            'name': 'Metadata',
            'choices': [{
                'id': key,
                'label': label
            } for key, label in meta_choices],
        },
        make_list(Parameter, "Parameter")
    ]
    return choices


@task
def read_columns(run, user=None):
    matched = get_columns(run)
    unknown_count = 0
    for info in matched:
        if info['type'] == 'unknown':
            unknown_count += 1
            # Add some useful context items for client
            info['unknown'] = True
            info['types'] = get_choices(run)

    return {
        'columns': matched,
        'unknown_count': unknown_count,
    }


# FIXME: These functions might make more sense as methods on Run
def get_columns(run):
    if run.already_parsed():
        return load_columns(run)
    else:
        return parse_columns(run)


def get_meta_columns(run):
    matched = get_columns(run)
    cols = OrderedDict()
    has_id = {}
    for col in matched:
        if 'colnum' not in col or col['type'] != 'meta':
            continue
        cols.setdefault(col['model'], [])
        cols[col['model']].append(col)
        if col['field_name'] == 'id':
            has_id[col['model']] = True
    for model in list(cols.keys()):
        if model not in has_id:
            cols.pop(model)
    return cols


def load_columns(run):
    table = run.load_io()
    cols = list(table.field_map.keys())
    matched = []
    for rng in run.range_set.exclude(type='data'):
        ident = rng.identifier
        info = {
            'match': str(ident),
            'rel_id': rng.pk,
            'type': ident.type,
        }

        if ident.type == 'meta':
            info['field_name'] = rng.identifier.field
            info['model'] = ctid(ident.content_type)
        elif ident.type == 'instance':
            info['%s_id' % ident.content_type.model] = ident.object_id
        else:
            info['value'] = ident.name

        if rng.type == 'list':
            col = rng.start_col
            info['name'] = cols[col].replace('\n', ' - ')
            info['column'] = colname(col)
            info['colnum'] = col

        elif rng.type == 'value':
            info['name'] = get_range_value(
                table, rng, rng.header_col, rng.start_col - 1
            )
            info['value'] = get_range_value(
                table, rng, rng.start_col, rng.end_col
            )
        matched.append(info)
    matched.sort(key=lambda info: info.get('colnum', -1))
    return matched


def get_range_value(table, rng, scol, ecol):
    if rng.start_row == rng.end_row and scol == ecol:
        return table.extra_data.get(rng.start_row, {}).get(scol)

    val = ""
    for r in range(rng.start_row, rng.end_row + 1):
        for c in range(scol, ecol + 1):
            val += str(table.extra_data.get(r, {}).get(c, ""))
    return val


def parse_columns(run):
    run.add_event('parse_columns')
    table = run.load_io()
    if table.tabular:
        for r in table.extra_data:
            row = table.extra_data[r]
            for c in row:
                if c + 1 in row and c - 1 not in row:
                    parse_column(
                        run,
                        row[c],
                        type='value',
                        start_row=r,
                        end_row=r,
                        header_col=c,
                        start_col=c + 1,
                        end_col=c + 1,
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
            run,
            name=name,
            type='list',
            header_row=header_row,
            start_row=start_row,
            end_row=start_row + len(table) - 1,
            start_col=i,
            end_col=i,
        )

    return load_columns(run)


def parse_column(run, name, **kwargs):
    matches = list(Identifier.objects.filter(name__iexact=name))
    if len(matches) > 0:
        matches.sort(
            key=lambda ident: PRIORITY.get(ident.type, 0)
        )
        ident = matches[0]
    else:
        ident = Identifier.objects.create(name=name)

    run.range_set.create(
        identifier=ident,
        **kwargs
    )


@task
def update_columns(run, user, post):
    run.add_event('update_columns')
    matched = get_columns(run)
    for col in matched:
        if col['type'] != 'unknown':
            continue
        val = post.get('rel_%s' % col['rel_id'], None)
        if not val:
            continue

        ident = run.range_set.get(pk=col['rel_id']).identifier
        assert(ident.content_type_id is None)
        assert(ident.object_id is None)
        assert(ident.field is None)

        if '/' in val:
            ctype, val = val.split('/')
            match = 'object_id'
        elif ':' in val:
            ctype, val = val.split(':')
            match = 'field'
        else:
            continue

        app_label, model = ctype.split('.')
        ident.content_type = ContentType.objects.get(
            app_label=app_label,
            model=model,
        )

        if match == 'object_id':
            cls = ident.content_type.model_class()
            if val == 'new':
                # FIXME: This assumes class is a wq.db IdentifiedModel
                obj = cls.objects.find(col['value'])
            else:
                obj = cls.objects.get(pk=val)
            ident.object_id = obj.pk
        else:
            ident.field = val

        ident.save()

        new_metadata.send(
            sender=update_columns,
            run=run,
            identifier=ident,
        )

    return read_columns(run)


@task
def read_row_identifiers(run, user=None):
    if run.range_set.filter(type='data').exists():
        return load_row_identifiers(run)
    else:
        return parse_row_identifiers(run)


def parse_row_identifiers(run):
    run.add_event('parse_row_identifiers')
    coltypes = get_meta_columns(run)
    ids = {}
    ranges = {}
    for mtype in coltypes:
        ids[mtype] = Counter()
        ranges[mtype] = {}

    start_col = 1e10
    start_row = 1e10
    end_col = -1
    end_row = -1
    table = run.load_io()
    for i, row in enumerate(table):
        for mtype, cols in coltypes.items():
            counter = ids[mtype]
            meta = OrderedDict()
            for col in cols:
                meta[col['field_name']] = row[col['colnum']]

            assert('id' in meta)
            meta['id'] = str(meta['id'])
            key = tuple(meta.items())

            ranges[mtype].setdefault(key, (1e10, 1e10, -1, -1))
            start_row, start_col, end_row, end_col = ranges[mtype][key]
            for col in cols:
                meta[col['field_name']] = row[col['colnum']]
                start_col = min(col['colnum'], start_col)
                end_col = max(col['colnum'], end_col)

            rownum = i
            if table.tabular:
                rownum += table.start_row
            start_row = min(start_row, rownum)
            end_row = max(end_row, rownum)

            assert(start_col < 1e10)
            assert(start_row < 1e10)
            assert(end_col > -1)
            assert(end_row > -1)

            counter[key] += 1
            ranges[mtype][key] = start_row, start_col, end_row, end_col

    for mtype in ids:
        app_label, model = mtype.split('.')
        ct = ContentType.objects.get(
            app_label=app_label,
            model=model,
        )
        cls = ct.model_class()
        assert cls, "%s.%s not found!" % (ct.app_label, ct.model)
        for key, count in ids[mtype].items():
            meta = OrderedDict(key)
            ident = Identifier.objects.filter(
                name__iexact=meta['id'],
                content_type=ct
            ).first()
            if ident:
                # FIXME: assert that meta matches any ident.meta?
                pass
            else:
                try:
                    obj = cls.objects.get_by_natural_key(meta['id'])
                except cls.DoesNotExist:
                    obj = None
                    other_meta = meta.copy()
                    other_meta.pop('id')
                    other_meta = json.dumps(other_meta)
                else:
                    # FIXME: assert that meta matches fields on obj?
                    other_meta = None
                ident = Identifier.objects.create(
                    name=meta['id'],
                    content_type=ct,
                    object_id=obj.pk if obj else None,
                    meta=other_meta,
                )

            start_row, start_col, end_row, end_col = ranges[mtype][key]
            run.range_set.create(
                type='data',
                identifier=ident,
                start_col=start_col,
                end_col=end_col,
                start_row=start_row,
                end_row=end_row,
                count=count,
            )
    return load_row_identifiers(run)


def load_row_identifiers(run):
    ids = {}
    for rng in run.range_set.filter(type='data'):
        ident = rng.identifier
        ids.setdefault(ident.content_type, {})
        ids[ident.content_type][ident] = rng.count

    unknown_ids = 0
    idgroups = []
    for mtype in ids:
        idinfo = {
            'type_id': ctid(mtype),
            'type_label': mtype.name.title(),
            'ids': []
        }
        for ident, count in ids[mtype].items():
            meta = json.loads(ident.meta) if ident.meta else {}
            info = {
                'value': ident.name,
                'count': count,
                'meta': [{
                    'name': k,
                    'value': v
                } for k, v in meta.items()]
            }
            if ident.object_id is not None:
                info['match'] = str(ident.content_object)
            else:
                assert(ident.type == 'unresolved')
                unknown_ids += 1
                info['ident_id'] = ident.pk
                info['unknown'] = True
                choices = run.get_id_choices(
                    ident.content_type.model_class(), meta
                )
                info['choices'] = [{
                    'id': choice.pk,
                    'label': str(choice),
                } for choice in choices]
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
def update_row_identifiers(run, user, post):
    run.add_event('update_row_identifiers')
    unknown = run.range_set.filter(
        type='data',
        identifier__resolved=False,
    )
    for rng in unknown:
        ident = rng.identifier
        cls = ident.content_type.model_class()
        ident_id = post.get('ident_%s_id' % ident.pk, None)
        if not ident_id:
            continue
        if ident_id == 'new':
            # Create new object (with primary identifier)
            # FIXME: This assumes class is a wq.db IdentifiedModel
            obj = cls.objects.find(ident.name)
            meta = json.loads(ident.meta) if ident.meta else {}

            if meta:
                # Set additional metadata fields on new object
                for col, val in meta.items():
                    setattr(obj, col, val)
                obj.save()
        else:
            # Add new identifier to existing object for future reference
            obj = cls.objects.get(pk=ident_id)

        ident.object_id = obj.pk
        ident.save()

        new_metadata.send(
            sender=update_row_identifiers,
            run=run,
            object=obj,
            identifier=ident,
        )

    return read_row_identifiers(run, user)


@task
def import_data(run, user):
    """
    Import all parseable data from the dataset instance's IO class.
    """
    result = do_import(run, user)
    return result


def do_import(run, user):
    run.add_event('do_import')

    # (Re-)Load data and column information
    table = run.load_io()
    matched = get_columns(run)

    # Set global defaults for metadata values
    if not user.is_authenticated():
        user = None
    run_globals = {
        # Metadata fields
        metaname(Event): {},
        metaname(Report): {
            'user': user,
            'status_id': DEFAULT_STATUS,
        },
        # *.result_meta, *.parameter_meta, and *.site_meta are defined on a
        # case-by-case basis; see create_record() below

        # Result values indexed by parameter (for "horizontal" tables)
        'param_vals': {}
    }

    # Set default to None for any event key fields that are not required
    for field_name in EVENT_KEY:
        field = Event._meta.get_field(field_name)
        if field.null:
            run_globals[metaname(Event)][field_name] = None

    # Set any global defaults defined within data themselves (usually as extra
    # cells above the headers in a spreadsheet)
    for col in matched:
        if 'value' in col:
            save_value(col, col['value'], run_globals)

    # Loop through table rows and add each record
    rows = len(table)
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
            'message': "Importing Data...",
            'stage': 'data',
            'current': i + 1,
            'total': rows,
            'skipped': skipped
        })

        # Create report, capturing any errors
        try:
            report = create_report(run, row, run_globals, matched)
        except Exception as e:
            # Note exception in database
            report = None
            success = False
            fail_reason = repr(e)
            skipped.append({'row': rownum(i) + 1, 'reason': fail_reason})
        else:
            success = True
            fail_reason = None

        # Record relationship between data source and resulting report (or
        # skipped record), including specific cell range.
        run.record_set.create(
            row=rownum(i),
            content_object=report,
            success=success,
            fail_reason=fail_reason
        )

    # Send completion signal (in case any server handlers are registered)
    status = {
        'current': i + 1,
        'total': rows,
        'skipped': skipped
    }
    run.add_event('import_complete')
    run.record_count = run.record_set.filter(success=True).count()
    run.save()
    import_complete.send(sender=import_data, run=run, status=status)

    # FIXME: Shouldn't this happen automatically?
    current_task.update_state(state='SUCCESS', meta=status)

    # Return status (thereby updating task state for status() on view)
    return status


def create_report(run, row, instance_globals, matched):
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
            val = row[col['colnum']]
            if col['type'] == 'meta' and col['field_name'] == 'id':
                rng = run.range_set.filter(
                    type='data',
                    start_col__lte=col['colnum'],
                    end_col__gte=col['colnum'],
                    identifier__name__iexact=str(val),
                ).first()
                # FIXME: This assumes class is a wq.db IdentifiedModel
                if rng is not None:
                    val = rng.identifier.content_object.slug
            save_value(col, val, record)

    # Handle "vertical" table values (parsed as metadata by save_value())
    if metaname(Result) in record and metaname(Parameter) in record:
        # FIXME: handle other parameter & result metadata
        parameter_id = record['parameter_meta']['id']
        result_value = record['result_meta']['value']
        param = Parameter.objects.get(pk=parameter_id)
        record['param_vals'][param.slug] = result_value

    if metaname(Site) in record:
        # FIXME: Handle other site metadata
        site_id = record[metaname(Site)]['id']
        record[metaname(Event)]['site'] = site_id

    # Ensure complete Event natural key (http://wq.io/docs/erav#natural-key)
    missing = set(EVENT_KEY) - set(record[metaname(Event)].keys())
    if missing:
        raise Exception(
            'Incomplete Record - missing %s' % ", ".join(missing)
        )

    # Create report instance
    report = Report.objects.create_report(
        EventKey(**record[metaname(Event)]),
        record['param_vals'],
        **record[metaname(Report)]
    )
    return report


def save_value(col, val, obj):
    """
    For each cell in each row, use parsed col(umn) information to determine how
    to apply the cell val(ue) to the obj(ect hash).
    """
    if col['type'] == "instance":
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

    param = Parameter.objects.get(pk=parameter_id)
    vals[param.slug] = val


def save_metadata_value(col, val, obj):
    """
    This column was identified as a metadata field; update the metadata
    for the related object with the cell value from this row.
    """

    # Skip empty values
    if val is None or val == '' or not col['model']:
        return

    # Assign metadata property based on meta_field (MetaColumn.name).
    meta_key = '%s_meta' % col['model']
    app_label, model = col['model'].split('.')
    meta_cls = ContentType.objects.get(
        app_label=app_label, model=model
    ).model_class()
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
    if col['model'] == 'result':
        meta_datatype = None
    else:
        try:
            meta_datatype = meta_cls._meta.get_field(
                meta_field,
            ).get_internal_type()
        except:
            meta_datatype = None

    # Automatically parse date values as such
    if (meta_datatype in DATE_FIELDS and isinstance(val, string_types) and
            part != 'time'):
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
        if (isinstance(time, float) and
                time >= 100 and time <= 2400):
            # "Numeric" time (hour * 100 + minutes)
            time = str(time)
        elif isinstance(time, string_types) and ":" in time:
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
