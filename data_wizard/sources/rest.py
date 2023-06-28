from rest_framework import serializers
from wq.db import rest
from wq.db.rest.serializers import ModelSerializer
from .models import FileSource, URLSource
from ..rest import user_filter


@rest.register(
    FileSource,
    url="filesources",
    background_sync=False,
    filter=user_filter,
    show_in_index="can_change",
    section="Data Wizard",
    order=200,
    icon="wizard",
)
class FileSourceSerializer(ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = FileSource
        fields = "__all__"



@rest.register(
    URLSource,
    url="urlsources",
    background_sync=False,
    filter=user_filter,
    show_in_index="can_change",
    section="Data Wizard",
    order=201,
    icon="wizard",
)
class URLSourceSerializer(ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = URLSource
        fields = "__all__"
