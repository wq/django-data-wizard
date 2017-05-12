from django.conf import settings

if settings.WITH_WQDB:
    from wq.db import rest
    from .models import File

    rest.router.register_model(File, fields="__all__")
