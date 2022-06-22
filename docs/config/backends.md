---
order: 6
---

# Task Backends

Any of the following backends can be configured with via the `BACKEND` setting:

```python
# myproject/settings.py

DATA_WIZARD = {
   "BACKEND": "data_wizard.backends.threading"  # Default
              "data_wizard.backends.immediate"
              "data_wizard.backends.celery"
}
```

### `data_wizard.backends.threading`

The `threading` backend creates a separate thread for long-running asynchronous tasks (i.e. `auto` and `data`).  The threading backend leverages the Django cache to pass results back to the status API.  This is the default backend, but it is still a good idea to set it explicitly.

### `data_wizard.backends.immediate`

The `immediate` backend completes all processing before returning a result to the client, even for the otherwise "asynchronous" tasks (`auto` and `data`).  This backend is suitable for small spreadsheets, or for working around threading issues.  This backend maintains minimal state, and is not recommended for use cases involving large spreadsheets or multiple simultanous import processes.

### `data_wizard.backends.celery`

The `celery` backend leverages [Celery] to handle asynchronous tasks, and is usually used with [Redis] as the memory store.
These additional dependencies are not installed with Django Data Wizard by default.  If you want to use this backend, be sure to configure these libraries first or the REST API may not work as expected.  You can use these steps on Ubuntu:

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

[Celery]: http://www.celeryproject.org/
[Redis]: https://redis.io/
[daemonization]: http://docs.celeryproject.org/en/latest/userguide/daemonizing.html
