from __future__ import absolute_import  # FIXME: Drop this in 2.0
from celery import task, current_task
from celery.result import AsyncResult
from .base import DataWizardBackend, ERROR_RAISE


class Backend(DataWizardBackend):
    on_async_error = ERROR_RAISE

    def run_async(self, task_name, run_id, user_id, post):
        task = run_async.delay(task_name, run_id, user_id, post)
        return task.task_id

    def update_async_status(self, state, meta):
        if not current_task:
            return
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
        elif result.state in ('FAILURE',):
            response.update(self.format_exception(result.result))
        return response


@task
def run_async(task_name, run_id, user_id, post):
    from .. import backend
    return backend.try_run_sync(task_name, run_id, user_id, post)
