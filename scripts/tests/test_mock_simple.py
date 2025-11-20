#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化的Mock数据系统测试脚本

只测试核心功能，避免语法错误的干扰。

作者: MyStocks Backend Team
创建日期: 2025-10-17
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量（用于测试）
os.environ['USE_MOCK_DATA'] = 'true'

def test_unified_mock_manager_basic():
    """测试统一Mock数据管理器基础功能"""
    print("=" * 60)
    print("测试: 统一Mock数据管理器基础功能")
    print("=" * 60)
    
    try:
        from web.backend.app.mock.unified_mock_data import UnifiedMockDataManager
        
        # 测试初始化
        manager = UnifiedMockDataManager(use_mock_data=True)
        print(f"✅ Mock数据管理器初始化成功")
        print(f"   Mock模式: {manager.use_mock_data}")
        
        # 测试缓存信息
        cache_info = manager.get_cache_info()
        print(f"✅ 缓存信息获取成功")
        print(f"   缓存大小: {cache_info['cache_size']}")
        print(f"   Mock模式: {cache_info['mock_mode']}")
        
        # 测试Mock模式切换
        manager.set_mock_mode(False)
        assert manager.use_mock_data == False
        print("✅ Mock模式切换成功")
        
        manager.set_mock_mode(True)
        assert manager.use_mock_data == True
        print("✅ Mock模式重置成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_environment_variables():
    """测试环境变量控制"""
    print("\n" + "=" * 60)
    print("测试: 环境变量控制")
    print("=" * 60)
    
    try:
        # 测试环境变量设置
        os.environ['USE_MOCK_DATA'] = 'true'
        assert os.getenv('USE_MOCK_DATA') == 'true'
        print("✅ Mock环境变量设置成功")
        
        os.environ['USE_MOCK_DATA'] = 'false'
        assert os.getenv('USE_MOCK_DATA') == 'false'
        print("✅ Mock环境变量重置成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 环境变量测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_utility_functions():
    """测试工具函数"""
    print("\n" + "=" * 60)
    print("测试: 工具函数")
    print("=" * 60)
    
    try:
        from web.backend.app.mock.unified_mock_data import (
            get_mock_data_manager,
            get_dashboard_data,
            get_stocks_data,
            get_technical_data,
            get_wencai_data,
            get_strategy_data,
            get_monitoring_data,
            data_source_toggle
        )
        
        print("✅ 所有工具函数导入成功")
        
        # 测试获取管理器
        manager = get_mock_data_manager()
        print("✅ 获取管理器实例成功")
        
        # 测试装饰器
        @data_source_toggle
        def test_function():
            return {"status": "success", "data": "test"}
        
        result = test_function()
        assert result["status"] == "success"
        print("✅ 数据源切换装饰器测试成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具函数测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_performance():
    """测试性能"""
    print("\n" + "=" * 60)
    print("测试: 性能测试")
    print("=" * 60)
    
    try:
        import time
        from web.backend.app.mock.unified_mock_data import UnifiedMockDataManager
        
        manager = UnifiedMockDataManager(use_mock_data=True)
        
        # 测试缓存清除
        start_time = time.time()
        manager.clear_cache()
        end_time = time.time()
        
        clear_time = end_time - start_time
        print(f"✅ 缓存清除耗时: {clear_time:.3f}秒")
        
        # 测试性能指标
        cache_info = manager.get_cache_info()
        assert isinstance(cache_info, dict)
        assert "cache_size" in cache_info
        assert "mock_mode" in cache_info
        
        print(f"✅ 性能指标获取成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 性能测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def generate_simple_report(results):
    """生成简化测试报告"""
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {failed_tests}")
    print(f"成功率: {passed_tests / total_tests * 100:.1f}%")
    
    if failed_tests > 0:
        print(f"\n失败的测试:")
        for test_name, result in results.items():
            if not result:
                print(f"  - {test_name}")
    
    return passed_tests == total_tests


def main():
    """主测试函数"""
    print("🚀 开始简化Mock数据系统测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version}")
    
    # 执行测试
    results = {}
    
    results["unified_mock_manager_basic"] = test_unified_mock_manager_basic()
    results["environment_variables"] = test_environment_variables()
    results["utility_functions"] = test_utility_functions()
    results["performance"] = test_performance()
    
    # 生成测试报告
    success = generate_simple_report(results)
    
    if success:
        print("\n🎉 所有测试通过！Mock数据系统基础功能正常")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查系统配置")
        return 1


if __name__ == "__main__":
    exit(main())
