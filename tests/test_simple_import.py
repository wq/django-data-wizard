from .base import BaseImportTestCase


class SimpleTestCase(BaseImportTestCase):
    serializer_name = 'data_wizard.registry.SimpleModelSerializer'

    def test_manual(self):
        run = self.upload_file('simplemodel.csv')

        # Inspect unmatched columns and select choices
        self.check_columns(run, 3, 1)
        self.update_columns(run, {
            'Simple Model': {
                'field notes': 'notes'
            }
        })

        # Start data import process, wait for completion
        self.start_import(run, [{
            'row': 5,
            'reason': '{"color": ["\\"orange\\" is not a valid choice."]}'
        }, {
            'row': 6,
            'reason': '{"date": ["Date has wrong format.'
                      ' Use one of these formats instead: YYYY-MM-DD."]}'
        }])

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
        # Should abort since "field notes" is not mapped
        run = self.upload_file('simplemodel.csv')
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
        ])

    def test_auto_no_serializer(self):
        # Should abort since no serializer is set
        run = self.upload_file('simplemodel.csv', skip_serializer=True)
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
        ])

    def test_auto_continue(self):
        # Should abort due to missing serializer
        run = self.upload_file('simplemodel.csv', skip_serializer=True)
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
        ])

        # Set serializer and try again, should abort due to unknown column
        self.set_serializer(run)
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
            'update_serializer',
            'auto_import',
            'parse_columns',
        ])

        # Set column and try again, should work now
        self.update_columns(run, {
            'Simple Model': {
                'field notes': 'notes'
            }
        })
        self.auto_import(run, expect_input_required=False)

        # Verify results
        self.check_data(run)
        self.assert_log(run, [
            'created',
            'auto_import',
            'update_serializer',
            'auto_import',
            'parse_columns',
            'update_columns',
            'auto_import',
            'parse_row_identifiers',
            'do_import',
            'import_complete',
        ])

    def test_auto_preset(self):
        # Initialize identifier before auto import
        self.create_identifier('field notes', 'notes')

        # Should succeed since field notes is already mapped
        run = self.upload_file('simplemodel.csv')
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

    def test_auto_url(self):
        self.create_identifier('field notes', 'notes')
        run = self.download_url(
            'https://raw.githubusercontent.com/wq/django-data-wizard'
            '/master/tests/media/simplemodel.csv'
        )
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
        self.assert_status(run, 3)
        self.assert_ranges(run, [
            "Data Column 'date -> date' at Rows 1-5, Column 0",
            "Data Column 'color -> color' at Rows 1-5, Column 1",
            "Data Column 'field notes -> notes' at Rows 1-5, Column 2",
        ])
        self.assert_records(run, [
            "Imported '2017-06-01: red (Test Note 1)' at row 1",
            "Imported '2017-06-02: green (Test Note 2)' at row 2",
            "Imported '2017-06-03: blue (Test Note 3)' at row 3",
            "Failed at row 4:"
            ' {"color": ["\\"orange\\" is not a valid choice."]}',
            "Failed at row 5:"
            ' {"date": ["Date has wrong format.'
            ' Use one of these formats instead: YYYY-MM-DD."]}'
        ])
        self.assert_urls(run, 'simplemodels/%s')

    def test_auto_ignore_extra(self):
        # Should abort due to unknown column
        run = self.upload_file('simplemodel_extra.csv')
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
        ])

        # Set column and try again, should work now
        self.update_columns(run, {
            'Other': {
                'extra': '__ignore__',
            }
        })
        self.auto_import(run, expect_input_required=False)

        # Verify results
        self.assert_status(run, 3)
        self.assert_ranges(run, [
            "Data Column 'date -> date' at Rows 1-5, Column 0",
            "Data Column 'color -> color' at Rows 1-5, Column 1",
            "Data Column 'notes -> notes' at Rows 1-5, Column 2",
            "Data Column 'extra -> (ignored)' at Rows 1-5, Column 3",
        ])
        self.assert_records(run, [
            "Imported '2017-06-01: red (Test Note 1)' at row 1",
            "Imported '2017-06-02: green (Test Note 2)' at row 2",
            "Imported '2017-06-03: blue (Test Note 3)' at row 3",
            "Failed at row 4:"
            ' {"color": ["\\"orange\\" is not a valid choice."]}',
            "Failed at row 5:"
            ' {"date": ["Date has wrong format.'
            ' Use one of these formats instead: YYYY-MM-DD."]}'
        ])
        self.assert_urls(run, 'simplemodels/%s')
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'update_columns',
            'auto_import',
            'parse_row_identifiers',
            'do_import',
            'import_complete',
        ])


class IncompleteTestCase(BaseImportTestCase):
    serializer_name = 'tests.data_app.wizard.IncompleteSerializer'

    def test_incomplete_serializer(self):
        # Initialize identifier before auto import
        self.create_identifier('field notes', 'notes')

        # Should succeed since field notes is already mapped
        run = self.upload_file('simplemodel.csv')
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
        self.assert_status(run, 4)
        self.assert_ranges(run, [
            "Data Column 'date -> date' at Rows 1-5, Column 0",
            "Data Column 'color -> color' at Rows 1-5, Column 1",
            "Data Column 'field notes -> notes' at Rows 1-5, Column 2",
        ])
        self.assert_records(run, [
            "Imported '2017-06-01: red (Test Note 1)' at row 1",
            "Imported '2017-06-02: green (Test Note 2)' at row 2",
            "Imported '2017-06-03: blue (Test Note 3)' at row 3",
            # SQLite ignores varchar field size
            "Imported '2017-06-04: orange (Test Note 4)' at row 4",
            "Failed at row 5: ValidationError(['\"2017-06-50\" value has the"
            " correct format (YYYY-MM-DD) but it is an invalid date.'])"
        ])
        self.assert_urls(run, 'simplemodels/%s')


class SerializerTestCase(BaseImportTestCase):
    def test_serializer_list(self):
        run = self.upload_file('simplemodel.csv', skip_serializer=True)
        result = self.get_url(run, 'serializers')
        choices = {
            row['name']: row['label']
            for row in result.data['serializer_choices']
        }
        self.assertIn(
            'tests.data_app.wizard.SlugSerializer',
            choices,
        )
        self.assertNotIn(
            'tests.data_app.wizard.IncompleteSerializer',
            choices,
        )
