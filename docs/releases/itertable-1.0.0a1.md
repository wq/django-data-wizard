---
repo: itertable
date: 2016-03-22
---

# wq.io 1.0 alpha

**wq.io 1.0.0a1** is an alpha release of the upcoming 1.0 version of [wq.io](../itertable/index.md).  The main change is better support for binary formats.
- Change `binary` from being defined on [loader](../itertable/loaders.md) classes to being defined on [parser](../itertable/parsers.md) classes, which makes more sense intuitively.  Removed `BinaryFileLoader` and made `FileLoader` check (rather than set) the `binary` attribute to determine file mode.
- Include binary support in `StringLoader` via a similar mechanism.
- Update `CsvParser` and tests to ensure they work whether or not `unicodecsv` is installed
