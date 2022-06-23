---
order: -2
icon: pin
---

Getting Started
===============

## Installation

```bash
# Recommended: create virtual environment
# python3 -m venv venv
# . venv/bin/activate

python3 -m pip install data-wizard
```

## Initial Configuration

Within a new or existing Django project, add `data_wizard` to your `INSTALLED_APPS`:

```python
# myproject/settings.py
INSTALLED_APPS = (
   # ...
   'data_wizard',
   'data_wizard.sources',
)
```

> If you want to use a [custom data source][sources] instead of the built-in data source tables (`FileSource` and `URLSource`), do not include `data_wizard.sources` in your `INSTALLED_APPS`.

Next, add `"data_wizard.urls"` to your URL configuration.

```python
# myproject/urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path('datawizard/', include('data_wizard.urls')),
]
```

> If you are using Django Data Wizard's [wq framework integration][wq-setup], you do not need to update urls.py.

Finally, if you would like to override any of the default settings, add a [`DATA_WIZARD` configuration][settings] to your Django settings.

### Target Model Registration

In order to use the wizard, you **must** register one or more target models and/or serializers.  Target model registration helps the wizard know where to put the data it finds in each row of the source spreadsheet.  (By contrast, *source* model registration is optional, as long as you are using the provided `data_wizard.sources` app.)

The target model registration API is modeled after the  Django admin and `admin.py`.  Specifically, Data Wizard will look for a `wizard.py` file in your app directory, which should have the following structure:

```python
# myapp/wizard.py
import data_wizard
from .models import MyModel

data_wizard.register(MyModel)
```

Internally, the wizard will automatically create a Django REST Framework serializer class corresponding to the target model.  If needed, you can also specify a [custom serializer class][serializers] to configure how the target model is validated and populated.

Once everything is configured, upload a source file in the provided [Django admin integration][admin], select "Import via data wizard" from the admin actions menu, and navigate through the provided workflow.

### [Next: Using Django Data Wizard][workflow]

[sources]: ../sources.md
[wq-setup]: ../guides/integrate-with-wq-framework.md
[settings]: ../config/settings.md
[serializers]: ../config/serializers.md
[admin]: ../api/admin.md
[workflow]: ../guides/using-django-data-wizard.md
