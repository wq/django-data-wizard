from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin

if settings.WITH_WQDB:
    from wq.db import rest
    wizard_urls = [url(r'^', include(rest.router.urls))]
else:
    wizard_urls = [url(r'^datawizard/', include('data_wizard.urls'))]


urlpatterns = [
    url(r'^admin/', admin.site.urls),
] + wizard_urls
