from django.conf import settings
from data_wizard.signals import progress
from rest_framework.settings import import_from_string


if getattr(settings, 'CELERY_RESULT_BACKEND', None):
    DEFAULT_BACKEND = 'data_wizard.backends.celery'
else:
    DEFAULT_BACKEND = 'data_wizard.backends.threading'


def create_backend():
    backend_path = getattr(
        settings,
        'DATA_WIZARD_BACKEND',
        DEFAULT_BACKEND,
    )
    backend_class = import_from_string(
        backend_path + '.Backend',
        'DATA_WIZARD_BACKEND'
    )
    backend = backend_class()
    progress.connect(backend.progress, weak=False)
    return backend
