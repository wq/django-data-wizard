from django.utils.module_loading import autodiscover_modules
from .registry import registry
from . import idmap


__all__ = (
    "autodiscover",
    "backend",
    "registry",
    "register",
    "set_loader",
    "default_app_config",
    "idmap",
)


backend = None


def autodiscover():
    autodiscover_modules('wizard', register_to=None)


def init_backend():
    global backend
    from .backends import create_backend
    backend = create_backend()


def register(*args, **kwargs):
    registry.register(*args, **kwargs)


def set_loader(*args, **kwargs):
    registry.set_loader(*args, **kwargs)


default_app_config = 'data_wizard.apps.WizardConfig'
