from .base import DataWizardBackend


class Backend(DataWizardBackend):
    current_state = None
    current_result = None

    def run_async(self, task_name, run_id, post):
        self.try_run_sync(task_name, run_id, post)
        return "current"

    def update_async_status(self, state, meta):
        self.current_state = state
        self.current_result = meta

    def get_async_status(self, task_id):
        assert task_id == "current"
        status = {"status": self.current_state}
        status.update(self.current_result)
        return status
