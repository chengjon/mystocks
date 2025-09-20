import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from manager.unified_data_manager import UnifiedDataManager

def test_unified_manager_with_financial():
    """测试UnifiedDataManager使用FinancialDataSource"""
    print("=" * 50)
    print("UnifiedDataManager 使用FinancialDataSource测试")
    print("=" * 50)
    
    # 1. 创建UnifiedDataManager实例
    print("1. 创建UnifiedDataManager实例...")
    manager = UnifiedDataManager()
    print("   ✓ UnifiedDataManager实例创建成功")
    
    # 2. 设置默认数据源为financial
    print("\n2. 设置默认数据源为financial...")
    manager.set_default_source('financial')
    print("   ✓ 默认数据源设置为financial")
    
    # 3. 测试获取股票日线数据
    print("\n3. 测试获取股票日线数据...")
    try:
        daily_data = manager.get_stock_daily('000001', '2024-01-01', '2024-12-31')
        if daily_data is not None and not daily_data.empty:
            print(f"   ✓ 成功获取到股票000001的日线数据，共{len(daily_data)}条记录")
            print("   数据预览:")
            print(daily_data.head())
        else:
            print("   ! 未能获取到股票000001的日线数据")
    except Exception as e:
        print(f"   ! 获取股票日线数据时出错: {e}")
    
    # 4. 测试获取股票基本信息
    print("\n4. 测试获取股票基本信息...")
    try:
        basic_info = manager.get_stock_basic('000001')
        if basic_info:
            print(f"   ✓ 成功获取到股票000001的基本信息")
            print(f"   基本信息预览: {basic_info}")
        else:
            print("   ! 未能获取到股票000001的基本信息")
    except Exception as e:
        print(f"   ! 获取股票基本信息时出错: {e}")
    
    # 5. 测试获取财务数据
    print("\n5. 测试获取财务数据...")
    try:
        financial_data = manager.get_financial_data('000001')
        if financial_data is not None and not financial_data.empty:
            print(f"   ✓ 成功获取到股票000001的财务数据，共{len(financial_data)}条记录")
            print("   数据预览:")
            print(financial_data.head())
        else:
            print("   ! 未能获取到股票000001的财务数据")
    except Exception as e:
        print(f"   ! 获取财务数据时出错: {e}")
    
    print("\n" + "=" * 50)
    print("UnifiedDataManager 使用FinancialDataSource测试完成")
    print("=" * 50)

if __name__ == "__main__":
    test_unified_manager_with_financial()