from django.conf.urls import patterns, include, url
from wq.db.rest import app
app.autodiscover()
urlpatterns = patterns('',
    url(r'^',       include(app.router.urls))
)
