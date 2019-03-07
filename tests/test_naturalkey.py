from .base import BaseImportTestCase
from tests.naturalkey_app.models import Place, Event


class NaturalKeyTestCase(BaseImportTestCase):
    serializer_name = 'tests.naturalkey_app.wizard.NoteSerializer'

    def test_manual(self):
        run = self.upload_file('naturalkey.csv')

        # Inspect unmatched columns and select choices
        self.check_columns(run, 3, 2)
        self.update_columns(run, {
            'Note': {
                'date': 'event[date]',
                'place': 'event[place][name]',
            }
        })

        # Start data import process, wait for completion
        self.start_import(run, [])

        # Verify results
        self.check_data(run)
        self.assert_log(run, [
            'created',
            'parse_columns',
            'update_columns',
            'do_import',
            'import_complete',
        ])

    def test_auto(self):
        # Map columns but not identifiers
        self.create_identifier('date', 'event[date]')
        self.create_identifier('place', 'event[place][name]')

        # Should abort due to unknown place identifiers
        run = self.upload_file('naturalkey.csv')
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'parse_row_identifiers',
        ])

    def test_auto_preset(self):
        mpls = Place.objects.find('mpls')
        chi = Place.objects.find('chi')

        # Map columns and place identifiers
        self.create_identifier('date', 'event[date]')
        self.create_identifier('place', 'event[place][name]')
        self.create_identifier('Minneapolis', 'event[place][name]', 'mpls')
        self.create_identifier('Chicago', 'event[place][name]', 'chi')

        # Should succeed since all identifers are mapped
        run = self.upload_file('naturalkey.csv')
        self.auto_import(run, expect_input_required=False)

        # Verify results
        self.check_data(run, extra_ranges=[
            "Cell value 'Minneapolis -> event[place][name]=mpls'"
            " at Rows 1-2, Column 0",
            "Cell value 'Chicago -> event[place][name]=chi'"
            " at Rows 3-4, Column 0",
        ])
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'parse_row_identifiers',
            'do_import',
            'import_complete',
        ])

        for record in run.record_set.all():
            self.assertIn(record.content_object.event.place, [mpls, chi])

    def test_manual_identifiers(self):
        # Create one place
        Place.objects.find('mpls')

        # Inspect unmatched columns and select choices
        run = self.upload_file('naturalkey.csv')
        self.check_columns(run, 3, 2)
        self.update_columns(run, {
            'Note': {
                'date': 'event[date]',
                'place': 'event[place][name]',
            }
        })

        # Match places (1 existing, 1 new)
        self.check_row_identifiers(run, 2, 2)
        self.update_row_identifiers(run, {
            'naturalkey_app.place': {
                'Minneapolis': 'mpls',
                'Chicago': 'new',
            }
        })

        # "new" place is not created until actual import
        self.assertEqual(Place.objects.count(), 1)

        # Start data import process, wait for completion
        self.start_import(run, [])

        # Verify results
        self.check_data(run, extra_ranges=[
            "Cell value 'Minneapolis -> event[place][name]=mpls'"
            " at Rows 1-2, Column 0",
            "Cell value 'Chicago -> event[place][name]=Chicago'"
            " at Rows 3-4, Column 0",
        ])
        self.assert_log(run, [
            'created',
            'parse_columns',
            'update_columns',
            'parse_row_identifiers',
            'update_row_identifiers',
            'do_import',
            'import_complete',
        ])

    def check_data(self, run, extra_ranges=[]):
        self.assertEqual(Event.objects.count(), 3)
        self.assertEqual(Place.objects.count(), 2)
        mpls, chi = Place.objects.order_by('pk')

        self.assert_status(run, 4)
        self.assert_ranges(run, [
            "Data Column 'place -> event[place][name]' at Rows 1-4, Column 0",
            "Data Column 'date -> event[date]' at Rows 1-4, Column 1",
            "Data Column 'note -> note' at Rows 1-4, Column 2",
        ] + extra_ranges)
        self.assert_records(run, [
            "Imported '%s on 2017-06-01: Test Note 1' at row 1" % mpls.name,
            "Imported '%s on 2017-06-01: Test Note 2' at row 2" % mpls.name,
            "Imported '%s on 2017-06-01: Test Note 3' at row 3" % chi.name,
            "Imported '%s on 2017-06-02: Test Note 4' at row 4" % chi.name,
        ])
        self.assert_urls(run, 'notes/%s')
