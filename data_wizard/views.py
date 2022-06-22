from django.urls import reverse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import pagination
from rest_framework import renderers
from .backends.base import TASK_META
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
        import_setting("AUTHENTICATION"),
    ]
    permission_classes = [
        import_setting("PERMISSION"),
    ]
    record_serializer_class = RecordSerializer
    queryset = Run.objects.all()

    @property
    def backend(self):
        from . import backend as data_wizard_backend

        return data_wizard_backend

    @property
    def template_name(self):
        if self.action in ("create", "retrieve"):
            template = "detail"
        else:
            template = self.task_action_paths.get(self.action, self.action)
        return "data_wizard/run_{}.html".format(template)

    def get_renderers(self):
        if self.action == "status":
            return [renderers.JSONRenderer()]
        else:
            return super(RunViewSet, self).get_renderers()

    @action(detail=True)
    def status(self, request, *args, **kwargs):
        task_id = request.GET.get("task", None)
        result = self.backend.get_async_status(task_id)
        status = result.get("status", "UNKNOWN")
        action = result.get("action", None)
        if not action and status == "SUCCESS":
            action = "records"
        if action:
            result["location"] = self.get_action_url(action)
        elif status == "FAILURE" and not result.get("error"):
            result["error"] = "Unknown Error"
        result["status"] = status
        return Response(result)

    _namespace = "data_wizard"

    def get_action_url(self, action):
        name = self._namespace + ":run-" + action
        return reverse(name, kwargs={"pk": self.get_object().pk})

    def run_and_retrieve(self, request, task_name):
        run = self.get_object()
        meta = TASK_META[task_name]

        if meta["use_async"] and request.method == "GET":
            task_id = request.GET.get("task", None)
            result = None
            if task_id:
                current_mode = meta["url_path"]
            else:
                self.action = "retrieve"
                current_mode = None
        else:
            task_id = None
            result = run.run_task(
                task_name,
                use_async=meta["use_async"],
                post=request.data if meta["user_input"] else None,
            )
            if meta["use_async"]:
                current_mode = meta["url_path"]
            else:
                current_mode = result.get("result", {}).pop(
                    "current_mode", None
                )

        response = self.retrieve(self.request, **self.kwargs)
        if result:
            response.data.update(result)

        if current_mode:
            self.action = current_mode
            response.data["current_mode"] = current_mode

        if task_id:
            response.data["task_id"] = task_id

        return response

    task_actions_ready = False
    task_action_paths = {}

    @classmethod
    def get_extra_actions(cls):
        if not cls.task_actions_ready:
            cls.init_task_actions()
            cls.task_actions_ready = True
        return super().get_extra_actions()

    @classmethod
    def init_task_actions(cls):
        for task_name, meta in TASK_META.items():
            cls.init_task_action(task_name, meta)

    @classmethod
    def init_task_action(cls, task_name, meta):
        if meta["url_path"] is False:
            return

        def task_action(self, request, *args, **kwargs):
            return self.run_and_retrieve(request, task_name)

        if meta["use_async"]:
            methods = ["POST", "GET"]
        elif meta["user_input"]:
            methods = ["POST"]
        else:
            methods = ["GET"]
        task_action_name = task_name.split(".")[-1]
        task_action.__name__ = task_action_name
        task_action = action(
            detail=True,
            methods=methods,
            url_path=meta["url_path"],
            url_name=meta["url_path"],
        )(task_action)

        setattr(cls, task_action_name, task_action)
        cls.task_action_paths[task_action_name] = (
            meta["url_path"] or task_action_name
        )

    @action(detail=True)
    def records(self, request, *args, **kwargs):
        response = self.retrieve(self.request, **kwargs)
        response.data["records"] = self.record_serializer_class(
            self.get_object().record_set.all(), many=True
        ).data
        return response
