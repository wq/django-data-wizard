from .. import set_loader
from .models import FileSource, URLSource


set_loader(FileSource, "data_wizard.loaders.FileLoader")
set_loader(URLSource, "data_wizard.loaders.URLLoader")
