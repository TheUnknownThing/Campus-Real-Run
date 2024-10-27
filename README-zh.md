# iOS 校园跑位置模拟器

这个工具使用 Python 在 iOS 设备上模拟 GPS 位置，用于校园跑步活动。相比传统的位置模拟工具，它提供了更稳定的解决方案。

## 前置要求

- Python 3.x
- iOS 设备（需要正确安装驱动）
- Windows 管理员权限

## 安装方法

1. 安装必需的 Python 包：
```bash
python -m pip install -U pymobiledevice3
```

2. 验证安装：
```bash
pymobiledevice3 version
```
确保版本号为 4.14.16 或更高。如果不是，请查看 [pymobiledevice3 仓库](https://github.com/doronz88/pymobiledevice3) 获取正确的安装说明。

## 使用方法

### 建立连接

1. 以管理员权限打开命令提示符并运行：
```bash
python -m pymobiledevice3 remote tunneld
```
保持此窗口始终运行。

2. 以管理员权限打开另一个命令提示符并运行：
```bash
python -m pymobiledevice3 lockdown start-tunnel
```

### 运行位置模拟

本仓库包含两个主要的 Python 脚本：

1. `generate_geojson.py` - 生成 GeoJSON 格式的路线文件
2. `main.py` - 模拟沿路线移动

#### 生成路线

`generate_geojson.py` 脚本会创建一个具有适当坐标间距的路线。你可以通过修改脚本参数来自定义起始坐标和距离：

```python
# 当前默认值：
lon = 121.4276  # 起始经度
lat = 31.19139  # 起始纬度
num_features = 170  # 大约 2 公里的路线
```

要找到特定位置的坐标，你可以使用[高德地图坐标拾取器](https://lbs.amap.com/tools/picker)。

#### 运行模拟

1. 生成路线文件：
```bash
python generate_geojson.py
```

2. 开始位置模拟：
```bash
python main.py
```

## 技术细节

- 坐标间距：脚本使用 0.00008 的经纬度增量来保持真实的跑步步调
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