from data_wizard import registry
from .models import FileSource, URLSource


registry.set_loader(FileSource, 'data_wizard.loaders.FileLoader')
registry.set_loader(URLSource, 'data_wizard.loaders.URLLoader')
