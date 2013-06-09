from wq.db.rest.views import InstanceModelView
from wq.db.patterns.base import swapper
from .models import MetaColumn
from wq.db.contrib.qual.io import tasks
from wq.db.rest.app import router

class FileTaskView(InstanceModelView):
    model = swapper.load_model('files', 'File')
    router = router
    task_name = None

    def get(self, request, *args, **kwargs):
        obj = super(FileTaskView, self).get(request, *args, **kwargs)
        result = getattr(tasks, self.task_name).delay(self.object)
        obj.data['result'] = result.get()
        return obj

class StartImportView(FileTaskView):
    template_name = "file_import.html"
    task_name = 'read_columns'
    def post(self, request, *args, **kwargs):
        obj = super(FileTaskView, self).get(request, *args, **kwargs)
        result = tasks.update_columns.delay(self.object, request.POST)
        obj.data['result'] = result.get()
        return obj

class ResetView(FileTaskView):
    template_name = "file_detail.html"
    task_name = 'reset'
