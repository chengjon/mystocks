from typing import Dict, Optional

from src.core.data_classification import DatabaseTarget, DataClassification


class DataRouter:
    """
    负责数据分类到存储目标的路由策略。
    从 DataManager 中分离，单一职责。
    """

    # 默认路由映射
    _DEFAULT_ROUTING_MAP: Dict[DataClassification, DatabaseTarget] = {
        # 第1类：市场数据 (6项) - 高频时序 → TDengine
        DataClassification.TICK_DATA: DatabaseTarget.TDENGINE,
        DataClassification.MINUTE_KLINE: DatabaseTarget.TDENGINE,
        DataClassification.DAILY_KLINE: DatabaseTarget.POSTGRESQL,
        DataClassification.ORDER_BOOK_DEPTH: DatabaseTarget.TDENGINE,
        DataClassification.LEVEL2_SNAPSHOT: DatabaseTarget.TDENGINE,
        DataClassification.INDEX_QUOTES: DatabaseTarget.TDENGINE,
        # 第2类：参考数据 (9项) → PostgreSQL
        DataClassification.SYMBOLS_INFO: DatabaseTarget.POSTGRESQL,
        DataClassification.INDUSTRY_CLASS: DatabaseTarget.POSTGRESQL,
        DataClassification.CONCEPT_CLASS: DatabaseTarget.POSTGRESQL,
        DataClassification.INDEX_CONSTITUENTS: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADE_CALENDAR: DatabaseTarget.POSTGRESQL,
        DataClassification.FUNDAMENTAL_METRICS: DatabaseTarget.POSTGRESQL,
        DataClassification.DIVIDEND_DATA: DatabaseTarget.POSTGRESQL,
        DataClassification.SHAREHOLDER_DATA: DatabaseTarget.POSTGRESQL,
        DataClassification.MARKET_RULES: DatabaseTarget.POSTGRESQL,
        # 第3类：衍生数据 (6项) → PostgreSQL+TimescaleDB
        DataClassification.TECHNICAL_INDICATORS: DatabaseTarget.POSTGRESQL,
        DataClassification.QUANT_FACTORS: DatabaseTarget.POSTGRESQL,
        DataClassification.MODEL_OUTPUT: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADE_SIGNALS: DatabaseTarget.POSTGRESQL,
        DataClassification.BACKTEST_RESULTS: DatabaseTarget.POSTGRESQL,
        DataClassification.RISK_METRICS: DatabaseTarget.POSTGRESQL,
        # 第4类：交易数据 (7项) → PostgreSQL
        DataClassification.ORDER_RECORDS: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADE_RECORDS: DatabaseTarget.POSTGRESQL,
        DataClassification.POSITION_HISTORY: DatabaseTarget.POSTGRESQL,
        DataClassification.REALTIME_POSITIONS: DatabaseTarget.POSTGRESQL,
        DataClassification.REALTIME_ACCOUNT: DatabaseTarget.POSTGRESQL,
        DataClassification.FUND_FLOW: DatabaseTarget.POSTGRESQL,
        DataClassification.ORDER_QUEUE: DatabaseTarget.POSTGRESQL,
        # 第5类：元数据 (6项) → PostgreSQL
        DataClassification.DATA_SOURCE_STATUS: DatabaseTarget.POSTGRESQL,
        DataClassification.TASK_SCHEDULE: DatabaseTarget.POSTGRESQL,
        DataClassification.STRATEGY_PARAMS: DatabaseTarget.POSTGRESQL,
        DataClassification.SYSTEM_CONFIG: DatabaseTarget.POSTGRESQL,
        DataClassification.DATA_QUALITY_METRICS: DatabaseTarget.POSTGRESQL,
        DataClassification.USER_CONFIG: DatabaseTarget.POSTGRESQL,
    }

    def __init__(self, custom_mapping: Optional[Dict[DataClassification, DatabaseTarget]] = None):
        self._routing_map = self._DEFAULT_ROUTING_MAP.copy()
        if custom_mapping:
            self._routing_map.update(custom_mapping)

    def get_target_database(self, classification: DataClassification) -> DatabaseTarget:
        """获取目标数据库"""
        return self._routing_map.get(classification, DatabaseTarget.POSTGRESQL)

    def get_stats(self) -> Dict:
        """获取路由统计"""
        return {
            "total_rules": len(self._routing_map),
            "tdengine_targets": sum(1 for t in self._routing_map.values() if t == DatabaseTarget.TDENGINE),
            "postgresql_targets": sum(1 for t in self._routing_map.values() if t == DatabaseTarget.POSTGRESQL),
        }
