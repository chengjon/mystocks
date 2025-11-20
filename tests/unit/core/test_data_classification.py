"""
DataClassification和DatabaseTarget枚举单元测试

测试数据分类和数据库目标枚举的完整性和一致性
"""

import pytest
import sys

# 确保能导入src模块
sys.path.insert(0, "/opt/claude/mystocks_spec")

from src.core.data_classification import DataClassification, DatabaseTarget, DeduplicationStrategy


class TestDataClassificationEnum:
    """测试DataClassification枚举定义"""

    def test_all_classifications_exist(self):
        """测试所有数据分类都存在"""
        all_classifications = DataClassification.get_all_classifications()
        # 实际枚举成员数量
        enum_members = list(DataClassification)
        assert len(all_classifications) == len(enum_members)

    def test_market_data_classifications_count(self):
        """测试市场数据分类有6项"""
        market_data = DataClassification.get_market_data_classifications()
        assert len(market_data) == 6

    def test_reference_data_classifications_count(self):
        """测试参考数据分类有9项"""
        reference_data = DataClassification.get_reference_data_classifications()
        assert len(reference_data) == 9

    def test_derived_data_classifications_count(self):
        """测试衍生数据分类有6项"""
        derived_data = DataClassification.get_derived_data_classifications()
        assert len(derived_data) == 6

    def test_transaction_data_classifications_count(self):
        """测试交易数据分类有7项"""
        transaction_data = DataClassification.get_transaction_data_classifications()
        assert len(transaction_data) == 7

    def test_metadata_classifications_count(self):
        """测试元数据分类有6项"""
        metadata = DataClassification.get_metadata_classifications()
        assert len(metadata) == 6

    def test_sum_of_classifications_matches_total(self):
        """测试所有子分类数量之和等于总数"""
        market = DataClassification.get_market_data_classifications()
        reference = DataClassification.get_reference_data_classifications()
        derived = DataClassification.get_derived_data_classifications()
        transaction = DataClassification.get_transaction_data_classifications()
        metadata = DataClassification.get_metadata_classifications()

        total = len(market) + len(reference) + len(derived) + len(transaction) + len(metadata)
        all_classifications = DataClassification.get_all_classifications()
        assert total == len(all_classifications)

    def test_no_duplicate_classifications(self):
        """测试没有重复的数据分类"""
        all_classifications = DataClassification.get_all_classifications()
        assert len(all_classifications) == len(set(all_classifications))

    def test_all_category_values_in_total(self):
        """测试所有子分类都包含在总分类中"""
        all_classifications = set(DataClassification.get_all_classifications())

        market = set(DataClassification.get_market_data_classifications())
        reference = set(DataClassification.get_reference_data_classifications())
        derived = set(DataClassification.get_derived_data_classifications())
        transaction = set(DataClassification.get_transaction_data_classifications())
        metadata = set(DataClassification.get_metadata_classifications())

        combined = market | reference | derived | transaction | metadata

        assert combined == all_classifications


class TestDataClassificationMarketData:
    """测试市场数据分类 (6项)"""

    def test_tick_data_exists(self):
        """测试TICK_DATA分类存在"""
        assert DataClassification.TICK_DATA.value == "TICK_DATA"
        assert DataClassification.TICK_DATA.value in DataClassification.get_market_data_classifications()

    def test_minute_kline_exists(self):
        """测试MINUTE_KLINE分类存在"""
        assert DataClassification.MINUTE_KLINE.value == "MINUTE_KLINE"
        assert DataClassification.MINUTE_KLINE.value in DataClassification.get_market_data_classifications()

    def test_daily_kline_exists(self):
        """测试DAILY_KLINE分类存在"""
        assert DataClassification.DAILY_KLINE.value == "DAILY_KLINE"
        assert DataClassification.DAILY_KLINE.value in DataClassification.get_market_data_classifications()

    def test_order_book_depth_exists(self):
        """测试ORDER_BOOK_DEPTH分类存在"""
        assert DataClassification.ORDER_BOOK_DEPTH.value == "ORDER_BOOK_DEPTH"
        assert DataClassification.ORDER_BOOK_DEPTH.value in DataClassification.get_market_data_classifications()

    def test_level2_snapshot_exists(self):
        """测试LEVEL2_SNAPSHOT分类存在"""
        assert DataClassification.LEVEL2_SNAPSHOT.value == "LEVEL2_SNAPSHOT"
        assert DataClassification.LEVEL2_SNAPSHOT.value in DataClassification.get_market_data_classifications()

    def test_index_quotes_exists(self):
        """测试INDEX_QUOTES分类存在"""
        assert DataClassification.INDEX_QUOTES.value == "INDEX_QUOTES"
        assert DataClassification.INDEX_QUOTES.value in DataClassification.get_market_data_classifications()


