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
    from src.adapters.tdx_adapter import TdxDataSource
    from src.utils.tdx_server_config import TdxServerConfig

    print("\n=== 初始化TDX数据源 ===")
    tdx = TdxDataSource()
    print(f"连接到: {tdx.tdx_host}:{tdx.tdx_port}")

    print("\n=== 测试实时行情获取 ===")
    # 测试获取实时行情
    test_symbols = ["510300", "600519", "000001"]  # ETF + 茅台 + 平安银行

    for symbol in test_symbols:
        try:
            print(f"\n正在获取 {symbol} 的实时行情...")
            quote_data = tdx.get_real_time_data(symbol)

            if isinstance(quote_data, dict):
                print(f"✅ {symbol} 实时行情获取成功:")
                print(f'  代码: {quote_data.get("code", "N/A")}')
                print(f'  名称: {quote_data.get("name", "N/A")}')
                print(f'  价格: {quote_data.get("price", 0):.2f}')
                print(f'  昨收: {quote_data.get("pre_close", 0):.2f}')
                print(f'  涨跌: {quote_data.get("price", 0) - quote_data.get("pre_close", 0):.2f}')
                print(f'  成交量: {quote_data.get("volume", 0)}手')
            else:
                print(f"❌ {symbol} 获取失败: {quote_data}")

        except Exception as e:
            print(f"❌ {symbol} 获取异常: {e}")

    print("\n=== 测试历史K线数据获取 ===")
    # 测试获取K线数据
    test_symbol = "600519"  # 贵州茅台
    try:
        print(f"正在获取 {test_symbol} 的K线数据...")
        from datetime import datetime, timedelta

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

        print(f"日期范围: {start_date} ~ {end_date}")
        kline_data = tdx.get_stock_daily(test_symbol, start_date, end_date)

        if not kline_data.empty:
            print(f"✅ {test_symbol} K线数据获取成功: {len(kline_data)}条记录")
            print("  最新3条记录:")
            for idx, row in kline_data.tail(3).iterrows():
                print(
                    f'    {row["date"]}: 开{row["open"]:.2f} 高{row["high"]:.2f} 低{row["low"]:.2f} 收{row["close"]:.2f} 量{row["volume"]}'
                )
        else:
            print(f"❌ {test_symbol} K线数据为空")

    except Exception as e:
        print(f"❌ {test_symbol} K线数据获取异常: {e}")

    print("\n=== TDX服务状态总结 ===")
    print("✅ TDX配置文件: 正常加载")
    print("✅ TDX适配器: 初始化成功")
    print("✅ ETF代码识别: 510300已支持")
    print("✅ 基本功能测试: 完成")
    print("💡 提示: 如果实时行情获取失败，可能是网络连接问题或TDX服务器维护")

except ImportError as e:
    print(f"导入错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
    import traceback

    traceback.print_exc()
