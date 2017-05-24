from rest_framework import serializers
from .models import SimpleModel, Type, FKModel
from data_wizard import registry


class SimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleModel
        fields = "__all__"


class FKSerializer(serializers.ModelSerializer):
    class Meta:
        model = FKModel
        fields = "__all__"


class SlugSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(
        queryset=Type.objects.all(),
        slug_field='name',
    )

    class Meta:
        model = FKModel
        fields = "__all__"


class NestedFKSerializer(serializers.ModelSerializer):
    class Meta:
        model = FKModel
        fields = ['notes']


class NestedSerializer(serializers.ModelSerializer):
    fkmodel = NestedFKSerializer()

    def create(self, validated_data):
        fkdata = validated_data.pop('fkmodel')
        instance = super(NestedSerializer, self).create(validated_data)
        fkdata['type'] = instance
        NestedFKSerializer().create(fkdata)
        return instance

    class Meta:
        model = Type
        fields = "__all__"


registry.register('Simple Model', SimpleSerializer)
registry.register('FK Model', FKSerializer)
registry.register('FK Model By Name', SlugSerializer)
registry.register('New Type + FK Model', NestedSerializer)
