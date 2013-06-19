from wq.db.rest import app
from rest_framework import serializers
from wq.db.patterns.annotate.serializers import AnnotationSerializer, ModelSerializer

from .models import Result
from wq.db.patterns.base import swapper
Event = swapper.load_model('vera', 'Event')

class ResultSerializer(AnnotationSerializer):
    value = serializers.Field('value')
    class Meta:
        exclude = ('value_text', 'value_numeric')

class EventSerializer(ModelSerializer):
    annotations = serializers.Field('annotations')

app.router.register_serializer(Result, ResultSerializer)
app.router.register_serializer(Event, EventSerializer)
