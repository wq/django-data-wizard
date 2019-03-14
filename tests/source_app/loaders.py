from data_wizard.loaders import BaseLoader
from wq.io import JsonStringIO


class CustomLoader(BaseLoader):
    default_serializer = 'data_wizard.registry.SimpleModelSerializer'

    def load_io(self):
        return JsonStringIO(string=self.content_object.json_data)
