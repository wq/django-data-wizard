from collections import OrderedDict
from .models import Identifier
from .signals import import_complete, new_metadata
from . import registry, wizard_task, InputNeeded

from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers
from natural_keys import NaturalKeySerializer
from html_json_forms import parse_json_form
import json
import logging

try:
    import reversion
except ImportError:
    reversion = None


PRIORITY = {
    "instance": 1,
    "attribute": 2,
    "meta": 3,
    "unresolved": 4,
    "unknown": 5,
}


def get_ct(model):
    return ContentType.objects.get_for_model(model)


def ctid(ct):
    return "%s.%s" % (ct.app_label, ct.model)


def metaname(cls):
    return ctid(get_ct(cls)) + "_meta"


def get_id(obj, field):
    if isinstance(field, NaturalKeySerializer):
        data = list(type(field)(obj).data.values())
        return data[0]
    else:
        return field.to_representation(obj)


def colname(i):
    if i >= 26:
        q, r = divmod(i, 26)
        return colname(q - 1) + colname(r)
    else:
        return chr(ord("A") + i)


@wizard_task(label="Processing Data", url_path="auto", use_async=True)
def auto_import(run):
    """
    Walk through all the steps necessary to interpret and import data from an
    Iter.  Meant to be called asynchronously.  Automatically suspends import if
    any additional input is needed from the user.
    """
    tasks = run.get_auto_import_tasks()
    run.add_event("auto_import")
    return run.run_all(tasks)


@wizard_task(label="Checking configuration...", url_path=False)
def check_serializer(run):
    if not run.serializer:
        raise InputNeeded("serializers")


@wizard_task(label="Serializers", url_path="serializers")
def list_serializers(run):
    result = {}
    result["serializer_choices"] = [
        {
            "name": s["class_name"],
            "label": s["name"],
        }
        for s in registry.get_serializers()
        if s["options"].get("show_in_list", True)
    ]
    return result


@wizard_task(label="Update Serializer")
def updateserializer(run, post={}):
    name = post.get("serializer", None)
    if name and registry.get_serializer(name):
        run.serializer = name
        run.save()
        run.add_event("update_serializer")

    result = list_serializers(run)
    result.update(
        current_mode="serializers",
    )
    return result


@wizard_task(label="Loading Data...", url_path=False)
def check_iter(run):
    # Preload Iter to catch any load errors early
    run.load_iter()


def get_attribute_field(field):
    for cname, cfield in field.child.fields.items():
        if isinstance(cfield, serializers.RelatedField):
            return cname, cfield
    return None, None


def compute_attr_field(value_field, attr_name):
    parts = value_field.split("[")
    parts[-1] = attr_name + "]"
    return "[".join(parts)


def get_choices(run):
    def make_list(choices):
        return [
            {
                "id": row.pk,
                "label": str(row),
            }
            for row in choices
        ]

    Serializer = run.get_serializer()
    field_choices = set()

    def load_fields(
        serializer,
        group_name,
        label_prefix="",
        name_prefix="",
        attribute_name=None,
        attribute_choices=None,
    ):
        fields = serializer.fields.items()
        if len(fields) == 1 and isinstance(serializer, NaturalKeySerializer):
            is_natkey_lookup = True
        else:
            is_natkey_lookup = False
        for name, field in fields:
            if field.read_only:
                continue
            if name_prefix:
                qualname = name_prefix + ("[%s]" % name)
            else:
                qualname = name

            label = (field.label or name).title()
            if label_prefix:
                quallabel = label_prefix + " " + label
            else:
                quallabel = label

            if isinstance(field, NaturalKeySerializer):
                load_fields(
                    field,
                    group_name,
                    label_prefix=quallabel,
                    name_prefix=qualname,
                )
            elif isinstance(field, serializers.ListSerializer):
                attr_name, attr_field = get_attribute_field(field)

                if not attr_field:
                    raise Exception(
                        "Could not determine EAV attribute field"
                        ' for nested "%s" serializer!' % qualname
                    )

                choices = make_list(attr_field.get_queryset())
                load_fields(
                    field.child,
                    group_name=quallabel,
                    label_prefix="",
                    name_prefix=qualname + "[]",
                    attribute_name=attr_name,
                    attribute_choices=choices,
                )
            elif attribute_choices:
                if isinstance(field, serializers.RelatedField):
                    continue
                for choice in attribute_choices:
                    field_choices.add(
                        (
                            group_name,
                            "%s;%s=%s"
                            % (qualname, attribute_name, choice["id"]),
                            "%s for %s" % (label, choice["label"]),
                            False,
                            field,
                        )
                    )
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

    if hasattr(Serializer, "Meta") and hasattr(Serializer.Meta, "model"):
        root_label = Serializer.Meta.model._meta.verbose_name.title()
    else:
        root_label = run.serializer_label

    serializer = Serializer(
        context={
            "data_wizard": {
                "run": run,
            }
        }
    )
    load_fields(serializer, root_label)

    field_choices.add(
        ("Other", "__ignore__", "Ignore this Column", False, None)
    )

    field_choices = sorted(field_choices, key=lambda d: d[1])

    choices = [
        {
            "id": name,
            "label": label,
            "is_lookup": is_lookup,
            "group": group_name,
            "field": field,
        }
        for group_name, name, label, is_lookup, field in field_choices
    ]

    return choices


