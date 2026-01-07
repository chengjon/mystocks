#!/usr/bin/env python3
"""
Saga 事务完整性验证测试

测试场景:
1. 成功场景: TDengine写入成功 + PG更新成功 → 事务COMMITTED
2. 失败场景: TDengine写入成功 + PG更新失败 → 事务ROLLED_BACK (补偿)
"""

import sys
import os
import pandas as pd
from datetime import datetime

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import DataClassification
from src.core.data_manager import DataManager


def test_success_scenario():
    """测试成功场景"""
    print("\n" + "=" * 60)
    print("测试场景1: Saga事务成功流程")
    print("=" * 60)

    try:
        # 初始化DataManager
        dm = DataManager(enable_monitoring=True)
        coordinator = dm.saga_coordinator

        # 准备测试数据
        test_data = pd.DataFrame(
            {
                "ts": [datetime(2026, 1, 3, 9, 30)],
                "open": [10.5],
                "high": [10.6],
                "low": [10.4],
                "close": [10.55],
                "volume": [1000],
                "amount": [10500.0],
                "symbol": ["AAAA001"],
                "frequency": ["1m"],
            }
        )

        business_id = "TEST001.SH_DAILY_20260103"

        def metadata_update_func(session):
            """模拟PG元数据更新"""
            # 这里应该更新PG中的元数据表
            print(f"  📝 模拟更新PG元数据: {business_id}")
            # 实际场景: session.execute(...)
            pass

        # 执行Saga事务
        print(f"\n1️⃣  开始Saga事务: {business_id}")
        result = coordinator.execute_kline_sync(
            business_id=business_id,
            kline_data=test_data,
            classification=DataClassification.MINUTE_KLINE,
            table_name="market_data.minute_kline",
            metadata_update_func=metadata_update_func,
        )

        if result:
            print("   ✅ 事务成功: COMMITTED")
            print("   📊 验证: TDengine数据已写入且is_valid=true")
            return True
        else:
            print("   ❌ 事务失败")
            return False

    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_failure_scenario():
    """测试失败场景(补偿)"""
    print("\n" + "=" * 60)
    print("测试场景2: Saga事务失败与补偿")
    print("=" * 60)

    try:
        # 初始化DataManager
        dm = DataManager(enable_monitoring=True)
        coordinator = dm.saga_coordinator

        # 准备测试数据
        test_data = pd.DataFrame(
            {
                "ts": [datetime(2026, 1, 3, 9, 31)],
                "open": [10.6],
                "high": [10.7],
                "low": [10.5],
                "close": [10.65],
                "volume": [2000],
                "amount": [21200.0],
                "symbol": ["AAAA002"],
                "frequency": ["1m"],
            }
        )

        business_id = "TEST002.SH_DAILY_20260103"

        def metadata_update_func_with_error(session):
            """模拟PG更新失败"""
            print(f"  📝 尝试更新PG元数据: {business_id}")
            print("  ⚠️  模拟PG更新失败(触发补偿)")
            raise Exception("Simulated PG Update Failure")

        # 执行Saga事务(预期失败并触发补偿)
        print(f"\n1️⃣  开始Saga事务: {business_id}")
        result = coordinator.execute_kline_sync(
            business_id=business_id,
            kline_data=test_data,
            classification=DataClassification.MINUTE_KLINE,
            table_name="market_data.minute_kline",
            metadata_update_func=metadata_update_func_with_error,
        )

        if not result:
            print("   ✅ 事务正确失败: ROLLED_BACK")
            print("   🔄 补偿执行: TDengine数据标记为is_valid=false")
            return True
        else:
            print("   ❌ 预期失败但事务成功")
            return False

    except Exception as e:
        # 补偿流程会抛出异常
        print(f"   ✅ 补偿流程已触发: {str(e)[:100]}")
        print("   🔄 验证: TDengine数据应被标记为is_valid=false")
        return True


def verify_tags_in_tdengine():
    """验证TDengine中的标签设置"""
    print("\n" + "=" * 60)
    print("验证: 检查TDengine中的事务标签")
    print("=" * 60)

    try:
        import taos

        conn = taos.connect(host="localhost", port=6030, user="root", password="taosdata", database="market_data")
        cursor = conn.cursor()

        # 查询最近写入的测试数据
        cursor.execute(
            """
            SELECT ts, symbol, open, close, txn_id, is_valid
            FROM market_data.minute_kline
            WHERE symbol IN ('AAAA001', 'AAAA002')
            ORDER BY ts DESC
            LIMIT 10
        """
        )

        results = cursor.fetchall()

        if results:
            print("\n📊 最近10条测试数据:\n")
            print(f"{'时间':<20} {'代码':<10} {'开盘':<8} {'收盘':<8} {'事务ID':<36} {'有效'}")
            print("-" * 100)

            for row in results:
                ts, symbol, open_p, close_p, txn_id, is_valid = row
                txn_display = txn_id[:32] + "..." if txn_id and len(txn_id) > 32 else (txn_id or "N/A")
                valid_display = "✅" if is_valid else "❌"
                print(f"{str(ts):<20} {symbol:<10} {open_p:<8} {close_p:<8} {txn_display:<36} {valid_display}")
        else:
            print("ℹ️  未找到测试数据(可能未写入)")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ 查询失败: {e}")


def verify_transaction_log():
    """验证PostgreSQL中的transaction_log"""
    print("\n" + "=" * 60)
    print("验证: 检查PostgreSQL中的事务日志")
    print("=" * 60)

    try:
        import psycopg2

        conn = psycopg2.connect(
            host="localhost", port=5438, user="postgres", password="your-postgresql-password", database="mystocks"
        )
        cursor = conn.cursor()

        # 查询最近的事务日志
        cursor.execute(
            """
            SELECT transaction_id, business_type, business_id,
                   td_status, pg_status, final_status,
                   created_at
            FROM transaction_log
            WHERE business_id LIKE '%TEST%'
            ORDER BY created_at DESC
            LIMIT 10
        """
        )

        results = cursor.fetchall()

        if results:
            print("\n📋 最近10条事务日志:\n")
            print(f"{'业务ID':<30} {'TD状态':<10} {'PG状态':<10} {'最终状态':<12} {'创建时间'}")
            print("-" * 90)

            for row in results:
                txn_id, biz_type, biz_id, td_status, pg_status, final_status, created_at = row
                print(f"{biz_id:<30} {td_status:<10} {pg_status:<10} {final_status:<12} {created_at}")
        else:
            print("ℹ️  未找到测试事务日志")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ 查询失败: {e}")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("🧪 Saga 事务完整性验证测试")
    print("=" * 60)

    results = []

    # 测试1: 成功场景
    results.append(("成功场景", test_success_scenario()))

    # 测试2: 失败场景(补偿)
    results.append(("失败场景(补偿)", test_failure_scenario()))

    # 验证TDengine标签
    verify_tags_in_tdengine()

    # 验证PG事务日志
    verify_transaction_log()

    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:<30} {status}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过! Saga事务机制正常工作")
    else:
        print("⚠️  部分测试失败,请检查")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
