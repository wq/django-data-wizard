---
repo: django-data-wizard
date: 2017-07-31
---

# Django Data Wizard 1.0.0

**Django Data Wizard 1.0.0** is finally here!  This is the first stable release of Django Data Wizard 1.0, which is now ready for production use. 

## Changes since Django Data Wizard 1.0.0 RC1
 * Fix generation of empty queryset (71bf665)
 * Add a simple list view (6a36cbc)
 * Incorporate [Code of Conduct](https://github.com/wq/django-data-wizard/blob/master/CODE_OF_CONDUCT.md) and [Contributing Guidelines](https://github.com/wq/django-data-wizard/blob/master/CONTRIBUTING.md)
 * Documentation updates

##  Other changes since vera 0.6.2
* Pre-Beta Changes
  * Extract from `wq.db.contrib.dbio` into standalone package with dependencies on [wq.db](https://github.com/powered-by-wq/vera) and [vera](https://github.com/powered-by-wq/vera) (wq/wq.db#29)
  * See the release notes for [wq.db 0.7](https://wq.io/releases/wq.db-0.7.0) and [vera 0.7](https://github.com/wq/vera/releases/tag/v0.7.0)
* [Changes in Beta 1](./django-data-wizard-1.0.0b1.md)
  * Rename package module from `dbio` to `data_wizard`; publish as `data-wizard` on PyPI
  * Use package-specific models (`Identifier`, `Range`, and `Record`) instead of wq.db's `identify` and `relate` patterns (#4)
* [Changes in Beta 2](./django-data-wizard-1.0.0b2.md)
  * Incorporate default wq-compatible templates for user interface
* [Changes in RC 1](./django-data-wizard-1.0.0rc1.md)
  * Create a registration API for importing arbitrary structured data via Django REST Framework model serializers; completely factor out `vera` dependency and minimize reliance on `wq.db`. (#1, #3, #5)
