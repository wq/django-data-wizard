from .base import BaseImportTestCase


class SimpleTestCase(BaseImportTestCase):
    def test_xlsx_zipcode_default(self):
        # Use auto-generated serializer (created by registering model)
        self.serializer_name = 'data_wizard.registry.AddressSerializer'
        run = self.upload_file('addresses.xlsx')

        # Import and verify results
        self.create_identifier('zipcode', 'postal_code')
        self.auto_import(run, expect_input_required=False)
        self.assert_status(run, 2)
        self.assert_ranges(run, [
            "Data Column 'city -> city' at Rows 1-2, Column 0",
            "Data Column 'zipcode -> postal_code' at Rows 1-2, Column 1",
        ])

        # Records imported, but with '.0' due to XLSX number parsing
        self.assert_records(run, [
            "Imported 'Minneapolis 55455.0' at row 1",
            "Imported 'Chicago 60611.0' at row 2",
        ])

    def test_xlsx_zipcode_improved(self):
        # Use custom serializer
        self.serializer_name = 'tests.data_app.wizard.AddressSerializer'
        run = self.upload_file('addresses.xlsx')

        # Import and verify results
        self.create_identifier('zipcode', 'postal_code')
        self.auto_import(run, expect_input_required=False)
        self.assert_status(run, 2)
        self.assert_ranges(run, [
            "Data Column 'city -> city' at Rows 1-2, Column 0",
            "Data Column 'zipcode -> postal_code' at Rows 1-2, Column 1",
        ])

        # With a custom serializer, the '.0' can be avoided
        self.assert_records(run, [
            "Imported 'Minneapolis 55455' at row 1",
            "Imported 'Chicago 60611' at row 2",
        ])
