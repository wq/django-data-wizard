from .base import DataWizardBackend
from django.core.cache import cache
import threading
import uuid


CACHE_PREFIX = 'data-wizard-'


class Backend(DataWizardBackend):
    current_state = None
    current_result = None

    def run_async(self, task_name, run_id, user_id, post):
        task_id = uuid.uuid4()
        thread = threading.Thread(
            name=task_id,
            target=self.run_sync,
            args=(task_name, run_id, user_id, post)
        )
        thread.start()
        return task_id

    def update_async_status(self, state, meta):
        task_id = threading.current_thread().name
        if not task_id:
            return
        cache.set(CACHE_PREFIX + task_id, {
            'state': state,
            'meta': meta,
        })

    def get_async_status(self, task_id):
        data = cache.get(CACHE_PREFIX + task_id)
        if not data:
            return {}
        status = {'status': data.get('state')}
        status.update(data.get('meta') or {})
        return status
