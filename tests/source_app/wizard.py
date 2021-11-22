import data_wizard
from .models import CustomSource, CustomWorkflow
from rest_framework import serializers


data_wizard.set_loader(CustomSource, "tests.source_app.loaders.CustomLoader")


class CustomWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomWorkflow
        data_wizard = {
            'auto_import_tasks': [
                 'tests.source_app.wizard.validate',
                 'tests.source_app.wizard.check_confirm',
                 'tests.source_app.wizard.finalize',
             ],
        }


data_wizard.register("Custom Workflow", CustomWorkflowSerializer)


@data_wizard.wizard_task(label="Validate", url_path="validate")
def validate(run):
    workflow = run.content_object
    if not workflow.validated:
        run.add_event('validated')
        workflow.validated = True
        workflow.save()
    return {}


@data_wizard.wizard_task(label="Check Confirmation", url_path=False)
def check_confirm(run):
    run.add_event('check_confirm')
    workflow = run.content_object
    if not workflow.confirmed:
        raise data_wizard.InputNeeded('confirm')


@data_wizard.wizard_task(label="Confirm", url_path="confirm")
def confirm(run):
    workflow = run.content_object
    return {
        "is_confirmed": workflow.confirmed,
    }


@data_wizard.wizard_task(label="Save Confirmation", url_path="saveconfirm")
def process_confirm(run, post={}):
    workflow = run.content_object
    if post.get('confirm'):
        run.add_event('process_confirm')
        workflow.confirmed = True
        workflow.save()

    return {
        **confirm(run),
        'current_mode': 'confirm',
    }


@data_wizard.wizard_task(label="Finalize", url_path="finalize")
def finalize(run):
    run.add_event('finalized')
    workflow = run.content_object
    workflow.finalized = True
    workflow.save()
    run.send_progress({
        "current": 3,
        "total": 3,
        "skipped": [],
    }, "SUCCESS")
