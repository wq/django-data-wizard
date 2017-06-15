from celery import task, current_task
from xlrd import colname
from collections import OrderedDict
from .models import Run, Identifier
from .signals import import_complete, new_metadata
from functools import wraps

from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from rest_framework import serializers
from natural_keys import NaturalKeySerializer
from html_json_forms import parse_json_form
import json

try:
    import reversion
except ImportError:
    reversion = None

User = get_user_model()


PRIORITY = {
    'instance': 1,
    'attribute': 2,
    'meta': 3,
    'unresolved': 4,
    'unknown': 5,
}


def get_ct(model):
    return ContentType.objects.get_for_model(model)


def ctid(ct):
    return '%s.%s' % (ct.app_label, ct.model)


def metaname(cls):
    return ctid(get_ct(cls)) + '_meta'


def get_id(obj, field):
    if isinstance(field, NaturalKeySerializer):
        data = list(type(field)(obj).data.values())
        return data[0]
    else:
        return field.to_representation(obj)


def update_state(state, meta):
    if not current_task:
        return
    current_task.update_state(state=state, meta=meta)


def lookuprun(fn):
    @wraps(fn)
    def wrapped(run, user=None, **kwargs):
        if not isinstance(run, Run):
            run = Run.objects.get(pk=run)
        if user and not isinstance(user, User):
            user = User.objects.get(pk=user)
        return fn(run, user, **kwargs)
    return wrapped


@task
@lookuprun
def auto_import(run, user):
    """
    Walk through all the steps necessary to interpret and import data from an
    IO.  Meant to be called asynchronously.  Automatically suspends import if
    any additional input is needed from the user.
    """
    run.add_event('auto_import')
    if not run.serializer:
        result = {
            'action': 'serializers',
            'message': 'Input Needed'
        }
        update_state(state='SUCCESS', meta=result)
        return result

    # Preload IO to catch any load errors early
    status = {
        'message': "Loading Data...",
        'stage': 'meta',
        'current': 1,
        'total': 4,
    }
    update_state(state='PROGRESS', meta=status)
    run.load_io()

    # Parse columns
    status.update(
        message="Parsing Columns...",
        current=2,
    )
    update_state(state='PROGRESS', meta=status)
    result = read_columns(run, user)
    if result['unknown_count']:
        result['action'] = "columns"
        result['message'] = "Input Needed"
        update_state(state='SUCCESS', meta=result)
        return result

    # Parse row identifiers
    status.update(
        message="Parsing Identifiers...",
        current=3,
    )
    update_state(state='PROGRESS', meta=status)
    result = read_row_identifiers(run, user)
    if result['unknown_count']:
        result['action'] = "ids"
        result['message'] = "Input Needed"
        update_state(state='SUCCESS', meta=result)
        return result

    status.update(
        message="Importing Data...",
        current=4,
    )

    # The rest is the same as import_data
    return do_import(run, user)


def get_attribute_field(field):
    for cname, cfield in field.child.get_fields().items():
        if isinstance(cfield, serializers.RelatedField):
            return cname, cfield


