"""
数据存储策略模块

定义数据分类到数据库的智能路由逻辑。
根据数据特性自动选择最优存储引擎。

创建日期: 2025-10-11
版本: 1.0.0
"""

from typing import Dict
from .data_classification import DataClassification, DatabaseTarget


class DataStorageStrategy:
    """
    数据存储策略类

    实现数据分类到数据库的智能路由映射。
    基于数据特性和使用模式自动选择最优存储引擎。
    """

    # 数据分类到数据库的映射表
    CLASSIFICATION_TO_DATABASE: Dict[DataClassification, DatabaseTarget] = {
        # 高频时序数据 → TDengine (极致压缩和写入性能)
        DataClassification.TICK_DATA: DatabaseTarget.TDENGINE,
        DataClassification.MINUTE_KLINE: DatabaseTarget.TDENGINE,
        DataClassification.ORDER_BOOK_DEPTH: DatabaseTarget.TDENGINE,
        DataClassification.LEVEL2_SNAPSHOT: DatabaseTarget.TDENGINE,
        DataClassification.INDEX_QUOTES: DatabaseTarget.TDENGINE,
        # 日线及以上数据 → PostgreSQL (复杂查询和历史分析)
        DataClassification.DAILY_KLINE: DatabaseTarget.POSTGRESQL,
        # 参考数据 → PostgreSQL (复杂关系查询)
        DataClassification.SYMBOLS_INFO: DatabaseTarget.POSTGRESQL,
        DataClassification.INDUSTRY_CLASS: DatabaseTarget.POSTGRESQL,
        DataClassification.CONCEPT_CLASS: DatabaseTarget.POSTGRESQL,
        DataClassification.INDEX_CONSTITUENTS: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADE_CALENDAR: DatabaseTarget.POSTGRESQL,
        DataClassification.FUNDAMENTAL_METRICS: DatabaseTarget.POSTGRESQL,
        DataClassification.DIVIDEND_DATA: DatabaseTarget.POSTGRESQL,
        DataClassification.SHAREHOLDER_DATA: DatabaseTarget.POSTGRESQL,
        DataClassification.MARKET_RULES: DatabaseTarget.POSTGRESQL,
        # 衍生数据 → PostgreSQL (计算密集，多维度分析)
        DataClassification.TECHNICAL_INDICATORS: DatabaseTarget.POSTGRESQL,
        DataClassification.QUANT_FACTORS: DatabaseTarget.POSTGRESQL,
        DataClassification.MODEL_OUTPUT: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADE_SIGNALS: DatabaseTarget.POSTGRESQL,
        DataClassification.BACKTEST_RESULTS: DatabaseTarget.POSTGRESQL,
        DataClassification.RISK_METRICS: DatabaseTarget.POSTGRESQL,
        # 交易数据 → PostgreSQL (冷热分离，审计合规)
        DataClassification.ORDER_RECORDS: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADE_RECORDS: DatabaseTarget.POSTGRESQL,
        DataClassification.POSITION_HISTORY: DatabaseTarget.POSTGRESQL,
        DataClassification.REALTIME_POSITIONS: DatabaseTarget.POSTGRESQL,
        DataClassification.REALTIME_ACCOUNT: DatabaseTarget.POSTGRESQL,
        DataClassification.FUND_FLOW: DatabaseTarget.POSTGRESQL,
        DataClassification.ORDER_QUEUE: DatabaseTarget.POSTGRESQL,
        # 元数据 → PostgreSQL (配置和监控)
        DataClassification.DATA_SOURCE_STATUS: DatabaseTarget.POSTGRESQL,
        DataClassification.TASK_SCHEDULE: DatabaseTarget.POSTGRESQL,
        DataClassification.STRATEGY_PARAMS: DatabaseTarget.POSTGRESQL,
        DataClassification.SYSTEM_CONFIG: DatabaseTarget.POSTGRESQL,
        DataClassification.DATA_QUALITY_METRICS: DatabaseTarget.POSTGRESQL,
        DataClassification.USER_CONFIG: DatabaseTarget.POSTGRESQL,
    }

    @classmethod
    def get_database_target(cls, classification: DataClassification) -> DatabaseTarget:
        """
        根据数据分类获取对应的数据库目标

        Args:
            classification: 数据分类枚举值

        Returns:
            DatabaseTarget: 对应的数据库类型

        Raises:
            KeyError: 如果分类没有对应的数据库映射
        """
        if classification not in cls.CLASSIFICATION_TO_DATABASE:
            raise KeyError(f"No database mapping found for classification: {classification}")

        return cls.CLASSIFICATION_TO_DATABASE[classification]

    @classmethod
    def get_tdengine_classifications(cls) -> list[DataClassification]:
        """
        获取所有路由到TDengine的数据分类

        Returns:
            List[DataClassification]: TDengine数据分类列表
        """
        return [
            classification
            for classification, target in cls.CLASSIFICATION_TO_DATABASE.items()
            if target == DatabaseTarget.TDENGINE
        ]

    @classmethod
    def get_postgresql_classifications(cls) -> list[DataClassification]:
        """
        获取所有路由到PostgreSQL的数据分类

        Returns:
            List[DataClassification]: PostgreSQL数据分类列表
        """
        return [
            classification
            for classification, target in cls.CLASSIFICATION_TO_DATABASE.items()
            if target == DatabaseTarget.POSTGRESQL
        ]

    @classmethod
    def is_high_frequency_data(cls, classification: DataClassification) -> bool:
        """
        判断是否为高频数据

        Args:
            classification: 数据分类

        Returns:
            bool: 是否为高频数据
        """
        high_freq_classifications = {
            DataClassification.TICK_DATA,
            DataClassification.MINUTE_KLINE,
            DataClassification.ORDER_BOOK_DEPTH,
            DataClassification.LEVEL2_SNAPSHOT,
            DataClassification.INDEX_QUOTES,
        }
        return classification in high_freq_classifications

    @classmethod
    def is_reference_data(cls, classification: DataClassification) -> bool:
        """
        判断是否为参考数据

        Args:
            classification: 数据分类

        Returns:
            bool: 是否为参考数据
        """
        reference_classifications = {
            DataClassification.SYMBOLS_INFO,
            DataClassification.INDUSTRY_CLASS,
            DataClassification.CONCEPT_CLASS,
            DataClassification.INDEX_CONSTITUENTS,
            DataClassification.TRADE_CALENDAR,
            DataClassification.FUNDAMENTAL_METRICS,
            DataClassification.DIVIDEND_DATA,
            DataClassification.SHAREHOLDER_DATA,
            DataClassification.MARKET_RULES,
        }
        return classification in reference_classifications


# 版本信息
__version__ = "1.0.0"
__all__ = ["DataStorageStrategy"]
