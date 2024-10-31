# iOS 校园跑位置模拟器

这个工具使用 Python 在 iOS 设备上模拟 GPS 位置，用于校园跑步活动。相比传统的位置模拟工具，它提供了更稳定的解决方案。

## 前置要求

- Python 3.x
- iOS 设备（需要正确安装驱动，且连接至电脑，开启开发者模式）
- 管理员权限（Windows-UAC，macOS-Linux-sudo）

## Todo

- [x] ~~目前`main.py`在模拟位置一段时间后会出现卡死的现象。经过检查，这是`lockdown start-tunnel`命令的问题。莫名其妙地会在一定时间后停止运行，而手动启动之不会有这个问题。关于这个问题的解决方案，欢迎提交PR。~~ 已修复。

- [ ] 增加自动生成操场路线的功能。

- [x] 双语支持。

## 注意

务必仔细阅读以下内容：

- 所有操作都需要管理员权限。请确保以**管理员身份**运行命令提示符。

- 如果你遇到问题“[winError 10054]远程主机强迫关闭了一个现有的连接。” **请先尝试重启你的电脑和手机，并检查是否有代理软件在后台运行！**请一步一步检查！每一个都可能trigger这个问题！如果有代理软件，请关闭！

- 尽管程序已经实现了`start-tunnel`,`tunneld`等开启的傻瓜化操作。但是在初次使用时，我们仍然推荐你手动操作命令行（见本文后半部分），以便更好地观察到（可能存在的）报错信息。

- 我的设备没有开启开发者权限怎么办/没有驱动怎么办？我推荐使用爱思助手。但我不推荐使用爱思助手的虚拟定位功能，因为其无法保证定位的稳定性（也即，会在目标位置和真实位置间反复横跳）

## 包安装

1. 安装必需的 Python 包：
```bash
python -m pip install -U pymobiledevice3
```

2. 验证安装：
```bash
pymobiledevice3 version
```
确保版本号为 4.14.16 或更高。如果不是，请查看 [pymobiledevice3 仓库](https://github.com/doronz88/pymobiledevice3) 获取正确的安装说明。

## 功能特点

- 支持 iOS 16 及以下版本设备
- 支持 iOS 17.4+ 设备（需要特殊初始化）
- 自定义路线导入（支持 GeoJSON 格式）
- 实时位置模拟

## 使用方法

1. 以管理员权限运行程序：
```bash
# Windows (管理员权限)
python campus_run.py

# Linux/macOS
sudo python campus_run.py
```

2. 正确的程序运行步骤：

- `init`：初始化设备连接
  ```bash
  run> init           # iOS 16 及以下版本
  run> init --ios17   # iOS 17.4+ 版本
  ```

- `load`：加载路线文件
  ```bash
  run> load               # 加载默认名为 data.geojson 文件
  run> load route.geojson # 加载指定的路线文件
  ```

- `start`：开始位置模拟
  ```bash
  run> start         # 适用于 iOS 17 及以上版本设备
  run> start --ios16 # 适用于 iOS 16 及以下版本设备
  ```

- `status`：查看当前状态
  ```bash
  run> status
  ```

- `cleanup`：清理连接和进程
  ```bash
  run> cleanup
  ```

- `exit`：退出程序
  ```bash
  run> exit
  ```

## 路线文件格式

程序使用 GeoJSON 格式的路线文件，示例结构如下：

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
          [longitude2, latitude2]
        ]
      }
    }
  ]
}
```

我提供了一个默认的路线文件 `example_data.geojson`，你也可以使用 `generate_geojson.py` 脚本生成自定义路线。

## 注意事项

1. 必须以管理员/root权限运行程序
2. 运行命令前确保设备已正确连接到电脑
3. 对于 iOS 17.4+ 的设备，需要使用 `init --ios17` 命令进行初始化
4. 使用 Ctrl+C 可以随时停止位置模拟
5. 如需重新初始化，请先使用 `cleanup` 命令清理现有连接

## 故障排除

1. 如果连接失败，请检查：
   - 设备是否正确连接
   - 是否以管理员权限运行
   - iOS 版本是否与初始化命令匹配

2. 如果位置模拟失败，请尝试：
   - 使用 `cleanup` 命令清理连接
   - 重新执行 `init` 命令
   - 确认路线文件格式是否正确

## 手动操作命令行步骤

### 注意

- 如果你是`iOS 17.3` **及以下**的用户，在第二步`START-TUNNEL`时，使用如下命令：`python -m pymobiledevice3 remote start-tunnel`。

### 建立连接

1. 以管理员权限打开命令提示符并运行：
```bash
python -m pymobiledevice3 remote tunneld
```
保持此窗口始终运行。

如果正确运行，你会看到类似以下的输出：
```bash
INFO:     Started server process [40388]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:49151 (Press CTRL+C to quit)
```

2. 以管理员权限打开另一个命令提示符并运行：
```bash
python -m pymobiledevice3 lockdown start-tunnel
```

如果正确运行，你会看到类似以下的输出：
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

3. 访问DVT Service
同样以管理员权限打开另一个命令提示符并运行：
```bash
python -m pymobiledevice3 developer dvt ls /
```

如果正确运行，你会看到类似以下的输出：
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

此时你已经成功99%了，接下来你可以关闭上面所述的所有窗口，运行`python main.py`，并进行傻瓜式操作。

### 运行位置模拟

本仓库包含两个主要的 Python 脚本：

1. `generate_geojson.py` - 生成 GeoJSON 格式的路线文件
2. `main.py` - 傻瓜操作，建立连接，导入路线，开始模拟

#### 生成路线

`generate_geojson.py` 脚本会创建一个具有适当坐标间距的路线。你可以通过修改脚本参数来自定义起始坐标和距离：

生成路线文件：
```bash
python generate_geojson.py
```

```python
# 当前默认值：
lon = 121.4276  # 起始经度
lat = 31.19139  # 起始纬度
num_features = 170  # 大约 2 公里的路线
```

要找到特定位置的坐标，你可以使用[高德地图坐标拾取器](https://lbs.amap.com/tools/picker)。

## 技术细节

- 坐标间距：脚本使用 0.00006 的经纬度增量来保持真实的跑步步调
- 更新间隔：位置更新每 2.5 秒进行一次，以确保稳定运行
- 路线长度：默认配置生成约 2 公里的路线

## 已知问题及解决方案

1. **速度注意事项**：
   - 坐标间距和更新间隔已针对真实跑步速度优化
   - 坐标间距过大可能导致无效的速度读数
   - 坐标间距过小可能导致系统卡顿

## 贡献

欢迎提交问题和功能改进请求！

## 注意事项

本工具仅供教育和测试目的使用。请遵守当地法规和政策，负责任地使用。

## 许可证

本仓库使用 GPL-3.0 许可证。