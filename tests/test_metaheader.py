from .base import BaseImportTestCase


class MetaHeaderTestCase(BaseImportTestCase):
    serializer_name = 'tests.naturalkey_app.wizard.NoteMetaSerializer'

    def test_manual(self):
        run = self.upload_file('naturalkey_meta.xlsx')

        # Inspect unmatched columns and select choices
        self.check_columns(run, 4, 4)
        self.update_columns(run, {
            'Note': {
                'Date:': 'event[date]',
                'Place:': 'event[place][name]',
                'Note': 'note',
                'Status': 'status',
            }
        })

        # Start data import process, wait for completion
        self.start_import(run, [])

        # Verify results
        self.assert_log(run, [
            'created',
            'parse_columns',
            'update_columns',
            'do_import',
            'import_complete',
        ])
        self.assert_records(run, [
            "Imported 'Minneapolis on 2019-01-01: Test Note 1' at row 4",
            "Imported 'Minneapolis on 2019-01-01: Test Note 2' at row 5",
            "Imported 'Minneapolis on 2019-01-01: Test Note 3' at row 6",
        ])
