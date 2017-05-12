from django.utils.module_loading import autodiscover_modules
from .registry import registry


__all__ = (
    "autodiscover",
    "registry",
    "default_app_config",
)


def autodiscover():
    autodiscover_modules('wizard', register_to=None)


default_app_config = 'data_wizard.apps.WizardConfig'
