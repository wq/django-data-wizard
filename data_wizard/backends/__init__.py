from data_wizard.signals import progress
from data_wizard.settings import get_setting, import_from_string


def create_backend():
    backend_path = get_setting('BACKEND')
    backend_class = import_from_string(backend_path + '.Backend', 'BACKEND')
    backend = backend_class()
    progress.connect(backend.progress, weak=False)
    return backend
