from django.urls import include, path
from django.conf import settings
from django.contrib import admin
from django import VERSION as DJANGO_VERSION

if settings.WITH_WQDB:
    from wq.db import rest

    wizard_urls = [path("", rest.router.urls)]
else:
    wizard_urls = [path("datawizard/", include("data_wizard.urls"))]


urlpatterns = [
    path("admin/", admin.site.urls),
] + wizard_urls
