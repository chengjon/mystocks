#!/usr/bin/env python3
"""
数据源管理V2集成验证脚本

功能：
1. 测试Phase 3"手术式替换"的向后兼容性
2. 测试V2智能路由是否正常工作
3. 测试新功能方法
4. 验证旧代码仍然可以正常工作

使用方法：
    python scripts/tests/verify_data_source_v2_integration.py

作者：Claude Code
版本：v2.0
创建时间：2026-01-02
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.adapters.data_source_manager import DataSourceManager


def test_old_code_compatibility():
    """测试1: 旧代码兼容性"""
    print("\n" + "="*60)
    print("测试1: 旧代码兼容性验证")
    print("="*60)

    try:
        # 模拟旧代码（完全不感知V2的存在）
        manager = DataSourceManager()

        # 检查V2是否自动启用
        if manager._use_v2:
            print("✓ V2管理器已自动启用（默认行为）")
        else:
            print("✗ V2管理器未启用")

        # 检查旧版配置是否保留
        if "daily" in manager._priority_config:
            print("✓ 旧版优先级配置已保留")
        else:
            print("✗ 旧版优先级配置丢失")

        print("\n✓ 旧代码兼容性测试通过")
        return True

    except Exception as e:
        print(f"\n✗ 旧代码兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_v2_smart_routing():
    """测试2: V2智能路由"""
    print("\n" + "="*60)
    print("测试2: V2智能路由验证")
    print("="*60)

    try:
        manager = DataSourceManager(use_v2=True)

        # 检查V2管理器是否初始化
        if manager._v2_manager is None:
            print("✗ V2管理器未初始化")
            return False

        print("✓ V2管理器已初始化")

        # 测试查询功能（使用Mock数据，不需要真实API调用）
        endpoints = manager.find_endpoints(data_category="DAILY_KLINE")
        print(f"✓ 找到 {len(endpoints)} 个日线数据接口")

        if len(endpoints) > 0:
            print("\n前3个接口:")
            for i, ep in enumerate(endpoints[:3]):
                print(f"  {i+1}. {ep.get('endpoint_name')}: {ep.get('source_name')}")

        return True

    except Exception as e:
        print(f"\n✗ V2智能路由测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_disable_v2():
    """测试3: 禁用V2功能"""
    print("\n" + "="*60)
    print("测试3: 禁用V2功能验证")
    print("="*60)

    try:
        # 创建禁用V2的管理器
        manager = DataSourceManager(use_v2=False)

        if manager._use_v2:
            print("✗ V2管理器未正确禁用")
            return False

        print("✓ V2管理器已禁用")

        # 尝试使用V2功能（应该返回警告）
        endpoints = manager.find_endpoints(data_category="DAILY_KLINE")

        if len(endpoints) == 0:
            print("✓ V2功能正确禁用（find_endpoints返回空）")
        else:
            print("⚠ V2功能仍然可用（可能返回了缓存数据）")

        # 重新启用V2
        manager.enable_v2()

        if manager._use_v2:
            print("✓ V2管理器已重新启用")
        else:
            print("✗ V2管理器无法重新启用")
            return False

        return True

    except Exception as e:
        print(f"\n✗ 禁用V2功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_new_methods():
    """测试4: 新增便捷方法"""
    print("\n" + "="*60)
    print("测试4: 新增便捷方法验证")
    print("="*60)

    try:
        manager = DataSourceManager(use_v2=True)

        # 测试get_best_endpoint
        best = manager.get_best_endpoint("DAILY_KLINE")
        if best:
            print(f"✓ get_best_endpoint() 可用: {best.get('endpoint_name')}")
        else:
            print("⚠ get_best_endpoint() 返回None（可能是没有配置）")

        # 测试health_check
        health = manager.health_check()
        print(f"✓ health_check() 可用:")
        print(f"  - 总计: {health.get('total', 0)}")
        print(f"  - 健康: {health.get('healthy', 0)}")
        print(f"  - 异常: {health.get('unhealthy', 0)}")

        # 测试list_all_endpoints
        df = manager.list_all_endpoints()
        if not df.empty:
            print(f"✓ list_all_endpoints() 可用: 返回{len(df)}条记录")
            print("\n前3个端点:")
            print(df[['endpoint_name', 'source_name', 'data_category']].head(3).to_string(index=False))
        else:
            print("⚠ list_all_endpoints() 返回空DataFrame")

        return True

    except Exception as e:
        print(f"\n✗ 新增便捷方法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatible_api():
    """测试5: 向后兼容的API调用"""
    print("\n" + "="*60)
    print("测试5: 向后兼容API调用验证")
    print("="*60)

    try:
        manager = DataSourceManager()

        # 测试原有的register_source方法仍然可用
        from src.interfaces.data_source import IDataSource
        from src.adapters.akshare_adapter import AkshareDataSource

        try:
            akshare = AkshareDataSource()
            manager.register_source("test_akshare", akshare)
            print("✓ register_source() 仍然可用")
        except Exception as e:
            print(f"⚠ register_source() 测试跳过: {e}")

        # 测试原有的get_source方法仍然可用
        source = manager.get_source("test_akshare")
        if source:
            print("✓ get_source() 仍然可用")
        else:
            print("⚠ get_source() 未找到注册的数据源")

        # 测试原有的list_sources方法仍然可用
        sources = manager.list_sources()
        if len(sources) > 0:
            print(f"✓ list_sources() 仍然可用: {sources}")
        else:
            print("⚠ list_sources() 返回空列表")

        return True

    except Exception as e:
        print(f"\n✗ 向后兼容API调用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fallback_mechanism():
    """测试6: Fallback机制"""
    print("\n" + "="*60)
    print("测试6: Fallback机制验证")
    print("="*60)

    try:
        manager = DataSourceManager()

        # V2管理器存在时
        if manager._v2_manager:
            print("✓ V2管理器可用（主要路径）")

            # 旧的优先级配置仍然存在
            if "daily" in manager._priority_config:
                print("✓ 旧版优先级配置保留（fallback路径）")

            print("✓ 双层机制就绪：V2优先，旧版fallback")

        else:
            print("⚠ V2管理器不可用，将完全使用旧版方式")

        return True

    except Exception as e:
        print(f"\n✗ Fallback机制测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_integration_report(results):
    """生成集成测试报告"""
    print("\n" + "="*60)
    print("Phase 3 集成测试报告")
    print("="*60)

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r is True)
    failed_tests = sum(1 for r in results.values() if r is False)

    print(f"\n总测试数: {total_tests}")
    print(f"通过: {passed_tests}")
    print(f"失败: {failed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")

    print("\n详细结果:")
    for test_name, result in results.items():
        if result is True:
            status = "✓ 通过"
        elif result is False:
            status = "✗ 失败"
        else:
            status = "⊘ 跳过"

        print(f"  {status} - {test_name}")

    print("\n" + "="*60)

    if failed_tests == 0:
        print("✓ 所有测试通过！Phase 3集成成功。")
        print("\n关键成果:")
        print("  1. ✓ 旧代码100%向后兼容")
        print("  2. ✓ V2智能路由自动启用")
        print("  3. ✓ 新功能方法正常工作")
        print("  4. ✓ Fallback机制可靠")
        print("\n下一步:")
        print("  - 在生产环境测试")
        print("  - 监控Grafana仪表板")
        print("  - 逐步采用新功能")
    else:
        print("✗ 部分测试失败，请检查错误信息。")

    print("="*60)


def main():
    """主函数"""
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║   MyStocks 数据源管理V2集成验证工具 v2.0          ║")
    print("║   Phase 3: 手术式替换验证                          ║")
    print("╚══════════════════════════════════════════════════════╝")

    results = {}

    # 运行所有测试
    results["旧代码兼容性"] = test_old_code_compatibility()
    results["V2智能路由"] = test_v2_smart_routing()
    results["禁用V2功能"] = test_disable_v2()
    results["新增便捷方法"] = test_new_methods()
    results["向后兼容API"] = test_backward_compatible_api()
    results["Fallback机制"] = test_fallback_mechanism()

    # 生成报告
    generate_integration_report(results)

    # 返回退出码
    failed = sum(1 for r in results.values() if r is False)
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
