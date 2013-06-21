from wq.db.rest import app
from rest_framework import serializers
from wq.db.patterns.annotate.serializers import AnnotationSerializer
from wq.db.rest.serializers import ModelSerializer

from .models import Result
from wq.db.patterns.base import swapper
Event = swapper.load_model('vera', 'Event')

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

app.router.register_serializer(Result, ResultSerializer)
app.router.register_serializer(Event, EventSerializer)