def get_choices(run):
    def make_list(choices):
        return [{
            'id': row.pk,
            'label': str(row),
        } for row in choices]

    Serializer = run.get_serializer()
    field_choices = set()

    def load_fields(serializer, group_name,
                    label_prefix="", name_prefix="",
                    attribute_name=None, attribute_choices=None):
        fields = serializer.get_fields().items()
        if len(fields) == 1 and isinstance(serializer, NaturalKeySerializer):
            is_natkey_lookup = True
        else:
            is_natkey_lookup = False
        for name, field in fields:
            if field.read_only:
                continue
            if name_prefix:
                qualname = name_prefix + ('[%s]' % name)
            else:
                qualname = name

            label = (field.label or name).title()
            if label_prefix:
                quallabel = label_prefix + " " + label
            else:
                quallabel = label

            if isinstance(field, NaturalKeySerializer):
                load_fields(
                    field, group_name,
                    label_prefix=quallabel, name_prefix=qualname
                )
            elif isinstance(field, serializers.ListSerializer):
                attr_name, attr_field = get_attribute_field(field)

                if not attr_field:
                    raise Exception("No attribute field found!")

                choices = make_list(attr_field.get_queryset())
                load_fields(
                    field.child,
                    group_name=quallabel,
                    label_prefix="",
                    name_prefix=qualname + '[]',
                    attribute_name=attr_name,
                    attribute_choices=choices,
                )
            elif attribute_choices:
                if isinstance(field, serializers.RelatedField):
                    continue
                for choice in attribute_choices:
                    field_choices.add((
                        group_name,
                        '%s;%s=%s' % (qualname, attribute_name, choice['id']),
                        '%s for %s' % (
                            label, choice['label']
                        ),
                        False,
                        field,
                    ))
            elif isinstance(field, serializers.ModelSerializer):
                load_fields(
                    field,
                    group_name=quallabel,
                    label_prefix="",
                    name_prefix=qualname,
                )
            else:
                if is_natkey_lookup:
                    is_lookup = True
                    lookup_field = serializer
                else:
                    is_lookup = isinstance(field, serializers.RelatedField)
                    lookup_field = field
                field_choices.add(
                    (group_name, qualname, quallabel, is_lookup, lookup_field)
                )

    load_fields(
        Serializer(),
        Serializer.Meta.model._meta.verbose_name.title(),
    )

    field_choices = sorted(field_choices, key=lambda d: d[1])

    choices = [{
        'id': name,
        'label': label,
        'is_lookup': is_lookup,
        'group': group_name,
        'field': field,
    } for group_name, name, label, is_lookup, field in field_choices]

    return choices


def get_choice_groups(run):
    choices = get_choices(run)
    groups = OrderedDict()

    for choice in choices:

        groups.setdefault(choice['group'], [])
        groups[choice['group']].append({
            'id': choice['id'],
            'label': choice['label'],
        })

    return [{
        'name': group,
        'choices': group_choices
    } for group, group_choices in groups.items()]


def get_choice_ids(run):
    return [choice['id'] for choice in get_choices(run)]


@task
@lookuprun
def read_columns(run, user=None):
    matched = get_columns(run)
    unknown_count = 0
    for info in matched:
        if info['type'] == 'unknown':
            unknown_count += 1
            # Add some useful context items for client
            info['unknown'] = True
            info['types'] = get_choice_groups(run)
        assert(info['type'] != 'unresolved')

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


