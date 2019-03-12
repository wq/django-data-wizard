import data_wizard
from .models import FileSource, URLSource


data_wizard.set_loader(FileSource, 'data_wizard.loaders.FileLoader')
data_wizard.set_loader(URLSource, 'data_wizard.loaders.URLLoader')
