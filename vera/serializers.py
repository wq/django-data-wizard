from wq.db.rest import app
from rest_framework import serializers
from wq.db.patterns.base.serializers import TypedAttachmentSerializer
from wq.db.rest.serializers import ModelSerializer

import swapper
from wq.db.patterns.base.models import extract_nested_key
Event = swapper.load_model('vera', 'Event')
Parameter = swapper.load_model('vera', 'Parameter')
Result = swapper.load_model('vera', 'Result')


class ResultSerializer(TypedAttachmentSerializer):
    attachment_fields = ['id', 'value']
    type_model = Parameter
    value = serializers.Field()
    object_field = 'report'

    def to_native(self, obj):
        result = super(ResultSerializer, self).to_native(obj)
        if getattr(obj.type, 'units', None) is not None:
            result['units'] = obj.type.units
        has_parent = self.parent and hasattr(self.parent.opts, 'model')
        if not has_parent:
            result['report_id'] = obj.report.pk
        return result

    def from_native(self, data, files):
        obj = super(ResultSerializer, self).from_native(data, files)
        obj.value = data['value']
        return obj

    class Meta:
        exclude = ('label', 'report_id', 'report_label',
                   'value_text', 'value_numeric')


class EventSerializer(ModelSerializer):
    is_valid = serializers.Field()

    def get_default_fields(self, *args, **kwargs):
        fields = super(EventSerializer, self).get_default_fields(
            *args, **kwargs
        )
        if self.opts.depth > 0:
            Serializer = app.router.get_serializer_for_model(Result)
            fields['results'] = Serializer(context=self.context)
        return fields


class ReportSerializer(ModelSerializer):
    is_valid = serializers.Field()

    def from_native(self, data, files):
        if hasattr(data, 'dict'):
            data = data.dict()
        event_key = extract_nested_key(data, Event)
        if event_key:
            event, is_new = Event.objects.get_or_create_by_natural_key(
                *event_key
            )
            data['event'] = event.pk
        if 'request' in self.context and not data.get('user', None):
            user = self.context['request'].user
            if user.is_authenticated():
                data['user'] = user.pk
        return super(ReportSerializer, self).from_native(data, files)
