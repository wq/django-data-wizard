from .base import BaseImportTestCase
from data_wizard.models import Run
from .source_app.models import CustomWorkflow


class CustomWorkflowTestCase(BaseImportTestCase):
    serializer_name = "tests.source_app.wizard.CustomWorkflowSerializer"

    def test_auto(self):
        workflow = CustomWorkflow.objects.create()
        run = Run.objects.create(
            content_object=workflow,
            user=self.user,
            serializer=self.serializer_name,
        )

        # First step is automatic, second requires input
        self.auto_import(run, expect_input_required=True)
        self.assert_log(
            run,
            [
                "created",
                "auto_import",
                "validated",
                "check_confirm",
            ],
        )
        workflow.refresh_from_db()
        self.assertTrue(workflow.validated)
        self.assertFalse(workflow.confirmed)
        self.assertFalse(workflow.finalized)

        # Submit input
        self.post_url(
            run,
            "saveconfirm",
            {"confirm": True},
        )
        workflow.refresh_from_db()
        self.assertTrue(workflow.validated)
        self.assertTrue(workflow.confirmed)
        self.assertFalse(workflow.finalized)

        # This time the full run should complete
        self.auto_import(run)
        self.assert_log(
            run,
            [
                "created",
                "auto_import",
                "validated",
                "check_confirm",
                "process_confirm",
                "auto_import",
                "check_confirm",
                "finalized",
            ],
        )
        workflow.refresh_from_db()
        self.assertTrue(workflow.validated)
        self.assertTrue(workflow.confirmed)
        self.assertTrue(workflow.finalized)
