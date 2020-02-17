from .compat import reverse, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import pagination
from rest_framework import renderers
from . import registry
from .serializers import RunSerializer, RecordSerializer
from .models import Run
from .settings import import_setting


class PageNumberPagination(pagination.PageNumberPagination):
    page_size = 50


class RunViewSet(ModelViewSet):
    serializer_class = RunSerializer
    pagination_class = PageNumberPagination
    renderer_classes = [
        renderers.TemplateHTMLRenderer,
        renderers.JSONRenderer,
        renderers.BrowsableAPIRenderer,
    ]
    authentication_classes = [
        import_setting('AUTHENTICATION'),
    ]
    permission_classes = [
        import_setting('PERMISSION'),
    ]
    record_serializer_class = RecordSerializer
    queryset = Run.objects.all()

    @property
    def backend(self):
        from . import backend as data_wizard_backend
        return data_wizard_backend

    @property
    def template_name(self):
        if self.action == 'retrieve':
            template = 'detail'
        else:
            template = self.action
        return 'data_wizard/run_{}.html'.format(template)

    def get_renderers(self):
        if self.action == 'status':
            return [renderers.JSONRenderer()]
        else:
            return super(RunViewSet, self).get_renderers()

    @action(detail=True)
    def status(self, request, *args, **kwargs):
        task_id = request.GET.get('task', None)
        result = self.backend.get_async_status(task_id)
        status = result.get('status', 'UNKNOWN')
        action = result.get('action', None)
        if not action and status == 'SUCCESS':
            action = 'records'
        if action:
            result['location'] = self.get_action_url(action)
        elif status == 'FAILURE' and not result.get('error'):
            result['error'] = "Unknown Error"
        result['status'] = status
        return Response(result)

    _namespace = 'data_wizard'

    def get_action_url(self, action):
        name = self._namespace + ':run-' + action
        return reverse(name, kwargs={'pk': self.get_object().pk})

    def run_task(self, name, use_async=False, post=None):
        run = self.get_object()
        return run.run_task(
            name,
            use_async=use_async,
            post=post,
            backend=self.backend,
            user=self.request.user
        )

    def retrieve_and_run(self, task_name, use_async=False, post=None):
        response = self.retrieve(self.request, **self.kwargs)
        result = self.run_task(task_name, use_async, post)
        response.data.update(result)
        return response

    @action(detail=True)
    def serializers(self, request, *args, **kwargs):
        response = self.retrieve(request, **self.kwargs)
        response.data['serializer_choices'] = [
            {
                'name': s['class_name'],
                'label': s['name'],
            } for s in registry.get_serializers()
            if s['options'].get('show_in_list', True)
        ]
        return response

    @action(detail=True, methods=['post'])
    def updateserializer(self, request, *args, **kwargs):
        run = self.get_object()
        self.action = 'serializers'
        name = request.POST.get('serializer', None)
        if name and registry.get_serializer(name):
            run.serializer = name
            run.save()
            run.add_event('update_serializer')
        return self.serializers(request)

    @action(detail=True)
    def columns(self, request, *args, **kwargs):
        return self.retrieve_and_run('read_columns')

    @action(detail=True, methods=['post'])
    def updatecolumns(self, request, *args, **kwargs):
        response = self.retrieve_and_run('read_columns')
        self.action = 'columns'
        result = self.run_task('update_columns', post=request.POST)
        response.data.update(result)
        return response

    @action(detail=True)
    def ids(self, request, *args, **kwargs):
        return self.retrieve_and_run('read_row_identifiers')

    @action(detail=True, methods=['post'])
    def updateids(self, request, *args, **kwargs):
        response = self.retrieve_and_run('read_row_identifiers')
        self.action = 'ids'
        result = self.run_task('update_row_identifiers', post=request.POST)
        response.data.update(result)
        return response

    @action(detail=True, methods=['post'])
    def data(self, request, *args, **kwargs):
        return self.retrieve_and_run('import_data', use_async=True)

    @action(detail=True, methods=['post', 'get'])
    def auto(self, request, *args, **kwargs):
        if request.method == 'GET':
            response = self.retrieve(request, **kwargs)
            task_id = request.GET.get('task', None)
            if task_id:
                response.data['task_id'] = task_id
            else:
                self.action = 'retrieve'
            return response
        return self.retrieve_and_run('auto_import', use_async=True)

    @action(detail=True)
    def records(self, request, *args, **kwargs):
        response = self.retrieve(self.request, **kwargs)
        response.data['records'] = self.record_serializer_class(
            self.get_object().record_set.all(),
            many=True
        ).data
        return response
