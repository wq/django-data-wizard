from django.contrib import admin
from wq.db.patterns import admin as patterns
from wq.db.patterns.models import Relationship
from .models import MetaColumn, Range


class MetaColumnAdmin(patterns.IdentifiedModelAdmin):
    list_filter = ['type']


class RangeInline(admin.TabularInline):
    model = Range
    extra = 0


class RelationshipAdmin(admin.ModelAdmin):
    inlines = [RangeInline]

admin.site.register(MetaColumn, MetaColumnAdmin)
admin.site.register(Relationship, RelationshipAdmin)
