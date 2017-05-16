from django.conf import settings

if settings.WITH_WQDB:
    from wq.db import rest
    from wq.db.patterns import serializers as patterns
    from .models import Entity, Value

    class ValueSerializer(patterns.TypedAttachmentSerializer):
        class Meta:
            model = Value
            exclude = ['entity']
            object_field = 'entity'
            type_field = 'attribute'
            type_filter = {}

    class EntitySerializer(patterns.AttachedModelSerializer):
        values = ValueSerializer(many=True)

    rest.router.register_model(
        Entity,
        serializer=EntitySerializer,
        fields="__all__",
    )
