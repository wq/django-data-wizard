from celery import task, current_task
from xlrd import colname
from collections import namedtuple
from wq.io import load_file as load_file_io
from wq.db.patterns.models import Identifier, Relationship, RelationshipType
from wq.db.patterns.base import swapper
from wq.db.contrib.files.models import File
from wq.db.rest.caching import jc_backend
from .models import MetaColumn, UnknownItem, SkippedRecord, Range
from django.conf import settings
import datetime
from .signals import import_complete

from wq.db.rest.models import get_ct, get_object_id

Site = swapper.load_model('vera', 'Site')
Event = swapper.load_model('vera', 'Event')
Report = swapper.load_model('vera', 'Report')
ReportStatus = swapper.load_model('vera', 'ReportStatus')
Parameter = swapper.load_model('annotate', 'AnnotationType')
Result = swapper.load_model('annotate', 'Annotation')

EVENT_KEY = [val for val, cls in Event.get_natural_key_info()]
EventKey = namedtuple('EventKey', EVENT_KEY)

CONTENT_TYPES = {
    File: get_ct(File),
    Parameter: get_ct(Parameter),
    MetaColumn: get_ct(MetaColumn),
    UnknownItem: get_ct(UnknownItem),
}

DATE_FIELDS = {
    'DateTimeField': datetime.datetime,
    'DateField': datetime.date,
}

if hasattr(settings, 'WQ_DEFAULT_REPORT_STATUS'):
    DEFAULT_STATUS = ReportStatus.objects.get(
        pk=settings.WQ_DEFAULT_REPORT_STATUS
    )
else:
    DEFAULT_STATUS = None

if not CONTENT_TYPES[Parameter].is_identified:
    raise Exception("AnnotationType should be swapped for an IdentifiedModel!"
                    + "\n(HINT: set WQ_ANNOTATIONTYPE_MODEL='vera.Parameter')")

PRIORITY = {
    'parameter': 1,
    'meta column': 2,
    'unknown item': 3,
}


def load_file(file_obj):
    filename = "%s/%s" % (settings.MEDIA_ROOT, file_obj.file.name)
    options = load_file_options(file_obj)
    return load_file_io(filename, options=options)


def get_choices(file_obj):
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
def read_columns(file, user=None):
    if already_parsed(file):
        matched = load_columns(file)
    else:
        matched = parse_columns(file)

    for info in matched:
        if info.get('unknown', False):
            info['types'] = get_choices(file)

    return matched


def already_parsed(file):
    return file.relationships.filter(
        type__name='Contains Column',
        range__type='list'
    ).exists()


def load_file_options(file):
    headers = file.relationships.filter(
        type__name='Contains Column',
        range__type='list'
    )
    if headers.exists():
        header_row = headers[0].range_set.get(type='head').start_row
        start_row = headers[0].range_set.get(type='list').start_row
        return {
            'header_row': header_row,
            'start_row': start_row
        }

    templates = file.inverserelationships.filter(type__inverse_name='Template')
    if templates.exists():
        return load_file_options(templates[0].right)

    return {}


def load_columns(file):
    rels = file.relationships.filter(type__name='Contains Column')
    table = load_file(file)

    matched = []
    for rel in rels:
        item = rel.right
        info = {
            'match': unicode(item),
            'rel_id': rel.pk,
        }
        if isinstance(item, UnknownItem):
            info['unknown'] = True

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


def parse_columns(file):
    table = load_file(file)
    for r in table.extra_data:
        row = table.extra_data[r]
        for c in row:
            if c + 1 in row and c - 1 not in row:
                parse_column(
                    file,
                    name=row[c],
                    head=[r, c, r, c],
                    body=[r, c + 1, r, c + 1],
                    body_type='value'
                )

    for i, name in enumerate(table.field_map.keys()):
        parse_column(
            file,
            name=name,
            head=[table.header_row, i, table.start_row - 1, i],
            body=[table.start_row, i, table.start_row + len(table), i],
            body_type='list'
        )

    return load_columns(file)