class TestDataClassificationReferenceData:
    """测试参考数据分类 (9项)"""

    def test_symbols_info_exists(self):
        """测试SYMBOLS_INFO分类存在"""
        assert DataClassification.SYMBOLS_INFO.value == "SYMBOLS_INFO"
        assert DataClassification.SYMBOLS_INFO.value in DataClassification.get_reference_data_classifications()

    def test_industry_class_exists(self):
        """测试INDUSTRY_CLASS分类存在"""
        assert DataClassification.INDUSTRY_CLASS.value == "INDUSTRY_CLASS"
        assert DataClassification.INDUSTRY_CLASS.value in DataClassification.get_reference_data_classifications()

    def test_concept_class_exists(self):
        """测试CONCEPT_CLASS分类存在"""
        assert DataClassification.CONCEPT_CLASS.value == "CONCEPT_CLASS"
        assert DataClassification.CONCEPT_CLASS.value in DataClassification.get_reference_data_classifications()

    def test_index_constituents_exists(self):
        """测试INDEX_CONSTITUENTS分类存在"""
        assert DataClassification.INDEX_CONSTITUENTS.value == "INDEX_CONSTITUENTS"
        assert DataClassification.INDEX_CONSTITUENTS.value in DataClassification.get_reference_data_classifications()

    def test_trade_calendar_exists(self):
        """测试TRADE_CALENDAR分类存在"""
        assert DataClassification.TRADE_CALENDAR.value == "TRADE_CALENDAR"
        assert DataClassification.TRADE_CALENDAR.value in DataClassification.get_reference_data_classifications()


class TestDataClassificationDerivedData:
    """测试衍生数据分类 (6项)"""

    def test_technical_indicators_exists(self):
        """测试TECHNICAL_INDICATORS分类存在"""
        assert DataClassification.TECHNICAL_INDICATORS.value == "TECHNICAL_INDICATORS"
        assert DataClassification.TECHNICAL_INDICATORS.value in DataClassification.get_derived_data_classifications()

    def test_quant_factors_exists(self):
        """测试QUANT_FACTORS分类存在"""
        assert DataClassification.QUANT_FACTORS.value == "QUANT_FACTORS"
        assert DataClassification.QUANT_FACTORS.value in DataClassification.get_derived_data_classifications()

    def test_model_output_exists(self):
        """测试MODEL_OUTPUT分类存在"""
        assert DataClassification.MODEL_OUTPUT.value == "MODEL_OUTPUT"
        assert DataClassification.MODEL_OUTPUT.value in DataClassification.get_derived_data_classifications()

    def test_trade_signals_exists(self):
        """测试TRADE_SIGNALS分类存在"""
        assert DataClassification.TRADE_SIGNALS.value == "TRADE_SIGNALS"
        assert DataClassification.TRADE_SIGNALS.value in DataClassification.get_derived_data_classifications()

    def test_backtest_results_exists(self):
        """测试BACKTEST_RESULTS分类存在"""
        assert DataClassification.BACKTEST_RESULTS.value == "BACKTEST_RESULTS"
        assert DataClassification.BACKTEST_RESULTS.value in DataClassification.get_derived_data_classifications()

    def test_risk_metrics_exists(self):
        """测试RISK_METRICS分类存在"""
        assert DataClassification.RISK_METRICS.value == "RISK_METRICS"
        assert DataClassification.RISK_METRICS.value in DataClassification.get_derived_data_classifications()


