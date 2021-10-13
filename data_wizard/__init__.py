from django.utils.module_loading import autodiscover_modules
from .registry import registry
from .backends.base import wizard_task, InputNeeded
from . import idmap


__all__ = (
    "autodiscover",
    "backend",
    "registry",
    "register",
    "set_loader",
    "default_app_config",
    "idmap",
    "wizard_task",
    "InputNeeded",
)


backend = None
discovered = False


def autodiscover():
    global discovered
    if discovered:
        return
    autodiscover_modules("wizard", register_to=None)
    from . import tasks  # noqa

    discovered = True


def init_backend():
    global backend
    from .backends import create_backend

    backend = create_backend()


def register(*args, **kwargs):
    registry.register(*args, **kwargs)


def set_loader(*args, **kwargs):
    registry.set_loader(*args, **kwargs)


default_app_config = "data_wizard.apps.WizardConfig"
