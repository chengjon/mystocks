#!/usr/bin/env python3

import os
import sys

# 添加项目根目录到路径
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "temp"))

print(f"当前工作目录: {os.getcwd()}")
print(f"项目根目录: {project_root}")

try:
    from src.utils.tdx_server_config import TdxServerConfig

    print("\n=== 测试TDX服务器配置 ===")
    config = TdxServerConfig()
    print(f"服务器配置: {config}")
    print(f"主服务器: {config.get_primary_server()}")
    print(f"可用服务器数量: {config.get_server_count()}")

    print("\n=== 测试TDX适配器 ===")
    from src.adapters.tdx_adapter import TdxDataSource

    tdx = TdxDataSource()
    print("TDX适配器初始化成功")

    # 测试健康检查
    print("\n=== 测试连接健康状态 ===")
    # TDX适配器没有check_connection方法，我们测试基本功能
    print(f"TDX服务器: {tdx.tdx_host}:{tdx.tdx_port}")
    print(f"重试次数: {tdx.max_retries}")

    print("\n=== 测试ETF代码识别 ===")
    # 测试ETF代码510300的识别
    try:
        market = tdx._get_market_code("510300")
        print(f"ETF代码510300的市场代码: {market}")
    except Exception as e:
        print(f"ETF代码510300识别失败: {e}")

    print("\n=== 测试股票代码识别 ===")
    for code in ["600519", "000001", "300750"]:
        try:
            market = tdx._get_market_code(code)
            print(f"{code} -> 市场{market}")
        except Exception as e:
            print(f"{code} -> 错误: {e}")

except ImportError as e:
    print(f"导入错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
    import traceback

    traceback.print_exc()
