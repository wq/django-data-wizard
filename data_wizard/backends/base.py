from .. import tasks
import logging


ERROR_RETURN = 1
ERROR_RAISE = 2
ERROR_UPDATE_ASYNC = 3


class DataWizardBackend(object):
    on_async_error = ERROR_UPDATE_ASYNC

    def run(self, task_name, run_id, user_id, use_async=False, post=None):
        if use_async:
            task_id = self.run_async(task_name, run_id, user_id, post)
            return {'task_id': task_id}
        else:
            return self.try_run_sync(
                task_name, run_id, user_id, post, ERROR_RETURN
            )

    def get_task_fn(self, task_name):
        return getattr(tasks, task_name)

    def run_sync(self, task_name, run_id, user_id, post=None):
        fn = self.get_task_fn(task_name)
        if post:
            result = fn(run_id, user_id, post=post)
        else:
            result = fn(run_id, user_id)
        return result

    def try_run_sync(self, task_name, run_id, user_id, post, on_error=None):
        if not on_error:
            on_error = self.on_async_error
        if not isinstance(on_error, tuple):
            on_error = (on_error,)
        try:
            result = self.run_sync(task_name, run_id, user_id, post)
        except Exception as e:
            logging.exception(e)
            error = self.format_exception(e)
            if ERROR_UPDATE_ASYNC in on_error:
                self.update_async_status('FAILURE', error)
            if ERROR_RAISE in on_error:
                raise
            if ERROR_RETURN in on_error:
                return error
        else:
            if ERROR_RETURN in on_error:
                return {'result': result}
            else:
                return result

    def format_exception(self, exception):
        error_string = '{name}: {message}'.format(
            name=type(exception).__name__,
            message=exception,
        )
        return {
            'error': error_string
        }

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
