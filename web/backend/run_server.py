#!/usr/bin/env python
"""
简单的服务器启动脚本
"""

import sys
import os

# 添加根目录到 Python 路径
sys.path.append("/opt/claude/mystocks_spec")
# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Python 路径:", sys.path)
print("当前目录:", os.getcwd())
print("模块查找路径:")
for path in sys.path:
    print(f"  - {path}")

# 尝试导入模块
try:
    print("\n尝试导入 app.main...")
    from app.main import app

    print("成功导入 app.main!")
except Exception as e:
    print(f"导入 app.main 失败: {e}")
    print(f"错误类型: {type(e).__name__}")
    import traceback

    traceback.print_exc()

# 只有在导入成功时才启动服务器
try:
    print("\n启动服务器...")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")  # 使用8000端口，根据API文档规范
except Exception as e:
    print(f"启动服务器失败: {e}")
    import traceback

    traceback.print_exc()
