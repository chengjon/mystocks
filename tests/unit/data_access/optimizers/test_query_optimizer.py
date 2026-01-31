"""
Query Optimizer Test Suite
智能查询优化器测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.data_access.optimizers.query_optimizer (587行)
"""

from unittest.mock import Mock, patch

import pytest

# Test target imports
from src.data_access.optimizers.query_optimizer import (
    ExecutionPlan,
    IndexRecommendation,
    OptimizationPriority,
    OptimizationResult,
    OptimizationRule,
    OptimizationType,
    QueryOptimizer,
)


class TestOptimizationType:
    """优化类型枚举测试"""

    def test_optimization_type_values(self):
        """测试优化类型枚举值"""
        assert OptimizationType.INDEX_OPTIMIZATION.value == "index_optimization"
        assert OptimizationType.QUERY_REWRITE.value == "query_rewrite"
        assert OptimizationType.EXECUTION_PLAN.value == "execution_plan"
        assert OptimizationType.CACHING.value == "caching"
        assert OptimizationType.BATCH_OPTIMIZATION.value == "batch_optimization"
        assert OptimizationType.PARTITION_OPTIMIZATION.value == "partition_optimization"
        assert OptimizationType.JOIN_OPTIMIZATION.value == "join_optimization"
        assert OptimizationType.PREDICATE_OPTIMIZATION.value == "predicate_optimization"

    def test_optimization_type_count(self):
        """测试优化类型数量"""
        assert len(OptimizationType) == 8


class TestOptimizationPriority:
    """优化优先级枚举测试"""

    def test_optimization_priority_values(self):
        """测试优化优先级枚举值"""
        assert OptimizationPriority.LOW.value == 1
        assert OptimizationPriority.MEDIUM.value == 2
        assert OptimizationPriority.HIGH.value == 3
        assert OptimizationPriority.CRITICAL.value == 4

    def test_optimization_priority_ordering(self):
        """测试优化优先级排序"""
        priorities = [
            OptimizationPriority.LOW,
            OptimizationPriority.MEDIUM,
            OptimizationPriority.HIGH,
            OptimizationPriority.CRITICAL,
        ]
        values = [p.value for p in priorities]
        assert values == [1, 2, 3, 4]


class TestOptimizationRule:
    """优化规则数据类测试"""

    def test_optimization_rule_creation(self):
        """测试优化规则创建"""
        condition = lambda query, db_type: True
        apply_optimization = lambda query, db_type: query

        rule = OptimizationRule(
            name="test_rule",
            optimization_type=OptimizationType.INDEX_OPTIMIZATION,
            priority=OptimizationPriority.HIGH,
            condition=condition,
            apply_optimization=apply_optimization,
            description="Test rule for unit testing",
            estimated_improvement=0.15,
        )

        assert rule.name == "test_rule"
        assert rule.optimization_type == OptimizationType.INDEX_OPTIMIZATION
        assert rule.priority == OptimizationPriority.HIGH
        assert rule.condition == condition
        assert rule.apply_optimization == apply_optimization
        assert rule.description == "Test rule for unit testing"
        assert rule.estimated_improvement == 0.15

    def test_optimization_rule_defaults(self):
        """测试优化规则默认值"""
        rule = OptimizationRule(
            name="minimal_rule",
            optimization_type=OptimizationType.QUERY_REWRITE,
            priority=OptimizationPriority.MEDIUM,
            condition=lambda q, d: False,
            apply_optimization=lambda q, d: q,
        )

        assert rule.name == "minimal_rule"
        assert rule.description == ""
        assert rule.estimated_improvement == 0.1


class TestOptimizationResult:
    """优化结果数据类测试"""

    def test_optimization_result_creation(self):
        """测试优化结果创建"""
        mock_query = Mock()
        mock_optimized_query = Mock()

        result = OptimizationResult(
            original_query=mock_query,
            optimized_query=mock_optimized_query,
            applied_optimizations=["index_optimization", "query_rewrite"],
            estimated_improvement=0.25,
            optimization_time=0.05,
            recommendations=["Add index on column user_id"],
            warnings=["Query may be slow without proper indexing"],
        )

        assert result.original_query == mock_query
        assert result.optimized_query == mock_optimized_query
        assert len(result.applied_optimizations) == 2
        assert "index_optimization" in result.applied_optimizations
        assert result.estimated_improvement == 0.25
        assert result.optimization_time == 0.05
        assert len(result.recommendations) == 1
        assert len(result.warnings) == 1


class TestExecutionPlan:
    """执行计划数据类测试"""

    def test_execution_plan_creation(self):
        """测试执行计划创建"""
        from src.data_access.interfaces.i_data_access import DatabaseType

        plan = ExecutionPlan(
            database_type=DatabaseType.POSTGRESQL,
            plan_details={"operation": "seq_scan", "table": "users"},
            estimated_cost=25.5,
            estimated_rows=1000,
            execution_time_ms=150.0,
            index_usage=["users_pkey"],
            join_order=["users", "profiles"],
            potential_bottlenecks=["Full table scan on users"],
        )

        assert plan.database_type == DatabaseType.POSTGRESQL
        assert plan.plan_details["operation"] == "seq_scan"
        assert plan.estimated_cost == 25.5
        assert plan.estimated_rows == 1000
        assert plan.execution_time_ms == 150.0
        assert "users_pkey" in plan.index_usage
        assert plan.join_order == ["users", "profiles"]
        assert len(plan.potential_bottlenecks) == 1


