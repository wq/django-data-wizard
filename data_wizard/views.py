from rest_framework.response import Response
from rest_framework.decorators import detail_route
from wq.db.rest.views import ModelViewSet
from data_wizard import tasks
from wq.io.exceptions import IoException
from celery.result import AsyncResult


class RunViewSet(ModelViewSet):
    @detail_route()
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
            self.get_object(), self.request.user
        )
        if async:
            response.data['task_id'] = task.task_id
        else:
            try:
                response.data['result'] = task.get()
            except IoException as e:
                response.data['error'] = str(e)

        return response

    @detail_route()
    def start(self, request, *args, **kwargs):
        self.action = 'columns'
        return self.run_task('read_columns')

    @detail_route(methods=['post'])
    def columns(self, request, *args, **kwargs):
        response = self.run_task('read_columns')
        result = tasks.update_columns.delay(
            self.get_object(), request.user, request.POST
        )
        response.data['result'] = result.get()
        return response

    @detail_route()
    def ids(self, request, *args, **kwargs):
        response = self.run_task('read_row_identifiers')
        return response

    @detail_route(methods=['post'])
    def updateids(self, request, *args, **kwargs):
        response = self.run_task('read_row_identifiers')
        self.action = 'ids'
        result = tasks.update_row_identifiers.delay(
            self.get_object(), request.user, request.POST
        )
        response.data['result'] = result.get()
        return response

    @detail_route(methods=['post'])
    def data(self, request, *args, **kwargs):
        return self.run_task('import_data', async=True)

    @detail_route(methods=['post'])
    def auto(self, request, *args, **kwargs):
        return self.run_task('auto_import', async=True)
