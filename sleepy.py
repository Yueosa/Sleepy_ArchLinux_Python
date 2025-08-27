# coding: utf-8
"""
archlinux_kde_wayland_kdotool.py
使用 kdotool 获取 KDE Wayland 焦点窗口并发送到服务器
依赖: kdotool, requests
"""

import subprocess
from requests import post
from datetime import datetime
from time import sleep
import signal
from sys import exit
import os
from dotenv import load_dotenv


# --- config start ---
load_dotenv()
SERVER = os.getenv("SERVER")
SECRET = os.getenv("SECRET")
DEVICE_ID = 'VM-ArchLinux'
DEVICE_SHOW_NAME = 'ArchLinux'
CHECK_INTERVAL = 2
BYPASS_SAME_REQUEST = True
SKIPPED_NAMES = ['', 'plasmashell']
NOT_USING_NAMES = ['[FAILED]']
KDTOOL_PATH = './kdotool'  # 你的 kdotool 二进制路径
# --- config end ---

last_window = ''


def print_log(msg: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def get_active_window_title():
    """调用 kdotool 获取当前活动窗口名"""
    try:
        result = subprocess.run([KDTOOL_PATH, "getactivewindow", "getwindowname"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print_log(f"kdotool return code {result.returncode}")
            return '[FAILED]'
    except Exception as e:
        print_log(f"Error calling kdotool: {e}")
        return '[FAILED]'


def send_update(window):
    global last_window

    if BYPASS_SAME_REQUEST and window == last_window:
        print_log("Window not changed, bypass sending")
        return

    if window in SKIPPED_NAMES:
        print_log(f"Skipped window: {window}")
        return

    using = True
    if window in NOT_USING_NAMES:
        using = False
        print_log(f"Window not using: {window}")

    json_data = {
        'secret': SECRET,
        'id': DEVICE_ID,
        'show_name': DEVICE_SHOW_NAME,
        'using': using,
        'status': window
    }
    print_log(f"\033[34m发送数据: {json_data}\033[0m")

    url = f"{SERVER}/api/device/set"
    try:
        resp = post(url, json=json_data, headers={'Content-Type': 'application/json'})
        if resp.status_code == 401:
            print_log(f"\033[31m错误: 密钥验证失败 (401 Unauthorized)\033[0m")
            return
        elif resp.status_code != 200:
            print_log(f"\033[31m错误: 服务器返回 {resp.status_code}\033[0m")
            return
        print_log(f"POST {url} -> {resp.status_code} {resp.text}")
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print_log(f"\033[31m发送请求出错: {e}\033[0m")
        return

    last_window = window


def send_shutdown():
    """程序关闭时发送未在使用状态"""
    url = f"{SERVER}/api/device/set"
    try:
        resp = post(url, json={
            'secret': SECRET,
            'id': DEVICE_ID,
            'show_name': DEVICE_SHOW_NAME,
            'using': False,
            'status': 'Shutdown'
        }, headers={'Content-Type': 'application/json'})
        print_log(f"Shutdown POST {resp.status_code} {resp.text}")
    except Exception as e:
        print_log(f"Error sending shutdown POST: {e}")


def sigterm_handler(signum, frame):
    print_log("SIGTERM received")
    send_shutdown()
    exit(0)


def main():
    signal.signal(signal.SIGTERM, sigterm_handler)
    try:
        while True:
            window = get_active_window_title()
            print_log(f"Active window: {window}")
            send_update(window)
            sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print_log("\033[33m收到中断信号，正在关闭...\033[0m")
        try:
            send_shutdown()
        except:
            pass
        exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # 主循环中已经处理了 KeyboardInterrupt
        pass
    except Exception as e:
        print_log(f"\033[31m发生未预期的错误: {e}\033[0m")
        try:
            send_shutdown()
        except:
            pass
        exit(1)
