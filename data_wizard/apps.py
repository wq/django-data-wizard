from django.apps import AppConfig


class WizardConfig(AppConfig):
    name = 'data_wizard'

    def ready(self):
        self.module.autodiscover()
