from IPython.core.magic import register_cell_magic
import psycopg2 as pg
from psycopg2.extras import RealDictCursor
import json
from IPython.display import HTML
import base64


def unload_ipython_extension(ipython):
    # If you want your extension to be unloadable, put that logic here.
    pass


def load_ipython_extension(ipython):
    def to_table(row):
        res = '<table>'
        for k in sorted(row.keys()):
            if 'geojson' not in k.lower():
                res += '<tr><th>%s</th><td>%s</td></tr>' % (k, row[k])
        return res + '</table>'

    def transform_row(row):
        res = []
        for k, v in row.iteritems():
            if 'geojson' in k.lower():
                geojson = json.loads(v)
                v = {
                    'type': 'Feature',
                    'properties': {'popup': to_table(row)},
                    'geometry': geojson
                }
                res.append(v)
        return res

    def run_query(database, *args, **kwargs):
        cursor = database.cursor(cursor_factory=RealDictCursor)
        cursor.execute(*args, **kwargs)
        rows = cursor.fetchall()
        geojson = reduce(lambda res, x: res + transform_row(x), rows, [])
        return json.dumps(geojson)

    def show_on_map(geojson):
        document = u"""
        <head>
          <link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.css" />
          <script src="http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.js"></script>
          <style>
            .a-map {width: 100%; height: 100%; position: relative;}
            th {text-align: right}
          </style>
        </head>
        <body>
          <div id="the-map" class="a-map"></div>
          <script type="text/javascript">
            function bindDaPopup(feature, layer) {
              if (feature.properties && feature.properties.popup) {
                layer.bindPopup(feature.properties.popup);
              }
            }

            var map = L.map('the-map');
            L.tileLayer('http://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png')
             .addTo(map);
            var geojson = """ + geojson + """;
            var geolayer = L.geoJson(geojson, {onEachFeature: bindDaPopup})
                            .addTo(map);
            map.fitBounds(geolayer.getBounds())
          </script>
        </body>
        """
        frame = '<iframe width="100%" height="600" src="data:text/html;base64,' + base64.encodestring(document) + '"></iframe>'
        return HTML(frame)

    @register_cell_magic
    def postgis(line, cell):
        """
        Execute query against a postgis database,
        and show all __geojson columns as geojson on a map
        """
        database = pg.connect(dbname=line.strip())
        try:
            return show_on_map(run_query(database, cell))
        except:
            import traceback
            traceback.print_exc()
        finally:
            database.commit()
