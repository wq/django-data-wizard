from data_wizard.test import WizardTestCase
from data_wizard.sources.models import FileSource, URLSource
from django.conf import settings


class BaseImportTestCase(WizardTestCase):
    available_apps = (
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'data_wizard',
        'data_wizard.sources',
        'tests.data_app',
        'tests.naturalkey_app',
        'tests.eav_app',
    )
    with_wqdb = settings.WITH_WQDB
    file_url = '/filesources.json'
    file_model = FileSource
    file_content_type = 'sources.filesource'
    url_model = URLSource
    url_content_type = 'sources.urlsource'
