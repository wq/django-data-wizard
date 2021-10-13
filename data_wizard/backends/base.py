from ..settings import import_from_string
from .. import signals
import logging
import inspect
from functools import wraps


ERROR_RETURN = 1
ERROR_RAISE = 2
ERROR_UPDATE_ASYNC = 3

TASK_FN = {}
TASK_META = {}


class InputNeeded(Exception):
    def __init__(self, action, unknown_count=None):
        self.action = action
        self.unknown_count = unknown_count


def wizard_task(label=None, url_path=None, use_async=False):
    def decorate_task(fn):
        task_name = f"{fn.__module__}.{fn.__qualname__}"
        parameters = inspect.signature(fn).parameters
        assert len(parameters) < 3

        if len(parameters) == 2:
            user_input = True
        else:
            user_input = False

        TASK_META[task_name] = {
            "label": label,
            "url_path": url_path,
            "use_async": use_async,
            "user_input": user_input,
        }

        @wraps(fn)
        def wrapped(run, **kwargs):
            from ..models import Run

            if not isinstance(run, Run):
                run = Run.objects.get(pk=run)
            return fn(run, **kwargs)

        TASK_FN[task_name] = wrapped
        return wrapped

    return decorate_task


class DataWizardBackend(object):
    on_async_error = ERROR_UPDATE_ASYNC

    def run(self, task_name, run_id, use_async=False, post=None):
        if use_async:
            task_id = self.run_async(task_name, run_id, post)
            return {"task_id": task_id}
        else:
            return self.try_run_sync(task_name, run_id, post, ERROR_RETURN)

    def get_task_fn(self, task_name):
        if task_name not in TASK_FN:
            TASK_FN[task_name] = import_from_string(task_name, "__task__")
        return TASK_FN[task_name]

    def run_sync(self, task_name, run_id, post=None):
        fn = self.get_task_fn(task_name)
        if post:
            result = fn(run_id, post=post)
        else:
            result = fn(run_id)
        return result

    def try_run_sync(self, task_name, run_id, post, on_error=None):
        if not on_error:
            on_error = self.on_async_error
        if not isinstance(on_error, tuple):
            on_error = (on_error,)
        try:
            result = self.run_sync(task_name, run_id, post)
        except Exception as e:
            logging.exception(e)
            error = self.format_exception(e)
            if ERROR_UPDATE_ASYNC in on_error:
                self.update_async_status("FAILURE", error)
            if ERROR_RAISE in on_error:
                raise
            if ERROR_RETURN in on_error:
                return error
        else:
            if ERROR_RETURN in on_error:
                return {"result": result}
            else:
                return result

    def format_exception(self, exception):
        error_string = "{name}: {message}".format(
            name=type(exception).__name__,
            message=exception,
        )
        return {"error": error_string}

    def run_async(self, task_name, run_id, post):
        raise NotImplementedError("This backend does not support async")

    def run_all(self, run, tasks):
        for i, task_name in enumerate(tasks):
            meta = TASK_META.get(task_name) or {}
            self.send_progress(
                run,
                {
                    "message": meta.get("label") or task_name,
                    "stage": "meta",
                    "current": i,
                    "total": len(tasks),
                },
            )
            fn = self.get_task_fn(task_name)
            try:
                result = fn(run)
            except InputNeeded as e:
                result = {"action": e.action, "message": "Input Needed"}
                if e.unknown_count:
                    result["unknown_count"] = e.unknown_count
                self.send_progress(run, result, state="SUCCESS")
                break

        return result

    def send_progress(self, run, meta, state="PROGRESS"):
        signals.progress.send(sender=self, run=run, state=state, meta=meta)

    def progress(self, sender, **kwargs):
        state = kwargs.get("state")
        meta = kwargs.get("meta")
        self.update_async_status(
            state=state,
            meta=meta,
        )

    def update_async_status(self, state, meta):
        raise NotImplementedError("This backend does not support async")

    def get_async_status(self, task_id):
        raise NotImplementedError("This backend does not support async")
