---
repo: django-data-wizard
date: 2017-06-16
---

# Django Data Wizard 1.0 RC

This is the release candidate for Django Data Wizard 1.0.   The dependency on [vera](https://github.com/powered-by-wq/vera) has been completely factored out, in favor of the ability to register Django REST Framework serializers to define the mapping between spreadsheet columns and database fields.  This means that the wizard now works with any data model (#3) and also is much less likely to have database-level validation errors as long as the serializer correctly validates the data beforehand (#1).  See the [updated README](../index.md#readme) for details on how to use these new features.
