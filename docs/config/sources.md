---
order: 4
---

# Custom Data Sources

Django Data Wizard uses [IterTable] to determine the source columns present on the spreadsheet or other data source.  Django Data Wizard can use any Django model instance as a source for its data, provided there is a registered loader that can convert the source model into a [Iter class][IterTable].  Data Wizard provides two out-of-the the box loaders, [FileLoader] and [URLLoader], that can be used with the provided models in `data_wizard.sources` (`FileSource` and `URLSource`, respectively).

### Extending FileLoader
The default `FileLoader` can be used with any Django model with a `FileField` named `file`.  You can use a model with a different `FileField` name by creating a subclass of `data_wizard.loaders.FileLoader` and setting it as the loader for your model.

```python
# myapp/models.py
from django.db import models

class FileModel(models.Model):
    spreadsheet = models.FileField(upload_to='spreadsheets')
```

```python
# myapp/loaders.py
from data_wizard import loaders

class FileLoader(loaders.FileLoader):
    file_attr = 'spreadsheet'
```

```python
# myapp/wizard.py
import data_wizard
from .models import FileModel

data_wizard.set_loader(FileModel, "myapp.loaders.FileLoader")
```

If you have a generic loader that can work with multiple source models, you can also set the default loader through the [global settings][settings]:

```python
# myapp/settings.py
DATA_WIZARD = {
    'LOADER': 'myapp.loaders.FileLoader'
}
```

You should register a custom `ModelAdmin` class to add the Import action in the admin panel for your model.

```python
# myapp/admin.py
from django.contrib import admin
from data_wizard.admin import ImportActionModelAdmin

from .models import FileModel


@admin.register(FileModel)
class FileModelAdmin(ImportActionModelAdmin):
    pass
```
    
### Custom Loader
The default loaders support any file format supported by [IterTable] (Excel, CSV, JSON, and XML).  Additional formats can be integrating by creating a [custom IterTable class][custom-iter] and then registering it with the wizard.  To do this, extend `data_wizard.loaders.BaseLoader` with a custom `load_iter()` function that returns the data from IterTable, as in the example below.

It is likely that you will want to use a specific serializer with your custom loader.  If so, override `default_serializer` or `get_serializer_name()` on the loader.  By default, these return `None`, which requires the user to specify the serializer when creating or executing the `Run`.

```python
# myapp/models.py
from django.db import models

class CustomIterSource(models.Model):
    some_option = models.TextField()
```

```python
# myapp/loaders.py
from data_wizard import loaders
from .iter import CustomIter

class CustomIterLoader(loaders.BaseLoader):
    default_serializer = 'mydataapp.wizard.CustomSerializer'
    def load_iter(self):
        source = self.run.content_object
        return CustomIter(some_option=source.some_option)
```

```python
# myapp/wizard.py
import data_wizard
from .models import CustomIterSource

data_wizard.set_loader(CustomIterSource, "myapp.loaders.CustomIterLoader")
```

[IterTable]: ../itertable/index.md
[FileLoader]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/loaders.py
[URLLoader]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/loaders.py
[settings]: ./settings.md
[custom-iter]: ../itertable/custom.md
