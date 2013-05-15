from wq.db.rest import app
from rest_framework import serializers
from wq.db.patterns.annotate.serializers import AnnotationSerializer

from .models import Result

class ResultSerializer(AnnotationSerializer):
    value = serializers.Field('value')
    class Meta:
        exclude = ('value_text', 'value_numeric')

app.router.register_serializer(Result, ResultSerializer)
