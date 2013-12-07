from wq.db.patterns import admin
from wq.db.patterns.models import Relationship
from .models import MetaColumn, Range


class RangeInline(admin.TabularInline):
    model = Range
    extra = 0


class RelationshipAdmin(admin.ModelAdmin):
    inlines = [RangeInline]

admin.site.register(MetaColumn, admin.IdentifiedModelAdmin)
admin.site.register(Relationship, RelationshipAdmin)