def get_lookup_columns(run):
    cols = []
    choices = {
        choice['id']: choice
        for choice in get_choices(run)
        if choice['is_lookup']
    }
    for col in get_columns(run):
        if 'colnum' not in col or col['type'] != 'meta':
            continue
        if col['field_name'] not in choices:
            continue
        col = col.copy()
        info = choices[col['field_name']]
        if isinstance(info['field'], NaturalKeySerializer):
            # FIXME: how to override this?
            queryset = info['field'].Meta.model.objects.all()
        else:
            queryset = info['field'].get_queryset()

        col['serializer_field'] = info['field']
        col['queryset'] = queryset
        cols.append(col)
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
        elif ident.type == 'attribute':
            info['field_name'] = rng.identifier.field
            info['attr_id'] = rng.identifier.attr_id
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
            info['meta_value'] = get_range_value(
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
    matches = list(Identifier.objects.filter(
        serializer=run.serializer,
        name__iexact=name,
    ))
    if len(matches) > 0:
        matches.sort(
            key=lambda ident: PRIORITY.get(ident.type, 0)
        )
        ident = matches[0]
    else:
        if name in get_choice_ids(run):
            field = name
        else:
            field = None
        ident = Identifier.objects.create(
            serializer=run.serializer,
            name=name,
            field=field,
            resolved=(field is not None),
        )

    run.range_set.create(
        identifier=ident,
        **kwargs
    )


@task
@lookuprun
def update_columns(run, user, post={}):
    run.add_event('update_columns')
    matched = get_columns(run)
    for col in matched:
        if col['type'] != 'unknown':
            continue
        val = post.get('rel_%s' % col['rel_id'], None)
        if not val:
            continue

        ident = run.range_set.get(pk=col['rel_id']).identifier
        assert(ident.field is None)

        if val not in get_choice_ids(run):
            continue

        if ';' in val:
            field, attr_info = val.split(';')
            attr_name, attr_id = attr_info.split('=')
        else:
            field = val
            attr_id = None

        ident.field = field
        ident.attr_id = attr_id
        ident.resolved = True
        ident.save()

        new_metadata.send(
            sender=update_columns,
            run=run,
            identifier=ident,
        )

    return read_columns(run)


@task
@lookuprun
def read_row_identifiers(run, user=None):
    if run.range_set.filter(type='data').exists():
        return load_row_identifiers(run)
    else:
        return parse_row_identifiers(run)


def parse_row_identifiers(run):
    run.add_event('parse_row_identifiers')

    lookup_cols = get_lookup_columns(run)
    lookup_fields = OrderedDict()
    for col in lookup_cols:
        field_name = col['field_name']
        lookup_fields.setdefault(field_name, {
            'cols': [],
            'ids': OrderedDict(),
            'start_col': 1e10,
            'end_col': -1,
        })
        info = lookup_fields[field_name]
        info['cols'].append(col)
        info['start_col'] = min(info['start_col'], col['colnum'])
        info['end_col'] = max(info['end_col'], col['colnum'])
        assert(info['start_col'] < 1e10)
        assert(info['end_col'] > -1)

    table = run.load_io()
    for i, row in enumerate(table):
        for field_name, info in lookup_fields.items():
            names = [str(row[col['colnum']]) for col in info['cols']]
            name = " ".join(names)
            info['ids'].setdefault(name, {
                'count': 0,
                'start_row': 1e10,
                'end_row': -1,
            })
            idinfo = info['ids'][name]
            idinfo['count'] += 1
            rownum = i
            if table.tabular:
                rownum += table.start_row
            idinfo['start_row'] = min(idinfo['start_row'], rownum)
            idinfo['end_row'] = max(idinfo['end_row'], rownum)

            assert(idinfo['start_row'] < 1e10)
            assert(idinfo['end_row'] > -1)

    for field_name, info in lookup_fields.items():
        for name, idinfo in info['ids'].items():
            ident = Identifier.objects.filter(
                serializer=run.serializer,
                field=field_name,
                name__iexact=name,
            ).first()

            if not ident:
                ident = Identifier.objects.create(
                    serializer=run.serializer,
                    field=field_name,
                    name=name,
                )

            run.range_set.create(
                type='data',
                identifier=ident,
                start_col=info['start_col'],
                end_col=info['end_col'],
                start_row=idinfo['start_row'],
                end_row=idinfo['end_row'],
                count=idinfo['count'],
            )

    return load_row_identifiers(run)


def load_row_identifiers(run):
    ids = {}
    lookup_cols = get_lookup_columns(run)
    for rng in run.range_set.filter(type='data'):
        ident = rng.identifier
        info = None
        for col in lookup_cols:
            if col['field_name'] == ident.field:
                info = col
        if not info:
            continue
        model = info['queryset'].model
        ids.setdefault(model, {})
        ids[model][ident] = rng.count, info

    unknown_ids = 0
    idgroups = []
    for model in ids:
        mtype = get_ct(model)
        idinfo = {
            'type_id': ctid(mtype),
            'type_label': mtype.name.title(),
            'ids': []
        }
        for ident, (count, col) in ids[model].items():
            info = {
                'value': ident.name,
                'count': count,
            }
            if ident.resolved:
                info['match'] = ident.value or ident.name
            else:
                assert(ident.type == 'unresolved')
                unknown_ids += 1
                field = col['serializer_field']

                info['ident_id'] = ident.pk
                info['unknown'] = True
                info['choices'] = [{
                    'id': get_id(choice, field),
                    'label': str(choice),
                } for choice in col['queryset']]

                if isinstance(field, NaturalKeySerializer):
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
@lookuprun
def update_row_identifiers(run, user, post={}):
    run.add_event('update_row_identifiers')
    unknown = run.range_set.filter(
        type='data',
        identifier__resolved=False,
    )
    for rng in unknown:
        ident = rng.identifier
        ident_id = post.get('ident_%s_id' % ident.pk, None)
        if not ident_id:
            continue

        if ident_id == 'new':
            ident.value = ident.name
        else:
            ident.value = ident_id

        ident.resolved = True
        ident.save()

        new_metadata.send(
            sender=update_row_identifiers,
            run=run,
            identifier=ident,
        )

    return read_row_identifiers(run, user)


@task
@lookuprun
def import_data(run, user):
    """
    Import all parseable data from the dataset instance's IO class.
    """
    result = do_import(run, user)
    return result


def do_import(run, user):
    if reversion:
        with reversion.create_revision():
            reversion.set_user(user)
            reversion.set_comment('Imported via %s' % run)
            result = _do_import(run, user)
    else:
        result = _do_import(run, user)
    return result


def _do_import(run, user):
    run.add_event('do_import')

    # (Re-)Load data and column information
    table = run.load_io()
    matched = get_columns(run)

    # Set global defaults for metadata values
    if not user.is_authenticated():
        user = None

    run_globals = {
        # Metadata fields
    }

    # Set any global defaults defined within data themselves (usually as extra
    # cells above the headers in a spreadsheet)
    for col in matched:
        if 'meta_value' in col:
            save_value(col, col['meta_value'], run_globals)
        elif 'attr_id' in col:
            Serializer = run.get_serializer()
            basename = col['field_name'].split('[')[0]
            field = Serializer().get_fields().get(basename)
            if field:
                attr_name, attr_field = get_attribute_field(field)
                run_globals['_attr_field'] = '%s[][%s]' % (
                    basename, attr_name
                )

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
        update_state(state='PROGRESS', meta={
            'message': "Importing Data...",
            'stage': 'data',
            'current': i,
            'total': rows,
            'skipped': skipped
        })

        # Create report, capturing any errors
        obj, error = import_row(run, row, run_globals, matched)
        if error:
            success = False
            fail_reason = error
            skipped.append({'row': rownum(i) + 1, 'reason': fail_reason})
        else:
            success = True
            fail_reason = None

        # Record relationship between data source and resulting report (or
        # skipped record), including specific cell range.
        run.record_set.create(
            row=rownum(i),
            content_object=obj,
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
    update_state(state='SUCCESS', meta=status)

    # Return status (thereby updating task state for status() on view)
    return status


def import_row(run, row, instance_globals, matched):
    """
    Create actual report instance from parsed values.
    """

    # Copy global values to record hash
    record = {
        key: instance_globals[key]
        for key in instance_globals
    }

    for col in matched:
        if 'colnum' in col:
            val = row[col['colnum']]
            save_value(col, val, record)

    seen = set()
    for col in matched:
        field_name = col['field_name']
        if col['type'] == 'meta' and field_name not in seen:
            seen.add(field_name)
            ident = Identifier.objects.filter(
                serializer=run.serializer,
                name__iexact=str(record[field_name]),
            ).first()
            if ident and ident.value:
                record[field_name] = ident.value

    record.pop('_attr_index', None)
    record.pop('_attr_field', None)

    Serializer = run.get_serializer()
    try:
        serializer = Serializer(data=parse_json_form(record))
        if serializer.is_valid():
            with transaction.atomic():
                obj = serializer.save()
            error = None
        else:
            obj = None
            error = json.dumps(serializer.errors)
    except Exception as e:
        obj = None
        error = repr(e)
    return obj, error


def save_value(col, val, obj):
    """
    For each cell in each row, use parsed col(umn) information to determine how
    to apply the cell val(ue) to the obj(ect hash).

    """
    # In some spreadsheets (i.e. "horizontal" tables), multiple columns
    # indicate attribute names and each row contains result values.  In others
    # (i.e. "vertical" tables), each row lists both the attribute name and the
    # value.

    if col['type'] == "attribute":
        # Attribute value in a "horizontal" table
        save_attribute_value(col, val, obj)
    elif col['type'] == "meta":
        # Metadata value in either a "horizontal" or "vertical" table
        set_value(obj, col['field_name'], val)


def save_attribute_value(col, val, obj):
    """
    This column was identified as an EAV attribute; update nested array with
    the cell value from this row.
    """
    if '_attr_field' not in obj:
        raise Exception("Unexpected EAV value!")
    if '_attr_index' not in obj:
        obj['_attr_index'] = {
            col['attr_id']: 0
        }
    else:
        obj['_attr_index'].setdefault(
            col['attr_id'], (max(obj['_attr_index'].values()) or 0) + 1
        )

    index = obj['_attr_index'][col['attr_id']]
    value_field = col['field_name'].replace('[]', '[%s]' % index)
    attr_field = obj['_attr_field'].replace('[]', '[%s]' % index)
    set_value(obj, value_field, val)
    obj[attr_field] = col['attr_id']


def set_value(obj, field_name, val):
    if field_name in obj:
        val = "%s %s" % (obj[field_name], val)
    obj[field_name] = val
