from rest_framework.response import Response
from rest_framework.decorators import link, action
from wq.db.rest.views import ModelViewSet
from wq.db.contrib.dbio import tasks
from celery.result import AsyncResult
from .proxy_models import FileIoProxy


class IoViewSet(ModelViewSet):
    cached = False

    @link()
    def status(self, request, *args, **kwargs):
        taskid = request.GET.get('task', None)
        if not taskid:
            return Response({})

        result = AsyncResult(taskid)
        response = {
            'status': result.state
        }
        if result.state in ('PROGRESS', 'SUCCESS'):
            response.update(result.result)
        elif result.state == 'FAILURE':
            response['error'] = repr(result.result)
        return Response(response)

    def run_task(self, name, async=False):
        response = self.retrieve(self.request, **self.kwargs)
        task = getattr(tasks, name).delay(
            self.get_instance(), self.request.user
        )
        if async:
            response.data['task_id'] = task.task_id
        else:
            response.data['result'] = task.get()
        return response

    @link()
    def start(self, request, *args, **kwargs):
        self.action = 'columns'
        return self.run_task('read_columns')

    @action()
    def columns(self, request, *args, **kwargs):
        response = self.run_task('read_columns')
        result = tasks.update_columns.delay(
            self.get_instance(), request.user, request.POST
        )
        response.data['result'] = result.get()
        return response

    @action()
    def reset(self, request, *args, **kwargs):
        self.task = 'retrieve'
        response = self.run_task('reset')
        return response

    @action()
    def data(self, request, *args, **kwargs):
        return self.run_task('import_data', async=True)

    @action()
    def auto(self, request, *args, **kwargs):
        response = self.run_task('read_columns')
        if response.data['result']['unknown_count']:
            return self.start(request, *args, **kwargs)
        else:
            self.action = 'data'
            return self.data(request, *args, **kwargs)

    def get_instance(self):
        return self.object


class FileViewSet(IoViewSet):
    def get_instance(self):
        return FileIoProxy.objects.get(pk=self.object.pk)
