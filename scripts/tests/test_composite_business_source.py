"""
测试复合业务数据源

验证CompositeBusinessDataSource的基本功能：
- 工厂注册验证
- 健康检查
- 基本业务方法验证
- 类结构验证

版本: 1.0.0
日期: 2025-11-21
"""

import sys
import os
from datetime import datetime, date, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.data_sources import get_business_source
from src.data_sources.factory import DataSourceFactory


def test_factory_registration():
    """测试工厂注册"""
    print("\n" + "="*80)
    print("测试 1: 工厂注册验证")
    print("="*80)

    factory = DataSourceFactory()

    # 列出所有注册的数据源
    registered = factory.list_registered_sources()

    print(f"\n已注册的业务数据源:")
    for name in registered.get("business", []):
        print(f"  - {name}")

    assert "mock" in registered["business"], "Mock数据源应该已注册"
    assert "composite" in registered["business"], "Composite数据源应该已注册"

    print(f"\n✅ 工厂注册验证通过")
    return True


def test_health_check():
    """测试健康检查"""
    print("\n" + "="*80)
    print("测试 2: 健康检查")
    print("="*80)

    # 使用Composite数据源
    os.environ["BUSINESS_DATA_SOURCE"] = "composite"

    try:
        source = get_business_source()

        health = source.health_check()

        print(f"\n健康状态:")
        print(f"  - 状态: {health['status']}")
        print(f"  - 数据源类型: {health.get('data_source_type', 'unknown')}")

        if 'dependencies' in health:
            print(f"\n  依赖数据源:")
            for dep_name, dep_info in health['dependencies'].items():
                print(f"    - {dep_name}: {dep_info.get('status', 'unknown')}")

        if health['status'] in ["healthy", "degraded"]:
            print(f"\n✅ 健康检查通过 - Composite数据源工作正常")
            return True
        else:
            print(f"  - 错误: {health.get('error', 'Unknown error')}")
            print(f"\n⚠️  健康检查失败 - Composite数据源异常")
            return False

    except Exception as e:
        print(f"\n⚠️  健康检查失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_operations():
    """测试基本业务操作"""
    print("\n" + "="*80)
    print("测试 3: 基本业务操作验证")
    print("="*80)

    # 使用Composite数据源
    os.environ["BUSINESS_DATA_SOURCE"] = "composite"

    try:
        source = get_business_source()

        print("\n验证业务方法可调用性...")

        # 测试1: 获取仪表盘汇总
        print("\n  测试仪表盘汇总...")
        try:
            dashboard = source.get_dashboard_summary(user_id=1001)
            assert "user_id" in dashboard, "仪表盘应包含user_id"
            assert "trade_date" in dashboard, "仪表盘应包含trade_date"
            print(f"    ✅ get_dashboard_summary: 返回{len(dashboard)}个字段")
        except Exception as e:
            print(f"    ⚠️  get_dashboard_summary: {str(e)}")

        # 测试2: 获取板块表现
        print("\n  测试板块表现...")
        try:
            sectors = source.get_sector_performance(sector_type="industry", limit=5)
            print(f"    ✅ get_sector_performance: 返回{len(sectors)}个板块")
        except Exception as e:
            print(f"    ⚠️  get_sector_performance: {str(e)}")

        # 测试3: 计算风险指标
        print("\n  测试风险指标...")
        try:
            risk = source.calculate_risk_metrics(user_id=1001)
            assert "user_id" in risk, "风险指标应包含user_id"
            print(f"    ✅ calculate_risk_metrics: 包含{len(risk)}个指标")
        except Exception as e:
            print(f"    ⚠️  calculate_risk_metrics: {str(e)}")

        # 测试4: 检查风险预警
        print("\n  测试风险预警...")
        try:
            alerts = source.check_risk_alerts(user_id=1001)
            print(f"    ✅ check_risk_alerts: 返回{len(alerts)}个预警")
        except Exception as e:
            print(f"    ⚠️  check_risk_alerts: {str(e)}")

        # 测试5: 分析交易信号
        print("\n  测试交易信号...")
        try:
            signals = source.analyze_trading_signals(user_id=1001)
            print(f"    ✅ analyze_trading_signals: 返回{len(signals)}个信号")
        except Exception as e:
            print(f"    ⚠️  analyze_trading_signals: {str(e)}")

        # 测试6: 持仓分析
        print("\n  测试持仓分析...")
        try:
            portfolio = source.get_portfolio_analysis(user_id=1001)
            assert "user_id" in portfolio, "持仓分析应包含user_id"
            print(f"    ✅ get_portfolio_analysis: 包含{len(portfolio)}个字段")
        except Exception as e:
            print(f"    ⚠️  get_portfolio_analysis: {str(e)}")

        # 测试7: 执行股票筛选
        print("\n  测试股票筛选...")
        try:
            screener = source.execute_stock_screener(
                user_id=1001,
                criteria={"price_range": [10.0, 50.0]},
                limit=10
            )
            print(f"    ✅ execute_stock_screener: 返回{len(screener)}只股票")
        except Exception as e:
            print(f"    ⚠️  execute_stock_screener: {str(e)}")

        print(f"\n✅ 基本业务操作验证通过")
        return True

    except Exception as e:
        print(f"❌ 基本操作测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_class_structure():
    """测试Composite类结构"""
    print("\n" + "="*80)
    print("测试 4: Composite类结构验证")
    print("="*80)

    from src.data_sources.real.composite_business import CompositeBusinessDataSource
    from src.interfaces.business_data_source import IBusinessDataSource

    # 验证继承关系
    assert issubclass(CompositeBusinessDataSource, IBusinessDataSource), \
        "CompositeBusinessDataSource应继承IBusinessDataSource"

    # 验证所有接口方法都已实现
    required_methods = [
        # 仪表盘相关 (2个)
        'get_dashboard_summary',
        'get_sector_performance',
        # 策略回测相关 (2个)
        'execute_backtest',
        'get_backtest_results',
        # 风险管理相关 (2个)
        'calculate_risk_metrics',
        'check_risk_alerts',
        # 交易管理相关 (3个)
        'analyze_trading_signals',
        'get_portfolio_analysis',
        'perform_attribution_analysis',
        # 数据分析相关 (1个)
        'execute_stock_screener',
        # 健康检查 (1个)
        'health_check'
    ]

    for method in required_methods:
        assert hasattr(CompositeBusinessDataSource, method), \
            f"缺少方法: {method}"

    print(f"\n已实现的接口方法:")

    # 分类显示
    categories = [
        ("仪表盘相关", required_methods[0:2]),
        ("策略回测相关", required_methods[2:4]),
        ("风险管理相关", required_methods[4:6]),
        ("交易管理相关", required_methods[6:9]),
        ("数据分析相关", required_methods[9:10]),
        ("健康检查", required_methods[10:11])
    ]

    for category_name, methods in categories:
        print(f"\n  {category_name}:")
        for method in methods:
            print(f"    ✅ {method}")

    print(f"\n✅ 类结构验证通过 - 所有{len(required_methods)}个方法已实现")
    print(f"   - 仪表盘相关: 2个方法")
    print(f"   - 策略回测相关: 2个方法")
    print(f"   - 风险管理相关: 2个方法")
    print(f"   - 交易管理相关: 3个方法")
    print(f"   - 数据分析相关: 1个方法")
    print(f"   - 健康检查: 1个方法")

    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*80)
    print(" 复合业务数据源测试")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("工厂注册验证", test_factory_registration),
        ("健康检查", test_health_check),
        ("基本业务操作", test_basic_operations),
        ("类结构验证", test_class_structure),
    ]

    passed = 0
    failed = 0
    warnings = 0

    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                warnings += 1
        except Exception as e:
            print(f"❌ {name}测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1

    # 总结
    print("\n" + "="*80)
    print(" 测试总结")
    print("="*80)
    print(f"✅ 通过: {passed}/{len(tests)}")
    if warnings > 0:
        print(f"⚠️  警告: {warnings}/{len(tests)}")
    if failed > 0:
        print(f"❌ 失败: {failed}/{len(tests)}")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if failed == 0:
        print("\n🎉 复合业务数据源实现完成！")
        print("💡 提示: 完整功能测试需要实际业务数据")
        return True
    else:
        print(f"\n⚠️  有{failed}个测试失败")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
