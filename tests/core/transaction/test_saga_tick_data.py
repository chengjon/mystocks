#!/usr/bin/env python3
"""
Saga 事务验证测试 - TICK_DATA (高频逐笔数据)

验证重点:
1. 批量 Tick 写入的一致性。
2. 超级表 (tick_data) 下的子表自动创建与写入。
3. 失败场景下的 Tick 数据批量失效补偿。
"""

import sys
import os
import pandas as pd
import pytest
from datetime import datetime, timedelta

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.core import DataClassification
from src.core.data_manager import DataManager


class TestSagaTickData:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.dm = DataManager(enable_monitoring=True)
        self.coordinator = self.dm.saga_coordinator
        self.symbol = "TICK999"
        self.exchange = "SZ"
        self.table_name = "market_data.tick_data"

    def generate_tick_data(self, count=10):
        """生成模拟 Tick 数据"""
        now = datetime.now()
        data = []
        for i in range(count):
            data.append(
                {
                    "ts": now + timedelta(milliseconds=i * 100),
                    "price": 15.5 + i * 0.01,
                    "volume": 100 * (i + 1),
                    "amount": 1550.0 + i * 1.5,
                    "symbol": self.symbol,
                    "exchange": self.exchange,
                }
            )
        return pd.DataFrame(data)

    def test_tick_success_scenario(self):
        """测试 Tick 数据成功写入场景"""
        print(f"\n🚀 开始 Tick Saga 成功测试: {self.symbol}")

        tick_df = self.generate_tick_data(5)
        business_id = f"{self.symbol}_TICK_SUCCESS_{int(datetime.now().timestamp())}"

        def metadata_mock(session):
            print(f"  📝 [PG] 模拟记录 Tick 同步元数据...")
            # 模拟执行成功
            pass

        result = self.coordinator.execute_kline_sync(
            business_id=business_id,
            kline_data=tick_df,
            classification=DataClassification.TICK_DATA,
            table_name=self.table_name,
            metadata_update_func=metadata_mock,
        )

        assert result is True
        print("  ✅ 事务状态: COMMITTED")

        # 验证 TDengine
        conn = self.dm._tdengine.db_manager.get_connection(self.dm._tdengine.db_type, "market_data")
        # 直接 SQL 查询验证
        sql = f"SELECT * FROM {self.table_name} WHERE symbol='{self.symbol}' AND is_valid=true ORDER BY ts DESC LIMIT 5"
        try:
            df_verify = pd.read_sql(sql, conn)
            assert not df_verify.empty
            assert len(df_verify) == 5
            print(f"  📊 验证成功: TDengine 已存入 {len(df_verify)} 条有效记录")
        except Exception as e:
            pytest.fail(f"TDengine 查询失败: {e}")

    def test_tick_failure_compensation(self):
        """测试 Tick 数据失败补偿场景"""
        print(f"\n🚀 开始 Tick Saga 失败补偿测试: {self.symbol}")

        tick_df = self.generate_tick_data(3)
        business_id = f"{self.symbol}_TICK_FAIL_{int(datetime.now().timestamp())}"

        def metadata_fail_mock(session):
            print(f"  ⚠️ [PG] 模拟更新失败，触发补偿...")
            raise Exception("Database unique constraint violation (Simulated)")

        result = self.coordinator.execute_kline_sync(
            business_id=business_id,
            kline_data=tick_df,
            classification=DataClassification.TICK_DATA,
            table_name=self.table_name,
            metadata_update_func=metadata_fail_mock,
        )

        assert result is False
        print("  ✅ 事务状态: ROLLED_BACK (通过补偿)")

        # 验证 TDengine 中的数据是否被标记为无效
        conn = self.dm._tdengine.db_manager.get_connection(self.dm._tdengine.db_type, "market_data")

        # 补偿后的数据 is_valid 应为 false
        # 注意: TDengine 查询时需要根据 txn_id 过滤，或者查询最新状态
        # 我们的补偿逻辑是插入新记录(is_valid=false)覆盖旧记录
        # 但由于我们这里是瞬间写入瞬间补偿，时间戳完全一样，取决于 TDengine 的去重策略
        # 我们的代码实现是：
        # 1. 查出 txn_id 的所有数据
        # 2. 改 is_valid=False
        # 3. 重新插入
        # 所以最终应该能查到 is_valid=False 的记录

        # 我们查询该 txn_id 关联的所有记录
        sql = f"SELECT * FROM {self.table_name} WHERE symbol='{self.symbol}' AND is_valid=false"

        try:
            df_verify = pd.read_sql(sql, conn)
            assert not df_verify.empty
            print(f"  🔄 验证成功: TDengine 中有 {len(df_verify)} 条记录已被标记为无效 (❌)")
        except Exception as e:
            pytest.fail(f"TDengine 查询失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
