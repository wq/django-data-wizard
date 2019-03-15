**Django Data Wizard** is an interactive tool for mapping tabular data (e.g. Excel, CSV, XML, JSON) into a normalized database structure via [Django REST Framework] and [wq.io].  Django Data Wizard allows novice users to map spreadsheet columns to serializer fields (and cell values to foreign keys) on-the-fly during the import process.  This reduces the need for preset spreadsheet formats, which most data import solutions require.

<img width="33%"
     alt="Column Choices"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/02-columns.png">
<img width="33%"
     alt="Auto Import - Progress Bar"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/08-data75.png">
<img width="33%"
     alt="Imported Records"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/10-records.png">

The Data Wizard supports straightforward one-to-one mappings from spreadsheet columns to database fields, as well as more complex scenarios like [natural keys] and [Entity-Attribute-Value] (or "wide") table mappings.  It was originally developed for use with the [ERAV data model][ERAV] provided by [vera].

[![Latest PyPI Release](https://img.shields.io/pypi/v/data-wizard.svg)](https://pypi.org/project/data-wizard)
[![Release Notes](https://img.shields.io/github/release/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/releases)
[![License](https://img.shields.io/pypi/l/data-wizard.svg)](https://wq.io/license)
[![GitHub Stars](https://img.shields.io/github/stars/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/network)
[![GitHub Issues](https://img.shields.io/github/issues/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/issues)

[![Travis Build Status](https://img.shields.io/travis/wq/django-data-wizard.svg)](https://travis-ci.org/wq/django-data-wizard)
[![Python Support](https://img.shields.io/pypi/pyversions/data-wizard.svg)](https://pypi.org/project/data-wizard)
[![Django Support](https://img.shields.io/pypi/djversions/data-wizard.svg)](https://pypi.org/project/data-wizard)

# Usage

Django Data Wizard provides a [web interface](#api-documentation), [JSON API](#api-documentation), and [CLI](#command-line-interface) for specifying a [data source](#custom-data-sources) to import (e.g. a previously-uploaded file), selecting a [serializer](#custom-serializers), mapping the data [columns](#columns) and [identifiers](#ids), and (asynchronously) importing the [data](#data) into the database.

## Installation

```bash
# Recommended: create virtual environment
# python3 -m venv venv
# . venv/bin/activate

pip install data-wizard
```

See <https://github.com/wq/django-data-wizard> to report any issues.

## Initial Configuration

Within a new or existing Django project, add `data_wizard` to your `INSTALLED_APPS`:

```python
# myproject/settings.py
INSTALLED_APPS = (
   # ...
   'data_wizard',
   'data_wizard.sources',  # Optional
)

# This can be omitted to use the defaults
DATA_WIZARD = {
    'BACKEND': 'data_wizard.backends.threading',
    'LOADER': 'data_wizard.loaders.FileLoader',
    'PERMISSION': 'rest_framework.permissions.IsAdminUser',
}
```

If you would like to use the built-in data source tables (`FileSource` and `URLSource`), also include `data_wizard.sources` in your `INSTALLED_APPS`.  Otherwise, you will want to configure one or more [custom data sources (see below)](#custom-data-sources).

> Note: In version 1.1.0 and later, Django Data Wizard uses a simple [threading backend](#data_wizardbackendsthreading) for executing asynchronous tasks.  The old [celery backend](#data_wizardbackendscelery) can also be used but this is no longer required.


Next, add `"data_wizard.urls"` to your URL configuration.

```python
# myproject/urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path('datawizard/', include('data_wizard.urls')),
]
```

> Note: If you are upgrading from 1.0, you will need to update your URLs to add the `datawizard/` prefix as shown above.

Finally, register one or more target models with the wizard.  Like the Django admin and `admin.py`, Data Wizard will look for a `wizard.py` file in your app directory:

```python
# myapp/wizard.py
import data_wizard
from .models import MyModel

data_wizard.register(MyModel)
```

If needed, you can use a [custom serializer class](#custom-serializers) to configure how the target model is validated and populated.

Once everything is configured, create a data source in the Django admin, select "Import via data wizard" from the admin actions menu, and navigate through the screens described below.

## API Documentation

Django Data Wizard is implemented as a series of views that can be accessed via the Django admin as well as via a JSON API.

---

<img align="right" width=320 height=240
     alt="Select Source & Start Import"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/A2-source-list.png">

### New Run

#### `POST /datawizard/`

Creates a new instance of the wizard (i.e. a `Run`).  If you are using the Django admin integration, this step is executed when you select "Import via Data Wizard" from the admin actions menu.  If you are using the JSON API, the returned run `id` should be used in all subsequent calls to the API.  Each `Run` is tied to the model containing the actual data via a [generic foreign key].

parameter         | description
------------------|----------------------------------------
`object_id` | The id of the object containing the data to be imported.
`content_type_id` | The app label and model name of the referenced model (in the format `app_label.modelname`).
`loader` | (Optional) The class name to use for loading the dataset via wq.io.  The default loader (`data_wizard.loaders.FileLoader`) assumes that the referenced model contains a `FileField` named `file`.
`serializer` | (Optional) The class name to use for serialization.  This can be left unset to allow the user to select it during the wizard run.

---

<img align="right" width=320 height=240
     alt="Auto Import - Progress Bar"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/06-data25.png">
     
### auto
#### `POST /datawizard/[id]/auto`

The `auto` task attempts to run the entire data wizard process from beginning to end.  If any input is needed, the import will halt and redirect to the necessary screen.  If no input is needed, the `auto` task is equivalent to starting the `data` task directly.  This is an asynchronous method, and returns a `task_id` to be used with the status API.

The [run_detail.html] template provides an example form that initiates the `auto` task.  The `auto` task itself uses the [run_auto.html] template.  

---

### status
#### `GET /datawizard/[id]/status.json?task=[task]`

The `status` API is used to check the status of an asynchronous task (one of `auto` or `data`).  The API is used by the provided [data_wizard/js/progress.js] to update the `<progress>` bar in the [run_auto.html] and [run_data.html] templates.  Unlike the other methods, this API is JSON-only and has no HTML equivalent.  An object of the following format will be returned:

```js
{
    // General properties
    "status": "PROGRESS", // or "SUCCESS", "FAILURE"
    "stage": "meta",      // or "data"
    "current": 23,        // currently processing row
    "total": 100,         // total number of rows
    
    // "FAILURE"
    "error": "Error Message",

    // Task complete ("SUCCESS")
    "action": "records",        // or "serializers", "columns" "ids"
    "message": "Input Needed",  // if action is not "records"
    "skipped": [...],           // rows that could not be imported
    "location": "/datawizard/[id]/records",
}
```

The potential values for the  `status` field are the same as common [Celery task states], even when not using the `celery` backend.  When running an `auto` task, the result is `SUCCESS` whenever the task ends without errors, even if there is additional input needed to fully complete the run.

The default [run_auto.html] and [run_data.html] templates include a `<progress>` element for use with the status task.

---

<img align="right" width=320 height=240
     alt="Serializer Choices"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/00-serializers.png">

### serializers
#### `GET /datawizard/[id]/serializers`
     
The `serializers` task provides a list of all registered serializers.  This screen is shown by the `auto` task if a serializer was not specified when the `Run` was created.  The default [run_serializers.html] template includes an interface for selecting a registered serializer.  If a serializer is already selected, the template will display the label and a button to (re)start the `auto` task.

<br>

---

<img align="right" width=320 height=240
     alt="Serializer Selected"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/01-updateserializer.png">
     
### updateserializer
#### `POST /datawizard/[id]/updateserializer`

The `updateserializer` task updates the specified `Run` with the selected serializer class name.  This is typically called from [the form][run_serializers.html] generated by the `serializers` task, and will redirect to that task when complete.

parameter    | description
-------------|----------------------------------------
`serializer` | The class name (or label) of the serializer to use for this run.

---

<img align="right" width=320 height=240
     alt="Column Choices"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/02-columns.png">

### columns
#### `GET /datawizard/[id]/columns`

The `columns` task lists all of the columns found in the dataset (i.e. spreadsheet) and their mappings to serializer fields.  This screen is shown by the `auto` task if there are any column names that could not be automatically mapped.  The potential mappings are one of:

  * simple serializer field names (e.g. `field`)
  * nested field names (for [natural keys], e.g. `nested[record][field]`)
  * [EAV][Entity-Attribute-Value] attribute-value mappings (e.g. `values[][value];attribute_id=1`).

To enable a natural key mapping, the registered serializer should be an instance of `NaturalKeyModelSerializer`, as in [this example][naturalkey_wizard].  To enable an EAV mapping, the registered serializer should include a nested serializer with `many=True` and at least one foreign key to the attribute table, as in [this example][eav_wizard].

The default [run_columns.html] template includes an interface for mapping data columns to serializer fields.  If all columns are already mapped, the template will display the mappings and a button to (re)start the `auto` task.

---

<img align="right" width=320 height=240
     alt="Columns Selected"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/03-updatecolumns.png">
     
### updatecolumns
#### `POST /datawizard/[id]/updatecolumns`

The `updatecolumns` task saves the specified mappings from data columns to serializer fields.  This is typically called from [the form][run_columns.html] generated by the `columns` task, and will redirect to that task when complete.

parameter     | description
--------------|----------------------------------------
`rel_[relid]` | The column to map to the specified serializer field.  The `relid` and the complete list of possible mappings will be provided by the `columns` task.

---

<img align="right" width=320 height=240
     alt="Identifier Choices"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/04-ids.png">

### ids
#### `GET /datawizard/[id]/ids`

The `ids` task lists all of the identifiers found in the dataset (i.e. spreadsheet) that are in a column known to correspond to a foreign key.  This screen is shown by the `auto` task if there are any identifiers that could not be automatically mapped to foreign key values.  The potential mappings depend on the serializer field used to represent the foreign key.

 * Existing record ID or slug (for [PrimaryKeyRelatedField], [SlugRelatedField], and [NaturalKeySerializer][natural keys])
 * `"new"` (`NaturalKeySerializer` only)

The primary difference is that `NaturalKeySerializer` allows for the possibility of creating new records in the foreign table on the fly, while the regular related fields do not.

The default [run_ids.html] template includes an interface for mapping row identifiers to foreign key values.   If all ids are already mapped (or indicated to be new natural keys), the template will display the mappings and a button to (re)start the `auto` task.

---

<img align="right" width=320 height=240
     alt="Identifiers Selected"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/05-updateids.png">
     
### updateids
#### `POST /datawizard/[id]/updateids`

The `updateids` task saves the specified mappings from row identifiers to foreign key values.  This is typically called from [the form][run_ids.html] generated by the `ids` task, and will redirect to that task when complete.

parameter            | description
---------------------|----------------------------------------
`ident_[identid]_id` | The identifier to map to the specified foreign key value.  The `identid` and the complete list of possible mappings will be provided by the `ids` task.

---

<img align="right" width=320 height=240
     alt="Auto Import - Progress Bar"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/08-data75.png">

### data
#### `POST /datawizard/[id]/data`

The `data` task starts the actual import process (and is called by `auto` behind the scenes).  Unlike `auto`, calling `data` directly will not cause a redirect to one of the other tasks if any meta input is needed.  Instead, `data` will attempt to import each record as-is, and report any errors that occured due to e.g. missing fields or unmapped foreign keys.

This is an asynchronous method, and returns a `task_id` to be used with the `status` API.  The default [run_data.html] template includes a `<progress>` element for use with status task.

---

<img align="right" width=320 height=240
     alt="Imported Records"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/10-records.png">

### records
#### `GET /datawizard/[id]/records`

The `records` task provides a list of imported rows (including errors).  It is redirected to by the `auto` and `data` tasks upon completion.  When possible, the `records` task includes links to the `get_absolute_url()` or to the admin screen for each newly imported record.  The default [run_records.html] template includes an interface for displaying the record details.

<br>

---

<img align="right" width=320 height=240
     alt="Run List"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/11-run-list.png">

### Run List
#### `GET /datawizard/`

Django Data Wizard provides a list view that summarises prior runs and the number of records imported by each.  Incomplete runs can also be restarted from this list.

<br><br>

---

<img align="right" width=320 height=240
     alt="Identifier Admin"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/A3-identifiers.png">
     
### Identifier Admin
#### `GET /admin/data_wizard/identifer/`

As of version 1.1.0, Django Data Wizard identifier mappings can be viewed and edited via the Django Admin.  Runs can also be viewed through the admin - though the Run List above will generally be more useful.

<br>

## Command-Line Interface

Django Data Wizard provides a single [management command], `runwizard`, that can be used to initiate the `auto` task from the command line.  This can be used to facilitate automated processing, for example as part of a regular cron job.  Note that the CLI does not (currently) support interactively mapping columns and ids, so these should be pre-mapped using the web or JSON API.

Usage:

```bash
./manage.py runwizard myapp.mymodel 123 \
    --loader myapp.loaders.customloader \
    --serializer myapp.serializer.customserializer \
    --username myusername
```

The basic usage is similar to the [New Run API](#new-run).  Only a content type and object id are required, while the other arguments will be auto-detected if possible.  In particular, you may want to use [set_loader()](#custom-loader) to predefine the default `loader` and `serializer` for any models you plan to use with the CLI.

The `runwizard` command will create a new `Run` and immediately start the `auto` task.  Errors will be shown on the console.

## Custom Serializers

Data Wizard uses instances of Django REST Framework's [Serializer class][ModelSerializer] to determine the destination fields on the database model.  Specifically, the default serializer is [NaturalKeyModelSerializer], which is based on [ModelSerializer].

You can override the default serializer by calling `data_wizard.register()` with a name and a serializer class instead of a model class.  Multiple serializers can be registered with the wizard to support multiple import configurations and destination models.  

```python
# myapp/wizard.py
from rest_framework import serializers
import data_wizard
from .models import TimeSeries


class TimeSeriesSerializer(serializers.ModelSerializer):
    # (custom fields here)
    class Meta:
        model = TimeSeries
        fields = '__all__'

# Use default name & serializer
data_wizard.register(TimeSeries)

# Use custom name & serializer
data_wizard.register("Time Series - Custom Serializer", TimeSeriesSerializer)
```

At least one serializer or model should be registered in order to use the wizard.  Note the use of a human-friendly serializer label when registering a serializer.  This name should be unique throughout the project, but can be changed later on without breaking existing data.  (The class path is used as the actual identifier behind the scenes.)

## Custom Data Sources

Django Data Wizard uses [wq.io] to determine the source columns present on the spreadsheet or other data source.  Django Data Wizard can use any Django model instance as a source for its data, provided there is a registered loader that can convert the source model into a [wq.io] iterable.  Data Wizard provides two out-of-the the box loaders, [FileLoader] and [URLLoader], that can be used with the provided models in `data_wizard.sources` (`FileSource` and `URLSource`, respectively).

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

You can also set the default loader globally:

```python
# myapp/settings.py
DATA_WIZARD = {
    'LOADER': 'myapp.loaders.FileLoader'
}
```

### Custom Loader
The default loaders support any file format supported by [wq.io] (Excel, CSV, JSON, and XML).  Additional formats can be integrating by creating a [custom wq.io class] and then registering it with the wizard.  For example, the [Climata Viewer] uses Django Data Wizard to import data from [climata]'s wq.io-based web service client.  To do this, extend `data_wizard.loaders.BaseLoader` with a custom `load_io()` function that returns the data from wq.io, as in the example below.

It is likely that you will want to use a specific serializer with your custom loader.  If so, override `default_serializer` or `get_serializer_name()` on the loader.  By default, these return `None`, which requires the user to specify the serializer when creating or executing the `Run`.

```python
# myapp/models.py
from django.db import models

class CustomIOSource(models.Model):
    some_option = models.TextField()
```

```python
# myapp/loaders.py
from data_wizard import loaders
from .io import CustomIO

class CustomIOLoader(loaders.BaseLoader):
    default_serializer = 'mydataapp.wizard.CustomSerializer'
    def load_io(self):
        source = self.run.content_object
        return CustomIO(some_option=source.some_option)
```

```python
# myapp/wizard.py
import data_wizard
from .models import CustomIOSource

data_wizard.set_loader(CustomIOSource, "myapp.loaders.CustomIOLoader")
```


## Task Backends

As of version 1.1.0, Django Data Wizard **no longer requires** the use of `celery` as a task runner.  Any of the following backends can be configured with via the `BACKEND` setting:

```python
# myproject/settings.py

DATA_WIZARD = {
   "BACKEND": "data_wizard.backends.threading"  # Default in 1.1.x
              "data_wizard.backends.immediate"
              "data_wizard.backends.celery"     # Only choice in 1.0.x
}
```

For backwards compatibility with 1.0.x, the default backend reverts to `celery` if you have `CELERY_RESULT_BACKEND` defined in your project settings.  However, it is recommended to explicitly set `BACKEND`, as this behavior may change in a future major version of Data Wizard.

### `data_wizard.backends.threading`

The `threading` backend creates a separate thread for long-running asynchronous tasks (i.e. `auto` and `data`).  The threading backend leverages the Django cache to pass results back to the status API.  As of Django Data Wizard 1.1.0, **this backend is the default** unless you have configured Celery.

### `data_wizard.backends.immediate`

The `immediate` backend completes all processing before returning a result to the client, even for the otherwise "asynchronous" tasks (`auto` and `data`).  This backend is suitable for small spreadsheets, or for working around threading issues.  This backend maintains minimal state, and is not recommended for use cases involving large spreadsheets or multiple simultanous import processes.

### `data_wizard.backends.celery`

The `celery` backend leverages [Celery] to handle asynchronous tasks, and is usually used with [Redis] as the memory store.
**Celery is no longer required to use Django Data Wizard,** unless you would like to use the `celery` backend.  If so, be sure to configure these libraries first or the REST API may not work as expected.  You can use these steps on Ubuntu:

```bash
# Install redis and celery
sudo apt-get install redis-server
pip install celery redis
```

Once Redis is installed, configure the following files in your project:
```python
# myproject/settings.py
DATA_WIZARD {
    'BACKEND': 'data_wizard.backends.celery'
}
CELERY_RESULT_BACKEND = BROKER_URL = 'redis://localhost:6379/1'

# myproject/celery.py
from __future__ import absolute_import
from celery import Celery
from django.conf import settings
app = Celery('myproject')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# myproject/__init__.py
from .celery import app as celery_app
```

Finally, run celery with `celery -A myproject`.  You may want to use celery's [daemonization] to keep the process running in the background.  Any time you change your serializer registration, be sure to reload celery in addition to restarting the Django WSGI instance.

> Note that the requirement for an extra daemon means this backend can break more easily after a server restart.  Even worse, you may not notice that the backend is down for several months (e.g. until a user tries to import a spreadsheet).  For this reason, **we recommend using one of the other backends** unless you are already using celery for other background processing tasks.

## wq Framework integration

The Django Data Wizard has built-in support for integration with the [wq framework].  Configuration is mostly the same, except that you do not need to add `"data_wizard.urls"` to your urls.py as the wizard with register itself with [wq.db] instead.

Data Wizard includes mustache templates for each of the above tasks to integrate with the wq.app UI.  Be sure to enable the [wq/progress.js] plugin for use with the `run_auto.html` and `run_data.html` template.  You could allow the user to initiate an import run by adding the following to the detail HTML for your model:

```html
<!-- filemodel_detail.html -->
<h1>{{label}}</h1>
<a href="{{rt}}/media/{{file}}" rel="external">Download File</a>

<form action="{{rt}}/datawizard/" method="post" data-ajax="true" data-wq-json="false">
  {{>csrf}}
  <input type="hidden" name="content_type_id" value="myapp.filemodel">
  <input type="hidden" name="object_id" value="{{id}}">
  <button type="submit">Import Data from This File</button>
</form>
```

```javascript
// myapp/main.js
define(['wq/app', 'wq/progress', ...],
function(app, progress, ...) {
    app.use(progress);
    app.init(config).then(...);
});
```

[wq.io]: https://wq.io/wq.io
[Django REST Framework]: http://www.django-rest-framework.org/
[natural keys]: https://github.com/wq/django-natural-keys
[Entity-Attribute-Value]: https://wq.io/docs/eav-vs-relational
[ERAV]: https://wq.io/docs/erav
[vera]: https://wq.io/vera

[wq.db]: https://wq.io/wq.db
[custom wq.io class]: https://wq.io/docs/custom-io
[Climata Viewer]: https://github.com/heigeo/climata-viewer
[climata]: https://github.com/heigeo/climata
[wq framework]: https://wq.io/
[wq.db.rest]: https://wq.io/docs/about-rest
[ModelSerializer]: http://www.django-rest-framework.org/api-guide/serializers/#modelserializer
[NaturalKeyModelSerializer]: https://github.com/wq/django-natural-keys#naturalkeymodelserializer
[FileLoader]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/loaders.py
[URLLoader]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/loaders.py
[generic foreign key]: https://docs.djangoproject.com/en/1.11/ref/contrib/contenttypes/
[data_wizard/js/progress.js]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/static/data_wizard/js/progress.js
[wq/progress.js]: https://wq.io/docs/progress-js
[Celery]: http://www.celeryproject.org/
[Redis]: https://redis.io/
[daemonization]: http://docs.celeryproject.org/en/latest/userguide/daemonizing.html
[wq.app]: https://wq.io/wq.app
[Celery task states]: http://docs.celeryproject.org/en/latest/userguide/tasks.html#task-states

[PrimaryKeyRelatedField]: http://www.django-rest-framework.org/api-guide/relations/#primarykeyrelatedfield
[SlugRelatedField]: http://www.django-rest-framework.org/api-guide/relations/#slugrelatedfield

[run_detail.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_detail.html
[run_auto.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_auto.html
[run_serializers.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_serializers.html
[run_columns.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_columns.html
[run_ids.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_ids.html
[run_data.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_data.html
[run_records.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_records.html

[naturalkey_wizard]: https://github.com/wq/django-data-wizard/blob/master/tests/naturalkey_app/wizard.py
[eav_wizard]: https://github.com/wq/django-data-wizard/blob/master/tests/eav_app/wizard.py
[management command]: https://docs.djangoproject.com/en/2.1/ref/django-admin/
