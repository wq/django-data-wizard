from celery import task, current_task
from celery.result import AsyncResult
from .base import DataWizardBackend


class CeleryBackend(DataWizardBackend):
    def run_async(self, task_name, run_id, user_id, post):
        task = run_async.delay(task_name, run_id, user_id, post)
        return task.task_id

    def update_async_status(self, state, meta):
        current_task.update_state(
            state=state,
            meta=meta,
        )

    def get_async_status(self, task_id):
        result = AsyncResult(task_id)
        response = {
            'status': result.state
        }
        if result.state in ('PROGRESS', 'SUCCESS'):
            response.update(result.result)
        return response


@task
def run_async(task_name, run_id, user_id, post):
    from data_wizard import backend
    return backend.run_sync(task_name, run_id, user_id, post)
