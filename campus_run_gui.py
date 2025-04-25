#!/usr/bin/env python3
# gui_campusrun.py

# Import required libraries
import importlib.util
import sys, os, subprocess, threading, io, contextlib, logging
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

##############################################################################
# 1. Load main.py dynamically and initialize CampusRunShell
##############################################################################
def load_shell_class():
    # Prompt the user to select the main.py file containing CampusRunShell class
    path = filedialog.askopenfilename(
        title="请选择包含 CampusRunShell 的 main.py 文件",
        filetypes=[("Python file", "*.py")])
    if not path:
        messagebox.showerror("未选择文件", "必须选择 main.py 才能继续")
        sys.exit(1)

    # Dynamically load the selected main.py file
    spec = importlib.util.spec_from_file_location("campus_main", path)
    campus_main = importlib.util.module_from_spec(spec)
    sys.modules["campus_main"] = campus_main
    spec.loader.exec_module(campus_main)

    # ---------------- Patch 1: Fix undefined 'route_loaded' ---------------- #
    # The original main.py didn't initialize 'route_loaded' in __init__,
    # causing AttributeError during 'do_status' or 'do_cleanup' calls.
    original_init = campus_main.CampusRunShell.__init__
    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.route_loaded = False
    campus_main.CampusRunShell.__init__ = patched_init

    # ---------------- Patch 2: Cross-platform run_command with output capture -------------- #
    # The original implementation used 'start cmd /k' on Windows, 
    # which was platform-dependent and couldn't capture the output.
    # Here, we replace it with a cross-platform solution.
    def patched_run_command(self, command, check_output=False):
        try:
            if check_output:
                return subprocess.check_output(
                    command, shell=True, text=True, stderr=subprocess.STDOUT)
            else:
                # Return Popen object to handle output in GUI later
                return subprocess.Popen(
                    command, shell=True, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"命令执行失败: {e}")
            return None
    campus_main.CampusRunShell.run_command = patched_run_command

    return campus_main.CampusRunShell

# Dynamically load and instantiate the patched CampusRunShell class
ShellClass = load_shell_class()
shell = ShellClass()  # Singleton instance for reusing the same connection

##############################################################################
# 2. GUI components setup
##############################################################################
root = tk.Tk()  # Main window
root.title("Campus-Real-Run GUI")

# Left-side button frame
btn_frame = tk.Frame(root)
btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

# Right-side scrollable output frame
output = scrolledtext.ScrolledText(root, width=100, height=35, state=tk.DISABLED)
output.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=4, pady=4)

# Redirect logs to GUI output
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

# Capture and display command execution output in the GUI
def execute_cmd(cmdline):
    """
    Executes shell.onecmd(cmdline) in a separate background thread,
    capturing both sys.stdout/sys.stderr and shell.stdout into a buffer.
    Once complete, the captured output is displayed in the GUI.
    """
    def _worker():
        buf = io.StringIO()
        # Backup the original shell.stdout
        orig_shell_stdout = shell.stdout
        try:
            # Redirect stdout and stderr to the buffer
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                # Also redirect shell.stdout to the same buffer
                shell.stdout = buf
                shell.onecmd(cmdline)
        except Exception as e:
            logging.error(e)
        finally:
            # Restore original shell.stdout
            shell.stdout = orig_shell_stdout

        gui_print(buf.getvalue())

    threading.Thread(target=_worker, daemon=True).start()

# Function to insert text into the GUI output box
def gui_print(text):
    if not text:
        return
    output.configure(state=tk.NORMAL)
    output.insert(tk.END, text)
    output.see(tk.END)
    output.configure(state=tk.DISABLED)

# Function to display the help panel with command buttons
def open_help_panel():
    """
    Opens a new window listing commonly used commands. Clicking a button 
    triggers execute_cmd(f"help {cmd}") to show specific help details.
    """
    cmds = [
        "init", "start", "check_dev_mode_status", "enable_dev_mode",
        "cleanup", "status", "exit", "quit", "EOF", "help"
    ]

    panel = tk.Toplevel(root)
    panel.title("命令帮助 Command Help")
    panel.resizable(False, False)

    tk.Label(panel, text="点击按钮查看该命令的帮助：", pady=4).pack(fill=tk.X)

    for c in cmds:
        tk.Button(panel, text=c, width=28,
                  command=lambda cmd=c: execute_cmd(f"help {cmd}")).pack(padx=8, pady=2)

##############################################################################
# 3. Button callback functions
##############################################################################
def init_ios16():
    execute_cmd("init")

def init_ios17():
    execute_cmd("init --ios17")

def show_help():
    execute_cmd("help")      # Show general help
    open_help_panel()        # Show specific command help panel

def enable_dev():
    execute_cmd("enable_dev_mode")

def check_dev():
    execute_cmd("check_dev_mode_status")

def start_gpx():
    # Allow user to select GPX file and start command with the selected file
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
# 4. Button creation
##############################################################################
# List of button labels and associated functions
btn_specs = [
    ("Init ≤ iOS16", init_ios16),
    ("Init ≥ iOS17", init_ios17),
    ("Help", show_help),
    ("Enable Dev-Mode", enable_dev),
    ("Check Dev-Mode", check_dev),
    ("Start GPX", start_gpx),
    ("Status", status),
    ("Clean Up", cleanup),
    ("Exit", exit_app),
]

# Generate buttons based on the button specs
for txt, fn in btn_specs:
    tk.Button(btn_frame, text=txt, width=18, command=fn).pack(fill=tk.X, pady=2)

# Start the main loop for the GUI
root.mainloop()