def get_choice_groups(run):
    choices = get_choices(run)
    groups = OrderedDict()

    for choice in choices:

        groups.setdefault(choice["group"], [])
        groups[choice["group"]].append(
            {
                "id": choice["id"],
                "label": choice["label"],
            }
        )

    return [
        {"name": group, "choices": group_choices}
        for group, group_choices in groups.items()
    ]


def get_choice_ids(run):
    return [choice["id"] for choice in get_choices(run)]


@wizard_task(label="Parsing Columns...", url_path=False)
def check_columns(run):
    result = read_columns(run)
    if result["unknown_count"]:
        raise InputNeeded("columns", result["unknown_count"])
    return result


@wizard_task("Columns", url_path="columns")
def read_columns(run):
    matched = get_columns(run)
    unknown_count = 0
    for info in matched:
        if info["type"] == "unknown":
            unknown_count += 1
            # Add some useful context items for client
            info["unknown"] = True
            info["types"] = get_choice_groups(run)
        assert info["type"] != "unresolved"

    # Parse row identifiers
    return {
        "columns": matched,
        "unknown_count": unknown_count,
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
        choice["id"]: choice
        for choice in get_choices(run)
        if choice["is_lookup"]
    }
    for col in get_columns(run):
        if "colnum" not in col or col["type"] != "meta":
            continue
        if col["field_name"] not in choices:
            continue
        col = col.copy()
        info = choices[col["field_name"]]
        if isinstance(info["field"], NaturalKeySerializer):
            # FIXME: how to override this?
            queryset = info["field"].Meta.model.objects.all()
        else:
            queryset = info["field"].get_queryset()

        col["serializer_field"] = info["field"]
        col["queryset"] = queryset
        cols.append(col)
    return cols


def load_columns(run):
    table = run.load_iter()
    cols = list(table.field_map.keys())
    matched = []
    ranges = run.range_set.filter(
        identifier__serializer=run.serializer
    ).exclude(type="data")
    for rng in ranges:
        ident = rng.identifier
        info = {
            "match": str(ident),
            "mapping": ident.mapping_label,
            "rel_id": rng.pk,
            "type": ident.type,
        }

        if ident.type == "meta":
            info["field_name"] = rng.identifier.field
        elif ident.type == "attribute":
            info["field_name"] = rng.identifier.field
            info["attr_id"] = rng.identifier.attr_id
            info["attr_field"] = rng.identifier.attr_field
        else:
            info["value"] = ident.name

        if rng.type == "list":
            col = rng.start_col
            info["name"] = cols[col].replace("\n", " - ")
            info["column"] = colname(col)
            info["colnum"] = col

        elif rng.type == "value":
            info["name"] = get_range_value(
                table, rng, rng.header_col, rng.start_col - 1
            )
            info["meta_value"] = get_range_value(
                table, rng, rng.start_col, rng.end_col
            )
            info["colnum"] = rng.start_col
            info["rownum"] = rng.start_row
        matched.append(info)
    matched.sort(key=lambda info: info.get("colnum", -1))
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
    run.add_event("parse_columns")
    table = run.load_iter()
    if table.tabular:
        for r in table.extra_data:
            row = table.extra_data[r]
            for c in row:
                if c + 1 in row and c - 1 not in row:
                    parse_column(
                        run,
                        row[c],
                        type="value",
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
            type="list",
            header_row=header_row,
            start_row=start_row,
            end_row=start_row + len(table) - 1,
            start_col=i,
            end_col=i,
        )

    return load_columns(run)


