from celery import shared_task, current_task
from celery.result import AsyncResult
from .base import DataWizardBackend, ERROR_RAISE


class Backend(DataWizardBackend):
    on_async_error = ERROR_RAISE
    test_reset_sequences = True

    def run_async(self, task_name, run_id, post):
        task = run_async.delay(task_name, run_id, post)
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
        response = {"status": result.state}
        if result.state in ("PROGRESS", "SUCCESS"):
            response.update(result.result)
        elif result.state in ("FAILURE",):
            response.update(self.format_exception(result.result))
        return response


@shared_task
def run_async(task_name, run_id, post):
    from .. import backend

    return backend.try_run_sync(task_name, run_id, post)
