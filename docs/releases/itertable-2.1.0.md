---
repo: itertable
date: 2022-06-22
tag: latest
tag_color: primary
---

# IterTable 2.1

**IterTable 2.1** brings compatibility with the latest Python versions, as well as several improvements for integration with [Django Data Wizard 2.0](./django-data-wizard-2.0.0.md).  All changes by @sheppard.

### API Improvements
 * Support loading data from arbitrary file-like sources, such as S3 (https://github.com/wq/django-data-wizard/issues/31)
 * Raise an error by default when loading a nonexistent file (https://github.com/wq/django-data-wizard/issues/33)
 * Option to load all sheets from workbook at once (by setting `sheet_name=None`) (98b994e, f67a908) 
 * Detect `application/csv` in addition to `text/csv` (acb9fa7)

### Ecosystem Updates
 * Support Python 3.10 (7d1a814; https://github.com/wq/django-data-wizard/issues/37)
 * Drop all remaining support for Python 2 (475eb6c)
 * Leverage [openpyxl](https://openpyxl.readthedocs.io/en/stable/) instead of xlrd when parsing XLSX format (475eb6c)
