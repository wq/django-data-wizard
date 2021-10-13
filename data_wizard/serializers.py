from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse, NoReverseMatch
from .models import Run, Record
from . import registry


# c.f SlugRelatedField
class ContentTypeIdField(serializers.RelatedField):
    default_error_messages = {
        "does_not_exist": "Content Type {app_label}.{model} does not exist.",
        "invalid": "Invalid value",
    }

    def to_internal_value(self, data):
        try:
            app_label, model = data.split(".")
        except ValueError:
            self.fail("invalid")
        try:
            return self.get_queryset().get(
                app_label=app_label,
                model=model,
            )
        except ContentType.DoesNotExist:
            self.fail("does_not_exist", app_label=app_label, model=model)

    def to_representation(self, value):
        return "%s.%s" % (value.app_label, value.model)


class RunSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    content_type_id = ContentTypeIdField(
        source="content_type", queryset=ContentType.objects.all()
    )
    label = serializers.ReadOnlyField(source="__str__")
    object_label = serializers.StringRelatedField(
        source="content_object", read_only=True
    )
    serializer_label = serializers.ReadOnlyField()
    last_update = serializers.ReadOnlyField()

    def get_fields(self):
        fields = super(RunSerializer, self).get_fields()
        fields["serializer"] = serializers.ChoiceField(
            choices=registry.get_choices(),
            required=False,
        )
        return fields

    class Meta:
        model = Run
        exclude = ["content_type"]


class RecordSerializer(serializers.ModelSerializer):
    row = serializers.SerializerMethodField()
    success = serializers.ReadOnlyField()
    fail_reason = serializers.ReadOnlyField()
    object_label = serializers.SerializerMethodField()
    object_url = serializers.SerializerMethodField()

    def get_row(self, instance):
        return instance.row + 1

    def get_object_label(self, instance):
        return str(instance.content_object)

    def get_object_url(self, instance):
        if not instance.content_object:
            return None
        obj = instance.content_object
        if hasattr(obj, "get_absolute_url"):
            object_url = obj.get_absolute_url()
        else:
            try:
                object_url = reverse(
                    "admin:{app}_{model}_change".format(
                        app=obj._meta.app_label,
                        model=obj._meta.model_name,
                    ),
                    args=[obj.pk],
                )
            except NoReverseMatch:
                object_url = None
        return object_url

    class Meta:
        model = Record
        fields = "__all__"
