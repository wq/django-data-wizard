from rest_framework import serializers
from .models import SimpleModel, Type, FKModel
import data_wizard


class IncompleteSerializer(serializers.ModelSerializer):
    # Serializer will report is_valid(), but save will fail

    date = serializers.CharField()  # Should be date field
    color = serializers.CharField()   # Should limit length (and choices)

    class Meta:
        model = SimpleModel
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


data_wizard.register(SimpleModel)
data_wizard.register('Simple Model - Incomplete', IncompleteSerializer)
data_wizard.register(FKModel)
data_wizard.register('FK Model By Name', SlugSerializer)
data_wizard.register('New Type + FK Model', NestedSerializer)
