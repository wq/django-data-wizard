---
repo: itertable
date: 2013-12-11
---

# wq.io 0.4.0

### Breaking Changes
- Moved domain-specific `contrib` modules (`cocorahs` and `hydromet`) to the [climata](https://github.com/heigeo/climata) library

### API Improvements
- Full read-write support for GIS data via the [Fiona](https://github.com/Toblerity/Fiona) and [Shapely](https://github.com/Toblerity/Shapely) libraries. (#1)
- NetLoaders now send a custom user-agent string.
- Improved `guess_type` which is now utilized by [wq.db.contrib.files](../wq.db/patterns.md).
- Switch to built-in Python XML library to speed up pip install (#4)
