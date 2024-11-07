import math
import random

def generate_gpx(points, round_count, fluctuation_range,speed):
    """生成GPX文件的主要函数。

    Args:
        points (list): 各坐标点列表。
        round_count (int): GPX路径需要重复的圈数。
        fluctuation_range (float): 坐标的随机浮动范围，单位为米。
    """
    def add_fluctuation(value, fluctuation_range):
        """为坐标点添加随机浮动。

        Args:
            value (float): 原始坐标点。
            fluctuation_range (float): 浮动范围。

        Returns:
            float: 添加浮动后的坐标点。
        """
        return value + (random.uniform(-fluctuation_range, fluctuation_range) / 111000)
    
    coordinate_spacing = speed/20/111000 # 计算坐标间隔经纬度
    # 提取初始坐标和边界值
    lon, lat = points[0][1], points[0][0]
    minlat = min(points, key=lambda x: x[0])[0]
    minlon = min(points, key=lambda x: x[1])[1]
    maxlat = max(points, key=lambda x: x[0])[0]
    maxlon = max(points, key=lambda x: x[1])[1]

    # GPX文件头部和尾部
    gpx_header = f'''<?xml version="1.0"?>
<gpx version="1.1" creator="GDAL 2.2.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogr="http://osgeo.org/gdal" xmlns="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
<metadata><bounds minlat="{minlat}" minlon="{minlon}" maxlat="{maxlat}" maxlon="{maxlon}"/></metadata>'''
    gpx_footer = '</gpx>'
    gpx_body = ''

    for _ in range(round_count):
        # 提取坐标点
        lat0, lon0 = points[0]
        lat1, lon1 = points[1]
        lat2, lon2 = points[2]

        # 生成从点0到点1的直线段
        distance_straight = math.hypot(lat1 - lat0, lon1 - lon0)
        num_points_straight = int(distance_straight / coordinate_spacing)
        lat_step = (lat1 - lat0) / num_points_straight
        lon_step = (lon1 - lon0) / num_points_straight

        gpx_body += '''
    <trk>
      <trkseg>'''
        for i in range(num_points_straight + 1):
            lat = lat0 + lat_step * i
            lon = lon0 + lon_step * i
            lat = add_fluctuation(lat, fluctuation_range)
            lon = add_fluctuation(lon, fluctuation_range)
            gpx_body += f'''
        <trkpt lat="{lat}" lon="{lon}">
        </trkpt>'''

        # 生成从点1到点2的弯曲段
        center_lat = (lat1 + lat2) / 2
        center_lon = (lon1 + lon2) / 2
        radius = math.hypot(lat1 - center_lat, lon1 - center_lon)
        num_points_curve = int((math.pi * radius) / coordinate_spacing)
        begin_angle = math.atan2(lat0 - lat1, -lon0 + lon1)

        for i in range(num_points_curve + 1):
            angle = math.pi * (1 - i / num_points_curve) + begin_angle
            lat = center_lat + radius * math.cos(angle)
            lon = center_lon + radius * math.sin(angle)
            lat = add_fluctuation(lat, fluctuation_range)
            lon = add_fluctuation(lon, fluctuation_range)
            gpx_body += f'''
        <trkpt lat="{lat}" lon="{lon}">
        </trkpt>'''

        gpx_body += '''
      </trkseg>
    </trk>'''

        # 再次生成直线段
        gpx_body += '''
    <trk>
        <trkseg>'''
        for i in range(num_points_straight + 1):
            lat = lat2 - lat_step * i
            lon = lon2 - lon_step * i
            lat = add_fluctuation(lat, fluctuation_range)
            lon = add_fluctuation(lon, fluctuation_range)
            gpx_body += f'''
        <trkpt lat="{lat}" lon="{lon}">
        </trkpt>'''
        gpx_body += '''
        </trkseg>
    </trk>'''

        # 再次生成弯曲段
        center_lat = (lat + lat0) / 2
        center_lon = (lon + lon0) / 2
        gpx_body += '''
    <trk>
        <trkseg>'''
        for i in range(num_points_curve + 1):
            angle = math.pi * (1 - i / num_points_curve) + begin_angle
            lat = center_lat - radius * math.cos(angle)
            lon = center_lon - radius * math.sin(angle)
            lat = add_fluctuation(lat, fluctuation_range)
            lon = add_fluctuation(lon, fluctuation_range)
            gpx_body += f'''
        <trkpt lat="{lat}" lon="{lon}">
        </trkpt>'''

        gpx_body += '''
        </trkseg>
    </trk>'''

    full_gpx = gpx_header + gpx_body + gpx_footer
    return full_gpx

def main():
    points = []
    lon_0 = 120.681379  # 起点经度
    lat_0 = 27.918553  # 起点纬度

    lon_1 = 120.681212  # 第二点经度
    lat_1 = 27.919372  # 第二点纬度

    lon_2 = 120.680402  # 第三点经度
    lat_2 = 27.919234  # 第三点纬度
    
    points.append((lat_0, lon_0))
    points.append((lat_1, lon_1))
    points.append((lat_2, lon_2))
    
    round_count = 10  # 重复圈数
    fluctuation_range = 0.5  # GPS浮动（米）
    # coordinate_spacing = 0.2 # 坐标间隔（米）
    speed = 3 # 速度（米每秒）
    result = generate_gpx(points, round_count, fluctuation_range,speed)
    
    file_extension = 'gpx'
    with open(f'data.{file_extension}', 'w') as f:
        f.write(result)

main()
