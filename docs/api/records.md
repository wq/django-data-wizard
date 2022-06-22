---
order: 11
---

# records

<img align="right" width=320 height=240
     alt="Imported Records"
     src="https://django-data-wizard.wq.io/images/screenshots/10-records.png">

#### `GET /datawizard/[id]/records`

The `records` task provides a list of imported rows (including errors).  It is redirected to by the `auto` and `data` tasks upon completion.  Successfully imported `Record` instances will have a [generic foreign key] pointing to the target model.  The `records` task will include links to the `get_absolute_url()` or admin screen for each newly imported target model instance.  The default [run_records.html] template (and corresponding [RunRecords] React view) includes an interface for displaying the record details.


[generic foreign key]: https://docs.djangoproject.com/en/1.11/ref/contrib/contenttypes/
[run_records.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_records.html
[RunRecords]: ../views/RunRecords.md
