"""
数据存储策略 (Week 3简化后 - PostgreSQL-only)

统一路由所有23个数据分类到PostgreSQL+TimescaleDB。
基于TimescaleDB的hypertable优化时序数据存储。

创建日期: 2025-10-11
版本: 2.0.0 (Week 3 PostgreSQL-only架构)
"""

from typing import Dict, List, Optional
from enum import Enum

from core.data_classification import DataClassification, DatabaseTarget


class DataStorageStrategy:
    """
    数据存储策略 (Week 3简化后 - PostgreSQL-only)

    统一路由所有数据分类到PostgreSQL+TimescaleDB:
    - 高频时序数据 → PostgreSQL TimescaleDB hypertables (自动压缩 + 分区)
    - 历史分析数据 → PostgreSQL 标准表 (复杂查询 + 事务支持)
    - 参考元数据 → PostgreSQL 标准表 (ACID + 索引优化)
    - 实时热数据 → PostgreSQL (应用层缓存支持)
    """

    # 静态路由映射表 (Week 3简化后 - 所有数据统一路由到PostgreSQL)
    _ROUTING_MAP: Dict[DataClassification, DatabaseTarget] = {
        # 市场数据 (6项) - 高频时序 → PostgreSQL TimescaleDB hypertables
        DataClassification.TICK_DATA: DatabaseTarget.POSTGRESQL,
        DataClassification.MINUTE_KLINE: DatabaseTarget.POSTGRESQL,
        DataClassification.DAILY_KLINE: DatabaseTarget.POSTGRESQL,
        DataClassification.ORDER_BOOK_DEPTH: DatabaseTarget.POSTGRESQL,
        DataClassification.LEVEL2_SNAPSHOT: DatabaseTarget.POSTGRESQL,
        DataClassification.INDEX_QUOTES: DatabaseTarget.POSTGRESQL,
        # 参考数据 (9项) - 相对静态 → PostgreSQL 标准表
        DataClassification.SYMBOLS_INFO: DatabaseTarget.POSTGRESQL,
        DataClassification.INDUSTRY_CLASS: DatabaseTarget.POSTGRESQL,
        DataClassification.CONCEPT_CLASS: DatabaseTarget.POSTGRESQL,
        DataClassification.INDEX_CONSTITUENTS: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADE_CALENDAR: DatabaseTarget.POSTGRESQL,
        DataClassification.FUNDAMENTAL_METRICS: DatabaseTarget.POSTGRESQL,
        DataClassification.DIVIDEND_DATA: DatabaseTarget.POSTGRESQL,
        DataClassification.SHAREHOLDER_DATA: DatabaseTarget.POSTGRESQL,
        DataClassification.MARKET_RULES: DatabaseTarget.POSTGRESQL,
        # 衍生数据 (6项) - 计算结果 → PostgreSQL 标准表
        DataClassification.TECHNICAL_INDICATORS: DatabaseTarget.POSTGRESQL,
        DataClassification.QUANT_FACTORS: DatabaseTarget.POSTGRESQL,
        DataClassification.MODEL_OUTPUT: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADE_SIGNALS: DatabaseTarget.POSTGRESQL,
        DataClassification.BACKTEST_RESULTS: DatabaseTarget.POSTGRESQL,
        DataClassification.RISK_METRICS: DatabaseTarget.POSTGRESQL,
        # 交易数据 (7项) - 统一存储 → PostgreSQL (应用层缓存实时数据)
        DataClassification.ORDER_RECORDS: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADE_RECORDS: DatabaseTarget.POSTGRESQL,
        DataClassification.POSITION_HISTORY: DatabaseTarget.POSTGRESQL,
        DataClassification.REALTIME_POSITIONS: DatabaseTarget.POSTGRESQL,
        DataClassification.REALTIME_ACCOUNT: DatabaseTarget.POSTGRESQL,
        DataClassification.FUND_FLOW: DatabaseTarget.POSTGRESQL,
        DataClassification.ORDER_QUEUE: DatabaseTarget.POSTGRESQL,
        # 元数据 (6项) - 配置管理 → PostgreSQL 标准表
        DataClassification.DATA_SOURCE_STATUS: DatabaseTarget.POSTGRESQL,
        DataClassification.TASK_SCHEDULE: DatabaseTarget.POSTGRESQL,
        DataClassification.STRATEGY_PARAMS: DatabaseTarget.POSTGRESQL,
        DataClassification.SYSTEM_CONFIG: DatabaseTarget.POSTGRESQL,
        DataClassification.DATA_QUALITY_METRICS: DatabaseTarget.POSTGRESQL,
        DataClassification.USER_CONFIG: DatabaseTarget.POSTGRESQL,
    }

    @classmethod
    def get_target_database(cls, classification: DataClassification) -> DatabaseTarget:
        """
        根据数据分类获取目标数据库

        Args:
            classification: 数据分类枚举

        Returns:
            目标数据库类型

        Raises:
            ValueError: 未知的数据分类
        """
        if classification not in cls._ROUTING_MAP:
            raise ValueError(
                f"未知的数据分类: {classification}\n"
                f"支持的分类: {list(cls._ROUTING_MAP.keys())}"
            )

        return cls._ROUTING_MAP[classification]

    @classmethod
    def get_classifications_by_database(
        cls, database: DatabaseTarget
    ) -> List[DataClassification]:
        """
        获取指定数据库负责的所有数据分类

        Args:
            database: 数据库类型

        Returns:
            数据分类列表
        """
        return [
            classification
            for classification, target in cls._ROUTING_MAP.items()
            if target == database
        ]

    @classmethod
    def validate_routing_completeness(cls) -> bool:
        """
        验证路由映射是否完整 (覆盖所有23个数据分类)

        Returns:
            True: 路由完整
            False: 存在未映射的分类
        """
        all_classifications = set(DataClassification)
        mapped_classifications = set(cls._ROUTING_MAP.keys())

        missing = all_classifications - mapped_classifications

        if missing:
            print(f"警告: 以下数据分类未配置路由: {missing}")
            return False

        return True

    @classmethod
    def get_routing_statistics(cls) -> Dict[DatabaseTarget, int]:
        """
        获取路由分布统计

        Returns:
            各数据库负责的数据分类数量
        """
        stats = {db: 0 for db in DatabaseTarget}

        for target in cls._ROUTING_MAP.values():
            stats[target] += 1

        return stats

    @classmethod
    def print_routing_map(cls):
        """打印完整的路由映射表 (用于调试和文档)"""
        print("=" * 80)
        print("数据存储路由映射表")
        print("=" * 80)

        for db_type in DatabaseTarget:
            classifications = cls.get_classifications_by_database(db_type)
            print(f"\n{db_type.value.upper()} ({len(classifications)}项):")
            for i, classification in enumerate(classifications, 1):
                print(f"  {i}. {classification.value}")

        print("\n" + "=" * 80)
        print("路由统计:")
        stats = cls.get_routing_statistics()
        for db_type, count in stats.items():
            percentage = (count / 23) * 100
            print(f"  {db_type.value}: {count}项 ({percentage:.1f}%)")

        print(f"\n总计: {sum(stats.values())}/23 项已配置路由")
        print("=" * 80)


