---
order: 2
---

The BaseIter class
==================

> Source: [`itertable.base`][itertable.base]

The `BaseIter` class forms the core of [IterTable]'s built-in classes, and should always be extended when [defining custom classes][custom].  `BaseIter` serves two primary functions:

 * Initializing the class and orchestrating the [load][loaders] and [parse][parsers] mixin tasks
 * Providing a convenient `iterable` interface for working with the parsed data (with support from a [mapper][mappers] mixin)

To accomplish these functions, BaseIter contains a number of methods and properties:

 1. Synchronization methods and configuration properties.  These are discussed below.
 2. Stub functions meant to be overridden by the mixin classes.
 3. Magic methods to facilitate iteration and data manipulation.  These should rarely need to be called directly or overridden.

## Methods

 name | purpose
------|--------
`refresh()` | Triggers the [load][loaders] and [parse][parsers] mixins to ensure the dataset is ready for iteration.  Called automatically when the class is initialized.
`copy(other_io, save=True)` | Copy the entire dataset to another Iter instance, which presumably uses a different loader or parser.  This method provides a means of converting data between formats.  Any existing data on the other Iter instance will be erased.  If `save` is `True` (the default), the `save()` method on the other Iter will be immediately triggered after the data is copied.
`sync(other_io, save=True)` | Like `copy()`, but uses `key_field` (see below) to update existing records in the other Iter rather than replacing the entire dataset.  If a key is not found it is added automatically.
`as_dataframe()` | Generates a [Pandas DataFrame] containing the data in the Iter instance.  Useful for more complex data analysis tasks.  Requires Pandas which is not installed by default.

## Properties

 name | purpose
------|--------
`field_names` | The field or column names in the dataset.  This can usually be determined automatically.
`key_field` | A "primary key" on the dataset.  If `key_field` is set, the Iter will behave more like a dictionary, e.g. the default iteration will be over the key field values instead of over the rows.
`nested` | Boolean indicating whether the Iter has a two-tiered API (see below).
`tabular` | Boolean indicating whether the dataset comes from an inherently tabular file format (e.g. a spreadsheet).  See [Parsers][parsers] for more details.

### Assigning Values to Properties

Most properties (including mixin properties) can be set by passing them as arguments when initializing the class.  However, in general it is better to create a subclass with the properties pre-set.

```python
# Works, but less re-usable
instance = CustomIter(field_names=['id','name'])

# Usually better
class MyCustomIter(CustomIter)
    field_names = ['id', 'name']
instance = MyCustomIter()
```

The main exception to this rule is for properties that are almost guaranteed to be different every time the Iter is instantiated, e.g. [FileLoader][loaders]'s  `filename` property.

### Nested Iters

IterTable pports the notion of "nested" tables containing two levels of iteration.  This is best illustrated by example:

```python

instance = MyNestedIter(option1=value)
for group in instance:
    print(group.group_name)
    for row in group.data:
        print(row.date, row.value)
```

For compatibility with tools that expect only a single level table (e.g. [Django Data Wizard]), nested tables can be "flattened" using a function from `itertable.util`:

```python
from itertable.util import flattened
instance = flattened(MyNestedIter, option1=value)
for row in instance:
    print(row.group_name, row.date, row.value)
```

To be compatible with `flattened()`, nested Iter classes need to have the following characteristics:
 1. `nested = True`
 2. Extend `TupleMapper`
 3. Each mapped row should have a `data` property pointing to a nested Iter class instance.

Note that none of the pre-mixed Iter classes in IterTable are nested.  The [climata library] provides a number of examples of nested Iter classes.

[itertable.base]: https://github.com/wq/itertable/blob/main/itertable/base.py

[IterTable]: ./index.md
[custom]: ./about.md
[base]: ./base.md
[loaders]: ./loaders.md
[parsers]: ./parsers.md
[mappers]: ./mappers.md
[gis]: ./gis.md

[Pandas DataFrame]: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html
[Django Data Wizard]: https://github.com/wq/django-data-wizard
[climata library]: https://github.com/heigeo/climata
