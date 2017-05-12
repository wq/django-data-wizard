from django.conf import settings

if settings.WITH_WQDB:
    from wq.db import rest
    from wq.db.patterns import serializers as patterns
    from .models import Note

    rest.router.register_model(
        Note,
        serializer=patterns.NaturalKeyModelSerializer,
        fields="__all__",
    )