class DataStorageRules:
    """
    数据存储规则 (Week 3简化后 - PostgreSQL-only)

    定义PostgreSQL的存储策略、保留周期、TimescaleDB压缩策略等
    """

    # 数据保留周期 (天) - 所有数据类型统一在PostgreSQL中管理
    RETENTION_POLICY = {
        DatabaseTarget.POSTGRESQL: {
            # 高频时序数据 (通过TimescaleDB自动压缩和分区管理)
            DataClassification.TICK_DATA: 30,  # Tick数据保留30天
            DataClassification.MINUTE_KLINE: 90,  # 分钟线保留90天
            DataClassification.ORDER_BOOK_DEPTH: 30,  # 盘口深度保留30天
            DataClassification.LEVEL2_SNAPSHOT: 30,  # L2快照保留30天
            DataClassification.INDEX_QUOTES: 365,  # 指数行情保留1年
            # 历史分析数据 (长期保留,通过TimescaleDB自动分区管理)
            DataClassification.DAILY_KLINE: 3650,  # 日线保留10年
            DataClassification.TECHNICAL_INDICATORS: 1825,  # 技术指标保留5年
            DataClassification.BACKTEST_RESULTS: 1825,  # 回测结果保留5年
            # 实时数据 (应用层缓存支持,数据库持久化)
            DataClassification.REALTIME_POSITIONS: None,  # 持久化,无过期
            DataClassification.REALTIME_ACCOUNT: None,  # 持久化,无过期
            DataClassification.ORDER_QUEUE: 7,  # 订单队列保留7天
            # 参考数据和元数据 (永久保留,业务逻辑定期清理)
            # 其他分类默认永久保留
        }
    }

    @classmethod
    def get_retention_days(cls, classification: DataClassification) -> Optional[int]:
        """
        获取数据保留天数 (Week 3简化后 - PostgreSQL-only)

        Args:
            classification: 数据分类

        Returns:
            保留天数 (None表示永久保留)
        """
        target_db = DataStorageStrategy.get_target_database(classification)

        if target_db in cls.RETENTION_POLICY:
            return cls.RETENTION_POLICY[target_db].get(classification)

        return None  # 默认永久保留


if __name__ == "__main__":
    """测试路由策略"""
    print("\n正在验证数据存储路由策略...\n")

    # 1. 验证路由完整性
    is_complete = DataStorageStrategy.validate_routing_completeness()
    print(f"路由完整性: {'✅ 通过' if is_complete else '❌ 失败'}\n")

    # 2. 打印路由映射表
    DataStorageStrategy.print_routing_map()

    # 3. 测试示例路由
    print("\n示例路由测试:")
    test_cases = [
        DataClassification.TICK_DATA,
        DataClassification.SYMBOLS_INFO,
        DataClassification.QUANT_FACTORS,
        DataClassification.REALTIME_POSITIONS,
    ]

    for classification in test_cases:
        target = DataStorageStrategy.get_target_database(classification)
        retention = DataStorageRules.get_retention_days(classification)
        retention_str = f"{retention}天" if retention else "永久保留"

        print(f"  {classification.value}")
        print(f"    → {target.value.upper()}")
        print(f"    → 保留周期: {retention_str}")