def parse_column(run, name, **kwargs):
    matches = list(
        Identifier.objects.filter(
            serializer=run.serializer,
            name__iexact=name,
        )
    )
    if len(matches) > 0:
        matches.sort(key=lambda ident: PRIORITY.get(ident.type, 0))
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

    run.range_set.create(identifier=ident, **kwargs)


@wizard_task(label="Update Columns", url_path="updatecolumns")
def update_columns(run, post={}):
    run.add_event("update_columns")

    if isinstance(post.get("columns"), list):
        for col in post["columns"]:
            rel_id = col.get("id")
            mapping = col.get("mapping")
            if rel_id and mapping:
                post[f"rel_{rel_id}"] = mapping

    matched = get_columns(run)
    for col in matched:
        if col["type"] != "unknown":
            continue
        val = post.get("rel_%s" % col["rel_id"], None)
        if not val:
            continue

        ident = run.range_set.get(pk=col["rel_id"]).identifier
        assert ident.field is None

        if val not in get_choice_ids(run):
            continue

        if ";" in val:
            field, attr_info = val.split(";")
            attr_name, attr_id = attr_info.split("=")
            attr_field = compute_attr_field(field, attr_name)
        else:
            field = val
            attr_id = None
            attr_field = None

        ident.field = field
        ident.attr_id = attr_id
        ident.attr_field = attr_field
        ident.resolved = True
        ident.save()

        new_metadata.send(
            sender=update_columns,
            run=run,
            identifier=ident,
        )

    result = read_columns(run)
    result.update(
        current_mode="columns",
    )
    return result


@wizard_task(label="Parsing Identifiers...", url_path=False)
def check_row_identifiers(run):
    result = read_row_identifiers(run)
    if result["unknown_count"]:
        raise InputNeeded("ids", result["unknown_count"])
    return result


@wizard_task(label="Identifiers", url_path="ids")
def read_row_identifiers(run):
    if run.range_set.filter(type="data").exists():
        return load_row_identifiers(run)
    else:
        return parse_row_identifiers(run)


def parse_row_identifiers(run):
    run.add_event("parse_row_identifiers")

    idmap = run.get_idmap()
    lookup_cols = get_lookup_columns(run)
    lookup_fields = OrderedDict()
    for col in lookup_cols:
        field_name = col["field_name"]
        lookup_fields.setdefault(
            field_name,
            {
                "cols": [],
                "ids": OrderedDict(),
                "serializer_field": col["serializer_field"],
                "start_col": 1e10,
                "end_col": -1,
            },
        )
        info = lookup_fields[field_name]
        info["cols"].append(col)
        info["start_col"] = min(info["start_col"], col["colnum"])
        info["end_col"] = max(info["end_col"], col["colnum"])

        if "meta_value" in col:
            info["is_meta_value"] = True
            info["ids"] = {
                col["meta_value"]: {
                    "count": 1,
                    "start_row": col["rownum"],
                    "end_row": col["rownum"],
                }
            }

        assert info["start_col"] < 1e10
        assert info["end_col"] > -1

    table = run.load_iter()
    for i, row in enumerate(table):
        for field_name, info in lookup_fields.items():
            if "is_meta_value" in info:
                continue
            names = [str(row[col["colnum"]]) for col in info["cols"]]
            name = " ".join(names)
            info["ids"].setdefault(
                name,
                {
                    "count": 0,
                    "start_row": 1e10,
                    "end_row": -1,
                },
            )
            idinfo = info["ids"][name]
            idinfo["count"] += 1
            rownum = i
            if table.tabular:
                rownum += table.start_row
            idinfo["start_row"] = min(idinfo["start_row"], rownum)
            idinfo["end_row"] = max(idinfo["end_row"], rownum)

            assert idinfo["start_row"] < 1e10
            assert idinfo["end_row"] > -1

    for field_name, info in lookup_fields.items():
        for name, idinfo in info["ids"].items():
            ident = Identifier.objects.filter(
                serializer=run.serializer,
                field=field_name,
                name__iexact=name,
            ).first()

            if not ident:
                value = idmap(name, info["serializer_field"])
                ident = Identifier.objects.create(
                    serializer=run.serializer,
                    field=field_name,
                    name=name,
                    value=value,
                    resolved=value is not None,
                )

            run.range_set.create(
                type="data",
                identifier=ident,
                start_col=info["start_col"],
                end_col=info["end_col"],
                start_row=idinfo["start_row"],
                end_row=idinfo["end_row"],
                count=idinfo["count"],
            )

    return load_row_identifiers(run)


