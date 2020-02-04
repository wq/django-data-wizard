from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


class WizardConfig(AppConfig):
    name = 'data_wizard'
    verbose_name = 'Data Wizard'

    def ready(self):
        from .compat import reverse

        self.module.autodiscover()
        self.module.init_backend()