def parse_column(file, name, head, body, body_type):
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
        from_type=CONTENT_TYPES[File],
        to_type=ctype,
        name='Contains Column',
        inverse_name='Column In'
    )
    rel = file.relationships.create(
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
def update_columns(file, user, post):
    matched = read_columns(file)
    for col in matched:
        if not col.get('unknown', False):
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

        item = file.relationships.get(pk=col['rel_id']).right
        if vid == 'new':
            obj = cls.objects.find(item.name)
            obj.contenttype = CONTENT_TYPES[Parameter]
            obj.save()
        else:
            obj = cls.objects.get_by_identifier(vid)
            obj.identifiers.create(
                name=item.name
            )

        reltype, is_new = RelationshipType.objects.get_or_create(
            from_type=CONTENT_TYPES[File],
            to_type=CONTENT_TYPES[cls],
            name='Contains Column',
            inverse_name='Column In'
        )
        rel = file.relationships.get(pk=col['rel_id'])
        rel.type = reltype
        rel.right = obj
        rel.save()

    return read_columns(file)


@task
def reset(file, user):
    file.relationships.all().delete()


@task
def import_data(file, user):
    matched = read_columns(file)
    table = load_file(file)
    if jc_backend:
        jc_backend.unpatch()

    for col in matched:
        col['item'] = file.relationships.get(pk=col['rel_id']).right
        col['item_id'] = get_object_id(col['item'])

    file_globals = {
        'event_key': {},
        'report_meta': {
            'user': user,
            'status': DEFAULT_STATUS,
        },
        'param_vals': {}
    }

    for field_name in EVENT_KEY:
        info = Event._meta.get_field_by_name(field_name)
        field = info[0]
        if field.null:
            file_globals['event_key'][field_name] = None

    def save_value(col, val, obj):
        item = col['item']
        if isinstance(item, Parameter):
            if col['item_id'] in obj['param_vals']:
                obj['param_vals'][col['item_id']] = "%s %s" % (
                    obj['param_vals'][col['item_id']],
                    val
                )
            else:
                obj['param_vals'][col['item_id']] = val
        elif isinstance(item, MetaColumn):
            if val is None or val == '':
                return
            if item.type == 'event':
                if '.' in item.name:
                    name, part = item.name.split('.')
                else:
                    name, part = item.name, None

                fld = Event._meta.get_field_by_name(
                    name
                )[0].get_internal_type()
                if (fld in DATE_FIELDS and isinstance(val, basestring)):
                    from dateutil.parser import parse
                    val = parse(val)
                    if fld == 'DateField':
                        val = val.date()

                # Handle date & time being separate columns
                if obj['event_key'].get(name) is not None:
                    other_val = obj['event_key'][name]
                    if not part:
                        raise Exception(
                            'Expected multi-column date and time for %s' % name
                        )
                    if part not in ('date', 'time'):
                        raise Exception(
                            'Unexpected field name: %s.%s!' % (name, part)
                        )
                    if part == 'date':
                        date, time = val, other_val
                    else:
                        date, time = other_val, val
                    if not isinstance(date, datetime.date):
                        raise Exception("Expected date but got %s!" % date)
                    if not isinstance(time, datetime.time):
                        if (isinstance(time, float)
                                and time >= 100 and time <= 2400):
                            time = str(time)
                            if len(time) == 3:
                                time = datetime.time(
                                    int(time[0]),
                                    int(time[1:2])
                                )
                            else:
                                time = datetime.time(
                                    int(time[0:1]),
                                    int(time[2:3])
                                )
                        else:
                            raise Exception("Expected time but got %s!" % time)
                    val = datetime.datetime.combine(date, time)

                obj['event_key'][name] = val
            elif item.type == 'report':
                obj['report_meta'][item.name] = val

    for col in matched:
        if 'value' in col:
            save_value(col, col['value'], file_globals)

    def add_record(row):
        record = {
            key: file_globals[key].copy()
            for key in file_globals
        }
        for col in matched:
            if 'colnum' in col:
                save_value(col, row[col['colnum']], record)

        if len(record['event_key'].keys()) < len(EVENT_KEY):
            raise Exception('Incomplete Record')

        return Report.objects.create_report(
            EventKey(**record['event_key']),
            record['param_vals'],
            **record['report_meta']
        )

    rows = len(table)
    errors = []
    skipped = []

    def rownum(i):
        return i + table.start_row + 1

    for i, row in enumerate(table):
        current_task.update_state(state='PROGRESS', meta={
            'current': i + 1,
            'total': rows,
            'skipped': skipped
        })
        skipreason = None
        try:
            report = add_record(row)
        except Exception as e:
            skipreason = repr(e)
            skipped.append({'row': rownum(i), 'reason': skipreason})
            report, is_new = SkippedRecord.objects.get_or_create(
                reason=skipreason
            )

        rel = file.create_relationship(
            report,
            'Contains Row',
            'Row In'
        )
        Range.objects.create(
            relationship=rel,
            type='row',
            start_row=i + table.start_row,
            start_column=0,
            end_row=i + table.start_row,
            end_column=len(row) - 1
        )

    status = {
        'current': i + 1,
        'total': rows,
        'skipped': skipped
    }
    if jc_backend:
        jc_backend.patch()
        if rows and rows > len(skipped):
            from johnny.cache import invalidate
            invalidate(*[
                cls._meta.db_table for cls in
                (File, Site, Event, Report, Parameter, Result, Relationship)
            ])

    import_complete.send(sender=import_data, file=file, status=status)
    return status
