from django.conf import settings

if settings.WITH_WQDB:
    from wq.db import rest
    from .models import SimpleModel, Type, FKModel

    rest.router.register_model(SimpleModel, fields="__all__")
    rest.router.register_model(Type, fields="__all__")
    rest.router.register_model(FKModel, fields="__all__")
