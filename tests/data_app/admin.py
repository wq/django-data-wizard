from django.contrib import admin
from .models import SimpleModel, Type, FKModel


admin.site.register(SimpleModel)
admin.site.register(Type)
admin.site.register(FKModel)
