import json
import time
import subprocess
import random

with open('data.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

# Extract coordinates from the GeoJSON data
coordinates = []
for feature in geojson_data['features']:
    if feature['geometry']['type'] == 'LineString':
        coordinates.extend(feature['geometry']['coordinates'])

skip_idx = 0
for coord in coordinates:
    if (skip_idx == 0 or skip_idx == 1):
        skip_idx += 1
        continue
    lat, long = coord[0], coord[1]
    print(f'Simulating location: {long}, {lat}')
    command = f'pymobiledevice3 developer dvt simulate-location set -- {long} {lat}'
    process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate(input=b'\n')
    skip_idx = 0
    # random sleep time between 2 to 2.5 seconds
    sleep_time = 2 + (0.5 * random.random())
    time.sleep(sleep_time)