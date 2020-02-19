from rest_framework import serializers
from .models import SimpleModel, Type, FKModel, Address
import data_wizard


class IncompleteSerializer(serializers.ModelSerializer):
    # Serializer will report is_valid(), but save will fail

    date = serializers.CharField()  # Should be date field
    color = serializers.CharField()   # Should limit length (and choices)

    class Meta:
        model = SimpleModel
        fields = "__all__"
        data_wizard = {
            'show_in_list': False,
        }


# FKModelSerializer = Data Wizard default


class FKMapExistingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FKModel
        fields = "__all__"
        data_wizard = {
             'idmap': data_wizard.idmap.existing
        }


class FKMapAlwaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = FKModel
        fields = "__all__"
        data_wizard = {
             'idmap': data_wizard.idmap.always
        }


class SlugSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(
        queryset=Type.objects.all(),
        slug_field='name',
    )

    class Meta:
        model = FKModel
        fields = "__all__"


class SlugMapExistingSerializer(SlugSerializer):
    class Meta(SlugSerializer.Meta):
        data_wizard = {
             'idmap': data_wizard.idmap.existing
        }


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


class NumericCharField(serializers.CharField):
    def to_internal_value(self, data):
        if isinstance(data, float):
            data = int(data)
        return str(data)


class AddressSerializer(serializers.ModelSerializer):
    postal_code = NumericCharField()

    class Meta:
        model = Address
        fields = "__all__"


data_wizard.register(SimpleModel)
data_wizard.register('Simple Model - Incomplete', IncompleteSerializer)
data_wizard.register(FKModel)
data_wizard.register('FK Model - Use existing FKs', FKMapExistingSerializer)
data_wizard.register('FK Model - Use FKs always', FKMapAlwaysSerializer)
data_wizard.register('FK Model By Name', SlugSerializer)
data_wizard.register(
    'FK Model By Name - Use existing', SlugMapExistingSerializer,
)
data_wizard.register('New Type + FK Model', NestedSerializer)
data_wizard.register(Address)
data_wizard.register('Address with Zip Code', AddressSerializer)