def load_row_identifiers(run):
    ids = {}
    lookup_cols = get_lookup_columns(run)
    for rng in run.range_set.filter(type="data"):
        ident = rng.identifier
        info = None
        for col in lookup_cols:
            if col["field_name"] == ident.field:
                info = col
        if not info:
            continue
        model = info["queryset"].model
        ids.setdefault(model, {})
        ids[model][ident] = rng.count, info

    unknown_ids = 0
    idgroups = []
    for model in ids:
        mtype = get_ct(model)
        idinfo = {
            "type_id": ctid(mtype),
            "type_label": mtype.name.title(),
            "ids": [],
        }
        for ident, (count, col) in ids[model].items():
            info = {
                "value": ident.name,
                "count": count,
            }
            if ident.resolved:
                info["match"] = ident.value or ident.name
            else:
                assert ident.type == "unresolved"
                unknown_ids += 1
                field = col["serializer_field"]

                info["ident_id"] = ident.pk
                info["unknown"] = True
                info["choices"] = [
                    {
                        "id": get_id(choice, field),
                        "label": str(choice),
                    }
                    for choice in col["queryset"]
                ]

                if isinstance(field, NaturalKeySerializer):
                    info["choices"].insert(
                        0,
                        {
                            "id": "new",
                            "label": "New %s" % idinfo["type_label"],
                        },
                    )

            idinfo["ids"].append(info)
        idinfo["ids"].sort(key=lambda info: info["value"])
        idgroups.append(idinfo)

    return {
        "unknown_count": unknown_ids,
        "types": idgroups,
    }


@wizard_task(label="Update Identifiers", url_path="updateids")
def update_row_identifiers(run, post={}):
    run.add_event("update_row_identifiers")

    for value in list(post.values()):
        if not isinstance(value, list):
            continue
        for ident in value:
            if not isinstance(ident, dict):
                continue

            ident_id = ident.get("id")
            mapping = ident.get("mapping")
            if ident_id and mapping:
                post[f"ident_{ident_id}_id"] = mapping

    unknown = run.range_set.filter(
        type="data",
        identifier__resolved=False,
    )
    for rng in unknown:
        ident = rng.identifier
        ident_id = post.get("ident_%s_id" % ident.pk, None)
        if not ident_id:
            continue

        if ident_id == "new":
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

    result = read_row_identifiers(run)
    result.update(
        current_mode="ids",
    )
    return result


@wizard_task(label="Importing Data...", url_path="data", use_async=True)
def import_data(run):
    """
    Import all parseable data from the dataset instance's Iter class.
    """
    if reversion:
        with reversion.create_revision():
            reversion.set_user(run.user)
            reversion.set_comment("Imported via %s" % run)
            result = _do_import(run)
    else:
        result = _do_import(run)
    return result


def get_rows(run):
    # (Re-)Load data and column information
    table = run.load_iter()
    matched = get_columns(run)

    # Set any global defaults defined within data themselves (usually as extra
    # cells above the headers in a spreadsheet)
    run_globals = {}
    for col in matched:
        if "meta_value" in col:
            save_value(col, col["meta_value"], run_globals)

    for row in table:
        yield build_row(run, row, run_globals, matched)


