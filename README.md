**Django Data Wizard** is an interactive tool for mapping tabular data (e.g. Excel, CSV, XML, JSON) into a normalized database structure via [Django REST Framework] and [IterTable].  Django Data Wizard allows novice users to map spreadsheet columns to serializer fields (and cell values to foreign keys) on-the-fly during the import process.  This reduces the need for preset spreadsheet formats, which most data import solutions require.

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
[![License](https://img.shields.io/pypi/l/data-wizard.svg)](https://github.com/wq/django-data-wizard/blob/master/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/network)
[![GitHub Issues](https://img.shields.io/github/issues/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/issues)

[![Travis Build Status](https://img.shields.io/travis/wq/django-data-wizard.svg)](https://travis-ci.org/wq/django-data-wizard)
[![Python Support](https://img.shields.io/pypi/pyversions/data-wizard.svg)](https://pypi.org/project/data-wizard)
[![Django Support](https://img.shields.io/pypi/djversions/data-wizard.svg)](https://pypi.org/project/data-wizard)

# Usage

Django Data Wizard provides a [web interface](#api-documentation), [JSON API](#api-documentation), and [CLI](#command-line-interface) for specifying a [data source](#custom-data-sources) to import (e.g. a previously-uploaded file), selecting a [serializer](#custom-serializers), mapping the data [columns](#columns) and [identifiers](#ids), and (asynchronously) importing the [data](#data) into any target model in the database.

Data Wizard is designed to allow users to iteratively refine their data import flow.  For example, decisions made during an initial data import are preserved for future imports of files with the same structure.  The included [data model](#data-model) makes this workflow possible. 

### Table Of Contents
 
 1. **Getting Started**
    * [Installation](#installation)
    * [Initial Configuration](#initial-configuration)
    * [**Target Model Registration (required)**](#target-model-registration)
 2. **API Documentation**
    * [Run API & Admin Screens](#api-documentation)
    * [Data Model](#data-model)
    * [Command-Line Interface](#command-line-interface)
 3. **Advanced Customization**
    * [Custom Serializers](#custom-serializers)
    * [Custom Data Sources](#custom-data-sources)
    * [Task Backends](#task-backends)
    * [wq Framework Integration](#wq-framework-integration)

## Installation

```bash
# Recommended: create virtual environment
# python3 -m venv venv
# . venv/bin/activate

python3 -m pip install data-wizard
```

See <https://github.com/wq/django-data-wizard> to report any issues.

## Initial Configuration

Within a new or existing Django project, add `data_wizard` to your `INSTALLED_APPS`:

```python
# myproject/settings.py
INSTALLED_APPS = (
   # ...
   'data_wizard',
   'data_wizard.sources',  # Recommended
)

# This can be omitted to use the defaults
DATA_WIZARD = {
    'BACKEND': 'data_wizard.backends.threading',
    'LOADER': 'data_wizard.loaders.FileLoader',
    'IDMAP': 'data_wizard.idmap.never',   # 'data_wizard.idmap.existing' in 2.0
    'AUTHENTICATION': 'rest_framework.authentication.SessionAuthentication',
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

### Target Model Registration

In order to use the wizard, you **must** register one or more target models and/or serializers.  Target model registration helps the wizard know where to put the data it finds in each row of the source spreadsheet.  (By contrast, *source* model registration is optional, as long as you are using the provided `data_wizard.sources` app.)

The registration API is modeled after the  Django admin and `admin.py`.  Specifically, Data Wizard will look for a `wizard.py` file in your app directory, which should have the following structure:

```python
# myapp/wizard.py
import data_wizard
from .models import MyModel

data_wizard.register(MyModel)
```

Internally, the wizard will automatically create a Django REST Framework serializer class corresponding to the target model.  If needed, you can also specify a [custom serializer class](#custom-serializers) to configure how the target model is validated and populated.

Once everything is configured, upload a source file in the Django admin, select "Import via data wizard" from the admin actions menu, and navigate through the screens described below.

## API Documentation

Django Data Wizard is implemented as a series of views that can be accessed via the Django admin as well as via a JSON API.

---

<img align="right" width=320 height=240
     alt="Select Source & Start Import"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/A2-source-list.png">

### New Run

#### `POST /datawizard/`

Creates a new instance of the wizard (i.e. a `Run`).  If you are using the Django admin integration, this step is executed when you select "Import via Data Wizard" from the admin actions menu.  If you are using the JSON API, the returned run `id` should be used in all subsequent calls to the API.  Each `Run` is tied to the source model via a [generic foreign key].

parameter         | description
------------------|----------------------------------------
`object_id` | The primary key of the *source* model instance containing the data to be imported.
`content_type_id` | The *source* model's app label and model name (in the format `app_label.modelname`).
`loader` | (Optional) The class name to use for loading the source dataset via [IterTable].  The default loader (`data_wizard.loaders.FileLoader`) assumes that the source model contains a `FileField` named `file`.
`serializer` | (Optional) The serializer class to use when populating the *target* model.  This can be left unset to allow the user to select the target during the wizard run.

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
     
The `serializers` task provides a list of all registered serializers (i.e. target models).  This screen is shown by the `auto` task if a serializer was not specified when the `Run` was created.  The default [run_serializers.html] template includes an interface for selecting a target.  If a serializer is already selected, the template will display the label and a button to (re)start the `auto` task.

<br>

---

<img align="right" width=320 height=240
     alt="Serializer Selected"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/01-updateserializer.png">
     
### updateserializer
#### `POST /datawizard/[id]/updateserializer`

The `updateserializer` task updates the specified `Run` with the selected target serializer name.  This is typically called from [the form][run_serializers.html] generated by the `serializers` task, and will redirect to that task when complete.

parameter    | description
-------------|----------------------------------------
`serializer` | The class name (or label) of the target serializer to use for this run.

---

<img align="right" width=320 height=240
     alt="Column Choices"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/02-columns.png">

### columns
#### `GET /datawizard/[id]/columns`

The `columns` task lists all of the columns found in the source dataset (i.e. spreadsheet) and their mappings to target serializer fields.  This screen is shown by the `auto` task if there are any column names that could not be automatically mapped.  The potential mappings are one of:

  * simple serializer field names (e.g. `field`)
  * nested field names (for [natural keys], e.g. `nested[record][field]`)
  * [EAV][Entity-Attribute-Value] attribute-value mappings (e.g. `values[][value];attribute_id=1`).  Note that EAV support requires a [custom serializer class](#custom-serializers).

The default [run_columns.html] template includes an interface for mapping data columns to serializer fields.  If all columns are already mapped, the template will display the mappings and a button to (re)start the `auto` task.

---

<img align="right" width=320 height=240
     alt="Columns Selected"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/03-updatecolumns.png">
     
### updatecolumns
#### `POST /datawizard/[id]/updatecolumns`

The `updatecolumns` task saves the specified mappings from source data columns to target serializer fields.  This is typically called from [the form][run_columns.html] generated by the `columns` task, and will redirect to that task when complete.

parameter     | description
--------------|----------------------------------------
`rel_[relid]` | The column to map to the specified serializer field.  The `relid` and the complete list of possible mappings will be provided by the `columns` task.

---

<img align="right" width=320 height=240
     alt="Identifier Choices"
     src="https://raw.githubusercontent.com/wq/django-data-wizard/master/images/04-ids.png">

### ids
#### `GET /datawizard/[id]/ids`

The `ids` task lists all of the foreign key values found in the source dataset (i.e. spreadsheet).  If there are any unmapped foreign key values, the auto task will stop and redirect to the `ids` task.  The default [run_ids.html] template includes an interface for mapping row identifiers to foreign key values.  The potential mappings depend on the serializer field used to represent the foreign key.

 * For [PrimaryKeyRelatedField], [SlugRelatedField], and [NaturalKeySerializer][natural keys], the choices will include all existing record ID or slugs.
 * For `NaturalKeySerializer` only, a`"new"` choice will also be included, allowing for the possibility of creating new records in the foreign table on the fly.
 
Once all ids are mapped, the template will display the mappings and a button to (re)start the `auto` task.

Note that the `auto` task will skip the `ids` task entirely if any of the following are true:
  * The file contains no foreign key columns
  * All foreign key values were already mapped during a previous import run
  * All foreign key values can be automatically mapped via the `DATA_WIZARD['IDMAP']` setting:
  
`DATA_WIZARD['IDMAP']` | notes | detail
--|--|--
`"data_wizard.idmap.never"` | Default&nbsp;in&nbsp;1.x | Require user to manually map all IDs the first time they are found in a file
`"data_wizard.idmap.existing"` | New&nbsp;in&nbsp;1.3, Default&nbsp;in&nbsp;2.0 | Automatically map existing IDs, but require user to map unknown ids
`"data_wizard.idmap.always"` | New&nbsp;in&nbsp;1.3 | Always map IDs (skip manual mapping).  Unknown IDs will be passed on as-is to the serializer, which will cause per-row errors unless using natural keys.
(custom import path) | New&nbsp;in&nbsp;1.3 | The function should accept an identifier and a serializer field, and return the mapped value (or `None` if no automatic mapping is available).  See the [built-in functions][idmap.py] for examples.

Note that the configured `IDMAP` function will only be called the first time a new identifier is encountered.  Once the mapping is established (manually or automatically), it will be re-used in subsequent wizard runs.

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

The `records` task provides a list of imported rows (including errors).  It is redirected to by the `auto` and `data` tasks upon completion.  Successfully imported `Record` instances will have a [generic foreign key] pointing to the target model.  The `records` task will include links to the `get_absolute_url()` or admin screen for each newly imported target model instance.  The default [run_records.html] template includes an interface for displaying the record details.

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

## Data Model

Django Data Wizard provides a number of Django models that help track the import process, and preserve data mapping decisions for future reuse.  While a *source* model is required, your *target* data model(s) generally do not have to be changed to support Data Wizard integration.

step | description | model
-----|-------------|--------
0 | Upload **source** file | Create `FileSource` (or custom source model)
1 | Start data wizard run | Create `Run`
2 | Select serializer (& target model) | Update `Run`
3 | Map columns to database field names | One `Identifier` per column, if needed
4 | Map cell values to foreign keys | One `Identifier` per unique value
5 | Import data into **target** model | One `Record` + one target model instance per row

The `Run` model includes a [generic foreign key] pointing to the source model (e.g. `FileSource`.)  Each row in the source spreadsheet will be mapped to a `Record`.  If the row was successfully imported, a new instance of the target data model will be created, and the `Record` will have a generic foreign key pointing to it.  The `Identifier` model contains no foreign keys, since identifier mappings are reused for subsequent imports.  Instead, a separate `Range` model tracks the location(s) (rows/columns) of each `Identifier` in each `Run`.

Note that the above workflow just describes the most common use case.  You can create [custom serializers](#custom-serializers) that update more than one target data model per spreadsheet row.  And you can specify [custom data sources](#custom-data-sources) that might not be a spreadsheet or even a file.

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

Data Wizard uses instances of Django REST Framework's [Serializer class][ModelSerializer] to determine the destination fields on the target model.  Specifically, the default serializer is [NaturalKeyModelSerializer], which is based on [ModelSerializer].

You can override the default serializer by calling `data_wizard.register()` with a name and a serializer class instead of a model class.  Multiple serializers can be registered with the wizard to support multiple import configurations and target models.  

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

        # Optional - see options below
        data_wizard = {
            'header_row': 0,
            'start_row': 1,
            'show_in_list': True,
            'idmap': data_wizard.idmap.existing,
        }

# Use default name & serializer
data_wizard.register(TimeSeries)

# Use custom name & serializer
data_wizard.register("Time Series - Custom Serializer", TimeSeriesSerializer)
```

At least one serializer or model should be registered in order to use the wizard.  Note the use of a human-friendly serializer label when registering a serializer.  This name should be unique throughout the project, but can be changed later on without breaking existing data.  (The class path is used as the actual identifier behind the scenes.)

### Serializer Options

In general, custom serializers have all the capabilities of regular [Django REST Framework serializers][serializers], including custom validation rules and the ability to populate multiple target models.  While the `request` context is not available, information about the run (including the user) can be retrieved through the `data_wizard` context instead.

When overriding a serializer for a [natural key model][natural keys], be sure to extend [NaturalKeyModelSerializer], as in [this example][naturalkey_wizard].  In other cases, extend [ModelSerializer] (as in the example above) or the base [Serializer](serializers) class.

Custom serializers can be used to support [Entity-Attribute-Value] spreadsheets where the attribute names are specified as additional columns.  To support this scenario, the `Entity` serializer should include a nested `Value` serializer with `many=True`, and the `Value` serializer should have a foreign key to the `Attribute` table, as in [this example][eav_wizard].

Data Wizard also supports additional configuration by setting a `data_wizard` attribute on the `Meta` class of the serializer.  The following options are supported.

name | default | notes
--|--|--
`header_row` | 0 | Specifies the first row of the spreadsheet that contains column headers.  If this is greater than 0, the space above the column headers will be scanned for anything that looks like a one-off "global" value intended to be applied to every row in the imported data.
`start_row` | 1 | The first row of data.  If this is greater than `header_row + 1`, the column headers will be assumed to span multiple rows.  A common case is when EAV parameter names are on the first row and units are on the second.
`show_in_list` | `True` | **New in 1.2**.  If set to `False`, the serializer will be available through the API but not listed in the wizard views.  This is useful if you have a serializer that should only be used during fully automated workflows.
`idmap` | [`IDMAP` setting](#ids) | **New in 1.3**.  Can be any of `data_wizard.idmap.*` or a custom function.  Unlike the `IDMAP` setting, this should always be an actual function and not an import path.

## Custom Data Sources

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

If you have a generic loader that can work with multiple source models, you can also set the default loader globally:

```python
# myapp/settings.py
DATA_WIZARD = {
    'LOADER': 'myapp.loaders.FileLoader'
}
```

As of Django Data Wizard 1.2, you should register a custom `ModelAdmin` class to add the Import action in the admin panel for your model.

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
The default loaders support any file format supported by [IterTable] (Excel, CSV, JSON, and XML).  Additional formats can be integrating by creating a [custom IterTable class][custom-iter] and then registering it with the wizard.  For example, the [Climata Viewer] uses Django Data Wizard to import data from [climata]'s IterTable-based web service client.  To do this, extend `data_wizard.loaders.BaseLoader` with a custom `load_iter()` function that returns the data from IterTable, as in the example below.

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

The Django Data Wizard has built-in support for integration with the [wq framework].  On the server, configuration is mostly the same, except that you do not need to add `"data_wizard.urls"` to your urls.py as the wizard will register itself with [wq.db] instead.

Data Wizard provides mustache templates for each of the above tasks to integrate with the wq.app UI.  These are rendered on the server and do not need to be included in your JavaScript build.  However, you should install the [@wq/progress] plugin via NPM and register it with [@wq/app].

```javascript
// src/index.js
import app from '@wq/app';
import progress from '@wq/progress';

app.use(progress);
app.init(config).then(...);
```

Once everything is set up, add the following `<form>` to the detail template that wq generates for your source model.  Note that you will need to add this `<form>` manually even if the source model is one of `data_wizard.sources`.  After adding the form, be sure to skip template regeneration for the source model.

```html
<!-- filesource_detail.html -->
<h1>{{label}}</h1>
<a href="{{rt}}/media/{{file}}" rel="external">Download File</a>

<form action="{{rt}}/datawizard/" method="post">
  {{>csrf}}
  <input type="hidden" name="content_type_id" value="sources.filesource">
  <input type="hidden" name="object_id" value="{{id}}">
  <button type="submit">Import Data from This File</button>
</form>
```

[IterTable]: https://github.com/wq/itertable
[Django REST Framework]: http://www.django-rest-framework.org/
[natural keys]: https://github.com/wq/django-natural-keys
[Entity-Attribute-Value]: https://wq.io/docs/eav-vs-relational
[ERAV]: https://wq.io/docs/erav
[vera]: https://wq.io/vera

[wq.db]: https://wq.io/wq.db
[custom-iter]: https://github.com/wq/itertable/blob/master/docs/about.md
[Climata Viewer]: https://github.com/heigeo/climata-viewer
[climata]: https://github.com/heigeo/climata
[wq framework]: https://wq.io/
[wq.db.rest]: https://wq.io/docs/about-rest
[ModelSerializer]: http://www.django-rest-framework.org/api-guide/serializers/#modelserializer
[serializers]: http://www.django-rest-framework.org/api-guide/serializers/
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
[idmap.py]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/idmap.py
[run_data.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_data.html
[run_records.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_records.html

[naturalkey_wizard]: https://github.com/wq/django-data-wizard/blob/master/tests/naturalkey_app/wizard.py
[eav_wizard]: https://github.com/wq/django-data-wizard/blob/master/tests/eav_app/wizard.py
[management command]: https://docs.djangoproject.com/en/2.1/ref/django-admin/

[@wq/progress]: https://github.com/wq/django-data-wizard/tree/master/packages/progress
[@wq/app]: https://wq.io/docs/app-js
