# Campus REAL Run

[README](README.md) | [中文文档](README-zh.md)

This tool uses Python to simulate GPS locations on iOS devices for campus running activities. Compared to traditional location simulation tools, it provides a more stable solution.

## Prerequisites

- Python 3.x
- iOS device (correctly installed drivers are required)
- Windows Administrator privileges

## Installation

1. Install the required Python packages:
```bash
python -m pip install -U pymobiledevice3
```

2. Verify the installation:
```bash
pymobiledevice3 version
```
Ensure the version number is 4.14.16 or higher. If not, check the [pymobiledevice3 repository](https://github.com/doronz88/pymobiledevice3) for proper installation instructions.

## Usage

### Note

All operations require Administrator privileges. Make sure to run the command prompt as **Administrator**.

### Establish Connection

1. Open the command prompt as Administrator and run:
```bash
python -m pymobiledevice3 remote tunneld
```
Keep this window running.

If it runs correctly, you should see output similar to:
```bash
INFO:     Started server process [40388]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:49151 (Press CTRL+C to quit)
```

2. Open another command prompt as Administrator and run:
```bash
python -m pymobiledevice3 lockdown start-tunnel
```

If it runs correctly, you should see output like:
```bash
2024-10-27 19:59:34 TheUnknownThing pymobiledevice3.cli.remote[16932] INFO tunnel created
Identifier: # UUID OF YOUR DEVICE #
Interface: pywintun
Protocol: TunnelProtocol.TCP
RSD Address: # RSD ADDRESS #
RSD Port: # RSD PORT #
Use the follow connection option:
--rsd #RSD ADDRESS # # RSD PORT #
```

3. Access the DVT Service
Similarly, open another command prompt as Administrator and run:
```bash
python -m pymobiledevice3 developer dvt ls /
```

If it runs correctly, you should see output similar to:
```bash
2024-10-27 17:41:29 TheUnknownThing __main__[21244] WARNING Got an InvalidServiceError. Trying again over tunneld since it is a developer command
/usr
/bin
/sbin
/.file
/etc
/System
/var
/Library
/private
/.b
/dev
/tmp
/Applications
/Developer
/cores
```

At this point, you are 99% done! Next, you can run the simulator.

### Run Location Simulation

This repository contains two main Python scripts:

1. `generate_geojson.py` - Generates a route file in GeoJSON format.
2. `main.py` - Simulates movement along the route.

#### Generate Route

The `generate_geojson.py` script creates a route with appropriate coordinate spacing. You can customize the starting coordinates and distance by modifying the script parameters:

```python
# Current default values:
lon = 121.4276  # Starting longitude
lat = 31.19139  # Starting latitude
num_features = 170  # Approximately a 2 km route
```

To find coordinates for a specific location, you can use the [Gaode Map Coordinate Picker](https://lbs.amap.com/tools/picker).

#### Run Simulation

1. Generate the route file:
```bash
python generate_geojson.py
```

2. Start the location simulation:
```bash
python main.py
```

If everything goes well, you should see output like:
```bash
Simulating location: 31.180029999999924, 121.43895999999957
Simulating location: 31.179949999999923, 121.43903999999957
Simulating location: 31.179869999999923, 121.43911999999956
Simulating location: 31.179789999999922, 121.43919999999956
Simulating location: 31.179709999999922, 121.43927999999956
```
Open a map application, and you will see the simulated location moving continuously. You can now start your campus run activity!

## Technical Details

- Coordinate Spacing: The script uses a latitude/longitude increment of 0.00006 to maintain a realistic running pace.
- Update Interval: Location updates occur every 2.5 seconds to ensure stable operation.
- Route Length: The default configuration generates a route of approximately 2 kilometers.

## Known Issues and Solutions

1. **Speed Considerations**:
   - Coordinate spacing and update intervals have been optimized for realistic running speeds.
   - Too large a coordinate spacing may result in invalid speed readings.
   - Too small a coordinate spacing may cause the system to lag.

## Contribution

Contributions, issue reports, and feature improvement requests are welcome!

## Disclaimer

This tool is intended for educational and testing purposes only. Please adhere to local laws and regulations and use it responsibly.

## License

This repository is licensed under the GPL-3.0 License.