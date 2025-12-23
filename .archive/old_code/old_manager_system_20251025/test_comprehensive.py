import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from manager.unified_data_manager import UnifiedDataManager


def test_comprehensive():
    """全面测试UnifiedDataManager的功能"""
    print("=" * 60)
    print("UnifiedDataManager 全面功能测试")
    print("=" * 60)

    # 1. 创建UnifiedDataManager实例
    print("1. 创建UnifiedDataManager实例...")
    manager = UnifiedDataManager()
    print("   ✓ UnifiedDataManager实例创建成功")

    # 2. 测试使用默认数据源(Akshare)获取数据
    print("\n2. 测试使用默认数据源(Akshare)获取数据...")
    try:
        # 获取股票日线数据
        daily_data = manager.get_stock_daily("000001", "2024-01-01", "2024-12-31")
        if daily_data is not None and not daily_data.empty:
            print(
                f"   ✓ Akshare成功获取到股票000001的日线数据，共{len(daily_data)}条记录"
            )
        else:
            print("   ! Akshare未能获取到股票000001的日线数据")
    except Exception as e:
        print(f"   ! Akshare获取股票日线数据时出错: {e}")

    try:
        # 获取股票基本信息
        basic_info = manager.get_stock_basic("000001")
        if basic_info:
            print("   ✓ Akshare成功获取到股票000001的基本信息")
        else:
            print("   ! Akshare未能获取到股票000001的基本信息")
    except Exception as e:
        print(f"   ! Akshare获取股票基本信息时出错: {e}")

    # 3. 测试使用FinancialDataSource获取数据
    print("\n3. 测试使用FinancialDataSource获取数据...")
    manager.set_default_source("financial")

    try:
        # 获取股票基本信息
        basic_info = manager.get_stock_basic("000001")
        if basic_info:
            print("   ✓ Financial成功获取到股票000001的基本信息")
        else:
            print("   ! Financial未能获取到股票000001的基本信息")
    except Exception as e:
        print(f"   ! Financial获取股票基本信息时出错: {e}")

    try:
        # 获取财务数据
        financial_data = manager.get_financial_data("000001")
        if financial_data is not None and not financial_data.empty:
            print(
                f"   ✓ Financial成功获取到股票000001的财务数据，共{len(financial_data)}条记录"
            )
        else:
            print("   ! Financial未能获取到股票000001的财务数据")
    except Exception as e:
        print(f"   ! Financial获取财务数据时出错: {e}")

    # 4. 测试数据源切换功能
    print("\n4. 测试数据源切换功能...")
    try:
        # 切换回Akshare数据源获取基本信息
        basic_info_ak = manager.get_stock_basic("000001", source_type="akshare")
        if basic_info_ak:
            print("   ✓ 成功切换到Akshare数据源并获取到股票000001的基本信息")
        else:
            print("   ! 切换到Akshare数据源未能获取到股票000001的基本信息")
    except Exception as e:
        print(f"   ! 切换数据源时出错: {e}")

    try:
        # 使用Financial数据源获取基本信息
        basic_info_fin = manager.get_stock_basic("000001", source_type="financial")
        if basic_info_fin:
            print("   ✓ 成功切换到Financial数据源并获取到股票000001的基本信息")
        else:
            print("   ! 切换到Financial数据源未能获取到股票000001的基本信息")
    except Exception as e:
        print(f"   ! 切换数据源时出错: {e}")

    print("\n" + "=" * 60)
    print("UnifiedDataManager 全面功能测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_comprehensive()
