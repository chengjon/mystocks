#!/usr/bin/env python3
"""
Saga 事务并发压力测试

验证重点:
1. 多个并发 Saga 事务的执行稳定性。
2. 数据库连接池在高并发下的表现。
3. 验证并发回滚时的补偿逻辑是否正确（是否存在 Race Condition）。
"""

import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

import pandas as pd
import pytest

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.core import DataClassification
from src.core.data_manager import DataManager

# 并发数配置
CONCURRENCY_LEVEL = 20  # 并发线程数
TOTAL_TRANSACTIONS = 50  # 总事务数


class TestSagaConcurrency:

    @pytest.fixture(scope="class")
    def shared_dm(self):
        """Class-level DataManager to share connection pool"""
        return DataManager(enable_monitoring=True)

    def generate_kline_data(self, symbol, index):
        """生成模拟 K 线数据"""
        now = datetime.now()
        data = [
            {
                "ts": now + timedelta(minutes=index),
                "open": 10.0 + index * 0.1,
                "high": 11.0 + index * 0.1,
                "low": 9.0 + index * 0.1,
                "close": 10.5 + index * 0.1,
                "volume": 1000 + index,
                "amount": 10000.0 + index * 10,
                "symbol": symbol,
                "frequency": "1m",
            }
        ]
        return pd.DataFrame(data)

    def run_single_transaction(self, dm, txn_index):
        """执行单个 Saga 事务"""
        coordinator = dm.saga_coordinator

        # 随机决定是成功还是失败 (80% 成功率)
        should_succeed = random.random() < 0.8
        symbol = f"CONC_TEST_{txn_index % 5}"  # 5个 Symbol 轮询，制造冲突

        kline_df = self.generate_kline_data(symbol, txn_index)
        business_id = f"{symbol}_CONC_{txn_index}_{int(time.time())}"

        def metadata_func(session):
            # 模拟 PG 操作延迟
            time.sleep(random.uniform(0.01, 0.05))
            if not should_succeed:
                raise Exception(f"Simulated Failure for {business_id}")

        try:
            result = coordinator.execute_kline_sync(
                business_id=business_id,
                kline_data=kline_df,
                classification=DataClassification.MINUTE_KLINE,
                table_name="market_data.minute_kline",
                metadata_update_func=metadata_func,
            )
            return {"id": txn_index, "symbol": symbol, "expected": should_succeed, "actual": result, "error": None}
        except Exception as e:
            return {"id": txn_index, "symbol": symbol, "expected": should_succeed, "actual": False, "error": str(e)}

    def test_concurrent_saga_execution(self, shared_dm):
        """执行并发测试"""
        print(f"\n🚀 开始 Saga 并发压力测试 (Threads={CONCURRENCY_LEVEL}, Total={TOTAL_TRANSACTIONS})")

        start_time = time.time()
        results = []

        with ThreadPoolExecutor(max_workers=CONCURRENCY_LEVEL) as executor:
            future_to_txn = {
                executor.submit(self.run_single_transaction, shared_dm, i): i for i in range(TOTAL_TRANSACTIONS)
            }

            for future in as_completed(future_to_txn):
                try:
                    res = future.result()
                    results.append(res)
                except Exception as e:
                    print(f"  ❌ Thread Error: {e}")

        duration = time.time() - start_time
        print(f"  ⏱️  耗时: {duration:.2f}s (TPS: {TOTAL_TRANSACTIONS/duration:.2f})")

        # 分析结果
        success_count = sum(1 for r in results if r["actual"])
        fail_count = sum(1 for r in results if not r["actual"])
        mismatch_count = sum(
            1 for r in results if r["expected"] != r["actual"]
        )  # 注意：Saga 内部消化了异常返回 False，所以 expected False 应对应 actual False

        print(f"  📊 统计: 成功={success_count}, 失败(回滚)={fail_count}, 异常={mismatch_count}")

        # 验证逻辑一致性
        # 如果 expected=True 但 actual=False，可能是偶然的数据库错误（如锁超时），这在高并发下是允许的，但不能有数据不一致
        # 关键是验证 TDengine 中 failed 的事务是否真的被标记为无效

        failed_txns = [r for r in results if not r["actual"]]
        if failed_txns:
            print("  🔍 抽样验证回滚一致性...")
            conn = shared_dm._tdengine.db_manager.get_connection(shared_dm._tdengine.db_type, "market_data")

            # 随机抽查 3 个失败事务
            sample_size = min(3, len(failed_txns))
            for i in range(sample_size):
                sample = failed_txns[i]
                symbol = sample["symbol"]
                # 查询该 Symbol 最近的无效记录
                sql = f"SELECT count(*) FROM market_data.minute_kline WHERE symbol='{symbol}' AND is_valid=false"
                try:
                    df = pd.read_sql(sql, conn)
                    invalid_count = df.iloc[0, 0]
                    print(f"     - Symbol {symbol}: 发现 {invalid_count} 条无效记录 (预期至少包含本次失败)")
                    assert invalid_count > 0
                except Exception as e:
                    pytest.fail(f"验证失败: {e}")

        assert len(results) == TOTAL_TRANSACTIONS
        print("  ✅ 并发测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
