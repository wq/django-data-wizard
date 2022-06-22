---
repo: itertable
date: 2014-06-13
---

# wq.io 0.5.0

### API Improvements
- Formalize notion of a `nested` IO, or an IO where each record contains a pointer to another IO.  This concept is used extensively by the [climata](https://github.com/heigeo/climata) library, for example in [climata.acis.StationDataIO](https://github.com/heigeo/climata/blob/master/climata/acis/__init__.py#L120).
- Added a utility function, `flattened()`, that converts nested IOs into single-level IOs through denormalization
- Other minor improvements
