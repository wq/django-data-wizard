from .base import BaseImportTestCase
from .eav_app.models import Attribute, Value


class EAVTestCase(BaseImportTestCase):
    serializer_name = 'tests.eav_app.wizard.EAVSerializer'
    attr_field = 'values[][attribute]'

    def setUp(self):
        super(EAVTestCase, self).setUp()
        Attribute.objects.create(pk=1, name="Temperature")
        Attribute.objects.create(pk=2, name="Notes")
        Attribute.objects.create(pk=3, name="Precipitation")

    def test_manual(self):
        run = self.upload_file('eav.csv')

        # Inspect unmatched columns and select choices
        self.check_columns(run, 6, 6)
        self.update_columns(run, {
            'Entity': {
                'place': 'name',
            }, 'Values': {
                'temperature': 'values[][value];attribute=1',
                'temperature units': 'values[][units];attribute=1',
                'precipitation': 'values[][value];attribute=3',
                'precipitation units': 'values[][units];attribute=3',
                'notes': 'values[][value];attribute=2',
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
        # Should abort since fields are not mapped
        run = self.upload_file('eav.csv')
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
        ])

    def test_auto_preset(self):
        # Initialize identifiers before auto import
        self.create_identifier('place', 'name')
        self.create_identifier('temperature', 'values[][value]', attr_id=1)
        self.create_identifier(
            'temperature units', 'values[][units]', attr_id=1
        )
        self.create_identifier('precipitation', 'values[][value]', attr_id=3)
        self.create_identifier(
            'precipitation units', 'values[][units]', attr_id=3
        )
        self.create_identifier('notes', 'values[][value]', attr_id=2)

        # Should succeed since fields are already mapped
        run = self.upload_file('eav.csv')
        self.auto_import(run, expect_input_required=False)

        # Verify results
        self.check_data(run)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'parse_row_identifiers',
            'do_import',
            'import_complete',
        ])

    def check_data(self, run):
        self.assert_status(run, 2)
        self.assert_ranges(run, [
            "Data Column 'place -> name' at Rows 1-2, Column 0",
            "Data Column 'temperature -> values.value (attribute=1)'"
            " at Rows 1-2, Column 1",
            "Data Column 'temperature units -> values.units (attribute=1)'"
            " at Rows 1-2, Column 2",
            "Data Column 'precipitation -> values.value (attribute=3)'"
            " at Rows 1-2, Column 3",
            "Data Column 'precipitation units -> values.units (attribute=3)'"
            " at Rows 1-2, Column 4",
            "Data Column 'notes -> values.value (attribute=2)'"
            " at Rows 1-2, Column 5",
        ])
        self.assert_records(run, [
            "Imported 'Minneapolis' at row 1",
            "Imported 'Chicago' at row 2",
        ])

        values = [str(value) for value in Value.objects.order_by('pk')]
        self.assertEqual(values, [
            'Temperature for Minneapolis: 20.8 C',
            'Precipitation for Minneapolis: 1 in',
            'Notes for Minneapolis: Test Note 1',
            'Temperature for Chicago: 70.2 F',
            'Precipitation for Chicago: 2 in',
            'Notes for Chicago: Test Note 2',
        ])
        self.assert_urls(run, 'entities/%s')
