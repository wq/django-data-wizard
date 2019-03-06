from django.contrib import admin
from .models import FileSource, URLSource


admin.site.register(FileSource)
admin.site.register(URLSource)
