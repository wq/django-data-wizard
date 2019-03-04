from django.conf import settings
from data_wizard.signals import progress
from rest_framework.settings import import_from_string


def create_backend():
    backend_path = getattr(
        settings,
        'DATA_WIZARD_BACKEND',
        'data_wizard.backends.celery.CeleryBackend'
    )
    backend_class = import_from_string(backend_path, 'DATA_WIZARD_BACKEND')
    backend = backend_class()
    progress.connect(backend.progress, weak=False)
    return backend
