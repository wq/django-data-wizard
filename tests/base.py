from data_wizard.test import WizardTestCase
from tests.file_app.models import File
from django.conf import settings


class BaseImportTestCase(WizardTestCase):
    available_apps = (
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'data_wizard',
        'tests.file_app',
        'tests.data_app',
        'tests.naturalkey_app',
        'tests.eav_app',
    )
    with_wqdb = settings.WITH_WQDB
    file_url = '/files.json'
    file_model = File
    file_content_type = 'file_app.file'
