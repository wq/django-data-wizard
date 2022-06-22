---
order: 1
---

Extending IterTable
===================

[IterTable] provides a consistent interface for working with data from a variety of common formats.  However, it is not possible to support every conceivable file format and data structure in a single library.  Because of this, IterTable is designed to be customized and extended.  To facilitate fully modular customization, the IterTable APIs are designed as combinations of a `BaseIter` class and several mixin classes.

The `BaseIter` class and mixins break the process into several steps:

1. The [BaseIter][base] class initializes each instance, saving any passed arguments as properties on the instance, then immediately triggering the next two steps.
2. A [Loader][loaders] mixin loads an external resource into file-like object and saves it to a `file` property on the instance
3. A [Parser][parsers] mixin extracts data from the `file` property and saves it to a `data` property, which should almost always be a `list` of `dict`s.
4. After initialization, the BaseIter class and a [Mapper][mappers] mixin provide a transparent interface for iterating over the instance's `data`, e.g. by transforming each row into a `namedtuple` for convenience.

These steps and their corresponding classes are detailed in the following pages.

When writing to a file, the above steps are done more or less in reverse: the [Mapper][mappers] transforms data back into the `dict` format used in the `data` list; and the [Parser][parsers] dumps the data into a file-like object prepared by the [Loader][loaders] which then writes the output file.

There are a number of pre-mixed classes directly exported by the [itertable module].  By convention, each pre-mixed class has a suffix "Iter", e.g. `ExcelFileIter`.  The class names provide hints to the mixins that were used in their creation: for example, `JsonFileIter` extends `FileLoader`, `JsonParser`, `TupleMapper`, and `BaseIter`.  Note that all of the pre-mixed classes extend `TupleMapper`, and all Iter classes extend `BaseIter` by definition.

To extend IterTable, you can subclass one of these pre-mixed classes:

```python
from itertable import JsonFileIter

class MyJsonFileIter(JsonFileIter):
    def parse(self):
        # custom parsing code...
```

... or, subclass one of the mixins and mix your own class:

```python
# Load base classes
from itertable.base import BaseIter
from itertable.loaders import FileLoader
from itertable.parsers import JsonParser
from itertable.mappers import TupleMapper

# Equivalent:
# from itertable import BaseIter, FileLoader, JsonParser, TupleMapper

# Define custom mixin class
class MyJsonParser(JsonParser):
    def parse(self):
        # custom parsing code ...

# Mix together a usable Iter class
class MyJsonFileIter(FileLoader, MyJsonParser, TupleMapper, BaseIter):
    pass
```

Note that the order of classes is important: `BaseIter` should always be listed last to ensure the correct method resolution order.

You can then use your new class like any other Iter class:

```python
for record in MyJsonFileIter(filename='file.json'):
    print(record.id)
```

[IterTable]: ./index.md
[base]: ./base.md
[loaders]: ./loaders.md
[parsers]: ./parsers.md
[mappers]: ./mappers.md
[gis]: ./gis.md

[itertable module]: https://github.com/wq/itertable/blob/main/itertable/__init__.py
