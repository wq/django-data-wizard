from rest_framework import serializers
from wq.db.rest.serializers import ModelSerializer, LabelRelatedField
from wq.db.rest.models import ContentType, get_object_id


class CurrentUserDefault(serializers.CurrentUserDefault):
    def __call__(self):
        user = super(CurrentUserDefault, self).__call__()
        return user.pk


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


class RunSerializer(ModelSerializer):
    user_id = serializers.HiddenField(default=CurrentUserDefault())
    content_type_id = ContentTypeIdField(queryset=ContentType.objects.all())
    object_label = LabelRelatedField(
        source='content_object', read_only=True
    )

    class Meta:
        exclude = ['content_type']


class RecordSerializer(serializers.Serializer):
    row = serializers.SerializerMethodField()
    success = serializers.ReadOnlyField()
    fail_reason = serializers.ReadOnlyField()
    object_label = serializers.ReadOnlyField(source='content_object.__str__')
    object_url = serializers.SerializerMethodField()

    def get_row(self, instance):
        return instance.row + 1

    def get_object_url(self, instance):
        if not instance.content_type_id:
            return None
        ct = ContentType.objects.get(pk=instance.content_type_id)
        if not ct.urlbase:
            return None
        return "%s/%s" % (ct.urlbase, get_object_id(instance))
