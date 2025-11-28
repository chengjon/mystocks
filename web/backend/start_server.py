#!/usr/bin/env python3
"""
启动 MyStocks Web 后端服务的脚本
自动设置 Python 路径并启动服务
"""

import os
import subprocess
import sys

# 设置项目根目录的Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 设置环境变量
os.environ["PYTHONPATH"] = project_root

# 启动命令
cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# 切换到后端目录
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

print(f"🚀 启动 MyStocks Web 后端服务...")
print(f"📁 项目根目录: {project_root}")
print(f"📁 后端目录: {backend_dir}")
print(f"🐍 Python路径已设置: {project_root}")

# 执行启动命令
subprocess.run(cmd)
