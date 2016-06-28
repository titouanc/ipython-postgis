# IPython + PostGIS

Display results of geographic queries in PostGIS on an interactive Leaflet map.

An IPython extension inspired by [mplleaflet](https://github.com/jwass/mplleaflet)
and [ipython-sql](https://github.com/catherinedevlin/ipython-sql).

## Usage

See [Demo.ipynb](http://nbviewer.jupyter.org/github/titouanc/ipython-postgis/blob/master/Demo.ipynb)

Geographies should be serialized as GeoJSON. All columns names that contain
`geojson` willl be displayed on the map (it is the case for geographies serialized
with `ST_AsGeojson`)
