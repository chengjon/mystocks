"""
启动脚本
用于启动 MyStocks 程序
"""
import os
import sys

# 将当前目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入主程序
from main import main

if __name__ == "__main__":
    # 运行主程序
    main()