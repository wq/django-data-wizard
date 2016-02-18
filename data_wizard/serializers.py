from rest_framework import serializers
from wq.db.rest.serializers import ModelSerializer, LabelRelatedField
from django.contrib.contenttypes.models import ContentType


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
