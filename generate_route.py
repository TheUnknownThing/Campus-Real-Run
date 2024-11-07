import math

def generate_gpx(points, round_count):
    lon = points[0][1]
    lat = points[0][0]
    minlat = min(points, key=lambda x: x[0])[0]
    minlon = min(points, key=lambda x: x[1])[1]
    maxlat = max(points, key=lambda x: x[0])[0]
    maxlon = max(points, key=lambda x: x[1])[1]
    gpx_header = f'''<?xml version="1.0"?>
<gpx version="1.1" creator="GDAL 2.2.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogr="http://osgeo.org/gdal" xmlns="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
<metadata><bounds minlat="{minlat}" minlon="{minlon}" maxlat="{maxlat}" maxlon="{maxlon}"/></metadata>'''
    gpx_footer = '</gpx>'
    gpx_body = ''
    # Extract points
    lat0, lon0 = points[0]
    lat1, lon1 = points[1]
    lat2, lon2 = points[2]
    # Generate straight segment between point 0 and point 1
    distance_straight = math.hypot(lat1 - lat0, lon1 - lon0)
    num_points_straight = int(distance_straight / 0.000002)
    lat_step = (lat1 - lat0) / num_points_straight
    lon_step = (lon1 - lon0) / num_points_straight
    gpx_body += '''
<trk>
  <trkseg>'''
    for i in range(num_points_straight + 1):
        lat = lat0 + lat_step * i
        lon = lon0 + lon_step * i
        gpx_body += f'''
    <trkpt lat="{lat}" lon="{lon}">
    </trkpt>'''
    # Generate curved segment between point 1 and point 2
    center_lat = (lat1 + lat2) / 2
    center_lon = (lon1 + lon2) / 2
    radius = math.hypot(lat1 - center_lat, lon1 - center_lon)
    num_points_curve = int((math.pi * radius) / 0.000002)
    begin_angle = math.atan2(lat0 - lat1, -lon0 + lon1)
    for i in range(num_points_curve + 1):
        angle = math.pi * (1 - i / num_points_curve) + begin_angle
        lat = center_lat + radius * math.cos(angle)
        lon = center_lon + radius * math.sin(angle)
        gpx_body += f'''
    <trkpt lat="{lat}" lon="{lon}">
    </trkpt>'''
    gpx_body += '''
  </trkseg>
</trk>'''
    # straight segment again
    gpx_body += '''
<trk>
    <trkseg>'''
    for i in range(num_points_straight + 1):
        lat = lat2 - lat_step * i
        lon = lon2 - lon_step * i
        gpx_body += f'''
    <trkpt lat="{lat}" lon="{lon}">
    </trkpt>'''
    gpx_body += '''
    </trkseg>
</trk>'''

    # curved segment again
    center_lat = (lat + lat0) / 2
    center_lon = (lon + lon0) / 2
    gpx_body += '''
<trk>
    <trkseg>'''
    for i in range(num_points_curve + 1):
        angle = math.pi * (1 - i / num_points_curve) + begin_angle
        lat = center_lat - radius * math.cos(angle)
        lon = center_lon - radius * math.sin(angle)
        gpx_body += f'''
    <trkpt lat="{lat}" lon="{lon}">
    </trkpt>'''
    gpx_body += '''
    </trkseg>
</trk>'''
    full_gpx = gpx_header + gpx_body * round_count + gpx_footer
    return full_gpx

def main():
    points = []
    lon_0 = 121.428446 # replace
    lat_0 = 31.022987 # replace

    lon_1 = 121.428666 # replace
    lat_1 = 31.021854 # replace

    lon_2 = 121.429524 # replace
    lat_2 = 31.022042 # replace
    points.append((lat_0, lon_0))
    points.append((lat_1, lon_1))
    points.append((lat_2, lon_2))
    round_count = 5 # 3圈操场
    result = generate_gpx(points, round_count)
    file_extension = 'gpx'
    with open(f'data.{file_extension}', 'w') as f:
        f.write(result)

main()