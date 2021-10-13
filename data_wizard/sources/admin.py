from django.contrib import admin

from data_wizard.admin import ImportActionModelAdmin
from .models import FileSource, URLSource


class SourceAdmin(ImportActionModelAdmin):
    readonly_fields = ("user",)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(FileSource, SourceAdmin)
admin.site.register(URLSource, SourceAdmin)
