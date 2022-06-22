---
order: 14
---

# Command-Line Interface

Django Data Wizard provides a single [management command], `runwizard`, that can be used to initiate the `auto` task from the command line.  This can be used to facilitate automated processing, for example as part of a regular cron job.  Note that the CLI does not (currently) support interactively mapping columns and ids, so these should be pre-mapped using the web or JSON API.

Usage:

```bash
./manage.py runwizard myapp.mymodel 123 \
    --loader myapp.loaders.customloader \
    --serializer myapp.serializer.customserializer \
    --username myusername
```

The basic usage is similar to the [New Run API][create].  Only a content type and object id are required, while the other arguments will be auto-detected if possible.  In particular, you may want to use [set_loader()][custom-loader] to predefine the default `loader` and `serializer` for any models you plan to use with the CLI.

The `runwizard` command will create a new `Run` and immediately start the `auto` task.  Errors will be shown on the console.

[management command]: https://docs.djangoproject.com/en/2.1/ref/django-admin/
[create]: ./api/create.md
[loaders]: ./loaders.md
