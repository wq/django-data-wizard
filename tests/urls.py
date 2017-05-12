from django.conf.urls import include, url
from django.conf import settings


if settings.WITH_WQDB:
    from wq.db import rest
    wizard_urls = rest.router.urls
else:
    wizard_urls = 'data_wizard.urls'


urlpatterns = [
    url(r'^', include(wizard_urls)),
]
