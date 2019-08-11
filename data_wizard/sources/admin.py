from django.contrib import admin

from data_wizard.admin import ImportActionModelAdmin
from .models import FileSource, URLSource

admin.site.register(FileSource, ImportActionModelAdmin)
admin.site.register(URLSource, ImportActionModelAdmin)
