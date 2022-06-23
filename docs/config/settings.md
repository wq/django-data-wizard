---
order: 1
---

# Django Settings

You can customize many aspects of [Django Data Wizard] through the configuration.  For many projects, the default configuration (shown below) will be sufficient.

```
DATA_WIZARD = {
    'BACKEND': 'data_wizard.backends.threading',
    'LOADER': 'data_wizard.loaders.FileLoader',
    'IDMAP': 'data_wizard.idmap.existing',
    'AUTHENTICATION': 'rest_framework.authentication.SessionAuthentication',
    'PERMISSION': 'rest_framework.permissions.IsAdminUser',
    'AUTO_IMPORT_TASKS': (
        'data_wizard.tasks.check_serializer',
        'data_wizard.tasks.check_iter',
        'data_wizard.tasks.check_columns',
        'data_wizard.tasks.check_row_identifiers',
        'data_wizard.tasks.import_data',
    ),
}
```

### `DATA_WIZARD['BACKEND']`

Setting | Description
---|---
`"data_wizard.backends.threading"` (default) | Run processing tasks asyncronously in a separate lightweight thread.
`"data_wizard.backends.immediate"` | Run tasks in the same thread (blocking the server response until complete)
`"data_wizard.backends.celery"` | Send tasks to a separate celery daemon

See [backends] for more details on how to configure the Celery backend.

### `DATA_WIZARD['LOADER']`

Setting | Description
---|---
`"data_wizard.loaders.FileLoader"` (default) | Load file data from a `file` attribute on the [source model][models] instance.
`"data_wizard.loaders.URLLoader"` | Make a request to the `url` specified in the source model.
(Path to class) | [Custom loader][loaders]

See [loaders] for more details on how to configure the default loaders, or create custom ones.


### `DATA_WIZARD['IDMAP']`

Setting | Description
---|---
`"data_wizard.idmap.existing"` (default) | Automatically map existing IDs, but require user to map unknown ids
`"data_wizard.idmap.never"` | Require user to manually map all IDs the first time they are found in a file
`"data_wizard.idmap.always"` | Always map IDs (skip manual mapping).  Unknown IDs will be passed on as-is to the serializer, which will cause per-row errors unless using natural keys.
(Path to function) | Custom mapping function (see below)

If a custom function is defined, it should accept an identifier and a serializer field, and return the mapped value (or `None` if no automatic mapping is available).  See the [built-in functions][idmap.py] for examples.

Note that the configured `IDMAP` function will only be called the first time a new identifier is encountered.  Once the mapping is established (manually or automatically), it will be re-used in subsequent wizard runs.

### `DATA_WIZARD['AUTHENTICATION']`

Setting | Description
---|---
`"rest_framework.authentication.SessionAuthentication"` (default) | Leverage existing `django.contrib.auth` session cookie.
(Path to class) | Any Django REST Framework [authentication class][authentication][

Note that `DATA_WIZARD['AUTHENTICATION']` is intentionally configured separately from `REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']`.  This is to avoid potential conflicts in projects that provide Django REST Framework APIs for a completely different set of users than those that will be using the Data Wizard.

### `DATA_WIZARD['PERMISSION']`

Setting | Description
---|---
`"rest_framework.permissions.IsAdminUser"` (default) | Only allow Admin users to start new Data Wizard import runs.
`"rest_framework.permissions.IsAuthenticated" | Allow any authenticated user
(Path to class) | Any Django REST Framework [permission class][permissions]

Note that `DATA_WIZARD['PERMISSION']` is intentionally configured separately from `REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES']`.  This is to avoid potential conflicts in projects that provide Django REST Framework APIs for a completely different set of users than those that will be using the Data Wizard.


### `DATA_WIZARD['AUTO_IMPORT_TASKS']`

This list defines the sequence of tasks to execute when running the [auto] API.  The default list is recommended for most projects.

Task | Description
-----|-------------
`data_wizard.tasks.check_serializer` | Ensure that a registered serializer (target model) is selected
`data_wizard.tasks.check_iter` | Ensure that the file data can be loaded from the source model
`data_wizard.tasks.check_columns` | Ensure that columns from the source file can be mapped to fields in the target model serializer
`data_wizard.tasks.check_row_identifiers` | Ensure that foreign key values can be resolved (if present)
`data_wizard.tasks.import_data` | Import each row from the source file to the target model

See [tasks] for more details on how to define custom processing tasks.

[Django Data Wizard]: ./index.md
[models]: ./models.md
[backends]: ./backends.md
[loaders]: ./loaders.md
[auto]: ./api/auto.md
[tasks]: ./tasks.md
[authentication]: https://www.django-rest-framework.org/api-guide/authentication/
[permissions]: https://www.django-rest-framework.org/api-guide/permissions/

[idmap.py]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/idmap.py