class TestDataClassificationTransactionData:
    """测试交易数据分类 (7项)"""

    def test_order_records_exists(self):
        """测试ORDER_RECORDS分类存在"""
        assert DataClassification.ORDER_RECORDS.value == "ORDER_RECORDS"
        assert DataClassification.ORDER_RECORDS.value in DataClassification.get_transaction_data_classifications()

    def test_trade_records_exists(self):
        """测试TRADE_RECORDS分类存在"""
        assert DataClassification.TRADE_RECORDS.value == "TRADE_RECORDS"
        assert DataClassification.TRADE_RECORDS.value in DataClassification.get_transaction_data_classifications()

    def test_realtime_positions_exists(self):
        """测试REALTIME_POSITIONS分类存在"""
        assert DataClassification.REALTIME_POSITIONS.value == "REALTIME_POSITIONS"
        assert DataClassification.REALTIME_POSITIONS.value in DataClassification.get_transaction_data_classifications()

    def test_realtime_account_exists(self):
        """测试REALTIME_ACCOUNT分类存在"""
        assert DataClassification.REALTIME_ACCOUNT.value == "REALTIME_ACCOUNT"
        assert DataClassification.REALTIME_ACCOUNT.value in DataClassification.get_transaction_data_classifications()


class TestDataClassificationMetadata:
    """测试元数据分类 (6项)"""

    def test_data_source_status_exists(self):
        """测试DATA_SOURCE_STATUS分类存在"""
        assert DataClassification.DATA_SOURCE_STATUS.value == "DATA_SOURCE_STATUS"
        assert DataClassification.DATA_SOURCE_STATUS.value in DataClassification.get_metadata_classifications()

    def test_task_schedule_exists(self):
        """测试TASK_SCHEDULE分类存在"""
        assert DataClassification.TASK_SCHEDULE.value == "TASK_SCHEDULE"
        assert DataClassification.TASK_SCHEDULE.value in DataClassification.get_metadata_classifications()

    def test_strategy_params_exists(self):
        """测试STRATEGY_PARAMS分类存在"""
        assert DataClassification.STRATEGY_PARAMS.value == "STRATEGY_PARAMS"
        assert DataClassification.STRATEGY_PARAMS.value in DataClassification.get_metadata_classifications()

    def test_system_config_exists(self):
        """测试SYSTEM_CONFIG分类存在"""
        assert DataClassification.SYSTEM_CONFIG.value == "SYSTEM_CONFIG"
        assert DataClassification.SYSTEM_CONFIG.value in DataClassification.get_metadata_classifications()

    def test_data_quality_metrics_exists(self):
        """测试DATA_QUALITY_METRICS分类存在"""
        assert DataClassification.DATA_QUALITY_METRICS.value == "DATA_QUALITY_METRICS"
        assert DataClassification.DATA_QUALITY_METRICS.value in DataClassification.get_metadata_classifications()

    def test_user_config_exists(self):
        """测试USER_CONFIG分类存在"""
        assert DataClassification.USER_CONFIG.value == "USER_CONFIG"
        assert DataClassification.USER_CONFIG.value in DataClassification.get_metadata_classifications()


class TestDatabaseTargetEnum:
    """测试DatabaseTarget枚举"""

    def test_all_2_database_targets_exist(self):
        """测试所有2种数据库类型都存在"""
        all_targets = DatabaseTarget.get_all_targets()
        assert len(all_targets) == 2

    def test_tdengine_target_exists(self):
        """测试TDengine数据库类型存在"""
        assert DatabaseTarget.TDENGINE.value == "tdengine"
        assert DatabaseTarget.TDENGINE.value in DatabaseTarget.get_all_targets()

    def test_postgresql_target_exists(self):
        """测试PostgreSQL数据库类型存在"""
        assert DatabaseTarget.POSTGRESQL.value == "postgresql"
        assert DatabaseTarget.POSTGRESQL.value in DatabaseTarget.get_all_targets()

    def test_no_duplicate_database_targets(self):
        """测试没有重复的数据库类型"""
        all_targets = DatabaseTarget.get_all_targets()
        assert len(all_targets) == len(set(all_targets))

    def test_database_target_values_are_lowercase(self):
        """测试所有数据库类型值都是小写"""
        all_targets = DatabaseTarget.get_all_targets()
        for target in all_targets:
            assert target.islower(), f"Database target {target} should be lowercase"


