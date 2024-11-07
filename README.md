# Campus REAL Run

[中文文档](README-zh.md) | [English Document](README.md)

This tool uses Python to simulate GPS locations on iOS devices for campus running activities. Compared to traditional location simulation tools, it provides a more stable solution.

## Prerequisites

- Python 3.x
- iOS device (requires proper driver installation, connected to computer, developer mode enabled)
- Administrator privileges (Windows-UAC, macOS-Linux-sudo)

## Todo

- [x] ~~Currently `main.py` experiences freezing after simulating location for a period of time. After inspection, this is an issue with the `lockdown start-tunnel` command. It mysteriously stops running after a certain time, though manually starting it doesn't have this issue. PRs for solving this issue are welcome.~~ Fixed.

- [x] Add functionality to automatically generate track routes.

- [x] Bilingual support.

## Important Notes

Please read the following content carefully:

- All operations require administrator privileges. Make sure to run the command prompt as **administrator**.

- If you encounter the error "[winError 10054] The remote host forcibly closed an existing connection." **First try restarting your computer and phone, and check if any proxy software is running in the background!** Please check step by step! Each one could trigger this issue! If you have proxy software, please close it!

- Although the program has implemented user-friendly operations for `start-tunnel`, `tunneld`, etc., for first-time users, we still recommend manually operating the command line (see latter part of this document) to better observe any (potential) error messages.

- What if I haven't installed drivers on Windows? I recommend using iMazing. However, I don't recommend using iMazing's virtual location feature as it cannot guarantee location stability (i.e., it will repeatedly jump between target and real locations)

## Package Installation

1. Install required Python packages:

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
- Custom route import (supports GPX format)
- Real-time location simulation

## Usage

1. Run the program with administrator privileges:

```bash
# Windows (Administrator privileges)
python main.py

# Linux/macOS
sudo python main.py
```

2. Correct program execution steps:

- `init`: Initialize device connection

  ```bash
  run> init           # iOS 16 and below
  run> init --ios17   # iOS 17.4+
  ```

- `start`: Begin location simulation

  ```bash
  run> start [data.gpx]
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

The program uses GPX format route files. Please refer to relevant documentation for specific format details.

I've provided a default route file `example_data.gpx`, and you can also use the `generate_route.py` script to generate custom routes.

## Important Notes

1. Must run program with administrator/root privileges
2. Ensure device is properly connected to computer before running commands
3. For iOS 17.4+ devices, use `init --ios17` command for initialization
4. Use Ctrl+C to stop location simulation at any time
5. If reinitialization is needed, use `cleanup` command first to clear existing connections

## Troubleshooting

1. If connection fails, check:

   - If device is properly connected
   - If running with administrator privileges
   - If iOS version matches initialization command

2. If location simulation fails, try:
   - Using `cleanup` command to clear connections
   - Re-executing `init` command
   - Confirming route file format is correct

## Manual Command Line Operation Steps

### Note

- If `main.py` works fine for you, you can skip this section.
- If you're using `iOS 17.3` **or below**, use the following command for `START-TUNNEL` in step 2: `python -m pymobiledevice3 remote start-tunnel`.

### Establishing Connection

1. Open command prompt with administrator privileges and run:

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

2. Open another command prompt with administrator privileges and run:

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
   Open another command prompt with administrator privileges and run:

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

At this point, you're 99% successful. You can now close all the windows described above, run `python main.py`, and proceed with the user-friendly operations.

### Running Location Simulation

This repository contains two main Python scripts:

1. `generate_route.py` - Generates route files in GeoJSON format
2. `main.py` - User-friendly operation, establishes connection, imports route, starts simulation

#### Generating Routes

The `generate_route.py` script creates a route with appropriate coordinate spacing. You can customize starting coordinates and distances by modifying script parameters:

Generate route file:

```bash
python generate_route.py
```

```python
# Current default values:
lon_0 = 121.426028 # replace
lat_0 = 31.025834 # replace

lon_1 = 121.426265 # replace
lat_1 = 31.024939 # replace

lon_2 = 121.427101 # replace
lat_2 = 31.0251 # replace

round_count = 3 # 3 laps around the track
```

Explanation of the above parameters:

- `lon_0` and `lat_0` are starting coordinates
- The straight section of the track is between `lon_0, lat_0` and `lon_1, lat_1`
- The curved section is between `lon_1, lat_1` and `lon_2, lat_2`; the line between these coordinates should be the diameter of the track's curve
- `round_count` is the number of laps around the track

So your running path is:

- Start from `lon_0, lat_0`
- Run along the straight section between `lon_0, lat_0` and `lon_1, lat_1`
- Run around the curve between `lon_1, lat_1` and `lon_2, lat_2`
- Run straight again, then curve again, back to start
- Repeat `round_count` times

To find coordinates for specific locations, you can use the [AMap Coordinate Picker](https://lbs.amap.com/tools/picker).

## Contributing

Issues and feature improvement requests are welcome!

## Disclaimer

This tool is for educational and testing purposes only. Please comply with local regulations and policies, and use responsibly.

## License

This repository is licensed under GPL-3.0.