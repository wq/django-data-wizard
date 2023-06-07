from django.conf import settings

if settings.WITH_WQDB:
    from wq.db import rest
    from .models import Entity, Value

    rest.router.register_model(
        Entity,
        nested_arrays=Value,
        fields="__all__",
    )
