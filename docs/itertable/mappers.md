---
order: 5
---

Mappers
=======

> Source: [`itertable.mappers`][itertable.mappers]


[IterTable]'s `Mapper` [mixin classes][custom] are used to make code for working with a loaded dataset more readable.  This is accomplished by "mapping" each item in the dataset to a "usable item".  Mappers are used during iteration, after the [parser][parsers] has created the `data` object as a `list` of `dicts`.  The primary mapper class is `TupleMapper`, which converts each `dict` in the dataset into a [namedtuple] so fields can be accessed as `row.name` instead of `row['name']`.

```python
from itertable import ExcelFileIter

# Loader and Parser do their work here
instance = ExcelFileIter(filename='example.xlsx')

# Mapper does its work here
for row in instance:
    print(row.name, row.date)

# You can also access the unmapped data directly
for row in instance.data:
    print(row['name'], row['date'])

``` 
    
A mapper class should have two methods to accomplish the mapping:

name | purpose
-----|---------
`usable_item(row)` | Convert the source `dict` into a "usable item", e.g. a `namedtuple`.  (This is just the method name, it's not meant to imply that dicts are unusable.)
`parse_usable_item(item)` | Convert a usable item back into the source `dict` format.  This is needed for full read+write support.

IterTable's [built-in mapper classes][mappers] build on this foundation and on each other.

### BaseMapper
`BaseMapper` breaks down `usable_item` and `parse_usable_item` into functions that work on each field individually.  All of the functions are effectively no-ops and meant to be overridden.  The usable item `BaseMapper` returns is still a `dict`.

name | purpose
-----|---------
`map_field(field)` | Map a field name into its "usable" equivalent
`unmap_field(field)` | Map a "usable" field name back to its original name
`map_value(field, value)` | Map a field value into its "usable" equivalent
`unmap_value(field, value)` | Map a "usable" value back into the source value

### DictMapper
`DictMapper` extends `BaseMapper` with two simple dictionaries that facilitate field and value mapping.  The usable item `DictMapper` returns is still a `dict`.

name | purpose
-----|---------
`field_map` | Map of fields to their usable equivalents: `{"source_field1": "usable_name1", "source_field2": "usable_name2"}`
`value_map` | Map of values to be replaced with usable equivalents.  If a value is not found in the map it will be preserved as is.

### TupleMapper
`TupleMapper` extends `DictMapper` with a `usable_item()` that returns a [namedtuple] instead of a `dict`.  Since `namedtuple` field names cannot contain spaces or punctuation, `TupleMapper` automatically computes a `field_map` with compatible values.  `TupleMapper` defines the following method to facilitate adding new records.

name | purpose
-----|---------
`create(**kwargs)` | Create an instance of the internal `namedtuple` class with values for each field given as keyword arguments.  This can be passed to `append()` which will update the underlying dataset as shown in the example below.

```python
from itertable import CsvFileIter
instance = CsvFileIter(filename="example.csv")
# len(instance) == len(instance.data) == 2

record = instance.create(name='test', value=123)
instance.append(record)
instance.save()

# len(instance) == len(instance.data) == 3

```

### TimeSeriesMapper

`TimeSeriesMapper` extends `TupleMapper` with a `map_value()` implementation that automatically converts string dates into [datetime] objects.  It can also automatically convert string number into `float`s.  Two properties are used to configure `TimeSeriesMapper`:

name | purpose
-----|---------
`date_formats` | A list of [format strings] to use when attempting to parse dates.
`map_floats` | Whether to attempt to map string numbers into floats (default `True`)

[itertable.mappers]: https://github.com/wq/itertable/blob/main/itertable/mappers.py

[IterTable]: ./index.md
[custom]: ./about.md
[base]: ./base.md
[loaders]: ./loaders.md
[parsers]: ./parsers.md
[mappers]: ./mappers.md
[gis]: ./gis.md

[namedtuple]: https://docs.python.org/3/library/collections.html#collections.namedtuple
[datetime]: https://docs.python.org/3/library/datetime.html
[format strings]: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
