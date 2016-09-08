**Django Data Wizard** is a [wq-powered][wq framework] web-based tool for mapping structured data (e.g. Excel, XML) into a highly normalized database structure via Django.  The current implementation relies heavily on the [ERAV] implementation provided by [vera], though there are plans to extend this to support any database structure ([#3]).

The unique feature of Django Data Wizard is that it allows novice users to map spreadsheet columns to database fields (and cell values to foreign keys) on-the-fly during the import process.  This reduces the need for preset spreadsheet formats, which most data import solutions require.

Django Data Wizard supports any format supported by [wq.io].  Additional formats can be integrating by creating a [custom wq.io class] and then registering it with the wizard.  For example, the [Climata Viewer] uses Django Data Wizard to import data from [climata]'s wq.io-based data loaders.


> *Note:* Django Data Wizard was formerly known as the **dbio** contrib module in [wq.db].  The implementation has been extracted from wq.db and renamed to avoid confusion with other similar libraries.

[![Latest PyPI Release](https://img.shields.io/pypi/v/data-wizard.svg)](https://pypi.python.org/pypi/data-wizard)
[![Release Notes](https://img.shields.io/github/release/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/releases)
[![License](https://img.shields.io/pypi/l/data-wizard.svg)](https://wq.io/license)
[![GitHub Stars](https://img.shields.io/github/stars/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/network)
[![GitHub Issues](https://img.shields.io/github/issues/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/issues)

[![Travis Build Status](https://img.shields.io/travis/wq/django-data-wizard.svg)](https://travis-ci.org/wq/django-data-wizard)
[![Python Support](https://img.shields.io/pypi/pyversions/data-wizard.svg)](https://pypi.python.org/pypi/data-wizard)
[![Django Support](https://img.shields.io/badge/Django-1.8%2C%201.9%2C%201.10-blue.svg)](https://pypi.python.org/pypi/data-wizard)

# Getting Started

```bash
pip3 install data-wizard
```

Django Data Wizard is an extension to [wq.db], the database component of the [wq framework].  See <https://github.com/wq/django-data-wizard> to report any issues.

# Examples

[![Climata Viewer](https://wq.io/media/screenshots/climata-02.png)](https://wq.io/projects/climata)

[![river.watch](https://wq.io/media/screenshots/riverwatch-overview.png)](https://wq.io/projects/river-watch)

[ERAV]: https://wq.io/docs/erav
[vera]: https://wq.io/vera
[#3]: https://github.com/wq/django-data-wizard/issues/3
[wq.io]: https://wq.io/wq.io
[wq.db]: https://wq.io/wq.db
[custom wq.io class]: https://wq.io/docs/custom-io
[Climata Viewer]: https://github.com/heigeo/climata-viewer
[climata]: https://github.com/heigeo/climata
[wq framework]: https://wq.io/
[wq.db.rest]: https://wq.io/docs/about-rest
