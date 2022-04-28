from django.contrib import admin
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from .models import Run, RunLog, Identifier, Range, Record
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _


class FixedTabularInline(admin.TabularInline):
    can_delete = False
    extra = 0

    def has_add_permission(self, request, obj):
        return False


class RangeInline(admin.TabularInline):
    model = Range
    fields = [
        "identifier",
        "type",
        "header_col",
        "start_col",
        "end_col",
        "header_row",
        "start_row",
        "end_row",
        "count",
    ]
    extra = 0


class RecordInline(FixedTabularInline):
    model = Record
    fields = readonly_fields = [
        "row",
        "success",
        "content_type",
        "content_object",
        "fail_reason",
    ]


class RunLogInline(FixedTabularInline):
    model = RunLog
    readonly_fields = ["event", "date"]


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "serializer_label",
        "record_count",
        "last_update",
    ]
    inlines = [RangeInline, RecordInline, RunLogInline]


@admin.register(Identifier)
class IdentifierAdmin(admin.ModelAdmin):
    list_display = [
        "serializer_label",
        "type_label",
        "name",
        "mapping_label",
        "resolved",
    ]
    list_display_links = ["name", "mapping_label"]
    list_filter = ["serializer"]


def start_data_wizard(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(
            request,
            "Select a single row to start data wizard.",
            level=messages.ERROR,
        )
        return
    instance = queryset.first()
    if isinstance(instance, Run):
        run = instance
    else:
        ct = ContentType.objects.get_for_model(queryset.model)
        run = Run.objects.create(
            user=request.user,
            content_type=ct,
            object_id=instance.pk,
        )
    return HttpResponseRedirect(
        reverse("data_wizard:run-serializers", kwargs={"pk": run.pk})
    )


start_data_wizard.short_description = _("Import via data wizard")


class ImportActionMixin(object):
    """
    Mixin with import functionality implemented as an admin action.
    """

    actions = [start_data_wizard]


class ImportActionModelAdmin(ImportActionMixin, admin.ModelAdmin):
    pass
