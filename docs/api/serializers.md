---
order: 4
---

# serializers

<img align="right" width=320 height=240
     alt="Serializer Choices"
     src="https://django-data-wizard.wq.io/images/screenshots/00-serializers.png">


#### `GET /datawizard/[id]/serializers`

     
The `serializers` task provides a list of all registered serializers (i.e. target models).  This screen is shown by the `auto` task if a serializer was not specified when the `Run` was created.  The default [run_serializers.html] template (and corresponding [RunSerializers] React view) includes an interface for selecting a target.  If a serializer is already selected, the template will display the label and a button to (re)start the `auto` task.

> Source: [`data_wizard.tasks.list_serializers`](https://github.com/wq/django-data-wizard/blob/main/data_wizard/tasks.py#L78)


[run_serializers.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_serializers.html
[RunSerializers]: ../views/RunSerializers
