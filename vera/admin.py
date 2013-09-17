from wq.db.patterns import admin
from wq.db.patterns.models import Authority, RelationshipType
from wq.db.patterns.base import swapper
from django.conf import settings


class ParameterAdmin(admin.AnnotationTypeAdmin, admin.IdentifiedModelAdmin):
    list_display = ('name', 'units')
    list_filter = ('units', 'is_numeric')
    exclude = ('contenttype',)

default_admin = {
    'Site': admin.IdentifiedRelatedModelAdmin,
    'Event': admin.ModelAdmin,
    'Report': admin.AnnotatedModelAdmin,
    'ReportStatus': admin.ModelAdmin,
}

# Register models with admin, but only if they haven't been swapped
for model in default_admin:
    if swapper.is_swapped('vera', model):
        continue
    admin.site.register(
        swapper.load_model('vera', model),
        default_admin[model]
    )

# Register AnnotationType, if it hasn't been swapped
if not swapper.is_swapped('annotate', 'AnnotationType'):
    admin.site.register(
        swapper.load_model('annotate', 'AnnotationType'),
        admin.AnnotationTypeAdmin
    )

# Register Parameter, if AnnotationType has been swapped for it
if swapper.is_swapped('annotate', 'AnnotationType') == 'vera.Parameter':
    admin.site.register(
        swapper.load_model('annotate', 'AnnotationType'),
        ParameterAdmin,
    )

# Register additional type models, if installed
if 'wq.db.patterns.identify' in settings.INSTALLED_APPS:
    admin.site.register(Authority, admin.AuthorityAdmin)
if 'wq.db.patterns.relate' in settings.INSTALLED_APPS:
    admin.site.register(RelationshipType)
