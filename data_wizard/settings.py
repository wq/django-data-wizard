from rest_framework.settings import import_from_string as drf_import
from django.conf import settings


DEFAULTS = {
    'BACKEND': 'data_wizard.backends.threading',
    'LOADER': 'data_wizard.loaders.FileLoader',
    'IDMAP': 'data_wizard.idmap.never',   # FIXME: Change to 'existing' in 2.0
    'AUTHENTICATION': 'rest_framework.authentication.SessionAuthentication',
    'PERMISSION': 'rest_framework.permissions.IsAdminUser',
}


def get_setting(name):
    #  FIXME: Drop this in 2.0
    if getattr(settings, 'CELERY_RESULT_BACKEND', None):
        DEFAULTS['BACKEND'] = 'data_wizard.backends.celery'

    wizard_settings = getattr(settings, 'DATA_WIZARD', {})
    return wizard_settings.get(name, DEFAULTS[name])


def import_from_string(path, setting_name):
    try:
        obj = drf_import(path, setting_name)
    except ImportError as e:
        msg = e.args[0].replace("API", "Data Wizard")
        raise ImportError(msg)
    else:
        return obj


def import_setting(name):
    path = get_setting(name)
    return import_from_string(path, name)
