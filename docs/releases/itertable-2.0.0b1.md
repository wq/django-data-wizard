---
repo: itertable
date: 2019-09-25
---

# IterTable 2.0 beta

**wq.io** is now **IterTable**!  This name better reflects the project purpose, and avoids confusion with the wq framework website (../index.md).  Similarly, IterTable's `*IO` classes have been renamed to `*Iter`, as the API is not intended to match that of Python's `StringIO` or other `io` classes.

The functionality is otherwise the same as wq.io 1.1.0.  Here is a mapping of top-level exports:

 old name | new name
------------|-------------
wq.io.load_file | itertable.load_file
wq.io.load_url | itertable.load_url
wq.io.load_string | itertable.load_string
wq.io.BaseIO | **itertable.BaseIter**
wq.io.CsvFileIO | **itertable.CsvFileIter**
wq.io.CsvNetIO | **itertable.CsvNetIter**
wq.io.CsvStringIO | **itertable.CsvStringIter**
wq.io.JsonFileIO | **itertable.JsonFileIter**
wq.io.JsonNetIO | **itertable.JsonNetIter**
wq.io.JsonStringIO | **itertable.JsonStringIter**
wq.io.XmlFileIO | **itertable.XmlFileIter**
wq.io.XmlNetIO | **itertable.XmlNetIter**
wq.io.XmlStringIO | **itertable.XmlStringIter**
wq.io.ExcelFileIO | **itertable.ExcelFileIter**
wq.io.make_io | **itertable.make_iter**
wq.io.guess_type | itertable.guess_type
wq.io.flattened | itertable.flattened
wq.io.VERSION | itertable.VERSION
wq.io.*Loader | itertable.*Loader
wq.io.*Parser | itertable.*Parser
wq.io.*Mapper | itertable.*Mapper
