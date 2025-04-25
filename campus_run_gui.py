#!/usr/bin/env python3
# gui_campusrun.py
import importlib.util
import sys, os, subprocess, threading, io, contextlib, logging
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

##############################################################################
# 1. 让用户选择 main.py，并把 CampusRunShell 动态载入
##############################################################################
def load_shell_class():
    path = filedialog.askopenfilename(
        title="请选择包含 CampusRunShell 的 main.py 文件",
        filetypes=[("Python file", "*.py")])
    if not path:
        messagebox.showerror("未选择文件", "必须选择 main.py 才能继续")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("campus_main", path)
    campus_main = importlib.util.module_from_spec(spec)
    sys.modules["campus_main"] = campus_main
    spec.loader.exec_module(campus_main)

    # ---------------- 补丁 1：修复未定义的 route_loaded ---------------- #
    # 原 main.py 在 __init__ 中未给 route_loaded 赋值，
    # 但 do_status / do_cleanup 要用到它，导致首次调用报 AttributeError。
    original_init = campus_main.CampusRunShell.__init__
    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.route_loaded = False
    campus_main.CampusRunShell.__init__ = patched_init

    # ---------------- 补丁 2：run_command 跨平台 & 捕捉输出 -------------- #
    # 原实现在 Windows 调用了 `start cmd /k ...`，不仅局限于 Windows，
    # 还无法把输出回传到 GUI。这里换成 cross-platform 的实现。
    def patched_run_command(self, command, check_output=False):
        try:
            if check_output:
                return subprocess.check_output(
                    command, shell=True, text=True, stderr=subprocess.STDOUT)
            else:
                # 直接启动子进程并返回 Popen 对象，方便 GUI 自行处理 stdout
                return subprocess.Popen(
                    command, shell=True, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"命令执行失败: {e}")
            return None
    campus_main.CampusRunShell.run_command = patched_run_command

    return campus_main.CampusRunShell

ShellClass = load_shell_class()          # 动态获得补丁后的类
shell = ShellClass()                     # 单例——复用同一条连接

##############################################################################
# 2. GUI 组件
##############################################################################
root = tk.Tk()
root.title("Campus-Real-Run GUI")

# 左侧按钮框
btn_frame = tk.Frame(root)
btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

# 中央输出框（滚动）
output = scrolledtext.ScrolledText(root, width=100, height=35, state=tk.DISABLED)
output.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=4, pady=4)

# 日志重定向到 GUI
class TextHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record) + "\n"
        output.configure(state=tk.NORMAL)
        output.insert(tk.END, msg)
        output.see(tk.END)
        output.configure(state=tk.DISABLED)
handler = TextHandler()
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

# 把 shell.onecmd 的 stdout/stderr 也写入 GUI
def execute_cmd(cmdline):
    """
    在后台线程里执行 shell.onecmd(cmdline)，
    把 sys.stdout / sys.stderr 以及 shell.stdout 同时重定向到 StringIO，
    完成后把捕获到的文本写进 GUI。
    """
    def _worker():
        buf = io.StringIO()
        # 1) 备份原来的 shell.stdout
        orig_shell_stdout = shell.stdout
        try:
            # 2) 同时重定向 sys.stdout / sys.stderr
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                # 3) 也把 shell.stdout 指向同一个缓冲区
                shell.stdout = buf
                shell.onecmd(cmdline)
        except Exception as e:
            logging.error(e)
        finally:
            # 4) 还原 shell.stdout，避免影响后续命令
            shell.stdout = orig_shell_stdout

        gui_print(buf.getvalue())

    threading.Thread(target=_worker, daemon=True).start()

def gui_print(text):
    if not text:
        return
    output.configure(state=tk.NORMAL)
    output.insert(tk.END, text)
    output.see(tk.END)
    output.configure(state=tk.DISABLED)

def open_help_panel():
    """
    弹出一个顶层窗口，列出常用命令按钮，点击按钮时调用
    execute_cmd(f"help {cmd}") 把具体帮助写到中央文本框
    """
    cmds = [
        "init", "start", "check_dev_mode_status", "enable_dev_mode",
        "cleanup", "status", "exit", "quit", "EOF", "help"
    ]

    panel = tk.Toplevel(root)
    panel.title("命令帮助 Command Help")
    panel.resizable(False, False)

    tk.Label(panel, text="点击按钮查看该命令的帮助：", pady=4)\
        .pack(fill=tk.X)

    for c in cmds:
        tk.Button(panel, text=c, width=28,
                  command=lambda cmd=c: execute_cmd(f"help {cmd}"))\
            .pack(padx=8, pady=2)


##############################################################################
# 3. 按钮回调
##############################################################################
def init_ios16():
    execute_cmd("init")

def init_ios17():
    execute_cmd("init --ios17")

def show_help():
    execute_cmd("help")      # 先输出总帮助
    open_help_panel()        # 然后弹出命令帮助面板

def enable_dev():
    execute_cmd("enable_dev_mode")

def check_dev():
    execute_cmd("check_dev_mode_status")

def start_gpx():
    gpx = filedialog.askopenfilename(
        title="选择 GPX 文件", filetypes=[("GPX files", "*.gpx")])
    if gpx:
        execute_cmd(f"start {gpx}")

def status():
    execute_cmd("status")

def cleanup():
    execute_cmd("cleanup")

def exit_app():
    cleanup()
    root.quit()

##############################################################################
# 4. 生成按钮
##############################################################################
btn_specs = [
    ("Init ≤ iOS16", init_ios16),
    ("Init ≥ iOS17", init_ios17),
    ("Help",          show_help),
    ("Enable Dev-Mode", enable_dev),
    ("Check Dev-Mode",  check_dev),
    ("Start GPX",      start_gpx),
    ("Status",         status),
    ("Clean Up",       cleanup),
    ("Exit",           exit_app),
]

for txt, fn in btn_specs:
    tk.Button(btn_frame, text=txt, width=18, command=fn)\
      .pack(fill=tk.X, pady=2)

##############################################################################
root.mainloop()
