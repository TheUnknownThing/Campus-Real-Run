# Campus REAL Run

[README](README.md) | [中文文档](README-zh.md)

This tool uses Python to simulate GPS locations on iOS devices for campus running activities. Compared to traditional location simulation tools, it provides a more stable solution.

## Prerequisites

- Python 3.x
- iOS device (properly installed drivers, connected to computer, developer mode enabled)
- Administrator privileges (Windows-UAC, macOS-Linux-sudo)

## Todo

- [x] ~~`main.py` may freeze after simulating locations for a period of time. After investigation, this issue is related to the `lockdown start-tunnel` command. It will inexplicably stop running after a certain period, while manually starting it does not have this issue. For a solution to this issue, please submit a PR.~~ fixed.

- [ ] add a feature to automatically generate a route file based on the user's input.

- [ ] bilingual support for the program.

## Important Notes

Please read the following carefully:

- All operations require administrator privileges. Make sure to run the command prompt as **administrator**.

- If you encounter the error "[winError 10054] The remote host forcibly closed an existing connection," **try restarting your computer and phone first, and check if any proxy software is running in the background!** Really important tips if you encounter the problem! If there is proxy software, please close it!

- Although the program has implemented user-friendly operations like `start-tunnel` and `tunneld`, we still recommend manual command-line operation (see latter part of this document) for first-time users to better observe potential error messages.

- What if my device hasn't enabled developer rights/doesn't have drivers? We recommend using iTools. However, we don't recommend using iTools' virtual location feature as it cannot guarantee location stability (i.e., it may repeatedly jump between target and actual locations)

## Package Installation

1. Install required Python package:
```bash
python -m pip install -U pymobiledevice3
```

2. Verify installation:
```bash
pymobiledevice3 version
```
Ensure the version is 4.14.16 or higher. If not, check the [pymobiledevice3 repository](https://github.com/doronz88/pymobiledevice3) for correct installation instructions.

## Features

- Supports iOS 16 and below devices
- Supports iOS 17.4+ devices (requires special initialization)
- Custom route import (supports GeoJSON format)
- Real-time location simulation

## Usage

1. Run the program with administrator privileges:
```bash
# Windows (Administrator privileges)
python campus_run.py

# Linux/macOS
sudo python campus_run.py
```

2. Correct program execution steps:

- `init`: Initialize device connection
  ```bash
  run> init           # iOS 16 and below
  run> init --ios17   # iOS 17.4+
  ```

- `load`: Load route file
  ```bash
  run> load               # Load default data.geojson file
  run> load route.geojson # Load specified route file
  ```

- `start`: Start location simulation
  ```bash
  run> start
  ```

- `status`: Check current status
  ```bash
  run> status
  ```

- `cleanup`: Clean up connections and processes
  ```bash
  run> cleanup
  ```

- `exit`: Exit program
  ```bash
  run> exit
  ```

## Route File Format

The program uses GeoJSON format route files. Example structure:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [longitude1, latitude1],
          [longitude2, latitude2],
          ...
        ]
      }
    }
  ]
}
```

I've provided a default route file `example_data.geojson`. You can also use the `generate_geojson.py` script to generate custom routes.

## Important Notes

1. Must run with administrator/root privileges
2. Ensure device is properly connected to computer before running commands
3. For iOS 17.4+ devices, use `init --ios17` command for initialization
4. Use Ctrl+C to stop location simulation at any time
5. Use `cleanup` command to clear existing connections before reinitializing

## Troubleshooting

1. If connection fails, check:
   - Device connection
   - Administrator privileges
   - iOS version matches initialization command

2. If location simulation fails, try:
   - Using `cleanup` command
   - Re-executing `init` command
   - Confirming route file format is correct

## Manual Command Line Steps

### Note

- For `iOS 17.3` **and below** users, use this command in step 2 `START-TUNNEL`: `python -m pymobiledevice3 remote start-tunnel`

### Establishing Connection

1. Open command prompt as administrator and run:
```bash
python -m pymobiledevice3 remote tunneld
```
Keep this window running.

If running correctly, you'll see output similar to:
```bash
INFO:     Started server process [40388]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:49151 (Press CTRL+C to quit)
```

2. Open another command prompt as administrator and run:
```bash
python -m pymobiledevice3 lockdown start-tunnel
```

If running correctly, you'll see output similar to:
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

3. Access DVT Service
Open another command prompt as administrator and run:
```bash
python -m pymobiledevice3 developer dvt ls /
```

If running correctly, you'll see output similar to:
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

At this point, you're 99% successful. You can close all the windows mentioned above, run `python main.py`, and perform user-friendly operations.

### Running Location Simulation

This repository contains two main Python scripts:

1. `generate_geojson.py` - Generates GeoJSON format route files
2. `main.py` - Simulates movement along the route

#### Generating Routes

The `generate_geojson.py` script creates a route with appropriate coordinate spacing. You can customize starting coordinates and distance by modifying script parameters:

Generate route file:
```bash
python generate_geojson.py
```

```python
# Current default values:
lon = 121.4276  # Starting longitude
lat = 31.19139  # Starting latitude
num_features = 170  # Approximately 2km route
```

To find coordinates for specific locations, you can use [AMap Coordinate Picker](https://lbs.amap.com/tools/picker).

## Technical Details

- Coordinate spacing: Script uses 0.00006 latitude/longitude increments to maintain realistic running pace
- Update interval: Location updates every 2.5 seconds for stable operation
- Route length: Default configuration generates approximately 2km route

## Known Issues and Solutions

1. **Speed Considerations**:
   - Coordinate spacing and update intervals optimized for realistic running speed
   - Too large spacing may result in invalid speed readings
   - Too small spacing may cause system lag

## Contributing

Issues and feature improvement requests are welcome!

## Disclaimer

This tool is for educational and testing purposes only. Please comply with local regulations and policies, and use responsibly.

## License

This repository is licensed under GPL-3.0.