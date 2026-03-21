"""
DataClassification测试文件
用于测试数据分类枚举功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest

from src.core.data_classification import DatabaseTarget, DataClassification


class TestDataClassification(unittest.TestCase):
    """DataClassification测试类"""

    def test_data_classification_enum_values(self):
        """测试数据分类枚举值"""
        # 测试所有枚举值
        self.assertEqual(DataClassification.TICK_DATA.value, "tick_data")
        self.assertEqual(DataClassification.MINUTE_KLINE.value, "minute_kline")
        self.assertEqual(DataClassification.DAILY_KLINE.value, "daily_kline")
        self.assertEqual(DataClassification.ORDER_BOOK_DEPTH.value, "order_book_depth")
        self.assertEqual(DataClassification.LEVEL2_SNAPSHOT.value, "level2_snapshot")
        self.assertEqual(DataClassification.INDEX_QUOTES.value, "index_quotes")
        self.assertEqual(DataClassification.SYMBOLS_INFO.value, "symbols_info")
        self.assertEqual(DataClassification.INDUSTRY_CLASS.value, "industry_class")
        self.assertEqual(DataClassification.CONCEPT_CLASS.value, "concept_class")
        self.assertEqual(DataClassification.INDEX_CONSTITUENTS.value, "index_constituents")
        self.assertEqual(DataClassification.TRADE_CALENDAR.value, "trade_calendar")
        self.assertEqual(DataClassification.FUNDAMENTAL_METRICS.value, "fundamental_metrics")
        self.assertEqual(DataClassification.DIVIDEND_DATA.value, "dividend_data")
        self.assertEqual(DataClassification.SHAREHOLDER_DATA.value, "shareholder_data")
        self.assertEqual(DataClassification.MARKET_RULES.value, "market_rules")
        self.assertEqual(DataClassification.TECHNICAL_INDICATORS.value, "technical_indicators")
        self.assertEqual(DataClassification.QUANT_FACTORS.value, "quant_factors")
        self.assertEqual(DataClassification.MODEL_OUTPUT.value, "model_output")
        self.assertEqual(DataClassification.TRADE_SIGNALS.value, "trade_signals")
        self.assertEqual(DataClassification.BACKTEST_RESULTS.value, "backtest_results")
        self.assertEqual(DataClassification.RISK_METRICS.value, "risk_metrics")
        self.assertEqual(DataClassification.ORDER_RECORDS.value, "order_records")
        self.assertEqual(DataClassification.TRADE_RECORDS.value, "trade_records")
        self.assertEqual(DataClassification.POSITION_HISTORY.value, "position_history")
        self.assertEqual(DataClassification.REALTIME_POSITIONS.value, "realtime_positions")
        self.assertEqual(DataClassification.REALTIME_ACCOUNT.value, "realtime_account")
        self.assertEqual(DataClassification.FUND_FLOW.value, "fund_flow")
        self.assertEqual(DataClassification.ORDER_QUEUE.value, "order_queue")
        self.assertEqual(DataClassification.DATA_SOURCE_STATUS.value, "data_source_status")
        self.assertEqual(DataClassification.TASK_SCHEDULE.value, "task_schedule")
        self.assertEqual(DataClassification.STRATEGY_PARAMS.value, "strategy_params")
        self.assertEqual(DataClassification.SYSTEM_CONFIG.value, "system_config")
        self.assertEqual(DataClassification.DATA_QUALITY_METRICS.value, "data_quality_metrics")
        self.assertEqual(DataClassification.USER_CONFIG.value, "user_config")

    def test_database_target_enum_values(self):
        """测试数据库目标枚举值"""
        # 测试数据库目标枚举值 (当前架构只有TDengine和PostgreSQL)
        self.assertEqual(DatabaseTarget.TDENGINE.value, "TDengine")
        self.assertEqual(DatabaseTarget.POSTGRESQL.value, "PostgreSQL")

    def test_data_classification_count(self):
        """测试数据分类数量"""
        # 当前实现包含核心分类与若干兼容别名
        all_classifications = list(DataClassification)
        self.assertEqual(len(all_classifications), 46)

    def test_database_target_count(self):
        """测试数据库目标数量"""
        # 验证数据库目标枚举数量 (2个: TDengine + PostgreSQL)
        all_targets = list(DatabaseTarget)
        self.assertEqual(len(all_targets), 2)


if __name__ == "__main__":
    unittest.main()
