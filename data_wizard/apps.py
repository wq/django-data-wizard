from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from .compat import reverse


class WizardConfig(AppConfig):
    name = 'data_wizard'
    verbose_name = 'Data Wizard'

    def ready(self):
        self.module.autodiscover()
        self.module.init_backend()

        # FIXME: Drop this check in 2.0
        if reverse('data_wizard:run-list') == '/':
            raise ImproperlyConfigured(
                "data_wizard.urls at /, add 'datawizard/' prefix"
            )
