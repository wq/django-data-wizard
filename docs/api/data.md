---
tag: data
tag_color: secondary
order: 10
---

# Import Data

![Auto Import - Progress Bar](../images/screenshots/08-data75.png)

#### `POST /datawizard/[id]/data`

The `data` task starts the actual import process (and is called by `auto` behind the scenes).  Unlike `auto`, calling `data` directly will not cause a redirect to one of the other tasks if any meta input is needed.  Instead, `data` will attempt to import each record as-is, and report any errors that occured due to e.g. missing fields or unmapped foreign keys.

This is an asynchronous method, and returns a `task_id` to be used with the `status` API.  The default [run_data.html] template (and corresponding [RunData] React view) includes a `<progress>` element for use with status task.

> Source: [`data_wizard.tasks.import_data`](https://github.com/wq/django-data-wizard/blob/main/data_wizard/tasks.py#L733)

[run_data.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_data.html
[RunData]: ../views/RunData.md
