---
repo: itertable
date: 2013-10-28
---

# wq.io 0.3.0

### New Classes & Modules
- **[TimeSeriesMapper](../itertable/mappers.md)**: Automatically maps text values containing dates or numbers to appropriate Python types.  TimeSeriesMapper also includes a notion of "key fields" (e.g. date, time, location) as opposed to "parameter fields", or the actual data being recorded in the series.
- **[make_date_mapper(fmt)](../itertable/mappers.md)**: Returns a function that parses dates with the provided [format string](https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior).
- **[SkipPreludeReader](../itertable/parsers.md)**: Subclass of [csv.DictReader](https://docs.python.org/2/library/csv.html#csv.DictReader) that allows ingestion of CSV files with non-CSV header preludes.
- **[contrib.hydromet](https://github.com/wq/wq.io/blob/master/contrib/hydromet.py)**: IOs for retrieving Hydromet and Agrimet data from https://www.usbr.gov

### API improvements
- **[contrib.cocorahs](https://github.com/wq/wq.io/blob/master/contrib/cocorahs.py)**: `CocorahsIO` Now utilizes new `TimeSeriesMapper`

You may also be interested in [climata](https://github.com/heigeo/climata), a new wq.io-based library for loading Applied Climate Information System (ACIS) data.
