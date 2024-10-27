# Campus REAL Run

[README](README.md) | [中文文档](README-zh.md)

This tool allows you to simulate GPS locations on iOS devices for campus running activities using Python. It provides a more stable solution compared to traditional location simulation tools.

## Prerequisites

- Python 3.x
- iOS device with proper drivers installed
- Administrator privileges on Windows

## Installation

1. Install the required Python package:
```bash
python -m pip install -U pymobiledevice3
```

2. Verify the installation:
```bash
pymobiledevice3 version
```
Make sure the version is 4.14.16 or higher. If not, please check the [pymobiledevice3 repository](https://github.com/doronz88/pymobiledevice3) for proper installation instructions.

## Usage

### Setting up the Connection

1. Open a Command Prompt with administrator privileges and run:
```bash
python -m pymobiledevice3 remote tunneld
```
Keep this window open throughout the process.

2. Open another Command Prompt with administrator privileges and run:
```bash
python -m pymobiledevice3 lockdown start-tunnel
```

### Running the Location Simulation

The repository contains two main Python scripts:

1. `generate_geojson.py` - Generates a route file in GeoJSON format
2. `main.py` - Simulates the movement along the route

#### Generating the Route

The `generate_geojson.py` script creates a route with appropriate coordinate spacing. You can customize the starting coordinates and distance by modifying the script parameters:

```python
# Current defaults:
lon = 121.4276  # Starting longitude
lat = 31.19139  # Starting latitude
num_features = 170  # Approximately 2km route
```

To find specific coordinates for your location, you can use the [Amap Coordinate Picker](https://lbs.amap.com/tools/picker).

#### Running the Simulation

1. Generate your route file:
```bash
python generate_geojson.py
```

2. Start the location simulation:
```bash
python main.py
```

## Technical Details

- Coordinate spacing: The scripts use an increment of 0.00008 for both latitude and longitude to maintain a realistic running pace
- Update interval: Location updates occur every 2.5 seconds to ensure stable operation
- Route length: The default configuration generates approximately 2km route

## Known Issues and Solutions

1. **Speed Considerations**: 
   - The coordinate spacing and update interval are optimized for realistic running speeds
   - Too large gaps between coordinates may result in invalid speed readings
   - Too small gaps may cause system lag

## Contributing

Feel free to submit issues and enhancement requests!

## Note

This tool is designed for educational and testing purposes. Please use responsibly and in accordance with your local regulations and policies.

## License

This repository is licensed under the GPL-3.0 License.