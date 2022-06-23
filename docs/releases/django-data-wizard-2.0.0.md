---
repo: django-data-wizard
date: 2022-06-23
tag: latest
tag_color: primary
---

# Django Data Wizard 2.0

**Django Data Wizard 2.0** has arrived!  This release brings improved customizability, as well as a new [React / Material UI interface][@wq/wizard] to supplement the existing [Django Admin integration][admin].

Be sure to check out the new [documentation site](../index.md)!

All changes by @sheppard.

## New Features

* New React/Material UI interface, [@wq/wizard], implemented as a [plugin][plugins] for [integration with wq 1.3][wq-setup] (f9050fa, 5859f67, da54e2c, 27aee57).  The existing Django Admin-themed templates are still supported and maintained (#36).
* Support for custom task flows with new [`AUTO_IMPORT_TASKS` setting][settings] and [`auto_import_tasks` serializer option][serializers] (4621e12, 62c0776, 0067e1a, 10bd328, ece3842, ab9cb73, #36)
 * Support for Python 3.10 and Django 4 (1caa9d8, 84b821b, #37)

## Breaking Changes
 * Dropped support for Python < 3.6, Django < 2.2, and Django REST Framework < 3.9 (22b36c0, 6f16312)
 * Dropped support for wq framework < 1.3 (jQuery Mobile / Mustache templates) (5859f67)
 * Changed default [IDMAP setting][settings] from `"data_wizard.idmap.never"` to `"data_wizard.idmap.existing"` (6f16312)
 * Always default the [BACKEND setting][settings] to `"data_wizard.backends.threading"`, even if Celery is installed.  If you want to use the `"data_wizard.backends.celery"` backend, set it explicitly.

## Other Minor Improvements
* Avoid making simultaneous requests to the [status API][status] (e722eae, d2235b5)
* Use `REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]`, but only when [integrating with wq.db][wq-setup] (54191ee)
* Update to openpyxl-based [IterTable] (5cb31c9, 96ac5d2)
* Ignore `None` values when merging cell data (0b6e627)
* Update lint & CI (9e247a6, 22b36c0)

[@wq/wizard]: ../@wq/wizard.md
[admin]: ../api/admin.md
[plugins]: https://wq.io/plugins/
[wq-setup]: ../guides/integrate-with-wq-framework.md
[settings]: ../config/settings.md
[serializers]: ../config/serializers.md
[status]: ../api/status.md
[IterTable]: ../itertable/index.md
