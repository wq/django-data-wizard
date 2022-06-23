<p align="center">
  <a href="https://django-data-wizard.wq.io">
    <img src="https://django-data-wizard.wq.io/images/django-data-wizard.svg" alt="Django Data Wizard">
  </a>
</p>

[**Django Data Wizard**][Django Data Wizard] is an interactive tool for mapping tabular data (e.g. Excel, CSV, XML, JSON) into a normalized database structure via [Django REST Framework] and [IterTable].  Django Data Wizard allows novice users to map spreadsheet columns to serializer fields (and cell values to foreign keys) on-the-fly during the import process.  This reduces the need for preset spreadsheet formats, which most data import solutions require.

[![Django Data Wizard Workflow](https://django-data-wizard.wq.io/images/screenshots/workflow.png)][workflow]

The Data Wizard supports straightforward one-to-one mappings from spreadsheet columns to database fields, as well as more complex scenarios like [natural keys] and [Entity-Attribute-Value] (or "wide") table mappings.

[![Latest PyPI Release](https://img.shields.io/pypi/v/data-wizard.svg)](https://pypi.org/project/data-wizard)
[![Release Notes](https://img.shields.io/github/release/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/releases)
[![License](https://img.shields.io/pypi/l/data-wizard.svg)](https://github.com/wq/django-data-wizard/blob/master/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/network)
[![GitHub Issues](https://img.shields.io/github/issues/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/issues)

[![Tests](https://github.com/wq/django-data-wizard/actions/workflows/test.yml/badge.svg)](https://github.com/wq/django-data-wizard/actions/workflows/test.yml)
[![Python Support](https://img.shields.io/pypi/pyversions/data-wizard.svg)](https://pypi.org/project/data-wizard)
[![Django Support](https://img.shields.io/pypi/djversions/data-wizard.svg)](https://pypi.org/project/data-wizard)

### [Documentation]

Django Data Wizard provides a [web interface][workflow], [JSON API][api], and [CLI][cli] for specifying a [data source][sources] to import (e.g. a previously-uploaded file), selecting a [serializer][serializers], mapping the data [columns] and [identifiers][ids], and (asynchronously) importing the [data] into any target model in the database.

Data Wizard is designed to allow users to iteratively refine their data import flow.  For example, decisions made during an initial data import are preserved for future imports of files with the same structure.  The included [data model][models] makes this workflow possible. 

 1. **Getting Started**
    * [Installation][installation]
    * [Initial Configuration][initial-configuration]
    * [**Target Model Registration (required)**][target-model-registration]
    * [Usage][workflow]
    * [wq Framework Integration (optional)][wq-setup]
 2. **API Documentation**
    * [Run API][api]
    * [Admin Screens][admin]
    * [Command-Line Interface][cli]
 3. **Advanced Customization**
    * [Django Settings][settings]
    * [Data Model][models]
    * [Custom Serializers][serializers]
    * [Custom Data Sources][sources]
    * [Custom Tasks][tasks]
    * [Task Backends][backends]


[Django Data Wizard]: https://django-data-wizard.wq.io/
[IterTable]: https://django-data-wizard.wq.io/itertable/
[Django REST Framework]: http://www.django-rest-framework.org/
[natural keys]: https://github.com/wq/django-natural-keys
[Entity-Attribute-Value]: https://wq.io/guides/eav-vs-relational

[Documentation]: https://django-data-wizard.wq.io/

[workflow]: https://django-data-wizard.wq.io/guides/using-django-data-wizard
[api]: https://django-data-wizard.wq.io/api/
[admin]: https://django-data-wizard.wq.io/api/admin
[cli]: https://django-data-wizard.wq.io/api/cli

[installation]: https://django-data-wizard.wq.io/overview/setup#installation
[initial-configuration]: https://django-data-wizard.wq.io/overview/setup#initial-configuration
[target-model-registration]: https://django-data-wizard.wq.io/overview/setup#target-model-registration
[wq-setup]: https://django-data-wizard.wq.io/guides/integrate-with-wq-framework

[sources]: https://django-data-wizard.wq.io/config/sources
[serializers]: https://django-data-wizard.wq.io/config/serializers
[columns]: https://django-data-wizard.wq.io/api/columns
[ids]: https://django-data-wizard.wq.io/api/ids
[data]: https://django-data-wizard.wq.io/api/data
[settings]: https://django-data-wizard.wq.io/config/settings
[models]: https://django-data-wizard.wq.io/config/models
[tasks]: https://django-data-wizard.wq.io/config/tasks
[backends]: https://django-data-wizard.wq.io/config/backends
