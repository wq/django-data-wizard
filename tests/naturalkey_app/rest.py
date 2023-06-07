from django.conf import settings

if settings.WITH_WQDB:
    from wq.db import rest
    from .models import Note

    rest.router.register_model(
        Note,
        fields="__all__",
    )
