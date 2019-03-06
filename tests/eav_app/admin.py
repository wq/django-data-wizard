from django.contrib import admin
from .models import Entity, Attribute, Value


class ValueInline(admin.TabularInline):
    model = Value


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    inlines = [ValueInline]


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    pass
