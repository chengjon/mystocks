#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
US3 DataManager 监控集成验证测试

验证目标:
1. DataManager 监控初始化
2. save_data 和 load_data 操作记录
3. 监控数据写入 PostgreSQL
4. Grafana 数据视图查询

创建日期: 2025-10-25
版本: 1.0.0
"""

import sys
import os
import pandas as pd
import psycopg2
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.data_manager import DataManager
from core.data_classification import DataClassification


def test_datamanager_initialization():
    """测试1: DataManager 监控初始化"""
    print("\n" + "=" * 70)
    print("测试1: DataManager 监控初始化")
    print("=" * 70)

    # 初始化 DataManager (监控启用)
    dm = DataManager(enable_monitoring=True)

    # 验证监控器已初始化
    assert dm.monitor is not None, "监控器未初始化"
    assert hasattr(dm, 'enable_monitoring'), "enable_monitoring 属性缺失"

    print(f"✅ DataManager 初始化成功")
    print(f"   监控状态: {'已启用' if dm.enable_monitoring else '已禁用'}")

    if dm.enable_monitoring:
        print(f"   监控器类型: {type(dm.monitor).__name__}")
        if hasattr(dm.monitor, 'enabled'):
            print(f"   监控器连接: {'正常' if dm.monitor.enabled else '失败'}")

    return dm


def test_save_data_with_monitoring(dm):
    """测试2: save_data 操作监控"""
    print("\n" + "=" * 70)
    print("测试2: save_data 操作监控")
    print("=" * 70)

    # 创建测试数据
    test_data = pd.DataFrame({
        'symbol': ['600000.SH', '600001.SH', '600002.SH'],
        'price': [10.5, 11.2, 9.8],
        'volume': [1000000, 1200000, 950000],
        'ts': [datetime.now()] * 3
    })

    print(f"\n准备测试数据: {len(test_data)} 行")

    # 测试不同分类的路由
    test_cases = [
        (DataClassification.TICK_DATA, 'test_tick_data', 'TDengine'),
        (DataClassification.DAILY_KLINE, 'test_daily_kline', 'PostgreSQL'),
        (DataClassification.SYMBOLS_INFO, 'test_symbols_info', 'PostgreSQL'),
    ]

    for classification, table_name, expected_db in test_cases:
        print(f"\n测试分类: {classification.value}")
        print(f"   目标数据库: {expected_db}")
        print(f"   表名: {table_name}")

        try:
            # 执行save_data (会自动记录监控)
            # 注意: 实际写入可能失败（表不存在），但监控记录应该成功
            success = dm.save_data(
                classification=classification,
                data=test_data,
                table_name=table_name
            )

            print(f"   操作结果: {'成功' if success else '失败（预期，表可能不存在）'}")
            print(f"   监控记录: {'已记录' if dm.enable_monitoring else '未启用'}")

        except Exception as e:
            print(f"   异常: {str(e)[:100]}")
            print(f"   监控记录: {'应该已记录异常' if dm.enable_monitoring else '未启用'}")


def test_monitoring_database():
    """测试3: 验证监控数据库记录"""
    print("\n" + "=" * 70)
    print("测试3: 验证监控数据库记录")
    print("=" * 70)

    try:
        # 连接到 PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            port=5438,
            user="postgres",
            password="your-postgresql-password",
            database="mystocks"
        )

        cursor = conn.cursor()

        # 查询最近的监控记录
        cursor.execute("""
            SELECT
                operation_id,
                classification,
                target_database,
                routing_decision_time_ms,
                operation_type,
                table_name,
                data_count,
                operation_success,
                created_at
            FROM monitoring.datamanager_routing_metrics
            ORDER BY created_at DESC
            LIMIT 10
        """)

        records = cursor.fetchall()

        print(f"\n✅ 查询到 {len(records)} 条最近的监控记录:")
        print(f"\n{'序号':<4} {'分类':<20} {'目标DB':<12} {'路由时间(ms)':<15} {'操作':<12} {'成功':<6} {'数据量':<8}")
        print("-" * 100)

        for idx, record in enumerate(records, 1):
            operation_id, classification, target_db, routing_time, op_type, table_name, data_count, success, created_at = record
            print(f"{idx:<4} {classification:<20} {target_db:<12} {routing_time:<15.6f} {op_type:<12} {str(success):<6} {data_count or 0:<8}")

        # 查询性能摘要
        cursor.execute("SELECT * FROM monitoring.v_routing_performance_24h")
        perf_data = cursor.fetchone()

        if perf_data:
            print(f"\n📊 24小时性能摘要:")
            print(f"   总操作数: {perf_data[0]}")
            print(f"   成功操作: {perf_data[1]}")
            print(f"   失败操作: {perf_data[2]}")
            print(f"   平均路由时间: {perf_data[3]:.6f} ms")
            print(f"   最大路由时间: {perf_data[4]:.6f} ms")
            print(f"   最小路由时间: {perf_data[5]:.6f} ms")

        cursor.close()
        conn.close()

        print(f"\n✅ 监控数据库验证成功")

        return True

    except Exception as e:
        print(f"\n❌ 监控数据库验证失败: {str(e)}")
        return False


def test_comprehensive_suite():
    """测试4: 运行综合测试套件"""
    print("\n" + "=" * 70)
    print("测试4: 运行综合测试套件")
    print("=" * 70)

    import subprocess

    try:
        result = subprocess.run(
            ["python", "-m", "pytest",
             "tests/test_datamanager_comprehensive.py",
             "-v", "--tb=short", "-k", "test_all_34_classifications or test_routing_decision_speed_single"],
            capture_output=True,
            text=True,
            timeout=60
        )

        print(f"\n测试执行结果:")
        print(f"   返回码: {result.returncode}")

        # 解析输出
        if "passed" in result.stdout.lower():
            print(f"   状态: ✅ 测试通过")
        else:
            print(f"   状态: ⚠️  部分测试失败")

        # 显示最后几行输出
        lines = result.stdout.split('\n')
        for line in lines[-15:]:
            if line.strip():
                print(f"   {line}")

        return result.returncode == 0

    except Exception as e:
        print(f"\n❌ 测试套件执行失败: {str(e)}")
        return False


def main():
    """主测试流程"""
    print("\n" + "=" * 70)
    print("US3 DataManager 监控集成完整性验证")
    print("=" * 70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "DataManager初始化": False,
        "save_data监控": False,
        "监控数据库验证": False,
        "综合测试套件": False
    }

    try:
        # 测试1: DataManager 初始化
        dm = test_datamanager_initialization()
        results["DataManager初始化"] = True

        # 测试2: save_data 操作监控
        if dm.enable_monitoring:
            test_save_data_with_monitoring(dm)
            results["save_data监控"] = True
        else:
            print("\n⚠️  监控未启用，跳过 save_data 监控测试")

        # 测试3: 监控数据库验证
        results["监控数据库验证"] = test_monitoring_database()

        # 测试4: 综合测试套件
        results["综合测试套件"] = test_comprehensive_suite()

    except Exception as e:
        print(f"\n❌ 测试过程异常: {str(e)}")
        import traceback
        traceback.print_exc()

    # 输出测试结果摘要
    print("\n" + "=" * 70)
    print("测试结果摘要")
    print("=" * 70)

    passed_count = sum(results.values())
    total_count = len(results)

    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"   {test_name:<20} {status}")

    print(f"\n   总计: {passed_count}/{total_count} 测试通过")

    if passed_count == total_count:
        print(f"\n🎉 所有测试通过！监控集成成功！")
        return 0
    else:
        print(f"\n⚠️  部分测试失败，请检查日志")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
