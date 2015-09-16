**Django Data Wizard** is a [wq-powered](https://wq.io/) web-based tool for mapping structured data (e.g. Excel, XML) into a highly normalized database structure via Django.  The current implementation relies heavily on the [ERAV] implementation provided by [vera], though there are plans to extend this to support any database structure ([#3]).

The unique feature of Django Data Wizard is that it allows novice users to map spreadsheet columns to database fields (and cell values to foreign keys) on-the-fly during the import process.  This reduces the need for preset spreadsheet formats, which most data import solutions require.

<!--
[![Latest PyPI Release](https://img.shields.io/pypi/v/data-wizard.svg)](https://pypi.python.org/pypi/data-wizard)
[![Release Notes](https://img.shields.io/github/release/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/releases)
[![License](https://img.shields.io/pypi/l/data-wizard.svg)](https://wq.io/license)
-->
[![GitHub Stars](https://img.shields.io/github/stars/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/network)
[![GitHub Issues](https://img.shields.io/github/issues/wq/django-data-wizard.svg)](https://github.com/wq/django-data-wizard/issues)

[![Travis Build Status](https://img.shields.io/travis/wq/django-data-wizard.svg)](https://travis-ci.org/wq/django-data-wizard)
<!--
[![Python Support](https://img.shields.io/pypi/pyversions/data-wizard.svg)](https://pypi.python.org/pypi/data-wizard)
[![Django Support](https://img.shields.io/badge/Django-1.7%2C%201.8-blue.svg)](https://pypi.python.org/pypi/data-wizard)
-->

[ERAV]: https://wq.io/docs/erav
[vera]: https://wq.io/vera
[#3]: https://github.com/wq/django-data-wizard/issues/3
