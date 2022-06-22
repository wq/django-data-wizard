---
repo: itertable
date: 2013-09-17
---

# wq.io 0.2.0

### API Improvements
- Better handling of Excel files in which data doesn't necessarily start on the second row.
- New `make_io()` function which can be used to mix the provided `loader`, `parser`, and optionally `mapper` classes together into a usable `IO` class.  The default mapper is `TupleMapper`.
- New `load_file()` function will attempt to automatically determine which loaders and parsers to use and create an `IO` class instance on-the-fly.
