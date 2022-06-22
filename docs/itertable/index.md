---
permalink: /itertable/
title: IterTable
wq_config:
  name: itertable
  url: itertable
  order: 23
  section: API Reference
  icon_data: "M7,22H9V24H7V22M11,22H13V24H11V22M15,22H17V24H15V22M5,4H19A2,2 0 0,1 21,6V18A2,2 0 0,1 19,20H5A2,2 0 0,1 3,18V6A2,2 0 0,1 5,4M5,8V12H11V8H5M13,8V12H19V8H13M5,14V18H11V14H5M13,14V18H19V14H13Z"
---

# IterTable

**IterTable** is a Pythonic API for iterating through tabular data formats, including CSV, XLSX, XML, and JSON.

```python
from itertable import load_file

for row in load_file("example.xlsx"):
    print(row.date, row.name)
```

[**IterTable on GitHub**](https://github.com/wq/itertable)

## Getting Started

```bash
# Recommended: create virtual environment
# python3 -m venv venv
# . venv/bin/activate

python3 -m pip install itertable

# GIS support (Fiona & Shapely)
python3 -m pip install itertable[gis]

# Excel 97-2003 (.xls) support
python3 -m pip install itertable[oldexcel]
# (xlsx support is enabled by default)

# Pandas integration
python3 -m pip install itertable[pandas]
```

## Overview

IterTable provides a general purpose API for loading, iterating over, and writing tabular datasets.  The goal is to avoid needing to remember the unique usage of e.g. [csv], [openpyxl], or [xml.etree] every time one needs to work with external data.  Instead, IterTable abstracts these libraries into a consistent interface that works as an [iterable] of [namedtuples].  Whenever possible, the field names for a dataset are automatically determined from the source file, e.g. the column headers in an Excel spreadsheet.

```python
from itertable import ExcelFileIter
data = ExcelFileIter(filename='example.xlsx')
for row in data:
    print(row.name, row.date)
```

IterTable provides a number of built-in classes like the above, including a `CsvFileIter`, `XmlFileIter`, and `JsonFileIter`.  There is also a convenience function, `load_file()`, that attempts to automatically determine which class to use for a given file.

```python
from itertable import load_file
data = load_file('example.csv')
for row in data:
    print(row.name, row.date)
```

All of the included `*FileIter` classes support both reading and writing to external files.

### Network Client

IterTable also provides network-capable equivalents of each of the above classes, to facilitate loading data from third party webservices.

```python
from itertable import JsonNetIter
class WebServiceIter(JsonNetIter):
    url = "http://example.com/api"
    
data = WebServiceIter(params={'type': 'all'})
for row in data:
    print(row.timestamp, row.value)
```

The powerful [requests] library is used internally to load data over HTTP.

### Pandas Analysis

When [Pandas] is installed (via `itertable[pandas]`), the `as_dataframe()` method on itertable classes can be used to create a [DataFrame], enabling more extensive analysis possibilities.

```python
instance = WebServiceIter(params={'type': 'all'})
df = instance.as_dataframe()
print(df.value.mean())
```

### GIS Support

When [Fiona] and [Shapely] are installed (via `itertable[gis]`), itertable can also open and create shapefiles and other OGR-compatible geographic data formats.

```python
from itertable import ShapeIter
data = ShapeIter(filename='sites.shp')
for id, site in data.items():
    print(id, site.geometry.wkt)
```

More information on IterTable's gis support is available [here][gis].

### Command-Line Interface

IterTable provides a simple CLI for rendering the content of a file or Iter class.  This can be useful for e.g. inspecting a file or for integrating a shell automation workflow.  The default output is CSV, but can be changed to JSON by setting `-f json`.

```bash
python3 -m itertable example.json         # JSON to CSV
python3 -m itertable -f json example.csv  # CSV to JSON
python3 -m itertable example.xlsx "start_row=5"
python3 -m itertable http://example.com/example.csv
python3 -m itertable itertable.CsvNetIter "url=http://example.com/example.csv"
```

### Extending IterTable

It is straightforward to [extend IterTable][custom] to support arbitrary formats.   Each provided class is composed of a [BaseIter][base] class and mixin classes ([loaders], [parsers], and [mappers]) that handle the various steps of the process.

[wq framework]: https://wq.io/
[csv]: https://docs.python.org/3/library/csv.html
[openpyxl]: https://openpyxl.readthedocs.io/en/stable/
[xml.etree]: https://docs.python.org/3/library/xml.etree.elementtree.html
[iterable]: https://docs.python.org/3/glossary.html#term-iterable
[namedtuples]: https://docs.python.org/3/library/collections.html#collections.namedtuple
[requests]: http://python-requests.org/
[Pandas]: http://pandas.pydata.org/
[DataFrame]: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html
[Fiona]: https://github.com/Toblerity/Fiona
[Shapely]: https://github.com/Toblerity/Shapely

[custom]: ./custom.md
[base]: ./base.md
[loaders]: ./loaders.md
[parsers]: ./parsers.md
[mappers]: ./mappers.md
[gis]: ./gis.md
