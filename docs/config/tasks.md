---
order: 5
---

# Custom Tasks

It is possible to override the sequence of tasks excecuted by the [auto] task, to remove steps or add new ones.  The list can be overridden in the [global settings][settings] (via `DATA_WIZARD['AUTO_IMPORT_TASKS']`), or on a per-[serializer][serializers] basis (by setting `Meta.data_wizard['auto_import_tasks']`).

Each custom task function should be registered with the `@data_wizard.wizard_task` decorator to configure a label and optionally the API path relative to `/datawizard/[id]/`.  The arguments to the decorator and the function determine the task type.


### Check Tasks

```python
@data_wizard.wizard_task(label="Custom Check", url_path=False)
def custom_check(run):
    if not some_condition_satisfied(run):
        raise data_wizard.InputNeeded("custominput")
```

Check tasks validate whether some condition is satisfied, redirecting to an Input task if needed.  `url_path` is usually set to False to disable the HTTP endpoint.  The task label will be shown in the progress bar (if the task takes more than a couple seconds to run).

### Input Tasks

```python
@data_wizard.wizard_task(label="Custom Input", url_path="custominput")
def custom_input(run):
   return {"some_template_context": []}
```

Input tasks enable the user to provide feedback to guide the wizard.  They should have a `url_path` (which will default to the function name) and a corresponding template (e.g. `data_wizard/run_custominput.html`).  The context returned by the task will be in the template under the `result` variable.  The template typically either renders a form with the needed inputs, or (if all inputs have been entered) a summary with the option to restart the auto task.

### Form Processing Tasks

```python
@data_wizard.wizard_task(label="Custom Input", url_path="customsave")
def custom_save(run, post={}):
   some_save_method(run, post)
   return {
       **custom_input(run),
       "current_mode": "custominput",
   }
```

Form Processing Tasks process the form submitted from a prior input task.  Registration is similar to Input Tasks except the function itself should accept an optional `post` kwarg.  Form Processing tasks should be registered with `url_path`, and redirect back to the input task (by setting `current_mode` on the response).

### Custom Auto Tasks

In very advanced use cases, it might be necessary to generate the list of tasks dynamically depending on a number of factors.  In that case, it is possible to define a fully custom auto task:

```python
@data_wizard.wizard_task(label="Custom Workflow", url_path="customauto", use_async=True)
def custom_auto(run):
    task_list = somehow_determine_tasks(run)
    return run.run_all(task_list)
```

Registration is similar as that for other tasks with the addition of the `use_async` keyword, which facilitates background processing via the configured task backend.

In general, the tasks in an automated task list should be check tasks or other auto tasks.  Input and Form Processing tasks should be executed outside of the automated flow.

[settings]: ./settings.md
[serializers]: ./serializers.md
