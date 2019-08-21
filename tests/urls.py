from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django import VERSION as DJANGO_VERSION

if settings.WITH_WQDB:
    from wq.db import rest
    wizard_urls = [url(r'^', include(rest.router.urls))]
elif DJANGO_VERSION[0] < 2:
    wizard_urls = [
        url(r'^datawizard/', include('data_wizard.urls', 'data_wizard'))
    ]
else:
    wizard_urls = [url(r'^datawizard/', include('data_wizard.urls'))]


urlpatterns = [
    url(r'^admin/', admin.site.urls),
] + wizard_urls
