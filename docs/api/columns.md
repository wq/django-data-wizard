---
tag: columns
tag_color: secondary
order: 6
---

# Column Choices

![Column Choices](../images/screenshots/02-columns.png)

#### `GET /datawizard/[id]/columns`

The `columns` task lists all of the columns found in the source dataset (i.e. spreadsheet) and their mappings to target serializer fields.  This screen is shown by the `auto` task if there are any column names that could not be automatically mapped.  The potential mappings are one of:

  * simple serializer field names (e.g. `field`)
  * nested field names (for [natural keys], e.g. `nested[record][field]`)
  * [EAV][Entity-Attribute-Value] attribute-value mappings (e.g. `values[][value];attribute_id=1`).  Note that EAV support requires a [custom serializer class][serializers].

The default [run_columns.html] template (and corresponding [RunColumns] React view) includes an interface for mapping data columns to serializer fields.  If all columns are already mapped, the template will display the mappings and a button to (re)start the [`auto`][auto] task.

> Source: [`data_wizard.tasks.read_columns`](https://github.com/wq/django-data-wizard/blob/main/data_wizard/tasks.py#L287)


[Entity-Attribute-Value]: https://wq.io/guides/eav-vs-relational
[serializers]: ../config/serializers.md
[run_columns.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_columns.html
[RunColumns]: ../views/RunColumns.md
[auto]: ./auto.md
