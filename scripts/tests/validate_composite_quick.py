"""
快速验证Composite业务数据源

仅验证工厂注册和类结构，不进行实际数据库操作
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

print("\n" + "="*80)
print(" Composite业务数据源快速验证")
print("="*80)

# 测试1: 验证导入
print("\n测试 1: 验证导入...")
try:
    from src.data_sources.real.composite_business import CompositeBusinessDataSource
    from src.interfaces.business_data_source import IBusinessDataSource
    print("  ✅ 导入成功")
except ImportError as e:
    print(f"  ❌ 导入失败: {e}")
    sys.exit(1)

# 测试2: 验证继承关系
print("\n测试 2: 验证继承关系...")
if issubclass(CompositeBusinessDataSource, IBusinessDataSource):
    print("  ✅ CompositeBusinessDataSource 继承 IBusinessDataSource")
else:
    print("  ❌ 继承关系错误")
    sys.exit(1)

# 测试3: 验证工厂注册
print("\n测试 3: 验证工厂注册...")
try:
    from src.data_sources.factory import DataSourceFactory
    factory = DataSourceFactory()
    registered = factory.list_registered_sources()

    if "composite" in registered.get("business", []):
        print("  ✅ Composite数据源已注册到工厂")
    else:
        print(f"  ❌ Composite数据源未注册")
        print(f"     已注册业务数据源: {registered.get('business', [])}")
        sys.exit(1)
except Exception as e:
    print(f"  ❌ 工厂注册验证失败: {e}")
    sys.exit(1)

# 测试4: 验证方法数量
print("\n测试 4: 验证接口方法...")
required_methods = [
    'get_dashboard_summary',
    'get_sector_performance',
    'execute_backtest',
    'get_backtest_results',
    'calculate_risk_metrics',
    'check_risk_alerts',
    'analyze_trading_signals',
    'get_portfolio_analysis',
    'perform_attribution_analysis',
    'execute_stock_screener',
    'health_check'
]

missing_methods = []
for method in required_methods:
    if not hasattr(CompositeBusinessDataSource, method):
        missing_methods.append(method)

if missing_methods:
    print(f"  ❌ 缺少方法: {missing_methods}")
    sys.exit(1)
else:
    print(f"  ✅ 所有 {len(required_methods)} 个方法已实现")

# 测试5: 验证__init__导出
print("\n测试 5: 验证模块导出...")
try:
    from src.data_sources.real import CompositeBusinessDataSource as CompositeBiz
    print("  ✅ CompositeBusinessDataSource 已从 src.data_sources.real 导出")
except ImportError as e:
    print(f"  ❌ 导出验证失败: {e}")
    sys.exit(1)

print("\n" + "="*80)
print(" 验证总结")
print("="*80)
print("✅ 所有验证通过 (5/5)")
print("\n方法列表:")
for i, method in enumerate(required_methods, 1):
    print(f"  {i:2d}. {method}")

print("\n🎉 Composite业务数据源验证完成!")
print("💡 注意: 完整功能测试需要实际数据库连接和数据")
