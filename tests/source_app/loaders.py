from data_wizard.loaders import BaseLoader
from itertable import JsonStringIter


class CustomLoader(BaseLoader):
    default_serializer = 'data_wizard.registry.SimpleModelSerializer'

    def load_iter(self):
        return JsonStringIter(string=self.content_object.json_data)
