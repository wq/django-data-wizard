from wq.db.rest import app
from rest_framework import serializers
from wq.db.patterns.annotate.serializers import AnnotationSerializer
from wq.db.rest.serializers import ModelSerializer

from .models import Result
from wq.db.patterns.base import swapper
from wq.db.patterns.base.models import extract_nested_key
Event = swapper.load_model('vera', 'Event')
Report = swapper.load_model('vera', 'Report')

class ResultSerializer(AnnotationSerializer):
    value = serializers.Field()
    def to_native(self, obj):
        result = super(ResultSerializer, self).to_native(obj)
        if hasattr(obj.type, 'units'):
            result['units'] = obj.type.units
        return result

    class Meta(AnnotationSerializer.Meta):
        exclude = AnnotationSerializer.Meta.exclude + ('value_text', 'value_numeric')

class EventSerializer(ModelSerializer):
    annotations = serializers.Field()

class ReportSerializer(ModelSerializer):
    def from_native(self, data, files):
        data = data.dict()
        event_key = extract_nested_key(data, Event)
        if event_key:
            event, is_new = Event.objects.get_or_create_by_natural_key(*event_key)
            data['event'] = event.pk
        if 'request' in self.context and not data.get('user', None):
            user = self.context['request'].user
            if user.is_authenticated():
                data['user'] = user.pk
        return super(ReportSerializer, self).from_native(data, files)

app.router.register_serializer(Result, ResultSerializer)
app.router.register_serializer(Event, EventSerializer)
app.router.register_serializer(Report, ReportSerializer)
