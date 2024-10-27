import json

def generate_geojson(num_features):
    features = []
    
    lon = 121.4276
    lat = 31.19139

    for i in range(num_features):
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [lon, lat],
                    [lon + 0.00008, lat - 0.00008],
                    [lon + 0.00008, lat - 0.00008]
                ]
            },
            "properties": {}
        }
        features.append(feature)
        lon += 0.00008
        lat -= 0.00008

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return json.dumps(geojson, indent=4)

def generate_gpx(num_features):
    lon = 121.4276
    lat = 31.19139
    gpx_header = '''<?xml version="1.0"?>
<gpx version="1.1" creator="GDAL 2.2.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogr="http://osgeo.org/gdal" xmlns="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
<metadata><bounds minlat="31.177789999999909" minlon="121.427599999999998" maxlat="31.191389999999998" maxlon="121.441199999999483"/></metadata>'''
    gpx_footer = '</gpx>'
    gpx_body = ''

    for i in range(num_features):
        gpx_body += f'''
<trk>
  <trkseg>
    <trkpt lat="{lat}" lon="{lon}">
    </trkpt>
    <trkpt lat="{lat - 0.00006}" lon="{lon + 0.00006}">
    </trkpt>
    <trkpt lat="{lat - 0.00006}" lon="{lon + 0.00006}">
    </trkpt>
  </trkseg>
</trk>'''
        lon += 0.00006
        lat -= 0.00006

    return gpx_header + gpx_body + gpx_footer

def main(num_features, output_format):
    if output_format == 'geojson':
        result = generate_geojson(num_features)
        file_extension = 'geojson'
    elif output_format == 'gpx':
        result = generate_gpx(num_features)
        file_extension = 'gpx'
    else:
        raise ValueError("Unsupported format. Please choose 'geojson' or 'gpx'.")

    with open(f'data.{file_extension}', 'w') as f:
        f.write(result)

num_features = 170 # approximate 2km
output_format = 'geojson'  # Change to 'gpx' for GPX output
main(num_features, output_format)