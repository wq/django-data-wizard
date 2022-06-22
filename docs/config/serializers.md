---
order: 3
---

# Custom Serializers

Data Wizard uses instances of Django REST Framework's [Serializer class][ModelSerializer] to determine the destination fields on the target model.  Specifically, the default serializer is [NaturalKeyModelSerializer], which is based on [ModelSerializer].

You can override the default serializer by calling `data_wizard.register()` with a name and a serializer class instead of a model class.  Multiple serializers can be registered with the wizard to support multiple import configurations and target models.  

```python
# myapp/wizard.py
from rest_framework import serializers
import data_wizard
from .models import TimeSeries


class TimeSeriesSerializer(serializers.ModelSerializer):
    # (custom fields here)
    class Meta:
        model = TimeSeries
        fields = '__all__'

        # Optional - see options below
        data_wizard = {
            'header_row': 0,
            'start_row': 1,
            'show_in_list': True,
            'idmap': data_wizard.idmap.existing,
            'auto_import_tasks': [ custom task list ],
        }

# Use default name & serializer
data_wizard.register(TimeSeries)

# Use custom name & serializer
data_wizard.register("Time Series - Custom Serializer", TimeSeriesSerializer)
```

At least one serializer or model should be registered in order to use the wizard.  Note the use of a human-friendly serializer label when registering a serializer.  This name should be unique throughout the project, but can be changed later on without breaking existing data.  (The class path is used as the actual identifier behind the scenes.)

### Serializer Options

In general, custom serializers have all the capabilities of regular [Django REST Framework serializers][serializers], including custom validation rules and the ability to populate multiple target models.  While the `request` context is not available, information about the run (including the user) can be retrieved through the `data_wizard` context instead.

When overriding a serializer for a [natural key model][natural keys], be sure to extend [NaturalKeyModelSerializer], as in [this example][naturalkey_wizard].  In other cases, extend [ModelSerializer], as in the example above, or the base [Serializer][serializers] class.

Custom serializers can be used to support [Entity-Attribute-Value] spreadsheets where the attribute names are specified as additional columns.  To support this scenario, the `Entity` serializer should include a nested `Value` serializer with `many=True`, and the `Value` serializer should have a foreign key to the `Attribute` table, as in [this example][eav_wizard].

Data Wizard also supports additional configuration by setting a `data_wizard` attribute on the `Meta` class of the serializer.  The following options are supported.

name | default | notes
--|--|--
`header_row` | 0 | Specifies the first row of the spreadsheet that contains column headers.  If this is greater than 0, the space above the column headers will be scanned for anything that looks like a one-off "global" value intended to be applied to every row in the imported data.
`start_row` | 1 | The first row of data.  If this is greater than `header_row + 1`, the column headers will be assumed to span multiple rows.  A common case is when EAV parameter names are on the first row and units are on the second.
`show_in_list` | `True` | If set to `False`, the serializer will be available through the API but not listed in the wizard views.  This is useful if you have a serializer that should only be used during fully automated workflows.
`idmap` | [`IDMAP` setting][settings] | Can be any of `data_wizard.idmap.*` or a custom function.  Unlike the `IDMAP` setting, this should always be an actual function and not an import path.
`auto_import_tasks` | [`AUTO_IMPORT_TASKS` setting][settings] | A list of import paths to functions registered with `@data_wizard.wizard_task` (see [Custom Tasks][tasks]).


[NaturalKeyModelSerializer]: https://github.com/wq/django-natural-keys#naturalkeymodelserializer
[ModelSerializer]: http://www.django-rest-framework.org/api-guide/serializers/#modelserializer
[serializers]: http://www.django-rest-framework.org/api-guide/serializers/
[natural keys]: https://github.com/wq/django-natural-keys
[naturalkey_wizard]: https://github.com/wq/django-data-wizard/blob/master/tests/naturalkey_app/wizard.py
[Entity-Attribute-Value]: https://wq.io/docs/eav-vs-relational
[eav_wizard]: https://github.com/wq/django-data-wizard/blob/master/tests/eav_app/wizard.py
[settings]: ./settings.md
[tasks]: ./tasks.md
