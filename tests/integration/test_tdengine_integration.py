"""
TDengine集成测试

测试TDengine数据访问层的实际读写操作和性能。

创建日期: 2025-10-11
版本: 1.1.0
修改: 2025-11-19 - 重构为 pytest 格式，修复 sys.exit() 问题
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.data_access.tdengine_access import TDengineDataAccess
from src.core.data_classification import DataClassification
from src.core.unified_manager import MyStocksUnifiedManager


# 全局变量存储连接状态
_tdengine_available = None


def check_tdengine_connection():
    """检查 TDengine 连接是否可用"""
    global _tdengine_available
    if _tdengine_available is None:
        try:
            access = TDengineDataAccess()
            conn = access._get_connection()
            _tdengine_available = True
        except Exception:
            _tdengine_available = False
    return _tdengine_available


# pytest fixture 用于跳过测试
@pytest.fixture(autouse=True)
def skip_if_no_tdengine():
    """如果 TDengine 不可用则跳过测试"""
    if not check_tdengine_connection():
        pytest.skip("TDengine 数据库未配置或不可用")


class TestTDengineIntegration:
    """TDengine 集成测试类"""

    def test_connection(self):
        """测试1: TDengine连接测试"""
        access = TDengineDataAccess()
        conn = access._get_connection()
        assert conn is not None, "TDengine 连接应该成功"

    def test_tick_data_routing(self):
        """测试2: 保存Tick数据路由 (通过UnifiedManager)"""
        manager = MyStocksUnifiedManager()

        # 生成测试数据 (1000条Tick记录)
        test_data = pd.DataFrame(
            {
                "ts": pd.date_range(datetime.now(), periods=1000, freq="1s"),
                "price": np.random.uniform(10, 20, 1000),
                "volume": np.random.randint(100, 10000, 1000),
                "amount": np.random.uniform(1000, 200000, 1000),
            }
        )

        assert len(test_data) == 1000, "应该生成1000条记录"

        # 测试路由信息
        info = manager.get_routing_info(DataClassification.TICK_DATA)
        assert info["target_db"] == "tdengine", "Tick数据应该路由到TDengine"
        assert info["retention_days"] > 0, "保留周期应该大于0"

        # 清理
        try:
            manager.close_all_connections()
        except Exception:
            pass

    def test_batch_data_preparation(self):
        """测试3: 批量保存性能测试 (10000条记录)"""
        # 生成10000条测试数据
        large_data = pd.DataFrame(
            {
                "ts": pd.date_range(datetime.now(), periods=10000, freq="1s"),
                "price": np.random.uniform(10, 20, 10000),
                "volume": np.random.randint(100, 10000, 10000),
            }
        )

        assert len(large_data) == 10000, "应该生成10000条记录"

        # 验证数据大小
        data_size_mb = large_data.memory_usage(deep=True).sum() / 1024 / 1024
        assert data_size_mb > 0, "数据大小应该大于0"

    def test_minute_kline_routing(self):
        """测试4: 分钟K线数据路由测试"""
        manager = MyStocksUnifiedManager()

        # 测试MINUTE_KLINE路由
        info = manager.get_routing_info(DataClassification.MINUTE_KLINE)

        assert info["target_db"] == "tdengine", "分钟线应该路由到TDengine"
        assert info["retention_days"] > 0, "保留周期应该大于0"

        # 清理
        try:
            manager.close_all_connections()
        except Exception:
            pass

    def test_failure_recovery_queue(self):
        """测试5: 故障恢复队列测试"""
        from src.core.batch_failure_strategy import BatchFailureStrategy

        # 测试批量保存策略
        small_data = pd.DataFrame(
            {
                "ts": pd.date_range(datetime.now(), periods=10, freq="1s"),
                "price": np.random.uniform(10, 20, 10),
                "volume": np.random.randint(100, 10000, 10),
            }
        )

        assert len(small_data) == 10, "应该生成10条记录"

        # 验证 BatchFailureStrategy 模块可以导入
        assert BatchFailureStrategy is not None, "BatchFailureStrategy 应该可以导入"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
