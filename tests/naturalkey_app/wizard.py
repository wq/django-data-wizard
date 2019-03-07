from natural_keys import NaturalKeyModelSerializer
from .models import Note
from data_wizard import registry


class NoteSerializer(NaturalKeyModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"


class NoteMetaSerializer(NoteSerializer):
    class Meta(NoteSerializer.Meta):
        data_wizard = {
            'header_row': 3,
            'start_row': 4,
        }


registry.register('Multiple Events with Notes', NoteSerializer)
registry.register('Single Event with Notes', NoteMetaSerializer)
