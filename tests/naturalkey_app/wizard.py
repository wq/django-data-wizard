from natural_keys import NaturalKeyModelSerializer
from .models import Note
from data_wizard import registry


class NoteSerializer(NaturalKeyModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"


registry.register('Note', NoteSerializer)
