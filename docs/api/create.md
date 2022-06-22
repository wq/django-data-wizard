---
order: 1
---

# Create New Run

<img align="right" width=320 height=240
     alt="Select Source & Start Import"
     src="https://django-data-wizard.wq.io/images/screenshots/A2-source-list.png">

#### `POST /datawizard/`

Creates a new instance of the wizard (i.e. a `Run`).  If you are using the Django [admin integration][admin], this step is executed when you select "Import via Data Wizard" from the admin actions menu.  If you are using the [wq framework integration][wq-setup], a form to trigger this step will appear after you upload a source, in the [SourceDetail] view.  If you are using the JSON API directly, the returned run `id` should be used in all subsequent calls to the API.  Each `Run` is tied to the source model via a [generic foreign key].

parameter         | description
------------------|----------------------------------------
`object_id` | The primary key of the *source* model instance containing the data to be imported.
`content_type_id` | The *source* model's app label and model name (in the format `app_label.modelname`).
`loader` | (Optional) The class name to use for loading the source dataset via [IterTable].  The default loader (`data_wizard.loaders.FileLoader`) assumes that the source model contains a `FileField` named `file`.
`serializer` | (Optional) The serializer class to use when populating the *target* model.  This can be left unset to allow the user to select the target during the wizard run.

[admin]: ./admin.md
[wq-setup]: ../overview/wq-setup.md
[generic foreign key]: https://docs.djangoproject.com/en/1.11/ref/contrib/contenttypes/
[SourceDetail]: ../views/SourceDetail.md
[IterTable] ../itertable/index.md
