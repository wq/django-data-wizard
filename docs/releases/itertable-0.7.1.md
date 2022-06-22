---
repo: itertable
date: 2015-01-31
---

# wq.io 0.7.1

**wq.io 0.7.1** brings a couple of minor bug fixes to 0.7.0:
- Ensure that `extra_data` is an instance property rather than a class property (b17aeef).  This was causing subtle issues in long-running [dbio](https://github.com/wq/dbio) processes.
- Account for Unicode normalization in Python 3 (a14d6a6).  See https://bugs.python.org/issue23091 for background.
