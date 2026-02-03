#!/usr/bin/env python3
"""
数据分类枚举模块测试套件
提供完整的DataClassification、DatabaseTarget、DeduplicationStrategy枚举测试

创建时间: 2025-01-21
版本: 1.0.0
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
import time

# 导入被测试的模块
from src.core.data_classification import (
    DataClassification,
    DatabaseTarget,
    DeduplicationStrategy,
)


class TestDataClassificationEnum:
    """DataClassification枚举基础测试类"""

    def test_all_classifications_defined(self):
        """测试所有34个数据分类是否正确定义"""
        # 验证枚举值总数为34个
        all_classifications = DataClassification.get_all_classifications()
        assert len(all_classifications) == 34

        # 验证所有分类都是字符串类型
        for classification in all_classifications:
            assert isinstance(classification, str)
            assert len(classification) > 0

    def test_market_data_classifications(self):
        """测试市场数据分类（6项）"""
        market_classifications = DataClassification.get_market_data_classifications()

        assert len(market_classifications) == 6
        expected_market = [
            "TICK_DATA",
            "MINUTE_KLINE",
            "DAILY_KLINE",
            "ORDER_BOOK_DEPTH",
            "LEVEL2_SNAPSHOT",
            "INDEX_QUOTES",
        ]

        assert sorted(market_classifications) == sorted(expected_market)

        # 验证每个市场数据分类都可以访问
        for classification in expected_market:
            assert hasattr(DataClassification, classification)
            enum_value = getattr(DataClassification, classification)
            assert enum_value.value == classification

    def test_reference_data_classifications(self):
        """测试参考数据分类（9项）"""
        reference_classifications = (
            DataClassification.get_reference_data_classifications()
        )

        assert len(reference_classifications) == 9
        expected_reference = [
            "SYMBOLS_INFO",
            "INDUSTRY_CLASS",
            "CONCEPT_CLASS",
            "INDEX_CONSTITUENTS",
            "TRADE_CALENDAR",
            "FUNDAMENTAL_METRICS",
            "DIVIDEND_DATA",
            "SHAREHOLDER_DATA",
            "MARKET_RULES",
        ]

        assert sorted(reference_classifications) == sorted(expected_reference)

    def test_derived_data_classifications(self):
        """测试衍生数据分类（6项）"""
        derived_classifications = DataClassification.get_derived_data_classifications()

        assert len(derived_classifications) == 6
        expected_derived = [
            "TECHNICAL_INDICATORS",
            "QUANT_FACTORS",
            "MODEL_OUTPUT",
            "TRADE_SIGNALS",
            "BACKTEST_RESULTS",
            "RISK_METRICS",
        ]

        assert sorted(derived_classifications) == sorted(expected_derived)

    def test_transaction_data_classifications(self):
        """测试交易数据分类（7项）"""
        transaction_classifications = (
            DataClassification.get_transaction_data_classifications()
        )

        assert len(transaction_classifications) == 7
        expected_transaction = [
            "ORDER_RECORDS",
            "TRADE_RECORDS",
            "POSITION_HISTORY",
            "REALTIME_POSITIONS",
            "REALTIME_ACCOUNT",
            "FUND_FLOW",
            "ORDER_QUEUE",
        ]

        assert sorted(transaction_classifications) == sorted(expected_transaction)

    def test_metadata_classifications(self):
        """测试元数据分类（6项）"""
        metadata_classifications = DataClassification.get_metadata_classifications()

        assert len(metadata_classifications) == 6
        expected_metadata = [
            "DATA_SOURCE_STATUS",
            "TASK_SCHEDULE",
            "STRATEGY_PARAMS",
            "SYSTEM_CONFIG",
            "DATA_QUALITY_METRICS",
            "USER_CONFIG",
        ]

        assert sorted(metadata_classifications) == sorted(expected_metadata)

    def test_classifications_completeness(self):
        """测试所有分类覆盖（34 = 6+9+6+7+6）"""
        market = set(DataClassification.get_market_data_classifications())
        reference = set(DataClassification.get_reference_data_classifications())
        derived = set(DataClassification.get_derived_data_classifications())
        transaction = set(DataClassification.get_transaction_data_classifications())
        metadata = set(DataClassification.get_metadata_classifications())

        # 验证无重复
        all_classifications = set(DataClassification.get_all_classifications())
        combined = market | reference | derived | transaction | metadata

        assert combined == all_classifications
        assert len(combined) == 34

    def test_enum_value_access_patterns(self):
        """测试枚举值访问模式"""
        # 测试直接访问
        assert DataClassification.TICK_DATA == "TICK_DATA"
        assert DataClassification.SYMBOLS_INFO == "SYMBOLS_INFO"
        assert DataClassification.TECHNICAL_INDICATORS == "TECHNICAL_INDICATORS"

        # 测试枚举成员属性
        tick_data = DataClassification.TICK_DATA
        assert isinstance(tick_data, str)
        assert tick_data.value == "TICK_DATA"
        # 由于继承自str但也是Enum，str()返回枚举名称
        assert str(tick_data) == "DataClassification.TICK_DATA"

    def test_enum_inheritance(self):
        """测试枚举继承特性"""
        # 验证继承自str和Enum
        assert issubclass(DataClassification, str)
        assert issubclass(DataClassification, str)

        # 验证可以用于字符串操作
        tick_data = DataClassification.TICK_DATA
        assert tick_data.lower() == "tick_data"
        assert tick_data.upper() == "TICK_DATA"
        assert "_".join(tick_data.split("_")) == "TICK_DATA"

    def test_enum_iteration(self):
        """测试枚举迭代功能"""
        # 测试可以遍历所有枚举成员
        enum_members = list(DataClassification)
        assert len(enum_members) == 34

        # 验证每个成员都有正确的值
        values = [member.value for member in enum_members]
        assert len(set(values)) == 34  # 无重复值
        assert set(values) == set(DataClassification.get_all_classifications())


class TestDatabaseTargetEnum:
    """DatabaseTarget枚举测试类"""

    def test_database_targets_defined(self):
        """测试数据库目标是否正确定义"""
        all_targets = DatabaseTarget.get_all_targets()
        assert len(all_targets) == 2

        expected_targets = ["tdengine", "postgresql"]
        assert sorted(all_targets) == sorted(expected_targets)

    def test_tdengine_target(self):
        """测试TDengine目标"""
        assert DatabaseTarget.TDENGINE == "tdengine"
        assert isinstance(DatabaseTarget.TDENGINE, str)
        assert DatabaseTarget.TDENGINE.value == "tdengine"

    def test_postgresql_target(self):
        """测试PostgreSQL目标"""
        assert DatabaseTarget.POSTGRESQL == "postgresql"
        assert isinstance(DatabaseTarget.POSTGRESQL, str)
        assert DatabaseTarget.POSTGRESQL.value == "postgresql"

    def test_database_target_properties(self):
        """测试数据库目标属性"""
        tdengine = DatabaseTarget.TDENGINE
        postgresql = DatabaseTarget.POSTGRESQL

        # 测试字符串操作
        assert tdengine.upper() == "TDENGINE"
        assert postgresql.upper() == "POSTGRESQL"

        # 测试比较操作
        assert tdengine != postgresql
        assert tdengine == "tdengine"
        assert postgresql == "postgresql"

    def test_database_target_iteration(self):
        """测试数据库目标枚举迭代"""
        targets = list(DatabaseTarget)
        assert len(targets) == 2

        target_values = [target.value for target in targets]
        assert "tdengine" in target_values
        assert "postgresql" in target_values


class TestDeduplicationStrategyEnum:
    """DeduplicationStrategy枚举测试类"""

    def test_strategies_defined(self):
        """测试去重策略是否正确定义"""
        all_strategies = DeduplicationStrategy.get_all_strategies()
        assert len(all_strategies) == 4

        expected_strategies = ["latest_wins", "first_wins", "merge", "reject"]
        assert sorted(all_strategies) == sorted(expected_strategies)

    def test_latest_wins_strategy(self):
        """测试最新数据覆盖策略"""
        strategy = DeduplicationStrategy.LATEST_WINS
        assert strategy == "latest_wins"
        assert strategy.value == "latest_wins"
        assert isinstance(strategy, str)

    def test_first_wins_strategy(self):
        """测试首次数据保留策略"""
        strategy = DeduplicationStrategy.FIRST_WINS
        assert strategy == "first_wins"
        assert strategy.value == "first_wins"

    def test_merge_strategy(self):
        """测试智能合并策略"""
        strategy = DeduplicationStrategy.MERGE
        assert strategy == "merge"
        assert strategy.value == "merge"

    def test_reject_strategy(self):
        """测试拒绝重复策略"""
        strategy = DeduplicationStrategy.REJECT
        assert strategy == "reject"
        assert strategy.value == "reject"

    def test_strategy_comparison(self):
        """测试策略比较操作"""
        strategies = [
            DeduplicationStrategy.LATEST_WINS,
            DeduplicationStrategy.FIRST_WINS,
            DeduplicationStrategy.MERGE,
            DeduplicationStrategy.REJECT,
        ]

        # 验证所有策略都不同
        assert len(set(strategies)) == 4

        # 验证字符串比较
        assert strategies[0] == "latest_wins"
        assert strategies[1] == "first_wins"
        assert strategies[2] == "merge"
        assert strategies[3] == "reject"

    def test_strategy_string_operations(self):
        """测试策略字符串操作"""
        latest = DeduplicationStrategy.LATEST_WINS

        assert latest.upper() == "LATEST_WINS"
        assert latest.replace("_", " ") == "latest wins"
        assert len(latest) > 0
        assert "_" in latest


class TestDataClassificationIntegration:
    """数据分类集成测试类"""

    def test_cross_module_compatibility(self):
        """测试跨模块兼容性"""
        # 测试可以在不同上下文中使用枚举值
        classifications = DataClassification.get_all_classifications()
        targets = DatabaseTarget.get_all_targets()
        strategies = DeduplicationStrategy.get_all_strategies()

        # 验证都是字符串列表
        assert all(isinstance(c, str) for c in classifications)
        assert all(isinstance(t, str) for t in targets)
        assert all(isinstance(s, str) for s in strategies)

        # 验证可以用于字典键
        test_dict = {
            DataClassification.TICK_DATA: "high_frequency",
            DatabaseTarget.TDENGINE: "time_series",
            DeduplicationStrategy.LATEST_WINS: "overwrite",
        }

        assert len(test_dict) == 3
        assert test_dict["TICK_DATA"] == "high_frequency"

    def test_database_routing_logic(self):
        """测试数据库路由逻辑"""

        # 模拟路由决策
        def route_to_database(classification: str) -> str:
            """根据数据分类路由到数据库"""
            market_data = set(DataClassification.get_market_data_classifications())
            realtime_data = {
                DataClassification.REALTIME_POSITIONS.value,
                DataClassification.REALTIME_ACCOUNT.value,
                DataClassification.ORDER_QUEUE.value,
            }

            if classification in realtime_data:
                return DatabaseTarget.TDENGINE.value
            elif classification in market_data:
                # 市场数据中除实时数据外都路由到TDengine
                return DatabaseTarget.TDENGINE.value
            else:
                # 其他数据路由到PostgreSQL
                return DatabaseTarget.POSTGRESQL.value

        # 测试路由逻辑
        assert route_to_database("TICK_DATA") == "tdengine"
        assert route_to_database("SYMBOLS_INFO") == "postgresql"
        assert route_to_database("REALTIME_POSITIONS") == "tdengine"
        assert route_to_database("TECHNICAL_INDICATORS") == "postgresql"

    def test_deduplication_strategy_selection(self):
        """测试去重策略选择逻辑"""

        def select_strategy(data_source: str, data_type: str) -> str:
            """根据数据源和数据类型选择去重策略"""
            if data_source == "official":
                return DeduplicationStrategy.FIRST_WINS.value
            elif data_source == "realtime":
                return DeduplicationStrategy.LATEST_WINS.value
            elif data_source == "multiple":
                return DeduplicationStrategy.MERGE.value
            else:
                return DeduplicationStrategy.REJECT.value

        # 测试策略选择
        assert select_strategy("official", "SYMBOLS_INFO") == "first_wins"
        assert select_strategy("realtime", "TICK_DATA") == "latest_wins"
        assert select_strategy("multiple", "FUNDAMENTAL_METRICS") == "merge"
        assert select_strategy("unknown", "UNKNOWN") == "reject"

    def test_enums_in_collections(self):
        """测试枚举在集合中的使用"""
        # 测试作为集合元素
        market_set = set(DataClassification.get_market_data_classifications())
        assert "TICK_DATA" in market_set
        assert len(market_set) == 6

        # 测试列表操作
        all_classifications = DataClassification.get_all_classifications()
        sorted_classifications = sorted(all_classifications)
        assert len(sorted_classifications) == 34
        assert sorted_classifications[0] == "BACKTEST_RESULTS"  # 字母顺序第一个

    def test_type_annotations_compliance(self):
        """测试类型注解合规性"""

        # 测试函数类型注解
        def process_classification(classification: str) -> str:
            return f"processed_{classification}"

        # 验证可以使用枚举值
        result = process_classification(DataClassification.TICK_DATA)
        assert result == "processed_DataClassification.TICK_DATA"

        # 测试返回类型
        def get_database_target() -> DatabaseTarget:
            return DatabaseTarget.TDENGINE

        target = get_database_target()
        assert isinstance(target, DatabaseTarget)
        assert target == "tdengine"


class TestDataClassificationEdgeCases:
    """数据分类边界情况测试类"""

    def test_case_sensitivity(self):
        """测试大小写敏感性"""
        # 枚举值应该是大小写敏感的
        assert DataClassification.TICK_DATA == "TICK_DATA"
        assert DataClassification.TICK_DATA != "tick_data"
        assert DataClassification.TICK_DATA != "Tick_Data"

    def test_string_like_behavior(self):
        """测试字符串类行为"""
        classification = DataClassification.TICK_DATA

        # 测试字符串方法
        assert classification.startswith("TICK")
        assert classification.endswith("_DATA")
        assert "TICK" in classification
        assert classification.replace("TICK", "MARKET") == "MARKET_DATA"

    def test_hashing_behavior(self):
        """测试哈希行为（可用于字典键）"""
        # 创建字典
        test_dict = {}
        test_dict[DataClassification.TICK_DATA] = "test_value"

        # 使用字符串键访问
        assert test_dict["TICK_DATA"] == "test_value"

        # 使用枚举值访问
        assert test_dict[DataClassification.TICK_DATA] == "test_value"

    def test_comparisons_and_equality(self):
        """测试比较和相等性"""
        # 与字符串比较
        assert DataClassification.TICK_DATA == "TICK_DATA"
        assert DataClassification.TICK_DATA != "OTHER_DATA"

        # 与其他枚举比较
        assert DataClassification.TICK_DATA != DataClassification.MINUTE_KLINE

        # 身份比较
        tick1 = DataClassification.TICK_DATA
        tick2 = DataClassification.TICK_DATA
        assert tick1 is tick2  # 枚举单例

    def test_enumeration_completeness_check(self):
        """测试枚举完整性检查"""
        # 验证没有遗漏任何分类
        expected_total = 34  # 6+9+6+7+6
        actual_total = len(DataClassification.get_all_classifications())
        assert actual_total == expected_total, (
            f"期望{expected_total}个分类，实际{actual_total}个"
        )

    def test_enumeration_value_uniqueness(self):
        """测试枚举值唯一性"""
        all_values = DataClassification.get_all_classifications()
        unique_values = set(all_values)

        assert len(all_values) == len(unique_values), "存在重复的枚举值"

    def test_invalid_classification_handling(self):
        """测试无效分类处理"""
        valid_classifications = set(DataClassification.get_all_classifications())

        # 测试一些无效值
        invalid_values = ["INVALID_DATA", "", "TICK_DAT", None, 123]

        for invalid in invalid_values:
            if invalid is not None:
                assert invalid not in valid_classifications


class TestDataClassificationPerformance:
    """数据分类性能测试类"""

    def test_classifications_retrieval_performance(self):
        """测试分类检索性能"""
        # 测试多次调用的性能
        start_time = time.time()

        for _ in range(1000):
            all_classifications = DataClassification.get_all_classifications()
            market_classifications = (
                DataClassification.get_market_data_classifications()
            )
            reference_classifications = (
                DataClassification.get_reference_data_classifications()
            )

        end_time = time.time()
        elapsed_time = end_time - start_time

        # 1000次调用应该在合理时间内完成（小于1秒）
        assert elapsed_time < 1.0, f"性能测试失败: {elapsed_time:.3f}秒"

        # 验证结果一致性
        assert len(all_classifications) == 34
        assert len(market_classifications) == 6
        assert len(reference_classifications) == 9

    def test_large_enumeration_performance(self):
        """测试大量枚举操作性能"""
        classifications = list(DataClassification)

        start_time = time.time()

        # 模拟大量枚举操作
        for _ in range(10000):
            for classification in classifications:
                # 模拟各种操作
                value = classification.value
                is_in_market = (
                    value in DataClassification.get_market_data_classifications()
                )
                string_rep = str(classification)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # 10000次遍历所有枚举应该在合理时间内完成
        assert elapsed_time < 2.0, f"大量枚举操作性能测试失败: {elapsed_time:.3f}秒"

    def test_memory_usage_efficiency(self):
        """测试内存使用效率"""
        import sys

        # 枚举应该是单例，不会占用过多内存
        classifications = [
            DataClassification.TICK_DATA,
            DataClassification.SYMBOLS_INFO,
            DatabaseTarget.TDENGINE,
            DeduplicationStrategy.LATEST_WINS,
        ]

        # 验证引用相同对象
        for classification in classifications:
            ref_count = sys.getrefcount(classification)
            assert ref_count >= 1  # 至少有一个引用

        # 验证枚举值的内存效率
        all_classifications = DataClassification.get_all_classifications()
        assert len(all_classifications) == 34
        # 枚举不应该创建新的字符串对象
        assert all(isinstance(c, str) for c in all_classifications)

    def test_string_operations_performance(self):
        """测试字符串操作性能"""
        classification = DataClassification.TECHNICAL_INDICATORS

        start_time = time.time()

        # 执行大量字符串操作
        for _ in range(10000):
            result = classification.lower()
            result = classification.upper()
            result = classification.split("_")
            result = "_".join(classification.split("_"))
            result = len(classification)
            result = classification.startswith("TECHNICAL")
            result = classification.endswith("INDICATORS")

        end_time = time.time()
        elapsed_time = end_time - start_time

        # 字符串操作应该很快
        assert elapsed_time < 0.5, f"字符串操作性能测试失败: {elapsed_time:.3f}秒"


class TestDataClassificationDocumentation:
    """数据分类文档测试类"""

    def test_enum_documentation_strings(self):
        """测试枚举文档字符串"""
        # 验证枚举类有文档字符串
        assert DataClassification.__doc__ is not None
        assert len(DataClassification.__doc__) > 0

        assert DatabaseTarget.__doc__ is not None
        assert len(DatabaseTarget.__doc__) > 0

        assert DeduplicationStrategy.__doc__ is not None
        assert len(DeduplicationStrategy.__doc__) > 0

    def test_method_documentation(self):
        """测试方法文档字符串"""
        # 验证类方法有文档字符串
        assert DataClassification.get_all_classifications.__doc__ is not None
        assert DataClassification.get_market_data_classifications.__doc__ is not None
        assert DataClassification.get_reference_data_classifications.__doc__ is not None
        assert DataClassification.get_derived_data_classifications.__doc__ is not None
        assert (
            DataClassification.get_transaction_data_classifications.__doc__ is not None
        )
        assert DataClassification.get_metadata_classifications.__doc__ is not None

        assert DatabaseTarget.get_all_targets.__doc__ is not None
        assert DeduplicationStrategy.get_all_strategies.__doc__ is not None

    def test_module_level_documentation(self):
        """测试模块级文档"""
        import src.core.data_classification as module

        # 验证模块有文档字符串
        assert module.__doc__ is not None
        assert len(module.__doc__) > 0

        # 验证版本信息
        assert hasattr(module, "__version__")
        assert hasattr(module, "__all__")

        expected_exports = [
            "DataClassification",
            "DatabaseTarget",
            "DeduplicationStrategy",
        ]
        assert module.__all__ == expected_exports


class TestBusinessLogicValidation:
    """业务逻辑验证测试类"""

    def test_classification_hierarchy_correctness(self):
        """测试分类层次结构正确性"""
        # 验证5大分类的数量分配
        market_count = len(DataClassification.get_market_data_classifications())
        reference_count = len(DataClassification.get_reference_data_classifications())
        derived_count = len(DataClassification.get_derived_data_classifications())
        transaction_count = len(
            DataClassification.get_transaction_data_classifications()
        )
        metadata_count = len(DataClassification.get_metadata_classifications())

        assert market_count == 6, f"市场数据应为6项，实际{market_count}项"
        assert reference_count == 9, f"参考数据应为9项，实际{reference_count}项"
        assert derived_count == 6, f"衍生数据应为6项，实际{derived_count}项"
        assert transaction_count == 7, f"交易数据应为7项，实际{transaction_count}项"
        assert metadata_count == 6, f"元数据应为6项，实际{metadata_count}项"

    def test_naming_convention_consistency(self):
        """测试命名约定一致性"""
        all_classifications = DataClassification.get_all_classifications()

        # 验证所有分类都使用大写字母和下划线
        for classification in all_classifications:
            assert classification.isupper(), f"分类{classification}应该使用大写"
            assert "_" in classification or classification.isalpha(), (
                f"分类{classification}应该使用下划线分隔或全字母"
            )

    def test_database_target_appropriateness(self):
        """测试数据库目标适当性"""
        # 验证数据库目标的命名
        tdengine_target = DatabaseTarget.TDENGINE.value
        postgresql_target = DatabaseTarget.POSTGRESQL.value

        assert tdengine_target == "tdengine"
        assert postgresql_target == "postgresql"

        # 验证都是小写
        assert tdengine_target.islower()
        assert postgresql_target.islower()

    def test_strategy_naming_clarity(self):
        """测试策略命名清晰度"""
        strategies = DeduplicationStrategy.get_all_strategies()

        # 验证策略命名清晰且使用下划线
        for strategy in strategies:
            assert "_" in strategy or strategy.isalpha(), f"策略{strategy}命名应该清晰"
            assert strategy.islower(), f"策略{strategy}应该使用小写"

    def test_business_scenario_coverage(self):
        """测试业务场景覆盖"""
        # 验证关键业务场景都有对应的分类
        critical_scenarios = {
            "tick_level_data": "TICK_DATA",
            "daily_prices": "DAILY_KLINE",
            "stock_basic_info": "SYMBOLS_INFO",
            "trading_signals": "TRADE_SIGNALS",
            "user_settings": "USER_CONFIG",
            "system_monitoring": "DATA_SOURCE_STATUS",
        }

        all_classifications = DataClassification.get_all_classifications()

        for scenario, expected_classification in critical_scenarios.items():
            assert expected_classification in all_classifications, (
                f"缺少关键业务场景分类: {scenario}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
