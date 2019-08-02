from . import set_loader
from .models import FileSource, URLSource


set_loader(FileSource, '.loaders.FileLoader')
set_loader(URLSource, '.loaders.URLLoader')
