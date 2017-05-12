from .base import BaseImportTestCase
from .data_app.models import Type


class BaseFKTestCase(BaseImportTestCase):
    def setUp(self):
        super(BaseFKTestCase, self).setUp()
        Type.objects.create(pk=1, name="Type #1")
        Type.objects.create(pk=2, name="Type #2")

    def check_data(self, run, expect_last_record=None, extra_ranges=[]):
        if 'imported' in expect_last_record:
            total = 4
        else:
            total = 3

        self.assert_status(run, total)
        self.assert_ranges(run, [
            "Data Column 'type -> type' at Rows 1-4, Column 0",
            "Data Column 'notes -> notes' at Rows 1-4, Column 1",
        ] + extra_ranges)
        self.assert_records(run, [
            "imported 'Type #1 (Test Note 1)' at row 1",
            "imported 'Type #1 (Test Note 2)' at row 2",
            "imported 'Type #2 (Test Note 3)' at row 3",
            expect_last_record
        ])
        self.assert_urls(run, 'fkmodels/%s')


class ForeignKeyTestCase(BaseFKTestCase):
    serializer_name = 'tests.data_app.wizard.FKSerializer'

    def test_manual(self):
        run = self.upload_file('fkid.csv')
        row4_error = ('{"type": ["Invalid pk \\"100\\"'
                      ' - object does not exist."]}')

        # Start data import process, wait for completion
        self.start_import(run, [{
            'row': 5,
            'reason': row4_error,
        }])

        # Verify results
        self.check_data(
            run, expect_last_record="failed at row 4: %s" % row4_error
        )
        self.assert_log(run, [
            'created',
            'do_import',
            'parse_columns',
            'import_complete',
        ])

    def test_auto(self):
        # Should abort due to unknown type id
        run = self.upload_file('fkid.csv')
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'parse_row_identifiers',
        ])


class SlugTestCase(BaseFKTestCase):
    serializer_name = 'tests.data_app.wizard.SlugSerializer'

    def test_manual(self):
        run = self.upload_file('fkname.csv')
        row4_error = ('{"type": ["Object with name=Type #2 - Alternate Name'
                      ' does not exist."]}')

        # Start data import process, wait for completion
        self.start_import(run, [{
            'row': 5,
            'reason': row4_error,
        }])

        # Verify results
        self.check_data(
            run, expect_last_record="failed at row 4: %s" % row4_error
        )
        self.assert_log(run, [
            'created',
            'do_import',
            'parse_columns',
            'import_complete',
        ])

    def test_auto(self):
        # Should abort due to unknown type id
        run = self.upload_file('fkname.csv')
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'parse_row_identifiers',
        ])

        # Update identifiers and try again
        self.update_row_identifiers(run, {
            'data_app.type': {
                'Type #1': 'Type #1',
                'Type #2': 'Type #2',
                'Type #2 - Alternate Name': 'Type #2',
            }
        })
        self.auto_import(run, expect_input_required=False)
        self.check_data(
            run,
            expect_last_record="imported 'Type #2 (Test Note 4)' at row 4",
            extra_ranges=[
                "Cell value 'Type #1 -> Type #1 (type)' at Rows 1-2, Column 0",
                "Cell value 'Type #2 -> Type #2 (type)' at Row 3, Column 0",
                "Cell value 'Type #2 - Alternate Name -> Type #2 (type)'"
                " at Row 4, Column 0",
            ]
        )
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'parse_row_identifiers',
            'update_row_identifiers',
            'auto_import',
            'do_import',
            'import_complete',
        ])

    def test_auto_preset(self):
        self.create_identifier('Type #1', 'type', 'Type #1')
        self.create_identifier('Type #2', 'type', 'Type #2')
        self.create_identifier('Type #2 - Alternate Name', 'type', 'Type #2')

        # Should succeed due to premapped type ids
        run = self.upload_file('fkname.csv')
        self.auto_import(run, expect_input_required=False)
        self.check_data(
            run,
            expect_last_record="imported 'Type #2 (Test Note 4)' at row 4",
            extra_ranges=[
                "Cell value 'Type #1 -> Type #1 (type)' at Rows 1-2, Column 0",
                "Cell value 'Type #2 -> Type #2 (type)' at Row 3, Column 0",
                "Cell value 'Type #2 - Alternate Name -> Type #2 (type)'"
                " at Row 4, Column 0",
            ]
        )
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'parse_row_identifiers',
            'do_import',
            'import_complete',
        ])
