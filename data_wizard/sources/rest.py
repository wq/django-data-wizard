from rest_framework import serializers
from wq.db import rest
from wq.db.rest.serializers import ModelSerializer
from .models import FileSource, URLSource
from ..rest import user_filter


class FileSourceSerializer(ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = FileSource
        fields = "__all__"


class URLSourceSerializer(ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = FileSource
        fields = "__all__"


rest.router.register_model(
    FileSource,
    serializer=FileSourceSerializer,
    background_sync=False,
    filter=user_filter,
)

rest.router.register_model(
    URLSource,
    serializer=URLSourceSerializer,
    background_sync=False,
    filter=user_filter,
)
