from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework import renderers
from data_wizard import registry
import data_wizard
from .serializers import RunSerializer, RecordSerializer
from .models import Run
from .settings import import_setting


class PageNumberPagination(PageNumberPagination):
    page_size = 50


class RunViewSet(ModelViewSet):
    serializer_class = RunSerializer
    pagination_class = PageNumberPagination
    renderer_classes = [
        renderers.TemplateHTMLRenderer,
        renderers.JSONRenderer,
        renderers.BrowsableAPIRenderer,
    ]
    permission_classes = [
        import_setting('PERMISSION'),
    ]
    record_serializer_class = RecordSerializer
    queryset = Run.objects.all()

    @property
    def backend(self):
        return data_wizard.backend

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

    @detail_route()
    def status(self, request, *args, **kwargs):
        task_id = request.GET.get('task', None)
        result = self.backend.get_async_status(task_id)
        status = result.get('status', 'UNKNOWN')
        action = result.get('action', None)
        if not action and status == 'SUCCESS':
            action = 'records'
        if action:
            url = '/datawizard/{pk}/{action}'.format(
                pk=self.get_object().pk,
                action=action,
            )
            result['location'] = url
        elif status == 'FAILURE' and not result.get('error'):
            result['error'] = "Unknown Error"
        result['status'] = status
        return Response(result)

    def run_task(self, name, use_async=False, post=None):
        run = self.get_object()
        return run.run_task(
            name,
            use_async=use_async,
            post=post,
            backend=self.backend,
            user=self.request.user,
        )

    def retrieve_and_run(self, task_name, use_async=False, post=None):
        response = self.retrieve(self.request, **self.kwargs)
        result = self.run_task(task_name, use_async, post)
        response.data.update(result)
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
        return self.serializers(request)

    @detail_route()
    def columns(self, request, *args, **kwargs):
        return self.retrieve_and_run('read_columns')

    @detail_route(methods=['post'])
    def updatecolumns(self, request, *args, **kwargs):
        response = self.retrieve_and_run('read_columns')
        self.action = 'columns'
        result = self.run_task('update_columns', post=request.POST)
        response.data.update(result)
        return response

    @detail_route()
    def ids(self, request, *args, **kwargs):
        return self.retrieve_and_run('read_row_identifiers')

    @detail_route(methods=['post'])
    def updateids(self, request, *args, **kwargs):
        response = self.retrieve_and_run('read_row_identifiers')
        self.action = 'ids'
        result = self.run_task('update_row_identifiers', post=request.POST)
        response.data.update(result)
        return response

    @detail_route(methods=['post'])
    def data(self, request, *args, **kwargs):
        return self.retrieve_and_run('import_data', use_async=True)

    @detail_route(methods=['post', 'get'])
    def auto(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.action = 'retrieve'
            return self.retrieve(request, **kwargs)
        return self.retrieve_and_run('auto_import', use_async=True)

    @detail_route()
    def records(self, request, *args, **kwargs):
        response = self.retrieve(self.request, **kwargs)
        response.data['records'] = self.record_serializer_class(
            self.get_object().record_set.all(),
            many=True
        ).data
        return response