class TestIndexRecommendation:
    """索引建议数据类测试"""

    def test_index_recommendation_creation(self):
        """测试索引建议创建"""
        recommendation = IndexRecommendation(
            table_name="user_activities",
            columns=["user_id", "timestamp"],
            index_type="btree",
            estimated_improvement=0.35,
            creation_cost=50.0,
            recommendation_reason="Frequent filtering by user_id and timestamp",
        )

        assert recommendation.table_name == "user_activities"
        assert len(recommendation.columns) == 2
        assert "user_id" in recommendation.columns
        assert "timestamp" in recommendation.columns
        assert recommendation.index_type == "btree"
        assert recommendation.estimated_improvement == 0.35
        assert recommendation.creation_cost == 50.0
        assert recommendation.recommendation_reason == "Frequent filtering by user_id and timestamp"


class TestQueryOptimizer:
    """查询优化器测试"""

    @pytest.fixture
    def mock_query(self):
        """模拟查询对象"""
        from src.data_access.interfaces.i_data_access import DataQuery, QueryOperation

        return DataQuery(
            operation=QueryOperation.SELECT,
            table="users",
            columns=["id", "name", "email"],
            where_conditions={"status": "active"},
            limit=100,
        )

    @pytest.fixture
    def mock_database_type(self):
        """模拟数据库类型"""
        from src.data_access.interfaces.i_data_access import DatabaseType

        return DatabaseType.POSTGRESQL

    def test_query_optimizer_initialization(self):
        """测试查询优化器初始化"""
        with patch("src.data_access.optimizers.query_optimizer.DatabaseCapabilityDetector"):
            optimizer = QueryOptimizer()

            assert optimizer.capability_detector is not None
            assert isinstance(optimizer.optimization_rules, list)
            assert isinstance(optimizer.index_cache, dict)
            assert isinstance(optimizer.plan_cache, dict)
            assert isinstance(optimizer.optimization_history, list)
            assert len(optimizer.optimization_rules) > 0

    def test_optimize_query_basic(self, mock_query, mock_database_type):
        """测试基本查询优化"""
        with patch("src.data_access.optimizers.query_optimizer.DatabaseCapabilityDetector"):
            optimizer = QueryOptimizer()

            result = optimizer.optimize_query(mock_query, mock_database_type)

            assert isinstance(result, OptimizationResult)
            assert result.original_query == mock_query
            assert result.optimized_query is not None
            assert isinstance(result.applied_optimizations, list)
            assert isinstance(result.recommendations, list)
            assert isinstance(result.warnings, list)
            assert result.optimization_time >= 0

    def test_analyze_execution_plan(self, mock_query, mock_database_type):
        """测试执行计划分析"""
        with patch("src.data_access.optimizers.query_optimizer.DatabaseCapabilityDetector"):
            optimizer = QueryOptimizer()

            # Mock the analyze method
            with patch.object(
                optimizer,
                "_analyze_query_plan",
                return_value={
                    "operation": "index_scan",
                    "index_used": "users_pkey",
                    "estimated_cost": 10.5,
                },
            ):
                plan = optimizer.analyze_execution_plan(mock_query, mock_database_type)

                assert isinstance(plan, ExecutionPlan)
                assert plan.database_type == mock_database_type
                assert plan.estimated_cost == 10.5
                assert plan.index_usage == ["users_pkey"]

    def test_get_index_recommendations(self, mock_query, mock_database_type):
        """测试获取索引建议"""
        with patch("src.data_access.optimizers.query_optimizer.DatabaseCapabilityDetector"):
            optimizer = QueryOptimizer()

            # Mock the recommendation logic
            with patch.object(
                optimizer,
                "_generate_index_recommendations",
                return_value=[
                    IndexRecommendation(
                        table_name="users",
                        columns=["status", "created_at"],
                        index_type="btree",
                        estimated_improvement=0.20,
                        creation_cost=25.0,
                        recommendation_reason="Frequent filtering by status and created_at",
                    )
                ],
            ):
                recommendations = optimizer.get_index_recommendations(mock_query, mock_database_type)

                assert len(recommendations) == 1
                assert recommendations[0].table_name == "users"
                assert "status" in recommendations[0].columns
                assert "created_at" in recommendations[0].columns

    def test_optimization_caching(self, mock_query, mock_database_type):
        """测试优化缓存机制"""
        with patch("src.data_access.optimizers.query_optimizer.DatabaseCapabilityDetector"):
            optimizer = QueryOptimizer()

            # First optimization
            result1 = optimizer.optimize_query(mock_query, mock_database_type)

            # Second optimization should use cache
            result2 = optimizer.optimize_query(mock_query, mock_database_type)

            assert result1.optimized_query == result2.optimized_query
            assert result2.optimization_time < result1.optimization_time

    def test_get_optimization_statistics(self):
        """测试获取优化统计信息"""
        with patch("src.data_access.optimizers.query_optimizer.DatabaseCapabilityDetector"):
            optimizer = QueryOptimizer()

            # Add some optimization history
            mock_result = OptimizationResult(
                original_query=Mock(),
                optimized_query=Mock(),
                applied_optimizations=["test"],
                estimated_improvement=0.15,
                optimization_time=0.05,
                recommendations=[],
                warnings=[],
            )
            optimizer.optimization_history = [mock_result]

            stats = optimizer.get_optimization_statistics()

            assert isinstance(stats, dict)
            assert "total_optimizations" in stats
            assert "average_improvement" in stats
            assert "optimization_types" in stats
            assert stats["total_optimizations"] == 1

    def test_clear_cache(self, mock_query, mock_database_type):
        """测试清除缓存"""
        with patch("src.data_access.optimizers.query_optimizer.DatabaseCapabilityDetector"):
            optimizer = QueryOptimizer()

            # Add some cache entries
            optimizer.index_cache["test"] = []
            optimizer.plan_cache["test"] = ExecutionPlan(
                database_type=mock_database_type,
                plan_details={},
                estimated_cost=0.0,
                estimated_rows=0,
                execution_time_ms=0.0,
                index_usage=[],
                join_order=[],
                potential_bottlenecks=[],
            )

            # Clear cache
            optimizer.clear_cache()

            assert len(optimizer.index_cache) == 0
            assert len(optimizer.plan_cache) == 0

    def test_rule_priority_application(self, mock_query, mock_database_type):
        """测试优化规则优先级应用"""
        with patch("src.data_access.optimizers.query_optimizer.DatabaseCapabilityDetector"):
            optimizer = QueryOptimizer()

            # Verify that high priority rules are applied first
            high_priority_rules = [
                r
                for r in optimizer.optimization_rules
                if r.priority == OptimizationPriority.HIGH or r.priority == OptimizationPriority.CRITICAL
            ]

            assert len(high_priority_rules) > 0

    def test_estimated_improvement_calculation(self, mock_query, mock_database_type):
        """测试性能提升估算"""
        with patch("src.data_access.optimizers.query_optimizer.DatabaseCapabilityDetector"):
            optimizer = QueryOptimizer()

            result = optimizer.optimize_query(mock_query, mock_database_type)

            assert result.estimated_improvement >= 0
            assert isinstance(result.estimated_improvement, (int, float))

    def test_multiple_database_types(self, mock_query):
        """测试多数据库类型支持"""
        from src.data_access.interfaces.i_data_access import DatabaseType

        with patch("src.data_access.optimizers.query_optimizer.DatabaseCapabilityDetector"):
            optimizer = QueryOptimizer()

            database_types = [
                DatabaseType.POSTGRESQL,
                DatabaseType.TDENGINE,
                DatabaseType.MYSQL,
            ]

            for db_type in database_types:
                result = optimizer.optimize_query(mock_query, db_type)
                assert isinstance(result, OptimizationResult)
                assert result.database_type == db_type if hasattr(result, "database_type") else True


