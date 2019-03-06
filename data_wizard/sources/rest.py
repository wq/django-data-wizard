from wq.db import rest
from .models import FileSource, URLSource


rest.router.register_model(FileSource, fields="__all__")
rest.router.register_model(URLSource, fields="__all__")
