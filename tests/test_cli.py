from django.core.management import call_command, CommandError
from django.test import TestCase
from tests.source_app.models import CustomSource
from tests.data_app.models import SimpleModel
from tests.naturalkey_app.models import Note, Place
from data_wizard.models import Identifier
from django.contrib.auth.models import User


class CLITestCase(TestCase):
    def setUp(self):
        User.objects.create(username='testuser')

    def test_auto(self):
        data = '[{"date": "2019-03-14", "color": "blue", "notes": "Test"}]'
        source = CustomSource.objects.create(json_data=data)
        call_command(
            'runwizard', 'source_app.customsource', str(source.pk),
            username='testuser',
        )
        instance = SimpleModel.objects.filter(
            date="2019-03-14",
            color="blue",
            notes="Test",
        ).first()
        self.assertTrue(instance)

    def test_need_input(self):
        data = '[{"time": "2019-03-14", "color": "blue", "message": "Test"}]'
        source = CustomSource.objects.create(json_data=data)
        with self.assertRaises(CommandError) as e:
            call_command(
                'runwizard', 'source_app.customsource', str(source.pk),
                username='testuser',
            )
        self.assertEqual(str(e.exception), "Input Needed for 2 columns")

    def test_specific_serializer(self):
        data = (
            '[{"event[date]": "2019-03-14",'
            '  "event[place][name]": "Minneapolis",'
            '  "note": "Test"}]'
        )
        source = CustomSource.objects.create(json_data=data)
        Place.objects.create(name="Minneapolis")
        Identifier.objects.create(
            serializer="tests.naturalkey_app.wizard.NoteSerializer",
            field="event[place][name]",
            name="Minneapolis",
            value="Minneapolis",
            resolved=True,
        )
        call_command(
            'runwizard', 'source_app.customsource', str(source.pk),
            serializer="tests.naturalkey_app.wizard.NoteSerializer",
            username='testuser',
        )
        instance = Note.objects.filter(
            event__date="2019-03-14",
            event__place__name="Minneapolis",
            note="Test",
        ).first()
        self.assertTrue(instance)

    def test_specific_serializer_need_input(self):
        data = (
            '[{"event[date]": "2019-03-14",'
            '  "event[place][name]": "Minneapolis",'
            '  "note": "Test"}]'
        )
        source = CustomSource.objects.create(json_data=data)
        with self.assertRaises(CommandError) as e:
            call_command(
                'runwizard', 'source_app.customsource', str(source.pk),
                serializer="tests.naturalkey_app.wizard.NoteSerializer",
                username='testuser',
            )
        self.assertEqual(str(e.exception), "Input Needed for 1 ids")
