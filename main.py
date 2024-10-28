import cmd
import json
import time
import subprocess
import sys
import os
import logging
from pathlib import Path
import random

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CampusRunShell(cmd.Cmd):
    intro = '''
Welcome to Campus-Real-Run CLI!
Type help or ? to list commands.
Start with 'init' to setup the connection.
Note: 
    - Please run this program with administrator privileges.
    - Use 'init --ios17' for iOS 17.4+ devices.
    - Connect your device to the computer before running the commands.

输入 help 或 ? 查看命令列表。
使用 'init' 命令初始化设备连接。
注意：
    - 请以管理员权限运行此程序。
    - 对于iOS 17.4+设备，请使用 'init --ios17' 命令。
    - 在运行命令前请先连接设备到电脑。
    '''
    prompt = 'run> '
    
    def __init__(self):
        super().__init__()
        self.tunneld_process = None
        self.tunnel_process = None
        self.is_ios17_plus = False
        self.coordinates = []
        self.initialized = False
        self.route_loaded = False
        
    def check_admin(self):
        try:
            return os.getuid() == 0
        except AttributeError:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0

    def run_command(self, command, check_output=False):
        try:
            if check_output:
                return subprocess.check_output(command, shell=True, text=True)
            else:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                return process
        except subprocess.CalledProcessError as e:
            logger.error(f"命令执行失败: {e}")
            return None

    def do_init(self, arg):
        """
        初始化设备连接
        用法: init [--ios17]
        示例:
            init         # 用于iOS 16及以下版本
            init --ios17 # 用于iOS 17.4及以上版本
        """
        if self.initialized:
            logger.warning("已经初始化过了！如需重新初始化，请先使用 'cleanup' 命令清理现有连接")
            return

        self.is_ios17_plus = "--ios17" in arg
        
        if not self.check_admin():
            logger.error("请使用管理员权限运行此程序！")
            return

        logger.info("正在启动tunneld服务...")
        self.tunneld_process = self.run_command("python -m pymobiledevice3 remote tunneld")
        time.sleep(2)

        logger.info("正在启动tunnel服务...")
        tunnel_command = "python -m pymobiledevice3 lockdown start-tunnel" if self.is_ios17_plus else \
                        "python -m pymobiledevice3 remote start-tunnel"
        self.tunnel_process = self.run_command(tunnel_command)
        time.sleep(2)

        logger.info("测试DVT服务...")
        test_output = self.run_command("python -m pymobiledevice3 developer dvt ls /", check_output=True)
        if test_output and "/Applications" in test_output:
            logger.info("连接成功建立！")
            self.initialized = True
        else:
            logger.error("连接失败，请检查设备连接和权限设置")

    def do_load(self, arg):
        """
        加载路线文件
        用法: load [文件路径]
        示例:
            load              # 加载默认的data.geojson文件
            load route.geojson  # 加载指定的路线文件
        """
        if not self.initialized:
            logger.error("请先使用 'init' 命令初始化连接！")
            return

        file_path = arg if arg else "data.geojson"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            
            self.coordinates = []
            for feature in geojson_data['features']:
                if feature['geometry']['type'] == 'LineString':
                    self.coordinates.extend(feature['geometry']['coordinates'])
            
            logger.info(f"成功加载 {len(self.coordinates)} 个坐标点，来自文件 {file_path}")
            self.route_loaded = True
        except Exception as e:
            logger.error(f"加载路线文件失败: {e}")

    def do_start(self, arg):
        """
        开始模拟位置移动
        用法: start
        提示: 使用Ctrl+C可以停止模拟
        """
        if not self.initialized:
            logger.error("请先使用 'init' 命令初始化连接！")
            return
        
        if not self.route_loaded:
            logger.error("请先使用 'load' 命令加载路线文件！")
            return

        try:
            skip_idx = 0
            logger.info("开始模拟位置移动...")
            logger.info("按Ctrl+C可以停止模拟")
            
            for coord in self.coordinates:
                if skip_idx == 0 or skip_idx == 1:
                    skip_idx += 1
                    continue
                
                lat, long = coord[0], coord[1]
                logger.info(f'正在模拟位置: {long}, {lat}')
                
                command = f'pymobiledevice3 developer dvt simulate-location set -- {long} {lat}'
                process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, 
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.communicate(input=b'\n')
                
                skip_idx = 0
                sleep_time = 2 + (0.5 * random.random())
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("\n停止位置模拟...")
        except Exception as e:
            logger.error(f"位置模拟过程中出错: {e}")

    def do_cleanup(self, arg):
        """
        清理所有连接和进程
        用法: cleanup
        """
        if self.tunneld_process:
            self.tunneld_process.terminate()
            self.tunneld_process = None
        if self.tunnel_process:
            self.tunnel_process.terminate()
            self.tunnel_process = None
        self.initialized = False
        self.route_loaded = False
        logger.info("已清理所有进程和连接")

    def do_status(self, arg):
        """
        显示当前状态
        用法: status
        """
        print("\n当前状态:")
        print(f"初始化状态: {'已初始化' if self.initialized else '未初始化'}")
        print(f"路线加载状态: {'已加载' if self.route_loaded else '未加载'}")
        print(f"iOS版本设置: {'iOS 17.4+' if self.is_ios17_plus else 'iOS 16及以下'}")
        print(f"已加载坐标点数量: {len(self.coordinates)}")
        print()

    def do_exit(self, arg):
        """
        退出程序
        用法: exit
        """
        self.do_cleanup(arg)
        logger.info("退出程序...")
        return True

    # 别名
    do_quit = do_exit
    do_EOF = do_exit

if __name__ == '__main__':
    try:
        CampusRunShell().cmdloop()
    except KeyboardInterrupt:
        logger.info("\n程序被中断，正在清理...")
        sys.exit(0)