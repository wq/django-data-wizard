from rest_framework import serializers
from .models import Entity, Value
from data_wizard import registry


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        fields = ("attribute", "value", "units")


class EAVSerializer(serializers.ModelSerializer):
    values = ValueSerializer(many=True)

    def create(self, validated_data):
        values_data = validated_data.pop('values', [])
        obj = super(EAVSerializer, self).create(validated_data)
        for value in values_data:
            value['entity'] = obj
            ValueSerializer().create(value)
        return obj

    class Meta:
        model = Entity
        fields = ("name", "values")


registry.register('EAV Model', EAVSerializer)
