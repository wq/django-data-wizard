---
order: 2
---

# Data Model

Django Data Wizard provides a number of Django models that help track the import process, and preserve data mapping decisions for future reuse.  The most important models are the *source model*, which usually includes a file or URL attributr, and a *target* model, which is any model from your existing application that you want to integrate with Data Wizard.  The wizard provides several additional models for tracking how source data is mapped to columns and rows.

Specifically, when [using Django Data Wizard][workflow], the following models are leveraged:

step | api | description | model
-----|-------------|--------
0 | [admin] or [wq framework] | Upload **source** file | Create `FileSource` (or custom source model)
1 | [create] | Start data wizard run | Create `Run`
2 | [serializers][api-serializers] | Select serializer (& target model) | Update `Run`
3 | [columns] | Map columns to database field names | Create or update `Identifier`; Map `Identifer` to `Run` via `Range`
4 | [ids] | Map cell values to foreign keys | Create or update `Identifier`; Map `Identifer` to `Run` via `Range`
5 | [data] | Import data into **target** model | Create one `Record` + one target model instance per row

The `Run` model includes a [generic foreign key] pointing to the source model (e.g. `FileSource`.)  Each row in the source spreadsheet will be mapped to a `Record`.  If the row was successfully imported, a new instance of the target data model will be created, and the `Record` will have a generic foreign key pointing to it.  The `Identifier` model contains no foreign keys, since identifier mappings are reused for subsequent imports.  Instead, a separate `Range` model tracks the location(s) (rows/columns) of each `Identifier` in each `Run`.

The `FileSource`, `Run`, and `Identifier` models are registered with the [Django admin][admin] by default.

Note that the above workflow just describes the most common use case.  You can create [custom serializers][serializers] that update more than one target data model per spreadsheet row, [custom data sources][sources] that might not be a spreadsheet or even a file, and [custom tasks][tasks] that make other arbitrary changes to your database.

> Source: [`data_wizard.models`](https://github.com/wq/django-data-wizard/blob/main/data_wizard/models.py) and [`data_wizard.sources.models`](https://github.com/wq/django-data-wizard/blob/main/data_wizard/sources/models.py)

[workflow]: ../guides/using-django-data-wizard.md
[admin]: ../api/admin.md
[wq framework]: ../guides/integrate-with-wq-framework.md
[create]: ../api/create.md
[api-serializers]: ../api/serializers.md
[columns]: ../api/columns.md
[ids]: ../api/ids.md
[data]: ../api/data.md
[generic foreign key]: https://docs.djangoproject.com/en/1.11/ref/contrib/contenttypes/
[serializers]: ./serializers.md
[sources]: ./sources.md
[tasks]: ./tasks.md
