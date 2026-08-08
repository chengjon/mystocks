#!/usr/bin/env python3
"""
Phase 6 Validation Test: Market Data Context
Phase 6验证测试：市场数据上下文

验证Market Data Context的实现质量。
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def test_market_data_context_imports():
    """测试市场数据上下文导入"""
    print("\n" + "=" * 60)
    print("  测试1: Market Data Context模块导入")
    print("=" * 60)

    passed = 0
    failed = 0

    tests = [
        ("Bar value object", "from src.domain.market_data.value_objects.bar import Bar"),
        ("Tick value object", "from src.domain.market_data.value_objects.tick import Tick"),
        ("Quote value object", "from src.domain.market_data.value_objects.quote import Quote"),
        (
            "IMarketDataRepository interface",
            "from src.domain.market_data.repository.imarket_data_repository import IMarketDataRepository",
        ),
    ]

    for test_name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            failed += 1

    print(f"\n导入测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_bar_value_object():
    """测试Bar值对象"""
    print("\n" + "=" * 60)
    print("  测试2: Bar值对象")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.market_data.value_objects.bar import Bar

        # 测试K线数据创建
        bar = Bar(
            symbol="000001.SZ",
            timestamp=datetime.now(),
            open=10.50,
            high=10.80,
            low=10.40,
            close=10.70,
            volume=1000000,
            amount=10700000.0,
            period="daily",
        )

        print("✅ Bar创建成功")
        passed += 1

        # 测试属性
        assert bar.symbol == "000001.SZ"
        assert bar.open == 10.50
        assert bar.close == 10.70
        assert bar.volume == 1000000
        print("✅ Bar属性正确")
        passed += 1

        # 测试阴阳线判断
        assert bar.is_bullish  # 收盘价 > 开盘价
        print("✅ 阳线判断正确")
        passed += 1

        # 测试振幅计算
        range_pct = bar.range_pct
        assert range_pct > 0
        print(f"✅ 振幅计算正确: {range_pct:.2f}%")
        passed += 1

        # 测试涨跌幅
        change_pct = bar.change_pct
        assert change_pct > 0  # 阳线
        print(f"✅ 涨跌幅计算正确: {change_pct:.2f}%")
        passed += 1

        # 测试实体大小
        body_size = bar.body_size
        print(f"   实体大小实际值: {body_size:.10f}, 期望值: 0.20")
        assert abs(body_size - 0.20) < 0.001  # 使用近似比较避免浮点精度问题
        print(f"✅ 实体大小计算正确: {body_size:.2f}")
        passed += 1

        # 测试上下影线
        upper_shadow = bar.upper_shadow
        lower_shadow = bar.lower_shadow
        assert upper_shadow >= 0
        assert lower_shadow >= 0
        print(f"✅ 上下影线计算正确: 上={upper_shadow:.2f}, 下={lower_shadow:.2f}")
        passed += 1

    except Exception as e:
        print(f"❌ Bar测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\nBar测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_bar_validation():
    """测试Bar验证逻辑"""
    print("\n" + "=" * 60)
    print("  测试3: Bar验证逻辑")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.market_data.value_objects.bar import Bar

        # 测试价格必须为正数
        try:
            Bar(
                symbol="000001.SZ",
                timestamp=datetime.now(),
                open=-10.50,  # 负数
                high=10.80,
                low=10.40,
                close=10.70,
                volume=1000000,
            )
            print("❌ 负数开盘价验证失败（应该抛出异常）")
            failed += 1
        except ValueError:
            print("✅ 负数开盘价验证正确")
            passed += 1

        # 测试最高价 >= 最低价
        try:
            Bar(
                symbol="000001.SZ",
                timestamp=datetime.now(),
                open=10.50,
                high=10.40,  # 低于最低价
                low=10.80,
                close=10.70,
                volume=1000000,
            )
            print("❌ 价格关系验证失败（应该抛出异常）")
            failed += 1
        except ValueError:
            print("✅ 价格关系验证正确")
            passed += 1

        # 测试阴线
        bearish_bar = Bar(
            symbol="000001.SZ",
            timestamp=datetime.now(),
            open=10.70,
            high=10.80,
            low=10.40,
            close=10.50,  # 收盘价 < 开盘价
            volume=1000000,
        )
        assert bearish_bar.is_bearish
        assert not bearish_bar.is_bullish
        print("✅ 阴线识别正确")
        passed += 1

    except Exception as e:
        print(f"❌ Bar验证测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\nBar验证测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_tick_value_object():
    """测试Tick值对象"""
    print("\n" + "=" * 60)
    print("  测试4: Tick值对象")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.market_data.value_objects.tick import Tick

        # 测试分笔数据创建
        tick = Tick(
            symbol="000001.SZ",
            timestamp=datetime.now(),
            price=10.55,
            volume=1000,
            amount=10550.0,
            direction=1,  # 买入
        )

        print("✅ Tick创建成功")
        passed += 1

        # 测试属性
        assert tick.symbol == "000001.SZ"
        assert tick.price == 10.55
        assert tick.volume == 1000
        assert tick.is_buy
        assert not tick.is_sell
        print("✅ Tick属性和方向判断正确")
        passed += 1

        # 测试平均价格
        avg_price = tick.avg_price
        assert abs(avg_price - 10.55) < 0.01
        print(f"✅ 平均价格计算正确: {avg_price:.2f}")
        passed += 1

        # 测试卖出方向
        sell_tick = Tick(
            symbol="000001.SZ",
            timestamp=datetime.now(),
            price=10.55,
            volume=1000,
            amount=10550.0,
            direction=-1,  # 卖出
        )
        assert sell_tick.is_sell
        assert not sell_tick.is_buy
        print("✅ 卖出方向判断正确")
        passed += 1

    except Exception as e:
        print(f"❌ Tick测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\nTick测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_tick_validation():
    """测试Tick验证逻辑"""
    print("\n" + "=" * 60)
    print("  测试5: Tick验证逻辑")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.market_data.value_objects.tick import Tick

        # 测试价格必须为正数
        try:
            Tick(
                symbol="000001.SZ",
                timestamp=datetime.now(),
                price=-10.55,  # 负数
                volume=1000,
                amount=10550.0,
            )
            print("❌ 负数价格验证失败（应该抛出异常）")
            failed += 1
        except ValueError:
            print("✅ 负数价格验证正确")
            passed += 1

        # 测试方向必须在{-1, 0, 1}范围内
        try:
            Tick(
                symbol="000001.SZ",
                timestamp=datetime.now(),
                price=10.55,
                volume=1000,
                amount=10550.0,
                direction=2,  # 无效方向
            )
            print("❌ 无效方向验证失败（应该抛出异常）")
            failed += 1
        except ValueError:
            print("✅ 无效方向验证正确")
            passed += 1

        # 测试成交量必须为正数
        try:
            Tick(
                symbol="000001.SZ",
                timestamp=datetime.now(),
                price=10.55,
                volume=-1000,  # 负数
                amount=10550.0,
            )
            print("❌ 负数成交量验证失败（应该抛出异常）")
            failed += 1
        except ValueError:
            print("✅ 负数成交量验证正确")
            passed += 1

    except Exception as e:
        print(f"❌ Tick验证测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\nTick验证测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_quote_value_object():
    """测试Quote值对象"""
    print("\n" + "=" * 60)
    print("  测试6: Quote值对象")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.market_data.value_objects.quote import Quote

        # 测试实时报价创建
        quote = Quote(
            symbol="000001.SZ",
            timestamp=datetime.now(),
            last_price=10.75,
            bid_price=10.74,
            bid_volume=10000,
            ask_price=10.76,
            ask_volume=15000,
            open_price=10.50,
            high_price=10.80,
            low_price=10.40,
            volume=5000000,
            amount=53750000.0,
        )

        print("✅ Quote创建成功")
        passed += 1

        # 测试买卖价差
        spread = quote.spread
        print(f"   价差实际值: {spread:.10f}, 期望值: 0.02")
        assert abs(spread - 0.02) < 0.001  # 使用近似比较避免浮点精度问题
        print(f"✅ 买卖价差计算正确: {spread:.2f}")
        passed += 1

        # 测试价差百分比
        spread_pct = quote.spread_pct
        assert spread_pct > 0
        print(f"✅ 价差百分比计算正确: {spread_pct:.4f}%")
        passed += 1

        # 测试中间价
        mid_price = quote.mid_price
        assert mid_price == 10.75  # (10.74 + 10.76) / 2
        print(f"✅ 中间价计算正确: {mid_price:.2f}")
        passed += 1

        # 测试距开盘价变化
        change = quote.change_from_open
        assert change == 0.25  # 10.75 - 10.50
        print(f"✅ 距开盘价变化计算正确: {change:.2f}")
        passed += 1

        # 测试变化百分比
        change_pct = quote.change_pct_from_open
        assert change_pct > 0
        print(f"✅ 变化百分比计算正确: {change_pct:.2f}%")
        passed += 1

    except Exception as e:
        print(f"❌ Quote测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\nQuote测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_quote_validation():
    """测试Quote验证逻辑"""
    print("\n" + "=" * 60)
    print("  测试7: Quote验证逻辑")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.market_data.value_objects.quote import Quote

        # 测试买一价 <= 卖一价
        try:
            Quote(
                symbol="000001.SZ",
                timestamp=datetime.now(),
                last_price=10.75,
                bid_price=10.76,  # 买一价高于卖一价
                ask_price=10.74,
            )
            print("❌ 买卖价差关系验证失败（应该抛出异常）")
            failed += 1
        except ValueError:
            print("✅ 买卖价差关系验证正确")
            passed += 1

        # 测试最新价必须为正数
        try:
            Quote(
                symbol="000001.SZ",
                timestamp=datetime.now(),
                last_price=-10.75,  # 负数
            )
            print("❌ 负数最新价验证失败（应该抛出异常）")
            failed += 1
        except ValueError:
            print("✅ 负数最新价验证正确")
            passed += 1

        # 测试仅有最新价的Quote
        minimal_quote = Quote(
            symbol="000001.SZ",
            timestamp=datetime.now(),
            last_price=10.75,
        )
        assert minimal_quote.last_price == 10.75
        assert minimal_quote.spread is None  # 没有买卖价
        print("✅ 最小Quote创建成功")
        passed += 1

    except Exception as e:
        print(f"❌ Quote验证测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\nQuote验证测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_repository_interface():
    """测试仓储接口定义"""
    print("\n" + "=" * 60)
    print("  测试8: IMarketDataRepository仓储接口")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.market_data.repository.imarket_data_repository import IMarketDataRepository

        # 检查K线数据方法
        bar_methods = ["get_bars", "get_latest_bar", "save_bars", "has_bars"]

        for method in bar_methods:
            if hasattr(IMarketDataRepository, method):
                print(f"✅ IMarketDataRepository.{method}() 存在")
                passed += 1
            else:
                print(f"❌ IMarketDataRepository.{method}() 缺失")
                failed += 1

        # 检查分笔数据方法
        tick_methods = ["get_ticks", "save_ticks", "has_ticks"]

        for method in tick_methods:
            if hasattr(IMarketDataRepository, method):
                print(f"✅ IMarketDataRepository.{method}() 存在")
                passed += 1
            else:
                print(f"❌ IMarketDataRepository.{method}() 缺失")
                failed += 1

        # 检查实时报价方法
        quote_methods = ["get_quote", "get_quotes", "save_quote"]

        for method in quote_methods:
            if hasattr(IMarketDataRepository, method):
                print(f"✅ IMarketDataRepository.{method}() 存在")
                passed += 1
            else:
                print(f"❌ IMarketDataRepository.{method}() 缺失")
                failed += 1

    except Exception as e:
        print(f"❌ 仓储接口测试失败: {e}")
        failed += 1

    print(f"\n仓储接口测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  Phase 6验证测试: Market Data Context")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    total_passed = 0
    total_failed = 0

    # 运行所有测试
    p, f = test_market_data_context_imports()
    total_passed += p
    total_failed += f

    p, f = test_bar_value_object()
    total_passed += p
    total_failed += f

    p, f = test_bar_validation()
    total_passed += p
    total_failed += f

    p, f = test_tick_value_object()
    total_passed += p
    total_failed += f

    p, f = test_tick_validation()
    total_passed += p
    total_failed += f

    p, f = test_quote_value_object()
    total_passed += p
    total_failed += f

    p, f = test_quote_validation()
    total_passed += p
    total_failed += f

    p, f = test_repository_interface()
    total_passed += p
    total_failed += f

    # 总结
    print("\n" + "=" * 60)
    print("  测试总结")
    print("=" * 60)
    print(f"总通过: {total_passed}")
    print(f"总失败: {total_failed}")
    print(f"成功率: {total_passed/(total_passed+total_failed)*100:.1f}%")

    if total_failed == 0:
        print("\n🎉 Phase 6验证测试全部通过！Market Data Context实施正确。")
        return 0
    else:
        print(f"\n⚠️  有{total_failed}项测试失败，请检查上述错误。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
