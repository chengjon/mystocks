"""
TDX多周期K线功能测试

测试新增功能:
- 分钟K线 (1m, 5m, 15m, 30m)
- 小时K线 (1h)
- 日线 (1d) - 使用新的通用接口

作者: MyStocks Team
日期: 2025-10-15
"""

import logging
from datetime import datetime, timedelta
from adapters.tdx_adapter import TdxDataSource

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_multiperiod_klines():
    """测试多周期K线获取"""
    print("\n" + "=" * 70)
    print("TDX多周期K线功能测试")
    print("=" * 70)

    tdx = TdxDataSource()

    # 测试日期范围(最近2天)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')

    print(f"\n测试日期范围: {start_date} ~ {end_date}")
    print(f"测试股票: 600519 (贵州茅台)\n")

    # 测试各种周期
    test_periods = [
        ('5m',  '5分钟'),
        ('15m', '15分钟'),
        ('30m', '30分钟'),
        ('1h',  '1小时'),
        ('1d',  '日线'),
    ]

    results = {}

    for period, desc in test_periods:
        print(f"\n{'='*70}")
        print(f"测试 {desc} K线 (period={period})")
        print('='*70)

        try:
            df = tdx.get_stock_kline('600519', start_date, end_date, period=period)

            if not df.empty:
                print(f"✓ 获取成功: {len(df)}条数据")
                print(f"  时间范围: {df['date'].min()} ~ {df['date'].max()}")
                print(f"  数据列: {list(df.columns)}")

                # 显示最近5条数据
                if len(df) >= 5:
                    print(f"\n  最近5条数据:")
                    display_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
                    available_cols = [col for col in display_cols if col in df.columns]
                    print(df[available_cols].tail(5).to_string(index=False))
                else:
                    print(f"\n  所有数据:")
                    display_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
                    available_cols = [col for col in display_cols if col in df.columns]
                    print(df[available_cols].to_string(index=False))

                results[period] = 'PASS'
            else:
                print(f"✗ 未获取到数据")
                results[period] = 'FAIL'

        except Exception as e:
            print(f"✗ 异常: {e}")
            results[period] = 'ERROR'

    # 汇总结果
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)

    for period, desc in test_periods:
        status = results.get(period, 'UNKNOWN')
        status_icon = "✓" if status == 'PASS' else "✗"
        print(f"{status_icon} {desc:10s} (period={period:4s}): {status}")

    passed = sum(1 for v in results.values() if v == 'PASS')
    total = len(test_periods)

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有多周期K线测试通过!")
        return 0
    else:
        print(f"\n⚠️  {total - passed}个测试失败/出错")
        return 1


def test_index_multiperiod():
    """测试指数多周期K线"""
    print("\n" + "=" * 70)
    print("指数多周期K线测试")
    print("=" * 70)

    tdx = TdxDataSource()

    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')

    print(f"\n测试指数: 000001 (上证指数)")
    print(f"测试周期: 1小时K线\n")

    df = tdx.get_index_kline('000001', start_date, end_date, period='1h')

    if not df.empty:
        print(f"✓ 获取成功: {len(df)}条数据")
        print(f"  时间范围: {df['date'].min()} ~ {df['date'].max()}")

        if len(df) > 0:
            print(f"\n  最近3条数据:")
            display_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
            available_cols = [col for col in display_cols if col in df.columns]
            print(df[available_cols].tail(3).to_string(index=False))

        return True
    else:
        print("✗ 未获取到数据")
        return False


if __name__ == '__main__':
    # 测试股票多周期K线
    stock_result = test_multiperiod_klines()

    # 测试指数多周期K线
    print("\n")
    index_result = test_index_multiperiod()

    print("\n" + "=" * 70)
    if stock_result == 0 and index_result:
        print("✅ 所有测试完成")
        exit(0)
    else:
        print("⚠️  部分测试失败")
        exit(1)
