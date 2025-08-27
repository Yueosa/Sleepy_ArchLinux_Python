# Sleepy_ArchLinux_Python

这是一个用于 **KDE Wayland 环境** 的窗口状态采集工具，基于 [kdotool](https://github.com/jinliu/kdotool) 实现（类似于 xdotool，但支持 Wayland），用于将当前窗口信息发送到 [Sleepy](https://github.com/Yueosa/sleepy) 服务端。

---

## 功能

- 获取当前活动窗口标题  
- 支持排除指定窗口  
- 自动发送窗口状态到 Sleepy 服务端  
- 可配置虚拟环境与 systemd 自启动  

---

## 环境准备

1. 下载依赖工具
   你需要下载 [kdotool](https://github.com/jinliu/kdotool) ，并将可执行文件路径配置到脚本中：

   ```python
   KDTOOL_PATH = './kdotool'  # 替换成你的 kdotool 二进制路径
   ```

2. 创建 Python 虚拟环境  
   ```bash
   python -m venv Sleepy
   source Sleepy/bin/activate
   pip install -r requirements.txt
   ```

3. 配置 `.env` 文件  
   在脚本同目录下创建 `.env` 文件，内容示例：
   ```dotenv
   SERVER=你的Server
   SECRET=你的Secret
   ```

---

## 使用方法

激活虚拟环境后运行：
```bash
python archlinux_kde_wayland_kdotool.py
```

脚本会每隔几秒检测活动窗口，并将状态发送到 Sleepy 服务端。

---

## 推荐：创建 systemd 用户服务

1. 创建 systemd 服务文件 `~/.config/systemd/user/sleepy.service`：

```ini
[Unit]
Description=Sleepy Python Client
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/Lian/Sakura/sleepy_python # 替换为你的工作目录
ExecStart=/home/Lian/Sakura/sleepy_python/Sleepy/bin/python /home/Lian/Sakura/sleepy_python/sleepy.py # Python Venv路径和py脚本路径
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target

```

2. 启用并启动服务：
```bash
systemctl --user daemon-reload
systemctl --user enable sleepy.service
systemctl --user start sleepy.service
```

这样脚本就会随用户登录自动启动，并持续发送窗口状态。

---
