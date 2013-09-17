from rest_framework.response import Response
from wq.db.rest.views import View, InstanceModelView
from .models import File
from wq.db.contrib.vera.io import tasks
from wq.db.rest.app import router
from celery.result import AsyncResult


class TaskStatusView(View):
    def get(self, request, *args, **kwargs):
        result = AsyncResult(kwargs['task_id'])
        response = {
            'status': result.state
        }
        if result.state in ('PROGRESS', 'SUCCESS'):
            response.update(result.result)
        elif result.state == 'FAILURE':
            response['error'] = repr(result.result)
        return Response(response)


class FileTaskView(InstanceModelView):
    cached = False
    model = File
    router = router
    task_name = None
    async = True

    def get(self, request, *args, **kwargs):
        response = super(FileTaskView, self).get(request, *args, **kwargs)
        task = getattr(tasks, self.task_name).delay(self.object, request.user)
        if self.async:
            response.data['task_id'] = task.task_id
        else:
            response.data['result'] = task.get()
        return response


class StartImportView(FileTaskView):
    template_name = "file_import.html"
    task_name = 'read_columns'
    async = False

    def post(self, request, *args, **kwargs):
        response = super(FileTaskView, self).get(request, *args, **kwargs)
        result = tasks.update_columns.delay(
            self.object, request.user, request.POST
        )
        response.data['result'] = result.get()
        return response


class ResetView(FileTaskView):
    template_name = "file_detail.html"
    task_name = 'reset'
    async = False


class ImportDataView(FileTaskView):
    template_name = 'file_data.html'
    task_name = 'import_data'
