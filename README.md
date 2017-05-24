**Django Data Wizard** is an interactive tool for mapping structured data (e.g. Excel, XML) into a normalized database structure via [wq.io] and the [Django REST Framework].  Django Data Wizard allows novice users to map spreadsheet columns to serializer fields (and cell values to foreign keys) on-the-fly during the import process.  This reduces the need for preset spreadsheet formats, which most data import solutions require.

By default, Django Data Wizard supports any format supported by [wq.io] (Excel, CSV, JSON, and XML).  Additional formats can be integrating by creating a [custom wq.io class] and then registering it with the wizard.  For example, the [Climata Viewer] uses Django Data Wizard to import data from [climata]'s wq.io-based web service client.

[![Latest PyPI Release](https://img.shields.io/pypi/v/data-wizard.svg)](https://pypi.python.org/pypi/data-wizard)
[![Release Notes](https://img.shields.io/github/release/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/releases)
[![License](https://img.shields.io/pypi/l/data-wizard.svg)](https://wq.io/license)
[![GitHub Stars](https://img.shields.io/github/stars/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/network)
[![GitHub Issues](https://img.shields.io/github/issues/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/issues)

[![Travis Build Status](https://img.shields.io/travis/wq/django-data-wizard.svg)](https://travis-ci.org/wq/django-data-wizard)
[![Python Support](https://img.shields.io/pypi/pyversions/data-wizard.svg)](https://pypi.python.org/pypi/data-wizard)
[![Django Support](https://img.shields.io/badge/Django-1.8%2C%201.9%2C%201.10%2C%201.11-blue.svg)](https://pypi.python.org/pypi/data-wizard)

# Usage

Django Data Wizard provides a JSON (and HTML) API for specifying a data set to import, selecting a serializer, mapping the data columns and identifiers, and (asynchronously) importing the data into the database.

## Installation

```bash
# Recommended: create virtual environment
# python3 -m venv venv
# . venv/bin/activate

pip install data-wizard
```

See <https://github.com/wq/django-data-wizard> to report any issues.

## Celery

Django Data Wizard requires [Celery] to handle asynchronous tasks, and is usually used with [Redis] as the memory store.  These should be configured first or the REST API may not work.  Once Redis is installed, you should be able to add the following to your project settings:
```python
# myproject/settings.py
CELERY_RESULT_BACKEND = BROKER_URL = 'redis://localhost:6379/1'
```

Then, define a celery app:
```python
# myproject/celery.py
from __future__ import absolute_import
from celery import Celery
from django.conf import settings
app = Celery('myproject')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
```

And reference it from your project:

```python
# myproject/__init__.py
from .celery import app as celery_app
```

Finally, make sure that celery is running in the background.  You can test with the following command, then move to a more stable configuration (e.g. [daemonization]).

```bash
# celery.sh
export DJANGO_SETTINGS_MODULE=apiary.settings
celery -A myproject worker -l info
```

Note that any time you change your serializer registration, you should reload celery in addition to restarting the Django WSGI  instance.

## Serializer Registration

As of version 1.0, Data Wizard relies on serializer classes as the primary means of detecting model fields.  These are subclasses of Django REST Framework's [ModelSerializer class].  You can register serializers by creating a `wizard.py` in your app directory (analagous to Django's `admin.py` and wq.db's `rest.py`).

```python
# myapp/wizard.py
from rest_framework import serializers
from data_wizard import registry
from .models import TimeSeries

class TimeSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSeries
        fields = '__all__'

registry.register("Time Series", TimeSeriesSerializer)
```

At least one serializer should be registered in order to use the wizard.  Note the use of a human-friendly serializer label when registering.  This name should be unique throughout the project, but can be changed later on without breaking existing data.  (The class path is used as the actual identifier behind the scenes.)

## REST API

The Data Wizard REST API provides the following capabilities.  If you are using wq.db, the wizard will automatically register itself with the router.  Otherwise, be sure to include `data_wizard.urls` in your URL configuration:

```python
# with wq.db (automatic)
# rest.router.register_model(data_wizard.models.Run, ...)

# without wq.db
from django.conf.urls import include, url

urlpatterns = [
    # ...
    url(r'^', include('data_wizard.urls')),
]
```

The API is accessible as JSON and as HTML - though the HTML interface is (currently) only accessible when using the Mustache template engine (i.e. with wq.db).

### POST /datawizard/

Create a new instance of the wizard (i.e. a `Run`).  The returned run `id` should be used in all subsequent calls to the API.  Each `Run` is tied to the model containing the actual data via a [generic foreign key].

parameter | description
----------|--------------
`object_id` | The id of the object containing the data to be imported.
`content_type_id` | The app label and model name of the referenced model (in the format `app_label.modelname`).
`loader` | (Optional) The class name to use for loading the dataset via wq.io.  The default loader (`data_wizard.loaders.FileLoader`) assumes that the referenced model contains a `FileField` named `file`.
`serializer` | (Optional) The class name to use for serialization.  This can be left unset to allow the user to select it during the wizard run.

If you are using wq.db, you could allow the user to initiate an import run by adding the following to the detail HTML for your model:

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

### POST /datawizard/[id]/auto

Attempt to automatically run the entire data wizard process from beginning to end.  If any input is needed, the import will halt and redirect to the necessary screen.  This is an asynchronous method, and returns a `task_id` to be used with the status API.

### GET /datawizard/[id]/status.json?task=[task]

The status API is used to check the status of an asynchronous task (one of `auto` or `data`).  The API is designed to be used in conjunction with the [wq/progress.js] plugin for [wq.app], which can be used as a reference for custom implementations.  Unlike the other methods, this API should always be called as JSON (either as `status.json` or `status?format=json`).  An object of the following format will be returned:

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
    "skipped": [...],     // information about rows that were skipped

    // Task complete ("SUCCESS"), but no data was imported
    "message": "Input Needed",
    "action": "columns",  // or "serializers", "ids"
    "location": "/datawizard/[id]/columns"
}
```

Note that the `status` field is directly derived from the underlying [Celery task state].

### GET /datawizard/[id]/serializers

### POST /datawizard/[id]/updateserializer

### GET /datawizard/[id]/columns

### POST /datawizard/[id]/updatecolumns

### GET /datawizard/[id]/ids

### POST /datawizard/[id]/updateids

### POST /datawizard/[id]/data

### GET /datawizard/[id]/records


# Examples

[![Climata Viewer](https://wq.io/media/700/screenshots/climata-02.png)](https://wq.io/projects/climata)

[![river.watch](https://wq.io/media/700/screenshots/riverwatch-overview.png)](https://wq.io/projects/river-watch)

[wq.io]: https://wq.io/wq.io
[Django REST Framework]: http://www.django-rest-framework.org/
[wq.db]: https://wq.io/wq.db
[custom wq.io class]: https://wq.io/docs/custom-io
[Climata Viewer]: https://github.com/heigeo/climata-viewer
[climata]: https://github.com/heigeo/climata
[wq framework]: https://wq.io/
[wq.db.rest]: https://wq.io/docs/about-rest
[ModelSerializer class]: http://www.django-rest-framework.org/api-guide/serializers/#modelserializer
[generic foreign key]: https://docs.djangoproject.com/en/1.11/ref/contrib/contenttypes/
[wq/progress.js]: https://wq.io/docs/progress-js
[Celery]: http://www.celeryproject.org/
[Redis]: https://redis.io/
[daemonization]: http://docs.celeryproject.org/en/latest/userguide/daemonizing.html
[wq.app]: https://wq.io/wq.app
[Celery task state]: http://docs.celeryproject.org/en/latest/userguide/tasks.html#task-states
