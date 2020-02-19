from .base import BaseImportTestCase
from .data_app.models import Type, FKModel


class BaseFKTestCase(BaseImportTestCase):
    def setUp(self):
        super(BaseFKTestCase, self).setUp()
        Type.objects.create(pk=1, name="Type #1")
        Type.objects.create(pk=2, name="Type #2")

    def check_data(self, run, expect_last_record=None, extra_ranges=[]):
        if 'Imported' in expect_last_record:
            total = 4
        else:
            total = 3

        self.assert_status(run, total)
        self.assert_ranges(run, [
            "Data Column 'type -> type' at Rows 1-4, Column 0",
            "Data Column 'notes -> notes' at Rows 1-4, Column 1",
        ] + extra_ranges)
        self.assert_records(run, [
            "Imported 'Type #1 (Test Note 1)' at row 1",
            "Imported 'Type #1 (Test Note 2)' at row 2",
            "Imported 'Type #2 (Test Note 3)' at row 3",
            expect_last_record
        ])
        self.assert_urls(run, 'fkmodels/%s')


class ForeignKeyTestCase(BaseFKTestCase):
    serializer_name = 'data_wizard.registry.FKModelSerializer'
    row4_error = '{"type": ["Invalid pk \\"100\\" - object does not exist."]}'

    def test_manual(self):
        run = self.upload_file('fkid.csv')

        # Start data import process, wait for completion
        self.start_import(run, [{
            'row': 5,
            'reason': self.row4_error,
        }])

        # Verify results
        self.check_data(
            run,
            expect_last_record="Failed at row 4: %s" % self.row4_error,
        )
        self.assert_log(run, [
            'created',
            'do_import',
            'parse_columns',
            'import_complete',
        ])

    def test_auto_idmap_never(self):
        # Should abort due to previously unmapped type ids
        run = self.upload_file('fkid.csv')
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'parse_row_identifiers',
        ])
        self.assert_ranges(run, [
            "Data Column 'type -> type' at Rows 1-4, Column 0",
            "Data Column 'notes -> notes' at Rows 1-4, Column 1",
            "Cell value 'Unresolved: 1' at Rows 1-2, Column 0",
            "Cell value 'Unresolved: 2' at Row 3, Column 0",
            "Cell value 'Unresolved: 100' at Row 4, Column 0",
        ])

    def test_auto_idmap_existing(self):
        # Should auto-map existing ids 1 & 2, but abort due to unknown id 100
        self.serializer_name = 'tests.data_app.wizard.FKMapExistingSerializer'
        run = self.upload_file('fkid.csv')
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'parse_row_identifiers',
        ])
        self.assert_ranges(run, [
            "Data Column 'type -> type' at Rows 1-4, Column 0",
            "Data Column 'notes -> notes' at Rows 1-4, Column 1",
            "Cell value '1 -> type=1' at Rows 1-2, Column 0",
            "Cell value '2 -> type=2' at Row 3, Column 0",
            "Cell value 'Unresolved: 100' at Row 4, Column 0",
        ])

    def test_auto_idmap_always(self):
        # Map all ids without checking, producing same result as test_manual

        self.serializer_name = 'tests.data_app.wizard.FKMapAlwaysSerializer'
        run = self.upload_file('fkid.csv')

        self.auto_import(run, expect_input_required=False)

        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'parse_row_identifiers',
            'do_import',
            'import_complete',
        ])

        self.check_data(
            run,
            expect_last_record="Failed at row 4: %s" % self.row4_error,
            extra_ranges=[
                "Cell value '1 -> type=1' at Rows 1-2, Column 0",
                "Cell value '2 -> type=2' at Row 3, Column 0",
                "Cell value '100 -> type=100' at Row 4, Column 0",
            ]
        )


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
            run, expect_last_record="Failed at row 4: %s" % row4_error
        )
        self.assert_log(run, [
            'created',
            'do_import',
            'parse_columns',
            'import_complete',
        ])

    def test_auto_idmap_never(self):
        # Should abort due to previously unmapped type ids
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
            expect_last_record="Imported 'Type #2 (Test Note 4)' at row 4",
            extra_ranges=[
                "Cell value 'Type #1 -> type=Type #1' at Rows 1-2, Column 0",
                "Cell value 'Type #2 -> type=Type #2' at Row 3, Column 0",
                "Cell value 'Type #2 - Alternate Name -> type=Type #2'"
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

    def test_auto_idmap_never_preset(self):
        self.create_identifier('Type #1', 'type', 'Type #1')
        self.create_identifier('Type #2', 'type', 'Type #2')
        self.create_identifier('Type #2 - Alternate Name', 'type', 'Type #2')

        # Should succeed due to premapped type ids
        run = self.upload_file('fkname.csv')
        self.auto_import(run, expect_input_required=False)
        self.check_data(
            run,
            expect_last_record="Imported 'Type #2 (Test Note 4)' at row 4",
            extra_ranges=[
                "Cell value 'Type #1 -> type=Type #1' at Rows 1-2, Column 0",
                "Cell value 'Type #2 -> type=Type #2' at Row 3, Column 0",
                "Cell value 'Type #2 - Alternate Name -> type=Type #2'"
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

    def test_auto_idmap_existing(self):
        # Should auto-map 2 existing slugs, but abort due to unknown Alt Name
        self.serializer_name = (
            'tests.data_app.wizard.SlugMapExistingSerializer'
        )
        run = self.upload_file('fkname.csv')
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'parse_row_identifiers',
        ])
        self.assert_ranges(run, [
            "Data Column 'type -> type' at Rows 1-4, Column 0",
            "Data Column 'notes -> notes' at Rows 1-4, Column 1",
            "Cell value 'Type #1 -> type=Type #1' at Rows 1-2, Column 0",
            "Cell value 'Type #2 -> type=Type #2' at Row 3, Column 0",
            "Cell value 'Unresolved: Type #2 - Alternate Name'"
            " at Row 4, Column 0"
        ])

        # Update identifiers and try again
        self.update_row_identifiers(run, {
            'data_app.type': {
                'Type #2 - Alternate Name': 'Type #2',
            }
        })
        self.auto_import(run, expect_input_required=False)
        self.check_data(
            run,
            expect_last_record="Imported 'Type #2 (Test Note 4)' at row 4",
            extra_ranges=[
                "Cell value 'Type #1 -> type=Type #1' at Rows 1-2, Column 0",
                "Cell value 'Type #2 -> type=Type #2' at Row 3, Column 0",
                "Cell value 'Type #2 - Alternate Name -> type=Type #2'"
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


class SplitTestCase(BaseFKTestCase):
    serializer_name = 'tests.data_app.wizard.SlugSerializer'

    def test_manual(self):
        run = self.upload_file('fksplit.csv')
        row4_error = ('{"type": ["Object with name=Type #2 - Alternate Name'
                      ' does not exist."]}')

        # 4 columns, all unmatched
        self.check_columns(run, 4, 4)
        self.update_columns(run, {
            'Fk Model': {
                'type group': 'type',
                'type num': 'type',
                'notes 1': 'notes',
                'notes 2': 'notes',
            }
        })

        # Start data import process, wait for completion
        self.start_import(run, [{
            'row': 5,
            'reason': row4_error,
        }])

        # Verify results
        self.check_data(
            run, expect_last_record="Failed at row 4: %s" % row4_error
        )
        self.assert_log(run, [
            'created',
            'parse_columns',
            'update_columns',
            'do_import',
            'import_complete',
        ])

    def test_auto(self):
        # Should abort due to unknown columns
        run = self.upload_file('fksplit.csv')
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
        ])

        # Update columns and try again
        self.update_columns(run, {
            'Fk Model': {
                'type group': 'type',
                'type num': 'type',
                'notes 1': 'notes',
                'notes 2': 'notes',
            }
        })
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'update_columns',
            'auto_import',
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
            expect_last_record="Imported 'Type #2 (Test Note 4)' at row 4",
            extra_ranges=[
                "Cell value 'Type #1 -> type=Type #1'"
                " at Rows 1-2, Column 0-1",
                "Cell value 'Type #2 -> type=Type #2' at Row 3, Column 0-1",
                "Cell value 'Type #2 - Alternate Name -> type=Type #2'"
                " at Row 4, Column 0-1",
            ]
        )
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'update_columns',
            'auto_import',
            'parse_row_identifiers',
            'update_row_identifiers',
            'auto_import',
            'do_import',
            'import_complete',
        ])

    def test_auto_preset(self):
        self.create_identifier('type group', 'type')
        self.create_identifier('type num', 'type')
        self.create_identifier('notes 1', 'notes')
        self.create_identifier('notes 2', 'notes')
        self.create_identifier('Type #1', 'type', 'Type #1')
        self.create_identifier('Type #2', 'type', 'Type #2')
        self.create_identifier('Type #2 - Alternate Name', 'type', 'Type #2')

        # Should succeed due to premapped type ids
        run = self.upload_file('fksplit.csv')
        self.auto_import(run, expect_input_required=False)
        self.check_data(
            run,
            expect_last_record="Imported 'Type #2 (Test Note 4)' at row 4",
            extra_ranges=[
                "Cell value 'Type #1 -> type=Type #1'"
                " at Rows 1-2, Column 0-1",
                "Cell value 'Type #2 -> type=Type #2' at Row 3, Column 0-1",
                "Cell value 'Type #2 - Alternate Name -> type=Type #2'"
                " at Row 4, Column 0-1",
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

    def check_data(self, run, expect_last_record=None, extra_ranges=[]):
        if 'Imported' in expect_last_record:
            total = 4
        else:
            total = 3
        self.assert_status(run, total)
        self.assert_ranges(run, [
            "Data Column 'type group -> type' at Rows 1-4, Column 0",
            "Data Column 'type num -> type' at Rows 1-4, Column 1",
            "Data Column 'notes 1 -> notes' at Rows 1-4, Column 2",
            "Data Column 'notes 2 -> notes' at Rows 1-4, Column 3",
        ] + extra_ranges)
        self.assert_records(run, [
            "Imported 'Type #1 (Test Note 1)' at row 1",
            "Imported 'Type #1 (Test Note 2)' at row 2",
            "Imported 'Type #2 (Test Note 3)' at row 3",
            expect_last_record,
        ])
        self.assert_urls(run, 'fkmodels/%s')


class NestedTestCase(BaseImportTestCase):
    serializer_name = 'tests.data_app.wizard.NestedSerializer'

    def test_nested(self):
        run = self.upload_file('nested.csv')

        # Inspect unmatched columns and select choices
        self.check_columns(run, 2, 1)
        self.update_columns(run, {
            'Fkmodel': {
                'initial note': 'fkmodel[notes]'
            }
        })

        # Start data import process, wait for completion
        self.assertEqual(FKModel.objects.count(), 0)
        self.start_import(run, [])
        self.assert_status(run, 2)
        self.assert_records(run, [
            "Imported 'Type #1' at row 1",
            "Imported 'Type #2' at row 2",
        ])
        self.assertEqual(FKModel.objects.count(), 2)
