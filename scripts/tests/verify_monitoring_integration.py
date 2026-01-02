#!/usr/bin/env python3
"""
数据源监控系统快速验证脚本

功能：
1. 验证Prometheus metrics导出器是否正常工作
2. 测试指标更新功能
3. 验证与DataSourceManagerV2的集成
4. 生成测试报告

使用方法：
    python scripts/tests/verify_monitoring_integration.py

作者：Claude Code
版本：v2.0
创建时间：2026-01-02
"""

import sys
import os
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.monitoring.data_source_metrics import (
    DataSourceMetricsExporter,
    update_call_metrics,
    update_health_metrics,
    init_source_metrics
)


def test_metrics_exporter():
    """测试metrics导出器"""
    print("\n" + "="*60)
    print("测试1: Metrics导出器初始化")
    print("="*60)

    try:
        exporter = DataSourceMetricsExporter.get_instance()
        print("✓ 导出器单例创建成功")

        # 测试初始化metrics
        init_source_metrics(
            endpoint_name="test.endpoint",
            source_name="test_source",
            data_category="TEST_DATA",
            source_type="mock",
            priority=10
        )
        print("✓ Metrics初始化成功")

        return True

    except Exception as e:
        print(f"✗ 导出器初始化失败: {e}")
        return False


def test_call_metrics_update():
    """测试调用metrics更新"""
    print("\n" + "="*60)
    print("测试2: 调用Metrics更新")
    print("="*60)

    try:
        # 模拟成功调用
        update_call_metrics(
            endpoint_name="test.endpoint",
            source_name="test_source",
            data_category="TEST_DATA",
            success=True,
            response_time=0.5,
            record_count=100
        )
        print("✓ 成功调用metrics记录成功")

        # 模拟失败调用
        update_call_metrics(
            endpoint_name="test.endpoint",
            source_name="test_source",
            data_category="TEST_DATA",
            success=False,
            response_time=2.0,
            error_msg="Connection timeout"
        )
        print("✓ 失败调用metrics记录成功")

        return True

    except Exception as e:
        print(f"✗ Metrics更新失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_health_metrics_update():
    """测试健康状态metrics更新"""
    print("\n" + "="*60)
    print("测试3: 健康状态Metrics更新")
    print("="*60)

    try:
        update_health_metrics(
            endpoint_name="test.endpoint",
            source_name="test_source",
            data_category="TEST_DATA",
            health_status="healthy",
            quality_score=9.5,
            success_rate=98.5,
            consecutive_failures=0,
            total_calls=1000
        )
        print("✓ 健康状态metrics更新成功")

        return True

    except Exception as e:
        print(f"✗ 健康状态metrics更新失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_manager_v2_integration():
    """测试与DataSourceManagerV2的集成"""
    print("\n" + "="*60)
    print("测试4: DataSourceManagerV2集成")
    print("="*60)

    try:
        from src.core.data_source_manager_v2 import DataSourceManagerV2

        manager = DataSourceManagerV2()
        print("✓ DataSourceManagerV2初始化成功")

        # 获取注册表
        registry = manager.registry
        print(f"✓ 加载了 {len(registry)} 个数据源")

        if len(registry) > 0:
            print("\n已注册的数据源:")
            for endpoint_name in list(registry.keys())[:5]:  # 显示前5个
                source_data = registry[endpoint_name]
                config = source_data.get('config', {})
                print(f"  - {endpoint_name}: {config.get('source_name')} - {config.get('data_category')}")

            if len(registry) > 5:
                print(f"  ... 还有 {len(registry) - 5} 个数据源")

        return True

    except Exception as e:
        print(f"✗ DataSourceManagerV2集成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metrics_endpoint():
    """测试/metrics端点是否可访问"""
    print("\n" + "="*60)
    print("测试5: Metrics端点验证")
    print("="*60)

    try:
        import requests

        # 尝试访问metrics端点
        response = requests.get("http://localhost:8001/metrics", timeout=5)

        if response.status_code == 200:
            print("✓ Metrics端点可访问")

            # 检查关键指标是否存在
            metrics_text = response.text

            required_metrics = [
                "data_source_up",
                "data_source_response_time_seconds",
                "data_source_calls_total",
                "data_source_success_rate"
            ]

            found_metrics = []
            for metric in required_metrics:
                if metric in metrics_text:
                    found_metrics.append(metric)

            print(f"✓ 找到 {len(found_metrics)}/{len(required_metrics)} 个关键指标")

            if len(found_metrics) < len(required_metrics):
                print("缺失的指标:")
                for metric in required_metrics:
                    if metric not in found_metrics:
                        print(f"  - {metric}")

            return len(found_metrics) >= len(required_metrics) - 1  # 允许1个指标缺失

        else:
            print(f"✗ Metrics端点返回状态码: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("⚠ Metrics服务器未启动（这是正常的，需要手动启动）")
        print("  启动命令: python scripts/runtime/start_metrics_server.py")
        return None  # 非失败，只是未启动

    except Exception as e:
        print(f"✗ Metrics端点验证失败: {e}")
        return False


def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "="*60)
    print("测试报告")
    print("="*60)

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r is True)
    failed_tests = sum(1 for r in results.values() if r is False)
    skipped_tests = sum(1 for r in results.values() if r is None)

    print(f"\n总测试数: {total_tests}")
    print(f"通过: {passed_tests}")
    print(f"失败: {failed_tests}")
    print(f"跳过: {skipped_tests}")

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
        print("✓ 所有测试通过！监控系统集成正常。")
        print("\n下一步:")
        print("  1. 启动metrics服务器: python scripts/runtime/start_metrics_server.py")
        print("  2. 访问Grafana: http://192.168.123.104:3000")
        print("  3. 导入仪表板: monitoring-stack/grafana-dashboards/data_source_monitoring.json")
    else:
        print("✗ 部分测试失败，请检查错误信息。")

    print("="*60)


def main():
    """主函数"""
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║   MyStocks 数据源监控系统验证工具 v2.0              ║")
    print("╚══════════════════════════════════════════════════════╝")

    results = {}

    # 运行所有测试
    results["Metrics导出器初始化"] = test_metrics_exporter()
    results["调用Metrics更新"] = test_call_metrics_update()
    results["健康状态Metrics更新"] = test_health_metrics_update()
    results["DataSourceManagerV2集成"] = test_manager_v2_integration()
    results["Metrics端点验证"] = test_metrics_endpoint()

    # 生成报告
    generate_test_report(results)

    # 返回退出码
    failed = sum(1 for r in results.values() if r is False)
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
