from rest_framework.response import Response
from rest_framework.decorators import link, action
from wq.db.rest.views import ModelViewSet
from wq.db.contrib.dbio import tasks
from wq.io.exceptions import *
from celery.result import AsyncResult


class IoViewSet(ModelViewSet):
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
            response['error'] = str(result.result)
        return Response(response)

    def run_task(self, name, async=False):
        response = self.retrieve(self.request, **self.kwargs)
        task = getattr(tasks, name).delay(
            self.get_instance(), self.request.user
        )
        if async:
            response.data['task_id'] = task.task_id
        else:
            try:
                response.data['result'] = task.get()
            except IoException as e:
                response.data['error'] = str(e)

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

    @link()
    def ids(self, request, *args, **kwargs):
        response = self.run_task('read_row_identifiers')
        return response

    @action()
    def updateids(self, request, *args, **kwargs):
        response = self.run_task('read_row_identifiers')
        self.action = 'ids'
        result = tasks.update_row_identifiers.delay(
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
        return self.run_task('auto_import', async=True)

    def get_instance(self):
        return self.object
