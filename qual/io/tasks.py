from celery import task
from xlrd import colname
from wq.io import ExcelFileIO
from wq.db.patterns.models import Identifier, RelationshipType
from wq.db.patterns.base import swapper
from wq.db.contrib.files.models import File
from .models import MetaColumn, UnknownItem, Range
from django.conf import settings
    
from wq.db.rest.models import get_ct, get_object_id
Parameter = swapper.load_model('annotate', 'AnnotationType')
CONTENT_TYPES = {
    File:     get_ct(File),
    Parameter: get_ct(Parameter),
    MetaColumn: get_ct(MetaColumn),
    UnknownItem: get_ct(UnknownItem),
}

if not CONTENT_TYPES[Parameter].is_identified:
    raise Exception("AnnotationType should be swapped for an IdentifiedModel!"
                 +  "\n(HINT: set WQ_ANNOTATIONTYPE_MODEL='qual.Parameter')")

PRIORITY = {
    'parameter': 1,
    'meta column': 2,
    'unknown item': 3,
}

def load_file(file_obj):
    filename = "%s/%s" % (settings.MEDIA_ROOT, file_obj.file.name)
    return ExcelFileIO(filename=filename)

def get_choices(file_obj):
    def make_list(cls, name):
        rows = cls.objects.exclude(
            pk__in = cls.objects.filter_by_related(
                file_obj
            ).values_list('id', flat=True)
        )
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
        make_list(Parameter,  "Parameter")
    ]

@task
def read_columns(file, with_rels=False):
    excel = load_file(file)
    matched_columns = []
    if with_rels:
        rels = []

    existing = file.relationships.filter(
        type__name='Contains Column'
    ).order_by('range__start_column')

    if existing.count() > 0:
        if with_rels:
            rels = existing
        for rel in existing:
            item = rel.right
            rng = rel.range_set.all()[0]
            if rng.start_row == excel.start_row:
                col = rng.start_column
                info = {
                    'name': excel.field_map.keys()[col],
                    'match': unicode(rel.right),
                    'column': colname(col),
                }
                if isinstance(rel.right, UnknownItem):
                    info['unknown'] = True
                matched_columns.append(info)
        
    else:
        for i, (name, attr_name) in enumerate(excel.field_map.items()):
            matches = list(Identifier.objects.filter_by_identifier(name))
            if len(matches) > 0:
                matches.sort(key=lambda ident: PRIORITY[ident.content_type.name])
                column = matches[0].content_object
                ctype = matches[0].content_type
            else:
                column = UnknownItem.objects.find(name)
                ctype  = CONTENT_TYPES[UnknownItem]

            reltype, is_new = RelationshipType.objects.get_or_create(
                from_type    = CONTENT_TYPES[File],
                to_type      = ctype,
                name         = 'Contains Column',
                inverse_name = 'Column In'
            )
            rel = file.relationships.create(
                type              = reltype,
                to_content_type   = ctype,
                to_object_id      = column.pk,
            )
            Range.objects.create(
                relationship = rel,
                start_row = excel.start_row,
                start_column = i,
                end_row = excel.start_row,
                end_column = i
            )
            info = {
                'name': name,
                'match': unicode(column),
                'column': colname(i),
            }
            if isinstance(column, UnknownItem):
                info['unknown'] = True
            matched_columns.append(info)
            if with_rels:
                rels.append(rel)

    for info in matched_columns:
        if info.get('unknown', False):
            info['types'] = get_choices(file)

    if with_rels:
        return matched_columns, rels
    else:
        return matched_columns

@task
def update_columns(file, post):
    matched_columns, rels = read_columns(file, True)
    for col, rel in zip(matched_columns, rels):
        if not col.get('unknown', False):
            continue
        val = post.get('column_%s' % col['column'], None)
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
            obj = cls.objects.find(col['name'])
        else:
            obj = cls.objects.get_by_identifier(vid)
            obj.identifiers.create(
                name = col['name']
            )

        reltype, is_new = RelationshipType.objects.get_or_create(
            from_type    = CONTENT_TYPES[File],
            to_type      = CONTENT_TYPES[cls],
            name         = 'Contains Column',
            inverse_name = 'Column In'
        )
        rel.type = reltype
        rel.right = obj
        rel.save()

    return read_columns(file)

@task
def reset(file):
    file.relationships.all().delete()
