from django.conf.urls import include, url
from wq.db import rest


urlpatterns = [
    url(r'^', include(rest.router.urls))
]
