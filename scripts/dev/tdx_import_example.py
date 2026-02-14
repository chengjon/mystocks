"""
TDX数据导入完整示例 (TDX Data Import Complete Example)

功能说明:
- 演示如何从通达信本地文件导入数据到MyStocks数据库
- 展示数据自动路由到正确的数据库（TDengine）
- 增量导入和全量导入示例

使用场景:
1. 初次搭建系统，全量导入历史数据
2. 每日定时任务，增量导入最新数据
3. 特定股票池数据导入

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from src.data_sources.tdx_binary_parser import TdxBinaryParser
from src.data_sources.tdx_importer import TdxImporter


def example_1_check_tdx_data():
    """示例1: 检查TDX本地数据状态"""
    print("\n" + "=" * 80)
    print("示例1: 检查TDX本地数据状态")
    print("=" * 80)

    parser = TdxBinaryParser()

    # 1.1 检查数据路径
    print(f"\nTDX数据路径: {parser.data_path}")
    print(f"路径是否存在: {os.path.exists(parser.data_path)}")

    # 1.2 列出可用市场
    print("\n可用市场:")
    for market in ["sh", "sz"]:
        stocks = parser.list_available_stocks(market)
        print(f"  - {market.upper()}: {len(stocks)} 只股票")

    # 1.3 检查示例股票数据
    print("\n检查示例股票数据:")
    test_symbols = ["sh000001", "sh600000", "sz000001", "sz000002"]

    for symbol in test_symbols:
        latest_date = parser.get_latest_date(symbol)
        if latest_date:
            print(f"  ✓ {symbol}: 最新数据 {latest_date}")
        else:
            print(f"  ✗ {symbol}: 无数据")

    # 1.4 读取示例数据
    print("\n读取 sh000001 (上证指数) 最近5天数据:")
    data = parser.read_day_data("sh000001", start_date=date.today() - timedelta(days=7))

    if not data.empty:
        print(data.tail())
    else:
        print("  ✗ 未读取到数据")


def example_2_parse_local_data():
    """示例2: 解析本地数据（不保存到数据库）"""
    print("\n" + "=" * 80)
    print("示例2: 解析本地数据")
    print("=" * 80)

    parser = TdxBinaryParser()

    # 2.1 读取单只股票日线数据
    print("\n读取 sh600000 (浦发银行) 2024年数据:")
    data = parser.read_day_data("sh600000", start_date=date(2024, 1, 1))

    if not data.empty:
        print(f"  ✓ 总记录数: {len(data)}")
        print(f"  ✓ 日期范围: {data['date'].min()} 至 {data['date'].max()}")
        print("\n  最近数据:")
        print(data[["date", "close", "volume"]].tail())

    # 2.2 读取多只股票
    print("\n读取多只股票最新数据:")
    symbols = ["sh600000", "sh600016", "sh600036", "sh600050"]

    summary = []
    for symbol in symbols:
        data = parser.read_day_data(symbol, start_date=date.today() - timedelta(days=1))
        if not data.empty:
            latest = data.iloc[-1]
            summary.append(
                {
                    "symbol": symbol,
                    "date": latest["date"],
                    "close": latest["close"],
                    "volume": latest["volume"],
                }
            )

    if summary:
        import pandas as pd

        df = pd.DataFrame(summary)
        print(df.to_string(index=False))


def example_3_import_without_database():
    """示例3: 模拟导入（不连接数据库）"""
    print("\n" + "=" * 80)
    print("示例3: 模拟导入（不连接数据库）")
    print("=" * 80)

    importer = TdxImporter(unified_manager=None)

    # 3.1 检查导入进度
    print("\n检查上海市场数据状态:")
    progress = importer.get_import_progress("sh")
    print(f"  总股票数: {progress['total_symbols']}")
    print(f"  有数据股票数（估算）: {progress['imported_symbols']}")

    # 3.2 模拟小批量导入
    print("\n模拟导入前20只股票的最近7天数据:")
    test_symbols = importer.parser.list_available_stocks("sh")[:20]

    result = importer.import_market_daily(
        market="sh",
        start_date=date.today() - timedelta(days=7),
        end_date=date.today(),
        symbols=test_symbols,
        batch_size=10,
    )

    print("\n导入结果:")
    print(f"  成功: {result['success_count']}/{result['total_symbols']}")
    print(f"  失败: {result['fail_count']}")
    print(f"  总记录数: {result['total_records']:,}")


def example_4_import_to_database():
    """示例4: 导入到数据库（需要UnifiedDataManager）"""
    print("\n" + "=" * 80)
    print("示例4: 导入到数据库")
    print("=" * 80)

    print("\n注意: 此示例需要配置MyStocks数据库连接")
    print("请确保已正确配置 .env 文件中的数据库连接信息\n")

    # 检查是否可以导入UnifiedDataManager
    try:
        from unified_manager import MyStocksUnifiedManager as UM

        print("✓ MyStocksUnifiedManager 可用")

        # 创建管理器实例
        print("\n初始化数据管理器...")
        manager = MyStocksUnifiedManager()

        # 创建导入器
        importer = TdxImporter(unified_manager=manager)

        # 导入前5只股票的最近1天数据（测试）
        print("\n导入测试数据（前5只股票，最近1天）:")
        test_symbols = importer.parser.list_available_stocks("sh")[:5]

        result = importer.import_market_daily(
            market="sh",
            start_date=date.today() - timedelta(days=1),
            end_date=date.today(),
            symbols=test_symbols,
            batch_size=5,
        )

        print("\n✓ 数据已保存到TDengine数据库")
        print(f"  成功导入: {result['success_count']} 只股票")
        print(f"  总记录数: {result['total_records']}")

    except ImportError as e:
        print(f"✗ 无法导入 MyStocksUnifiedManager: {e}")
        print("\n如需导入到数据库，请确保:")
        print("  1. 已配置 .env 文件")
        print("  2. 数据库服务正在运行")
        print("  3. MyStocksUnifiedManager 可用")

    except Exception as e:
        print(f"✗ 导入失败: {e}")
        print("\n可能的原因:")
        print("  1. 数据库连接失败")
        print("  2. 表结构不存在")
        print("  3. 权限不足")


def example_5_incremental_import():
    """示例5: 增量导入（每日更新场景）"""
    print("\n" + "=" * 80)
    print("示例5: 增量导入模拟")
    print("=" * 80)

    print("\n增量导入适用场景:")
    print("  - 每日定时任务更新最新数据")
    print("  - 只导入最近N天的数据")
    print("  - 减少导入时间和数据库压力\n")

    importer = TdxImporter(unified_manager=None)

    # 模拟增量导入（最近7天）
    print("模拟增量导入（最近7天，前10只股票）:")
    result = importer.import_incremental(market="sh", lookback_days=7)

    print("\n增量导入完成:")
    print(f"  时间范围: {date.today() - timedelta(days=7)} 至 {date.today()}")
    print(f"  处理股票: {result['total_symbols']}")
    print(f"  成功导入: {result['success_count']}")


def main():
    """主函数 - 运行所有示例"""
    print("=" * 80)
    print("TDX数据导入完整示例")
    print("=" * 80)

    # 运行各个示例
    example_1_check_tdx_data()
    example_2_parse_local_data()
    example_3_import_without_database()

    # 示例4和5需要数据库连接，默认不运行
    # 如需运行，取消下面的注释:
    # example_4_import_to_database()
    # example_5_incremental_import()

    print("\n" + "=" * 80)
    print("所有示例运行完成")
    print("=" * 80)

    print("\n提示:")
    print("  - 示例1-3: 不需要数据库连接，可直接运行")
    print("  - 示例4-5: 需要配置数据库连接")
    print("\n  要启用数据库导入，请在代码中取消注释 example_4 和 example_5")


if __name__ == "__main__":
    main()
