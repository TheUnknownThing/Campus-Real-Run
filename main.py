import cmd
import json
import time
import subprocess
import sys
import os
import logging
from pathlib import Path
import random
import psutil
import re

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
    - !important: Please run this program with administrator privileges.
    - !important: Use 'init --ios17' for iOS 17.4+ devices.
    - !important: Connect your device to the computer before running the commands.
    - !important: DO NOT close the terminal window while the program is running.

输入 help 或 ? 查看命令列表。
使用 'init' 命令初始化设备连接。
注意：
    - !重要：请以管理员权限运行此程序。
    - !重要：对于iOS 17.4+设备，请使用 'init --ios17' 命令。
    - !重要：在运行命令前请先连接设备到电脑。
    - !重要：程序运行时请勿关闭终端窗口。
    '''
    prompt = 'run> '
    
    def __init__(self):
        super().__init__()
        self.tunneld_process = None
        self.tunnel_process = None
        self.is_ios17_plus = False
        self.coordinates = []
        self.initialized = False
        self.python_cmd = f'"{sys.executable}"'

    def detect_python_version(self):
        try:
            subprocess.check_output("python3 --version", shell=True)
            return "python3"
        except subprocess.CalledProcessError:
            return "python"

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
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                return process
        except subprocess.CalledProcessError as e:
            logger.error(f"命令执行失败: {e} / Command execution failed: {e}")
            return None

    def do_init(self, arg):
        """
        初始化设备连接 / Initialize device connection
        用法 / Usage: init [--ios17]
        示例 / Example:
            init         # 用于iOS 16及以下版本 / For iOS 16 and below
            init --ios17 # 用于iOS 17.4及以上版本 / For iOS 17.4 and above
        """
        if self.initialized:
            logger.warning("已经初始化过了！如需重新初始化，请先使用 'cleanup' 命令清理现有连接 / Already initialized! To reinitialize, please use the 'cleanup' command to clear existing connections")
            return

        self.is_ios17_plus = "--ios17" in arg
        
        if not self.check_admin():
            logger.error("请使用管理员权限运行此程序！ / Please run this program with administrator privileges!")
            return

        logger.info("检查开发者模式状态... / Checking developer mode status...")
        dev_mode_status = self.run_command(f"{self.python_cmd} -m pymobiledevice3 amfi developer-mode-status", check_output=True)
        if dev_mode_status == str():
            logger.error("设备未连接 / Device is not connected.")
            return
        elif "false" in dev_mode_status.lower():
            logger.error("开发者模式未启用，请使用 'enable_dev_mode' 命令启用开发者模式 / Developer mode is not enabled, please use the 'enable_dev_mode' command to enable developer mode")
            return

        logger.info("正在启动tunneld服务... / Starting tunneld service...")
        self.tunneld_process = self.run_command(f"{self.python_cmd} -m pymobiledevice3 remote tunneld")

        logger.info("正在启动tunnel服务... / Starting tunnel service...")
        tunnel_command = f"{self.python_cmd} -m pymobiledevice3 lockdown start-tunnel" if self.is_ios17_plus else \
                        f"{self.python_cmd} -m pymobiledevice3 remote start-tunnel"
        self.tunnel_process = self.run_command(tunnel_command)
        time.sleep(5)

        if self.tunneld_process.poll() is None and self.tunnel_process.poll() is None:
            logger.info("连接成功建立！ / Connection established successfully!")
            self.initialized = True
        else:
            logger.error("连接失败，请检查设备连接和权限设置 / Connection failed, please check device connection and permission settings")
            for process in [self.tunneld_process, self.tunnel_process]:
                if process.poll() is None:
                    kill_subprocess(process)
                else:
                    out, err = process.communicate()
                    logger.error(str(process.args) + "fails with output: ")
                    logger.error(err)
            self.do_cleanup('')

    def do_enable_dev_mode(self, arg):
        """
        启用开发者模式 / Enable developer mode
        用法 / Usage: enable_dev_mode
        """
        logger.info("启用开发者模式... / Enabling developer mode...")
        self.run_command(f"{self.python_cmd} -m pymobiledevice3 amfi enable-developer-mode")
        logger.info("设备正在重启，请稍后再检查开发者模式状态 / Device is restarting, please check developer mode status later")

    def do_check_dev_mode_status(self, arg):
        """
        检查开发者模式状态 / Check developer mode status
        用法 / Usage: check_dev_mode_status
        """
        logger.info("检查开发者模式状态... / Checking developer mode status...")
        status = self.run_command(f"{self.python_cmd} -m pymobiledevice3 amfi developer-mode-status", check_output=True)
        logger.info(f"开发者模式状态: {status.strip()} / Developer mode status: {status.strip()}")

    def do_start(self, arg):
        """
        开始模拟位置移动 / Start simulating location movement
        用法 / Usage: start [data.gpx]
        字段说明 / Field description: [data.gpx] - GPX文件路径 / GPX file path, 必填 / Required
        提示 / Note: 使用Ctrl+C可以停止模拟 / Use Ctrl+C to stop simulation
        """
        if not self.initialized:
            logger.error("请先使用 'init' 命令初始化连接！ / Please initialize connection first using 'init' command!")
            return

        if not arg:
            logger.error("请提供GPX文件路径！ / Please provide the GPX file path!")
            return
        
        if not arg.endswith('.gpx'):
            logger.error("无效的GPX文件路径！ / Invalid GPX file path!")
            return
        
        gpx_file = Path(arg)

        logger.info("开始模拟位置移动... / Starting location simulation...")
        logger.info("按Ctrl+C可以停止模拟 / Press Ctrl+C to stop simulation")

        logger.info('启动模拟位置 / Simulating location')

        command = f'pymobiledevice3 developer dvt simulate-location play {gpx_file} 1000'
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            for line in process.stdout:
                if "ERROR" in line:
                    plain_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                    raise RuntimeError(plain_line)
                print(line, end='')

        except KeyboardInterrupt:
            logger.info("\n停止位置模拟... / Stopping location simulation...")
            process.terminate()

    def do_cleanup(self, arg):
        """
        清理所有连接和进程 / Clean up all connections and processes
        用法 / Usage: cleanup
        """
        if self.tunneld_process:
            kill_subprocess(self.tunneld_process)
            self.tunneld_process.wait()
            self.tunneld_process = None
        if self.tunnel_process:
            kill_subprocess(self.tunnel_process)
            self.tunnel_process.wait()
            self.tunnel_process = None
        self.initialized = False
        self.route_loaded = False
        logger.info("已清理所有进程和连接 / All processes and connections have been cleaned up")

    def do_status(self, arg):
        """
        显示当前状态 / Show current status
        用法 / Usage: status
        """
        print("\n当前状态 / Current status:")
        print(f"初始化状态: {'已初始化' if self.initialized else '未初始化'} / Initialization status: {'Initialized' if self.initialized else 'Not initialized'}")
        print(f"路线加载状态: {'已加载' if self.route_loaded else '未加载'} / Route load status: {'Loaded' if self.route_loaded else 'Not loaded'}")
        print(f"iOS版本设置: {'iOS 17.4+' if self.is_ios17_plus else 'iOS 16及以下'} / iOS version setting: {'iOS 17.4+' if self.is_ios17_plus else 'iOS 16 and below'}")
        print(f"已加载坐标点数量: {len(self.coordinates)} / Number of loaded coordinates: {len(self.coordinates)}")
        print()

    def do_exit(self, arg):
        """
        退出程序 / Exit the program
        用法 / Usage: exit
        """
        self.do_cleanup(arg)
        logger.info("退出程序... / Exiting the program...")
        return True

    # 别名
    do_quit = do_exit
    do_EOF = do_exit

def kill_subprocess(process: subprocess.Popen):
    try:
        parent = psutil.Process(process.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass

if __name__ == '__main__':
    shell = CampusRunShell()
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        logger.info("\n程序被中断，正在清理... / Program interrupted, cleaning up...")
        shell.do_cleanup('')
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常终止: {e} / Program terminated with exception: {e}")
        shell.do_cleanup('')
        # Show Windows popup
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                f"程序异常终止:\n{e}",
                "Campus-Real-Run 异常 / Exception",
                0x10  # MB_ICONERROR
            )
        except Exception as popup_err:
            logger.error(f"无法弹出异常提示窗口: {popup_err}")
        sys.exit(1)
        