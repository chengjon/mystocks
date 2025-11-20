"""
数据源使用示例
演示如何使用数据源工厂动态切换数据源
"""

import os
from src.factories.data_source_factory import get_data_source, data_source_factory


def demo_data_source_usage():
    """
    演示数据源使用方法
    """
    print("数据源使用示例")
    print("="*50)
    
    # 获取数据源实例
    data_source = get_data_source()
    
    # 检查当前使用的是哪种数据源
    if data_source_factory.is_using_mock():
        print("当前使用: Mock数据源")
    else:
        print("当前使用: 真实数据源")
    
    print()
    
    # 调用一些示例方法
    print("1. 获取股票列表:")
    stock_list = data_source.get_stock_list({"limit": 5})
    print(f"   获取到 {len(stock_list)} 只股票")
    if stock_list:
        for stock in stock_list[:3]:  # 只显示前3只
            print(f"   - {stock.get('symbol', '')}: {stock.get('name', '')}")
    
    print()
    
    print("2. 获取实时行情 (示例股票 600519):")
    real_time_data = data_source.get_real_time_quote("600519")
    if real_time_data:
        print(f"   股票名称: {real_time_data.get('name', '')}")
        print(f"   当前价格: {real_time_data.get('price', 0.0)}")
        print(f"   涨跌幅: {real_time_data.get('change_percent', 0.0)}")
    else:
        print("   未获取到数据")
    
    print()
    
    print("3. 获取技术指标 (示例股票 600519):")
    indicators = data_source.get_all_indicators("600519")
    if indicators:
        print(f"   股票代码: {indicators.get('symbol', '')}")
        trend = indicators.get('trend', {})
        if trend:
            print(f"   MA5: {trend.get('ma5', 'N/A')}")
            print(f"   MA10: {trend.get('ma10', 'N/A')}")
    else:
        print("   未获取到数据")
    
    print()
    
    print("4. 获取监控摘要:")
    summary = data_source.get_monitoring_summary()
    if summary:
        print(f"   总股票数: {summary.get('total_stocks', 0)}")
        print(f"   涨停数: {summary.get('limit_up_count', 0)}")
        print(f"   跌停数: {summary.get('limit_down_count', 0)}")
    else:
        print("   未获取到数据")


def demo_data_source_switching():
    """
    演示数据源切换功能
    """
    print("\n数据源切换演示")
    print("="*50)
    
    # 切换到Mock数据源
    print("切换到Mock数据源:")
    data_source_factory.switch_to_mock()
    print(f"当前使用Mock数据源: {data_source_factory.is_using_mock()}")
    
    # 获取数据源并调用方法
    data_source = get_data_source()
    stock_list = data_source.get_stock_list({"limit": 3})
    print(f"Mock数据源获取到 {len(stock_list)} 只股票")
    
    # 切换到真实数据源
    print("\n切换到真实数据源:")
    data_source_factory.switch_to_real()
    print(f"当前使用Mock数据源: {data_source_factory.is_using_mock()}")
    
    # 获取数据源并调用方法
    data_source = get_data_source()
    stock_list = data_source.get_stock_list({"limit": 3})
    print(f"真实数据源获取到 {len(stock_list)} 只股票")


if __name__ == "__main__":
    # 设置环境变量来控制默认数据源
    os.environ['USE_MOCK_DATA'] = 'true'
    
    # 演示数据源使用
    demo_data_source_usage()
    
    # 演示数据源切换
    demo_data_source_switching()