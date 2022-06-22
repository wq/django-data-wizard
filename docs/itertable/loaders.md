---
order: 3
---

Loaders
=======

> Source: [`itertable.loaders`][itertable.loaders]

[IterTables]'s `Loader` [mixin classes][custom] facilitate loading an external resource from the local filesystem or from the web into a file-like object.  A loader is essentially just a class with `load()` and `save()` methods defined.  The canonical example is `FileLoader`, represented in its entirely below:

```python
class FileLoader(BaseLoader):
    filename = None
    read_mode = 'r'
    write_mode = 'w+'

    def load(self):
        try:
            self.file = open(self.filename, self.read_mode)
            self.empty_file = False
        except IterError:
            self.file = StringIter()
            self.empty_file = True

    def save(self):
        file = open(self.filename, self.write_mode)
        self.dump(file)
        file.close()
```

As can be seen above, every `Loader`'s `load()` method should take no arguments, instead determining what to load based on properties on the class instance.  (Remember that the [BaseIter][base] class provides a convenient method for setting class properties on initialization).  `load()` should set two properties on the class:

 * `file`, a file-like object that will be accessed by the parser
 * `empty_file`, a boolean indicating that the file was empty or nonexistent (used to short-circuit avoid parser errors)

To support file output, loaders should define a `save()` method, which should prepare a file-like object for writing, call `self.dump()` with the output file, and perform any needed wrap-up operations.

### Built-In Loaders

There are six built-in loader classes defined in [itertable.loaders].

name | purpose
-----|---------
`FileLoader` | Loads text data from a local file (e.g a CSV or XML file).  Expects a `filename` property to be set on the class instance.
`BinaryFileLoader` | Loads binary data from the local filesystem (e.g. an Excel spreadsheet).  Expects a `filename` property.
`ZipFileLoader` | Opens a local zip file and extracts a single inner file.  If there is more than one inner file, the `inner_filename` property should be set.  If the inner file is binary, `inner_binary` should be set to `True`.
`StringLoader` | Loads data to and from a `string` property that should be set on the class instance.
`NetLoader` | Loads data over HTTP(S) and expects a `url` property to be set or computed by the class or instance.
`ZipNetLoader` | Loads a zip file over HTTP(S) and extracts a single inner file.  If there is more than one inner file, the `inner_filename` property should be set.  If the inner file is binary, `inner_binary` should be set to true.

`NetLoader` and `ZipNetLoader` support optional HTTP `username`, `password`, and URL `params` properties.  Note that `save()` is not implemented for these loaders.

### Custom Loaders

The built in loaders should be enough for many use cases.  The most common use for a custom loader is to encapsulate a number of `NetLoader` options into a reusable mixin class.  For example, the [climata library] defines a `WebserviceLoader` for this purpose.

[itertable.loaders]: https://github.com/wq/itertable/blob/main/itertable/loaders.py

[IterTable]: ./index.md
[custom]: ./about.md
[base]: ./base.md
[loaders]: ./loaders.md
[parsers]: ./parsers.md
[mappers]: ./mappers.md
[gis]: ./gis.md

[climata library]: https://github.com/heigeo/climata
