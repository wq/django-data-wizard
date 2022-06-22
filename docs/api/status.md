---
order: 3
---

# status

#### `GET /datawizard/[id]/status.json?task=[task]`

The `status` API is used to check the status of an asynchronous task (one of `auto` or `data`).  The API is used by the provided [@wq/progress.js] plugin to update the `<progress>` bar in the [run_auto.html] and [run_data.html] templates (and corresponding [RunAuto] and [RunData] React views).  Unlike the other methods, this API is JSON-only and has no HTML equivalent.  An object of the following format will be returned:

```js
{
    // General properties
    "status": "PROGRESS", // or "SUCCESS", "FAILURE"
    "stage": "meta",      // or "data"
    "current": 23,        // currently processing row
    "total": 100,         // total number of rows
    
    // "FAILURE"
    "error": "Error Message",

    // Task complete ("SUCCESS")
    "action": "records",        // or "serializers", "columns" "ids"
    "message": "Input Needed",  // if action is not "records"
    "skipped": [...],           // rows that could not be imported
    "location": "/datawizard/[id]/records",
}
```

The potential values for the  `status` field are the same as common [Celery task states], even when not using the `celery` backend.  When running an `auto` task, the result is `SUCCESS` whenever the task ends without errors, even if there is additional input needed to fully complete the run.

The default [run_auto.html] and [run_data.html] templates include a `<progress>` element for use with the status task.

[@wq/progress]: ../@wq/progress.md
[run_auto.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_auto.html
[run_data.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_data.html
[RunAuto]: ../views/RunAuto.md
[RunData]: ../views/RunData.md
[Celery task states]: http://docs.celeryproject.org/en/latest/userguide/tasks.html#task-states
