---
order: 4
---

Parsers
=======

> Source: [`itertable.parsers`][itertable.parsers]


[IterTable]'s `Parser` [mixin classes][custom] facilitate parsing data from a loaded `file` object into a `list` of `dict`s.  A parser is essentially just a class with `parse()` and `dump()` methods defined.  In general, a parser class should just provide a wrapper around a third party API (e.g. [csv], [xml.etree] or [xlrd]).  A hypothetical parser class would look like this:

```python
from some_library import some_api

class HypotheticalParser(BaseParser):
    def parse(self):
        self.data = some_api.load(self.file)

    def dump(self, file):
        some_api.dump(self.data, file)
```

As can be seen in the above example, the `parse()` function takes no arguments, instead assuming `self.file` has already been defined by a [Loader][loaders] mixin.  The data object should be defined as a `list` of `dict`s (e.g. `[{"id":1},{"id":2}]`.  If the result returned by the API has some other structure, it should be processed to match the expected format.  The `dump()` function should accept a writable file handle as an argument and use the API to write the data object back to the file.

## Extending Parser Classes
There are two main ways in which parser classes are customized.  One way is to define a completely new class to support a file format or API not currently supported by the built-in IterTable parsers.  The other way, which is much more common, is to extend or change the behavior of an existing parser.  With that in mind, each of the built-in parser classes is discussed below together with common customization options and techniques.

### Non-Tabular Parsers
Two of the built-in parsers are used for file formats that are *not* inherently tabular and can describe arbitrary data structures.  While these file data formats are not inherently tabular, they often are used represent table-like data.  These parsers directly extend `BaseParser` and have the `tabular` property set to `False`.

> Non-tabular file formats allow for some records to have more fields than others.  By default, IterTable only searches the first record when automatically determining field names.  This can cause issues with [TupleMapper][mappers] in particular which expects consistent field names throughout the dataset.  If this happens to you, set `scan_fields = True` on your class to tell IterTable to scan the entire dataset when determining field names.

#### [JsonParser][itertable.parsers.text]

The JSON parser is a simple wrapper around Python's built-in [json] API.  `JsonParser` assumes the result of `json.load(self.file)` will either be an array or an object with an array somewhere in an inner property (in which case `namespace` should be set).  Each item in the array is assumed to be a relatively flat key-value mapping.  The keys of the first item in the array will be assumed to be the same for the rest of the items.

JsonParser supports the following options, specified as properties on the class or instance:

##### Properties

name | purpose
-----|---------
`namespace` | The dotted path to the array within the JSON object.  For example, if the expected JSON will be of the form `{"records":[{"id":1},{"id":2}]}` then the namespace should be "records".
`indent` | Used by the `dump()` method, which passes it on to `json.dump` to "pretty-print" the output JSON file.

#### [XmlParser][itertable.parsers.text]

The XML parser is a simple wrapper around Python's built-in [xml.etree] API.  While it can be adapted to work with arbitrary XML documents, it assumes a basic structure like the following:

```xml
<root>
  <item>
    <id>1</id>
    <value>val</value>
  </item>
  <item>
    <id>2</id>
    <value>val</value>
  </item>
</root>
```

In addition to the `parse()` and `dump()` methods, `XmlParser` provides row-level methods, described below.

##### Properties & Methods

name | purpose
-----|---------
`root_tag` | The name of the top level XML tag.  Determined automatically by `parse()`; only required for `dump()`.
`item_tag` | The name of the series tag.  Defaults to the name of the first child tag under the root.  `parse()` will conduct a search for all instances of `item_tag` (whether explicitly specified or computed) and call `parse_item()` on each result.  Required for `dump_item()`.
`parse_item(elem)` | If overridden, should return a `dict` corresponding to the item.  The default implementation assumes each property is specified as an inner tag name and XML attributes are ignored.
`dump_item(obj)` | The inverse of `parse_item()`; if overridden, should accept a `dict` and return an `Element` instance.

### Tabular Parsers

The tabular parsers are geared toward handling spreadsheets and other tabular data formats.  These formats are differentiated from the non-tabular formats in that there is typically a single grid structure encompassing the entire file, and the field names / column headings are listed only once (usually, but not always, in the first row of the file).

The tabular parsers extend [itertable.base.TableParser][itertable.parsers.base], which defines the following properties:

name | purpose
-----|-----------
`tabular = True` | The `tabular` property is used to signify the presence of these other properties.  It is checked by [Django Data Wizard] when importing data.
`header_row` | The location of the column headers within the table.  This is often 0 (the first row), but can be determined automatically by examining the first few rows of the table.
`max_header_row` | The maximum number of rows to scan looking for the column headers.  The default is 20.
`start_row` | The first row containing actual data.  This defaults to `header_row` + 1.  Useful when there is an empty row or two between the column headers and data in a spreadsheet.
`extra_data` | A sparse matrix containing any data found in the cells above the header row.  The format is `{row: {col: "Data"}}`.  Currently only supported by `ExcelParser`.

#### [CsvParser][itertable.parsers.text]

`CsvParser` utilizes Python's [csv] module to provide a CSV-capable `TableParser`.  `CsvParser` leverages [SkipPreludeReader][itertable.parsers.readers], a customized [DictReader] that adds support for files that have extra "prelude" text before the actual header row.

##### Properties & Methods
name | purpose
-----|-----------
delimiter | Column separator, default is `,`
quotechar | Quotation character for text values containing spaces or delimiters, default is `"`
reader_class() | Method returning an uninstantiated `DictReader` class for use in parsing the data.  The default method returns a subclass of `SkipPreludeReader` that passes along the `max_header_row` option.

#### [ExcelParser (`WorkbookParser`)[itertable.parsers.xls]
`ExcelParser` provides support for `.xlsx` files via the [openpyxl] module, while `OldExcelParser` supports `.xls` if [xlrd] and [xlwt] are installed.  `ExcelParser` and `OldExcelParser` extend a somewhat more generic `WorkbookParser`, with the idea that the latter could eventually be extended to other "workbook" style formats like ODS.

> Note: In previous versions of itertable, `ExcelParser` relied on [xlrd] to support both `.xlsx` and `.xls` formats.  Now that xlrd has dropped `.xlsx` support, `ExcelParser` has been rewritten to use [openpyxl], which only supports `.xlsx` files.  The old `xlrd`-based `ExcelParser` class has been renamed to `OldExcelParser`.  (In most cases you can just use `itertable.load_file()` which automatically determines whether to use `ExcelParser` or `OldExcelParser`).

##### Properties
name | purpose
-----|---------
`sheet_name` | Determines which sheet to load data from in an multi-sheet workbook.  Defaults to `0` (the first sheet)

##### Methods
name | purpose
-----|---------
`sheet_names` | List the available sheets in the workbook (declared as a `@property` method).
`parse_workbook()` | Load `self.file` into a `Workbook` or equivalent class and save it to `self.workbook`
`parse_worksheet(name)` | Load the specified worksheet into memory and save an array of row objects to `self.worksheet`
`parse_row(row)` | Convert the given row object into a dict, usually by mapping the column header to the value in each cell
`get_value(cell)` | Retrieve the actual value from the cell.

The methods listed above are called in turn by `parse()`, which is defined by `WorkbookParser`.  Working implementations of the methods are defined in `ExcelParser` and `OldExcelParser`.

[itertable.parsers]: https://github.com/wq/itertable/blob/main/itertable/parsers/
[itertable.parsers.base]: https://github.com/wq/itertable/blob/main/itertable/parsers/base.py
[itertable.parsers.readers]: https://github.com/wq/itertable/blob/main/itertable/parsers/readers.py
[itertable.parsers.text]: https://github.com/wq/itertable/blob/main/itertable/parsers/text.py
[itertable.parsers.xls]: https://github.com/wq/itertable/blob/main/itertable/parsers/xls.py

[IterTable]: ./index.md
[custom]: ./about.md
[base]: ./base.md
[loaders]: ./loaders.md
[parsers]: ./parsers.md
[mappers]: ./mappers.md
[gis]: ./gis.md

[csv]: https://docs.python.org/3/library/csv.html
[xml.etree]: https://docs.python.org/3/library/xml.etree.elementtree.html
[xlrd]: http://www.python-excel.org/
[json]: https://docs.python.org/3/library/json.html
[Django Data Wizard]: https://github.com/wq/django-data-wizard
[DictReader]: https://docs.python.org/3/library/csv.html#csv.DictReader
[xlwt]: http://www.python-excel.org/
[openpyxl]: https://openpyxl.readthedocs.io/en/stable/
