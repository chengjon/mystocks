"""
DataClassification测试文件
用于测试数据分类枚举功能
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from src.core.data_classification import DataClassification, DatabaseTarget


class TestDataClassification(unittest.TestCase):
    """DataClassification测试类"""
    
    def test_data_classification_enum_values(self):
        """测试数据分类枚举值"""
        # 测试所有枚举值
        self.assertEqual(DataClassification.TICK_DATA.value, "TICK_DATA")
        self.assertEqual(DataClassification.MINUTE_KLINE.value, "MINUTE_KLINE")
        self.assertEqual(DataClassification.DAILY_KLINE.value, "DAILY_KLINE")
        self.assertEqual(DataClassification.ORDER_BOOK_DEPTH.value, "ORDER_BOOK_DEPTH")
        self.assertEqual(DataClassification.LEVEL2_SNAPSHOT.value, "LEVEL2_SNAPSHOT")
        self.assertEqual(DataClassification.INDEX_QUOTES.value, "INDEX_QUOTES")
        self.assertEqual(DataClassification.SYMBOLS_INFO.value, "SYMBOLS_INFO")
        self.assertEqual(DataClassification.INDUSTRY_CLASS.value, "INDUSTRY_CLASS")
        self.assertEqual(DataClassification.CONCEPT_CLASS.value, "CONCEPT_CLASS")
        self.assertEqual(DataClassification.INDEX_CONSTITUENTS.value, "INDEX_CONSTITUENTS")
        self.assertEqual(DataClassification.TRADE_CALENDAR.value, "TRADE_CALENDAR")
        self.assertEqual(DataClassification.FUNDAMENTAL_METRICS.value, "FUNDAMENTAL_METRICS")
        self.assertEqual(DataClassification.DIVIDEND_DATA.value, "DIVIDEND_DATA")
        self.assertEqual(DataClassification.SHAREHOLDER_DATA.value, "SHAREHOLDER_DATA")
        self.assertEqual(DataClassification.MARKET_RULES.value, "MARKET_RULES")
        self.assertEqual(DataClassification.TECHNICAL_INDICATORS.value, "TECHNICAL_INDICATORS")
        self.assertEqual(DataClassification.QUANT_FACTORS.value, "QUANT_FACTORS")
        self.assertEqual(DataClassification.MODEL_OUTPUT.value, "MODEL_OUTPUT")
        self.assertEqual(DataClassification.TRADE_SIGNALS.value, "TRADE_SIGNALS")
        self.assertEqual(DataClassification.BACKTEST_RESULTS.value, "BACKTEST_RESULTS")
        self.assertEqual(DataClassification.RISK_METRICS.value, "RISK_METRICS")
        self.assertEqual(DataClassification.ORDER_RECORDS.value, "ORDER_RECORDS")
        self.assertEqual(DataClassification.TRADE_RECORDS.value, "TRADE_RECORDS")
        self.assertEqual(DataClassification.POSITION_HISTORY.value, "POSITION_HISTORY")
        self.assertEqual(DataClassification.REALTIME_POSITIONS.value, "REALTIME_POSITIONS")
        self.assertEqual(DataClassification.REALTIME_ACCOUNT.value, "REALTIME_ACCOUNT")
        self.assertEqual(DataClassification.FUND_FLOW.value, "FUND_FLOW")
        self.assertEqual(DataClassification.ORDER_QUEUE.value, "ORDER_QUEUE")
        self.assertEqual(DataClassification.DATA_SOURCE_STATUS.value, "DATA_SOURCE_STATUS")
        self.assertEqual(DataClassification.TASK_SCHEDULE.value, "TASK_SCHEDULE")
        self.assertEqual(DataClassification.STRATEGY_PARAMS.value, "STRATEGY_PARAMS")
        self.assertEqual(DataClassification.SYSTEM_CONFIG.value, "SYSTEM_CONFIG")
        self.assertEqual(DataClassification.DATA_QUALITY_METRICS.value, "DATA_QUALITY_METRICS")
        self.assertEqual(DataClassification.USER_CONFIG.value, "USER_CONFIG")
        
    def test_database_target_enum_values(self):
        """测试数据库目标枚举值"""
        # 测试数据库目标枚举值 (当前架构只有TDengine和PostgreSQL)
        self.assertEqual(DatabaseTarget.TDENGINE.value, "tdengine")
        self.assertEqual(DatabaseTarget.POSTGRESQL.value, "postgresql")

    def test_data_classification_count(self):
        """测试数据分类数量"""
        # 验证枚举数量是否正确 (34个分类)
        all_classifications = list(DataClassification)
        self.assertEqual(len(all_classifications), 34)

    def test_database_target_count(self):
        """测试数据库目标数量"""
        # 验证数据库目标枚举数量 (2个: TDengine + PostgreSQL)
        all_targets = list(DatabaseTarget)
        self.assertEqual(len(all_targets), 2)


if __name__ == '__main__':
    unittest.main()