class TestEnumStringBehavior:
    """测试枚举的字符串行为"""

    def test_data_classification_string_value(self):
        """测试DataClassification枚举可作为字符串使用"""
        classification = DataClassification.TICK_DATA
        assert classification.value == "TICK_DATA"
        assert str(classification) == "DataClassification.TICK_DATA"

    def test_database_target_string_value(self):
        """测试DatabaseTarget枚举可作为字符串使用"""
        target = DatabaseTarget.TDENGINE
        assert target.value == "tdengine"
        assert str(target) == "DatabaseTarget.TDENGINE"

    def test_data_classification_equality(self):
        """测试DataClassification枚举相等性"""
        assert DataClassification.TICK_DATA == DataClassification.TICK_DATA
        assert DataClassification.TICK_DATA != DataClassification.MINUTE_KLINE

    def test_database_target_equality(self):
        """测试DatabaseTarget枚举相等性"""
        assert DatabaseTarget.TDENGINE == DatabaseTarget.TDENGINE
        assert DatabaseTarget.TDENGINE != DatabaseTarget.POSTGRESQL


class TestEnumIteration:
    """测试枚举迭代功能"""

    def test_can_iterate_data_classifications(self):
        """测试可以迭代DataClassification"""
        classifications = list(DataClassification)
        # 验证枚举包含所有定义的成员
        all_values = DataClassification.get_all_classifications()
        assert len(classifications) == len(all_values)
        assert DataClassification.TICK_DATA in classifications

    def test_can_iterate_database_targets(self):
        """测试可以迭代DatabaseTarget"""
        targets = list(DatabaseTarget)
        assert len(targets) == 2
        assert DatabaseTarget.TDENGINE in targets


class TestModuleMetadata:
    """测试模块元数据"""

    def test_module_version_exists(self):
        """测试模块版本信息存在"""
        from src.core import data_classification
        assert hasattr(data_classification, '__version__')
        assert data_classification.__version__ == "1.0.0"

    def test_module_exports_correct_classes(self):
        """测试模块正确导出类"""
        from src.core import data_classification
        assert hasattr(data_classification, '__all__')
        assert "DataClassification" in data_classification.__all__
        assert "DatabaseTarget" in data_classification.__all__


class TestDeduplicationStrategy:
    """测试DeduplicationStrategy枚举"""

    def test_deduplication_strategy_values(self):
        """测试去重策略值"""
        assert DeduplicationStrategy.LATEST_WINS.value == "latest_wins"
        assert DeduplicationStrategy.FIRST_WINS.value == "first_wins"
        assert DeduplicationStrategy.MERGE.value == "merge"
        assert DeduplicationStrategy.REJECT.value == "reject"

    def test_get_all_strategies(self):
        """测试获取所有去重策略"""
        strategies = DeduplicationStrategy.get_all_strategies()
        assert len(strategies) == 4
        assert "latest_wins" in strategies
        assert "first_wins" in strategies
        assert "merge" in strategies
        assert "reject" in strategies

    def test_deduplication_strategy_is_string_enum(self):
        """测试DeduplicationStrategy继承自str"""
        assert isinstance(DeduplicationStrategy.LATEST_WINS, str)
        assert DeduplicationStrategy.LATEST_WINS == "latest_wins"

    def test_module_exports_deduplication_strategy(self):
        """测试模块导出DeduplicationStrategy"""
        from src.core import data_classification
        assert "DeduplicationStrategy" in data_classification.__all__
        assert hasattr(data_classification, "DeduplicationStrategy")
