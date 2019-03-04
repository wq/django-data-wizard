from django.utils.module_loading import autodiscover_modules
from .registry import registry


__all__ = (
    "autodiscover",
    "backend",
    "registry",
    "default_app_config",
)


backend = None


def autodiscover():
    autodiscover_modules('wizard', register_to=None)


def init_backend():
    global backend
    from .backends import create_backend
    backend = create_backend()


default_app_config = 'data_wizard.apps.WizardConfig'
