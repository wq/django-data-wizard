from django.conf.urls import patterns, url

from wq.db.rest import app
from .views import StartImportView, ResetView

slug = app.router.SLUG
fmt  = app.router.FORMAT

urlpatterns = patterns('',
    url(slug + "import" + fmt,   StartImportView.as_view()),
    url(slug + "import$",        StartImportView.as_view()),
    url(slug + "reset" + fmt,    ResetView.as_view()),
    url(slug + "reset$",         ResetView.as_view()),
)
