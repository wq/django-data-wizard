from data_wizard import tasks


class DataWizardBackend(object):
    def run(self, task_name, run_id, user_id, use_async=False, post=None):
        if use_async:
            task_id = self.run_async(task_name, run_id, user_id, post)
            return {'task_id': task_id}
        else:
            try:
                result = self.run_sync(task_name, run_id, user_id, post)
            except Exception as e:
                return {'error': str(e)}
            else:
                return {'result': result}

    def get_task_fn(self, task_name):
        return getattr(tasks, task_name)

    def run_sync(self, task_name, run_id, user_id, post=None):
        fn = self.get_task_fn(task_name)
        if post:
            result = fn(run_id, user_id, post=post)
        else:
            result = fn(run_id, user_id)
        return result

    def run_async(self, task_name, run_id, user_id, post):
        raise NotImplementedError("This backend does not support async")

    def progress(self, sender, **kwargs):
        state = kwargs.get('state')
        meta = kwargs.get('meta')
        self.update_async_status(
            state=state,
            meta=meta,
        )

    def update_async_status(self, state, meta):
        raise NotImplementedError("This backend does not support async")

    def get_async_status(self, task_id):
        raise NotImplementedError("This backend does not support async")