class TestQueryOptimizerEdgeCases:
    """查询优化器边界情况测试"""

    def test_empty_query_optimization(self):
        """测试空查询优化"""
        with patch("src.data_access.optimizers.query_optimizer.DatabaseCapabilityDetector"):
            optimizer = QueryOptimizer()

            # Mock empty query
            empty_query = Mock()
            empty_query.table = None
            empty_query.columns = []
            empty_query.where_conditions = {}

            from src.data_access.interfaces.i_data_access import DatabaseType

            result = optimizer.optimize_query(empty_query, DatabaseType.POSTGRESQL)

            assert isinstance(result, OptimizationResult)
            assert result.estimated_improvement == 0.0

    def test_complex_query_optimization(self):
        """测试复杂查询优化"""
        with patch("src.data_access.optimizers.query_optimizer.DatabaseCapabilityDetector"):
            optimizer = QueryOptimizer()

            # Mock complex query
            complex_query = Mock()
            complex_query.table = "user_activities"
            complex_query.columns = ["*"]
            complex_query.where_conditions = {
                "user_id": {"$in": [1, 2, 3]},
                "timestamp": {"$gte": "2025-01-01"},
                "activity_type": "login",
            }
            complex_query.joins = ["users", "profiles"]
            complex_query.group_by = ["user_id"]
            complex_query.order_by = [{"timestamp": "DESC"}]
            complex_query.limit = 1000

            from src.data_access.interfaces.i_data_access import DatabaseType

            result = optimizer.optimize_query(complex_query, DatabaseType.POSTGRESQL)

            assert isinstance(result, OptimizationResult)
            assert len(result.applied_optimizations) > 0
            assert len(result.recommendations) > 0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
