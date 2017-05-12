from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Run, Record
from data_wizard import registry


# c.f SlugRelatedField
class ContentTypeIdField(serializers.RelatedField):
    default_error_messages = {
        'does_not_exist': 'Content Type {app_label}.{model} does not exist.',
        'invalid': 'Invalid value',
    }

    def to_internal_value(self, data):
        try:
            app_label, model = data.split('.')
        except ValueError:
            self.fail('invalid')
        try:
            return self.get_queryset().get(
                app_label=app_label,
                model=model,
            ).pk
        except ContentType.DoesNotExist:
            self.fail('does_not_exist', app_label=app_label, model=model)

    def to_representation(self, content_type_id):
        ct = ContentType.objects.get(pk=content_type_id)
        return '%s.%s' % (ct.app_label, ct.model)


class RunSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    content_type_id = ContentTypeIdField(queryset=ContentType.objects.all())
    object_label = serializers.StringRelatedField(
        source='content_object', read_only=True
    )

    def get_fields(self):
        fields = super(RunSerializer, self).get_fields()
        fields['serializer'] = serializers.ChoiceField(
            choices=registry.get_choices(),
        )
        return fields

    class Meta:
        model = Run
        exclude = ['content_type']


class RecordSerializer(serializers.ModelSerializer):
    row = serializers.SerializerMethodField()
    success = serializers.ReadOnlyField()
    fail_reason = serializers.ReadOnlyField()
    object_label = serializers.ReadOnlyField(source='content_object.__str__')
    object_url = serializers.SerializerMethodField()

    def get_row(self, instance):
        return instance.row + 1

    def get_object_url(self, instance):
        router = self.context.get('router', None)
        if not router:
            # Not using wq.db
            return

        return
        # FIXME:
        if not instance.content_type_id:
            return None
        ct = ContentType.objects.get(pk=instance.content_type_id)
        if not ct.urlbase:
            return None
        # return "%s/%s" % (ct.urlbase, get_object_id(instance.content_object))

    class Meta:
        model = Record
        fields = "__all__"
