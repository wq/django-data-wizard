from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.viewsets import ModelViewSet
from data_wizard import tasks
from data_wizard import registry
from wq.io.exceptions import IoException
from celery.result import AsyncResult
from .serializers import RunSerializer, RecordSerializer
from .models import Run


class RunViewSet(ModelViewSet):
    serializer_class = RunSerializer
    record_serializer_class = RecordSerializer
    queryset = Run.objects.all()

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
            action = result.result.get('action', None)
            if not action and result.state == 'SUCCESS':
                action = 'records'
            if action:
                url = '/datawizard/{pk}/{action}'.format(
                    pk=self.get_object().pk,
                    action=action,
                )
                response['location'] = url
        elif result.state == 'FAILURE':
            response['error'] = str(result.result)
        return Response(response)

    def run_task(self, name, async=False):
        response = self.retrieve(self.request, **self.kwargs)

        run = self.get_object()
        user = self.request.user

        task = getattr(tasks, name).delay(run.pk, user.pk)
        if async:
            response.data['task_id'] = task.task_id
        else:
            try:
                response.data['result'] = task.get()
            except IoException as e:
                response.data['error'] = str(e)

        return response

    @detail_route()
    def serializers(self, request, *args, **kwargs):
        response = self.retrieve(request, **self.kwargs)
        response.data['serializer_choices'] = [{
            'name': s['class_name'],
            'label': s['name'],
        } for s in registry.get_serializers()]
        return response

    @detail_route(methods=['post'])
    def updateserializer(self, request, *args, **kwargs):
        run = self.get_object()
        self.action = 'serializers'
        name = request.POST.get('serializer', None)
        if name and registry.get_serializer(name):
            run.serializer = name
            run.save()
            run.add_event('update_serializer')
        return self.retrieve(request)

    @detail_route()
    def columns(self, request, *args, **kwargs):
        return self.run_task('read_columns')

    @detail_route(methods=['post'])
    def updatecolumns(self, request, *args, **kwargs):
        response = self.run_task('read_columns')
        self.action = 'columns'
        result = tasks.update_columns.delay(
            self.get_object().pk, request.user.pk, post=request.POST
        )
        response.data['result'] = result.get()
        return response

    @detail_route()
    def ids(self, request, *args, **kwargs):
        return self.run_task('read_row_identifiers')

    @detail_route(methods=['post'])
    def updateids(self, request, *args, **kwargs):
        response = self.run_task('read_row_identifiers')
        self.action = 'ids'
        result = tasks.update_row_identifiers.delay(
            self.get_object().pk, request.user.pk, post=request.POST
        )
        response.data['result'] = result.get()
        return response

    @detail_route(methods=['post'])
    def data(self, request, *args, **kwargs):
        return self.run_task('import_data', async=True)

    @detail_route(methods=['post', 'get'])
    def auto(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.action = 'retrieve'
            return self.retrieve(request, **kwargs)
        return self.run_task('auto_import', async=True)

    @detail_route()
    def records(self, request, *args, **kwargs):
        response = self.retrieve(self.request, **kwargs)
        response.data['records'] = self.record_serializer_class(
            self.get_object().record_set.all(),
            many=True
        ).data
        return response
