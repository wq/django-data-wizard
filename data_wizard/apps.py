from django.apps import AppConfig


class WizardConfig(AppConfig):
    name = 'data_wizard'
    verbose_name = 'Data Wizard'

    def ready(self):
        self.module.autodiscover()
        self.module.init_backend()