def _do_import(run):
    run.add_event("do_import")

    # Loop through table rows and add each record
    table = run.load_iter()
    rows = len(table)
    skipped = []

    if table.tabular:

        def rownum(i):
            return i + table.start_row

    else:

        def rownum(i):
            return i

    for i, row in enumerate(get_rows(run)):
        # Update state (for status() on view)
        run.send_progress(
            {
                "message": "Importing Data...",
                "stage": "data",
                "current": i,
                "total": rows,
                "skipped": skipped,
            }
        )

        # Create report, capturing any errors
        obj, error = import_row(run, i, row)
        if error:
            success = False
            fail_reason = error
            skipped.append({"row": rownum(i) + 1, "reason": fail_reason})
        else:
            success = True
            fail_reason = None

        # Record relationship between data source and resulting report (or
        # skipped record), including specific cell range.
        run.record_set.create(
            row=rownum(i),
            content_object=obj,
            success=success,
            fail_reason=fail_reason,
        )

    # Send completion signal (in case any server handlers are registered)
    status = {"current": i + 1, "total": rows, "skipped": skipped}
    run.add_event("import_complete")
    run.record_count = run.record_set.filter(success=True).count()
    run.save()
    run.send_progress(status, state="SUCCESS")
    import_complete.send(sender=import_data, run=run, status=status)

    return status


def build_row(run, row, instance_globals, matched):
    """
    Compile spreadsheet row into serializer data format
    """

    # Copy global values to record hash
    record = {key: instance_globals[key] for key in instance_globals}

    for col in matched:
        if "colnum" in col and "meta_value" not in col:
            val = row[col["colnum"]]
            save_value(col, val, record)

    seen = set()
    for col in matched:
        field_name = col["field_name"]
        if col["type"] == "meta" and field_name not in seen:
            seen.add(field_name)
            ident = Identifier.objects.filter(
                serializer=run.serializer,
                name__iexact=str(record[field_name]),
            ).first()
            if ident and ident.value:
                record[field_name] = ident.value

    record.pop("_attr_index", None)

    return parse_json_form(record)


def import_row(run, i, record):
    """
    Create actual report instance from parsed values.
    """
    Serializer = run.get_serializer()
    try:
        serializer = Serializer(
            data=record,
            context={
                "data_wizard": {
                    "run": run,
                    "row": i,
                }
            },
        )
        if serializer.is_valid():
            with transaction.atomic():
                obj = serializer.save()
            error = None
        else:
            obj = None
            error = json.dumps(serializer.errors)
    except Exception as e:
        logging.warning(
            "{run}: Error In Row {row}".format(
                run=run,
                row=i,
            )
        )
        logging.exception(e)
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

    if col["type"] == "attribute":
        # Attribute value in a "horizontal" table
        save_attribute_value(col, val, obj)
    elif col["type"] == "meta":
        # Metadata value in either a "horizontal" or "vertical" table
        set_value(obj, col["field_name"], val)


def save_attribute_value(col, val, obj):
    """
    This column was identified as an EAV attribute; update nested array with
    the cell value from this row.
    """
    if "attr_field" not in col:
        raise Exception("Unexpected EAV value!")
    if "_attr_index" not in obj:
        obj["_attr_index"] = {col["attr_id"]: 0}
    else:
        obj["_attr_index"].setdefault(
            col["attr_id"], (max(obj["_attr_index"].values()) or 0) + 1
        )

    index = obj["_attr_index"][col["attr_id"]]
    value_field = col["field_name"].replace("[]", "[%s]" % index)
    attr_field = col["attr_field"].replace("[]", "[%s]" % index)
    set_value(obj, value_field, val)
    obj[attr_field] = col["attr_id"]


def set_value(obj, field_name, val):
    if field_name in obj and val is not None:
        if obj[field_name] is None:
            obj[field_name] = val
        else:
            val = "%s %s" % (obj[field_name], val)
    obj[field_name] = val
