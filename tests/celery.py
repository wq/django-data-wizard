from __future__ import absolute_import
import os

if os.environ.get("TEST_BACKEND") == "celery":
    from celery import Celery
    from django.conf import settings

    app = Celery("tests")
    app.config_from_object("django.conf:settings")
    app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
