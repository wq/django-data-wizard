---
order: 6
---

Geospatial support
==================

> Source: [`itertable.gis`][itertable.gis]

[IterTable] includes a [gis submodule][itertable.gis] with a number of extensions for working with geospatial data.  This submodule requires [Fiona], [Shapely], and [GeoPandas], which can be installed by specifying `itertable[gis]`. itertable.gis provides a Fiona-powered [loader][loaders] and [parser][parsers], as well as three Shapely and GeoPandas-powered [mapper][mappers] classes.  These are combined with a GIS-aware [BaseIter][base] extension to provide a set of three pre-mixed base classes, described below.

To leverage all of these features:
```bash
python3 -m pip install itertable[gis]
```

### GisIter

The `GisIter` class (and the corresponding `GisMapper` mixin) provide an API similar to `TupleMapper`, but with a `geometry` field on each row containing the [GeoJSON-like objects] returned from Fiona.

```python
from itertable.gis import GisIter
data = GisIter(filename='sites.shp')
for id, site in data.items():
    print(id, site.name, site.geometry['type'])
```

Note that all of the gis Iter classes assume a `key_field` of "id" and will behave like a `dict` (See [BaseIter][base]).
  
### ShapeIter

The `ShapeIter` class (and corresponding `ShapeMapper` mixin) replaces the GeoJSON-like `geometry` attribute with a [Shapely geometry object] for convenient manipulation and computation.

```python
from itertable.gis import ShapeIter
data = ShapeIter(filename='sites.shp')
for id, site in data.items():
    print(id, site.name, site.geometry.area)
```

### WktIter

The `WktIter` class (and corresponding `WktMapper` mixin) replaces the Shapely `geometry` attribute with a [WKT string] to simplify use with other libraries.

```python
from itertable.gis import WktIter
data = WktIter(filename='sites.shp')
for id, site in data.items():
    OrmModel.objects.create(name=site.name, geometry=site.geometry)
```

### GeoDataFrame

Like all IterTable classes, the gis Iter classes provide an `as_dataframe()` function for Pandas-powered analysis.

```python
from itertable.gis import ShapeIter
data = ShapeIter(filename='sites.shp')
df = data.as_dataframe()
df.plot()
```

### Syncing gis Iter classes

All gis Iter classes support the `sync()` operation (see [BaseIter][base]).  Additional care is taken to ensure the Shapely metadata (other than the driver) is synced together with the data.

```python
source = ShapeIter(filename="source.shp")
dest = ShapeIter(filename="dest.geojson")
source.sync(dest)
```

[itertable.gis]:  https://github.com/wq/itertable/blob/main/itertable/gis/

[IterTable]: ./index.md
[custom]: ./about.md
[base]: ./base.md
[loaders]: ./loaders.md
[parsers]: ./parsers.md
[mappers]: ./mappers.md
[gis]: ./gis.md

[Fiona]: https://github.com/Toblerity/Shapely
[Shapely]: https://github.com/Toblerity/Shapely
[GeoPandas]: http://geopandas.org/
[GeoJSON-like objects]: http://toblerity.org/fiona/manual.html#data-model
[Shapely geometry object]: http://toblerity.org/shapely/manual.html#geometric-objects
[WKT String]: http://en.wikipedia.org/wiki/Well-known_text
