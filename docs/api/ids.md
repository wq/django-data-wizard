---
tag: ids
tag_color: secondary
order: 8
---

# Identifier Choices

![Identifier Choices](../images/screenshots/04-ids.png)

#### `GET /datawizard/[id]/ids`

The `ids` task lists all of the foreign key values found in the source dataset (i.e. spreadsheet).  If there are any unmapped foreign key values, the auto task will stop and redirect to the `ids` task.  The default [run_ids.html] template (and corresponding [RunIds] react view) includes an interface for mapping row identifiers to foreign key values.  The potential mappings depend on the serializer field used to represent the foreign key.

 * For [PrimaryKeyRelatedField], [SlugRelatedField], and [NaturalKeySerializer][natural keys], the choices will include all existing record ID or slugs.
 * For `NaturalKeySerializer` only, a`"new"` choice will also be included, allowing for the possibility of creating new records in the foreign table on the fly.
 
Once all ids are mapped, the template will display the mappings and a button to (re)start the `auto` task.

Note that the `auto` task will skip the `ids` task entirely if any of the following are true:
  * The file contains no foreign key columns
  * All foreign key values were already mapped during a previous import run
  * All foreign key values can be automatically mapped via the [`DATA_WIZARD['IDMAP']`][settings] setting.

> Source: [`data_wizard.tasks.read_row_identifiers`](https://github.com/wq/django-data-wizard/blob/main/data_wizard/tasks.py#L520)

[run_ids.html]: https://github.com/wq/django-data-wizard/blob/master/data_wizard/templates/data_wizard/run_ids.html
[RunIds]: ../views/RunIds.md

[PrimaryKeyRelatedField]: http://www.django-rest-framework.org/api-guide/relations/#primarykeyrelatedfield
[SlugRelatedField]: http://www.django-rest-framework.org/api-guide/relations/#slugrelatedfield
[natural keys]: https://github.com/wq/django-natural-keys
[settings]: ../config/settings.md
