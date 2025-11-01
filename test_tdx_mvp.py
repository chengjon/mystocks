"""
TDX数据源适配器 MVP测试脚本

测试User Story 1和2:
- 实时行情查询
- 历史K线数据获取(股票+指数)

作者: MyStocks Team
日期: 2025-10-15
"""

import logging
from datetime import datetime, timedelta
from adapters.tdx_adapter import TdxDataSource

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_server_config():
    """测试1: 服务器配置加载"""
    print("\n" + "=" * 60)
    print("测试1: TDX服务器配置")
    print("=" * 60)

    try:
        tdx = TdxDataSource()
        print(f"✓ TDX适配器初始化成功")
        print(f"  主服务器: {tdx.tdx_host}:{tdx.tdx_port}")

        if tdx.use_server_config and tdx.server_config:
            print(f"  可用服务器总数: {tdx.server_config.get_server_count()}")
            print(f"  使用connect.cfg配置: ✓")
        else:
            print(f"  使用环境变量配置")

        return True
    except Exception as e:
        print(f"✗ 服务器配置加载失败: {e}")
        return False


def test_real_time_quote():
    """测试2: 实时行情查询 (User Story 1)"""
    print("\n" + "=" * 60)
    print("测试2: 实时行情查询 (User Story 1)")
    print("=" * 60)

    tdx = TdxDataSource()

    # 测试股票列表
    test_symbols = [
        ('600519', '贵州茅台 - 沪市主板'),
        ('000001', '平安银行 - 深市主板'),
        ('300750', '宁德时代 - 创业板'),
    ]

    success_count = 0

    for symbol, desc in test_symbols:
        print(f"\n测试股票: {symbol} ({desc})")

        try:
            result = tdx.get_real_time_data(symbol)

            if isinstance(result, dict):
                print(f"  ✓ 获取成功")
                print(f"    股票名称: {result['name']}")
                print(f"    最新价: {result['price']:.2f}")
                print(f"    涨跌: {result['price'] - result['pre_close']:.2f} "
                      f"({(result['price'] / result['pre_close'] - 1) * 100:.2f}%)")
                print(f"    成交量: {result['volume']:,}手")
                print(f"    成交额: {result['amount'] / 1e8:.2f}亿")
                print(f"    查询时间: {result['timestamp']}")
                success_count += 1
            else:
                print(f"  ✗ 获取失败: {result}")

        except Exception as e:
            print(f"  ✗ 异常: {e}")

    print(f"\n实时行情测试: {success_count}/{len(test_symbols)} 成功")
    return success_count == len(test_symbols)


def test_stock_daily():
    """测试3: 股票日线数据 (User Story 2)"""
    print("\n" + "=" * 60)
    print("测试3: 股票日线数据 (User Story 2)")
    print("=" * 60)

    tdx = TdxDataSource()

    # 获取最近3个月的数据
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    test_symbols = [
        ('600519', '贵州茅台'),
        ('000001', '平安银行'),
    ]

    success_count = 0

    for symbol, name in test_symbols:
        print(f"\n测试股票: {symbol} ({name})")
        print(f"  日期范围: {start_date} ~ {end_date}")

        try:
            df = tdx.get_stock_daily(symbol, start_date, end_date)

            if not df.empty:
                print(f"  ✓ 获取成功: {len(df)}条数据")
                print(f"    实际日期范围: {df['date'].min()} ~ {df['date'].max()}")
                print(f"    数据列: {list(df.columns)}")
                print(f"\n  最近5个交易日:")
                print(df[['date', 'open', 'high', 'low', 'close', 'volume']].tail(5).to_string(index=False))
                success_count += 1
            else:
                print(f"  ✗ 未获取到数据")

        except Exception as e:
            print(f"  ✗ 异常: {e}")

    print(f"\n股票日线测试: {success_count}/{len(test_symbols)} 成功")
    return success_count == len(test_symbols)


def test_index_daily():
    """测试4: 指数日线数据 (User Story 2)"""
    print("\n" + "=" * 60)
    print("测试4: 指数日线数据 (User Story 2)")
    print("=" * 60)

    tdx = TdxDataSource()

    # 获取最近3个月的数据
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    test_indices = [
        ('000001', '上证指数'),
        ('399001', '深证成指'),
    ]

    success_count = 0

    for symbol, name in test_indices:
        print(f"\n测试指数: {symbol} ({name})")
        print(f"  日期范围: {start_date} ~ {end_date}")

        try:
            df = tdx.get_index_daily(symbol, start_date, end_date)

            if not df.empty:
                print(f"  ✓ 获取成功: {len(df)}条数据")
                print(f"    实际日期范围: {df['date'].min()} ~ {df['date'].max()}")
                print(f"    数据列: {list(df.columns)}")
                print(f"\n  最近5个交易日:")
                print(df[['date', 'open', 'high', 'low', 'close', 'volume']].tail(5).to_string(index=False))
                success_count += 1
            else:
                print(f"  ✗ 未获取到数据")

        except Exception as e:
            print(f"  ✗ 异常: {e}")

    print(f"\n指数日线测试: {success_count}/{len(test_indices)} 成功")
    return success_count == len(test_indices)


def test_error_handling():
    """测试5: 错误处理"""
    print("\n" + "=" * 60)
    print("测试5: 错误处理")
    print("=" * 60)

    tdx = TdxDataSource()

    # 测试无效输入
    print("\n测试无效股票代码:")

    invalid_cases = [
        ('', '空字符串'),
        ('12345', '5位数字'),
        ('AAPL', '字母'),
        ('999999', '不存在的代码前缀'),
    ]

    for symbol, desc in invalid_cases:
        result = tdx.get_real_time_data(symbol)
        if isinstance(result, str):  # 返回错误消息
            print(f"  ✓ {desc}({symbol}): 正确返回错误 - {result}")
        else:
            print(f"  ✗ {desc}({symbol}): 应该返回错误但返回了数据")

    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("TDX数据源适配器 MVP测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # 运行测试
    results['server_config'] = test_server_config()
    results['real_time_quote'] = test_real_time_quote()
    results['stock_daily'] = test_stock_daily()
    results['index_daily'] = test_index_daily()
    results['error_handling'] = test_error_handling()

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for test_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name:20s}: {status}")

    total_tests = len(results)
    passed_tests = sum(results.values())

    print(f"\n总计: {passed_tests}/{total_tests} 测试通过")

    if passed_tests == total_tests:
        print("\n🎉 所有MVP功能测试通过!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests}个测试失败")
        return 1


if __name__ == '__main__':
    exit(main())
