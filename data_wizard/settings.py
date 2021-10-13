from rest_framework.settings import import_from_string as drf_import
from django.conf import settings


DEFAULTS = {
    "BACKEND": "data_wizard.backends.threading",
    "LOADER": "data_wizard.loaders.FileLoader",
    "IDMAP": "data_wizard.idmap.existing",
    "AUTHENTICATION": "rest_framework.authentication.SessionAuthentication",
    "PERMISSION": "rest_framework.permissions.IsAdminUser",
    "AUTO_IMPORT_TASKS": (
        "data_wizard.tasks.check_serializer",
        "data_wizard.tasks.check_iter",
        "data_wizard.tasks.check_columns",
        "data_wizard.tasks.check_row_identifiers",
        "data_wizard.tasks.import_data",
    ),
}


def get_setting(name):
    wizard_settings = getattr(settings, "DATA_WIZARD", {})
    return wizard_settings.get(name, DEFAULTS[name])


def import_from_string(path, setting_name):
    try:
        obj = drf_import(path, setting_name)
    except ImportError as e:
        if setting_name == "__task__":
            msg = e.args[0].replace(
                "API setting '__task__'",
                "Data Wizard task specifier",
            )
        else:
            msg = e.args[0].replace("API", "Data Wizard")
        raise ImportError(msg)
    else:
        return obj


def import_setting(name):
    path = get_setting(name)
    return import_from_string(path, name)
