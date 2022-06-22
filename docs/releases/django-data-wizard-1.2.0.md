---
repo: django-data-wizard
date: 2019-09-02
---

# Django Data Wizard 1.2.0

**Django Data Wizard 1.2.0** brings several additional features and bug fixes.

## New Features
 * Ensure compatibility with Django REST Framework 3.9 (#22)
 * Django Integration Improvements (#21/#23 via @bomba1990)
    * New `ImportActionModelAdmin` and `ImportActionMixin` classes for use with [custom source models]
    * Support translation of "Import via data wizard" action text
    * Use `reverse()` when redirecting between Data Wizard views
    * Don't assume `user` is set in request
 * If no serializers are registered, show a warning instead of a blank list (#16)
 * Test ability to import number-formatted cells without float point (#20)
 * Document and extend available [serializer configuration options](https://github.com/wq/django-data-wizard#serializer-options) (e51edba, b9640f3f)
 * Add option to ignore spreadsheet columns during importing (1b7774f)

## Bug Fixes
 * Explicitly list `djangorestframework` in dependencies (#16)
 * Code cleanup (#17, #18, #23 via @bomba1990)
 * Avoid re-parsing the same data source more than necessary (edd6ccb)
 * Fix pagination when integrating with [wq.db](../wq.db/index.md) (c30e180)

## Upgrade Notes

In 1.1.0, the "Import via data wizard" action was applied to all models in the admin, rather than only to those that made sense as sources.  As noted above, 1.2.0 instead provides `ImportActionModelAdmin` and `ImportActionMixin` classes.  If you are using [custom source models], you just need to update your admin.py:
```python

from django.contrib import admin
from .models import MySource
from data_wizard.admin import `ImportActionModelAdmin`

admin.site.register(MySource, ImportActionModelAdmin)

## To restore old "always available" behavior:
# from data_wizard.admin import start_data_wizard
# admin.site.add_action(start_data_wizard, 'data_wizard')
```

The built-in `data_wizard.sources` module already incorporates the new usage.

[custom source models]: https://github.com/wq/django-data-wizard#custom-data-sources
