from django.apps import AppConfig


class WizardConfig(AppConfig):
    name = "data_wizard"
    verbose_name = "Data Wizard"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        self.module.autodiscover()
        self.module.init_backend()
