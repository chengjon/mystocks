"""
智能查询优化器
针对不同数据库特性进行查询优化和性能调优
"""

import re
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

from ..interfaces.i_data_access import (
    DataQuery,
    QueryOperation,
    DatabaseType,
    IQueryOptimizer,
)
from ..capabilities.database_detector import DatabaseCapabilityDetector

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """优化类型"""

    INDEX_OPTIMIZATION = "index_optimization"
    QUERY_REWRITE = "query_rewrite"
    EXECUTION_PLAN = "execution_plan"
    CACHING = "caching"
    BATCH_OPTIMIZATION = "batch_optimization"
    PARTITION_OPTIMIZATION = "partition_optimization"
    JOIN_OPTIMIZATION = "join_optimization"
    PREDIATE_OPTIMIZATION = "predicate_optimization"


class OptimizationPriority(Enum):
    """优化优先级"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class OptimizationRule:
    """优化规则"""

    name: str
    optimization_type: OptimizationType
    priority: OptimizationPriority
    condition: Callable[[DataQuery, DatabaseType], bool]
    apply_optimization: Callable[[DataQuery, DatabaseType], DataQuery]
    description: str = ""
    estimated_improvement: float = 0.1  # 预估性能提升比例


@dataclass
class OptimizationResult:
    """优化结果"""

    original_query: DataQuery
    optimized_query: DataQuery
    applied_optimizations: List[str]
    estimated_improvement: float
    optimization_time: float
    recommendations: List[str]
    warnings: List[str]


@dataclass
class ExecutionPlan:
    """执行计划"""

    database_type: DatabaseType
    plan_details: Dict[str, Any]
    estimated_cost: float
    estimated_rows: int
    execution_time_ms: float
    index_usage: List[str]
    join_order: List[str]
    potential_bottlenecks: List[str]


@dataclass
class IndexRecommendation:
    """索引建议"""

    table_name: str
    columns: List[str]
    index_type: str
    estimated_improvement: float
    creation_cost: float
    recommendation_reason: str


class QueryOptimizer(IQueryOptimizer):
    """查询优化器"""

    def __init__(self):
        self.capability_detector = DatabaseCapabilityDetector()
        self.optimization_rules: List[OptimizationRule] = []
        self.index_cache: Dict[str, List[IndexRecommendation]] = {}
        self.plan_cache: Dict[str, ExecutionPlan] = {}
        self.optimization_history: List[OptimizationResult] = []
        self._initialize_optimization_rules()

    def _initialize_optimization_rules(self):
        """初始化优化规则"""
        # PostgreSQL 优化规则
        self.optimization_rules.extend(
            [
                OptimizationRule(
                    name="postgresql_join_reordering",
                    optimization_type=OptimizationType.JOIN_OPTIMIZATION,
                    priority=OptimizationPriority.MEDIUM,
                    condition=lambda q, db: db == DatabaseType.POSTGRESQL and q.join_clauses,
                    apply_optimization=self._optimize_postgresql_joins,
                    description="PostgreSQL JOIN顺序优化",
                    estimated_improvement=0.15,
                ),
                OptimizationRule(
                    name="postgresql_index_hints",
                    optimization_type=OptimizationType.INDEX_OPTIMIZATION,
                    priority=OptimizationPriority.HIGH,
                    condition=lambda q, db: db == DatabaseType.POSTGRESQL and q.filters,
                    apply_optimization=self._add_postgresql_index_hints,
                    description="PostgreSQL索引提示优化",
                    estimated_improvement=0.25,
                ),
                OptimizationRule(
                    name="postgresql_cte_optimization",
                    optimization_type=OptimizationType.QUERY_REWRITE,
                    priority=OptimizationPriority.MEDIUM,
                    condition=lambda q, db: db == DatabaseType.POSTGRESQL and self._has_complex_subqueries(q),
                    apply_optimization=self._optimize_postgresql_cte,
                    description="PostgreSQL CTE优化",
                    estimated_improvement=0.20,
                ),
                OptimizationRule(
                    name="postgresql_partition_pruning",
                    optimization_type=OptimizationType.PARTITION_OPTIMIZATION,
                    priority=OptimizationPriority.HIGH,
                    condition=lambda q, db: db == DatabaseType.POSTGRESQL and self._has_time_filter(q),
                    apply_optimization=self._optimize_postgresql_partition_pruning,
                    description="PostgreSQL分区裁剪优化",
                    estimated_improvement=0.30,
                ),
            ]
        )

        # TDengine 优化规则
        self.optimization_rules.extend(
            [
                OptimizationRule(
                    name="tdengine_super_table_optimization",
                    optimization_type=OptimizationType.QUERY_REWRITE,
                    priority=OptimizationPriority.CRITICAL,
                    condition=lambda q, db: db == DatabaseType.TDENGINE and self._is_time_series_query(q),
                    apply_optimization=self._optimize_tdengine_super_tables,
                    description="TDengine超级表优化",
                    estimated_improvement=0.40,
                ),
                OptimizationRule(
                    name="tdengine_tag_filtering",
                    optimization_type=OptimizationType.PREDICATE_OPTIMIZATION,
                    priority=OptimizationPriority.HIGH,
                    condition=lambda q, db: db == DatabaseType.TDENGINE and q.filters,
                    apply_optimization=self._optimize_tdengine_tag_filtering,
                    description="TDengine标签过滤优化",
                    estimated_improvement=0.35,
                ),
                OptimizationRule(
                    name="tdengine_time_range_optimization",
                    optimization_type=OptimizationType.PREDICATE_OPTIMIZATION,
                    priority=OptimizationPriority.CRITICAL,
                    condition=lambda q, db: db == DatabaseType.TDENGINE and self._has_time_filter(q),
                    apply_optimization=self._optimize_tdengine_time_range,
                    description="TDengine时间范围优化",
                    estimated_improvement=0.50,
                ),
                OptimizationRule(
                    name="tdengine_batch_size_optimization",
                    optimization_type=OptimizationType.BATCH_OPTIMIZATION,
                    priority=OptimizationPriority.MEDIUM,
                    condition=lambda q, db: db == DatabaseType.TDENGINE
                    and q.operation in [QueryOperation.BATCH_INSERT, QueryOperation.BATCH_UPDATE],
                    apply_optimization=self._optimize_tdengine_batch_size,
                    description="TDengine批处理大小优化",
                    estimated_improvement=0.20,
                ),
            ]
        )

        # 通用优化规则
        self.optimization_rules.extend(
            [
                OptimizationRule(
                    name="limit_optimization",
                    optimization_type=OptimizationType.PREDICATE_OPTIMIZATION,
                    priority=OptimizationPriority.MEDIUM,
                    condition=lambda q, db: q.limit is None and self._is_large_dataset_query(q),
                    apply_optimization=self._add_limit_clause,
                    description="添加LIMIT子句优化",
                    estimated_improvement=0.15,
                ),
                OptimizationRule(
                    name="column_pruning",
                    optimization_type=OptimizationType.QUERY_REWRITE,
                    priority=OptimizationPriority.LOW,
                    condition=lambda q, db: q.columns is None or len(q.columns) > 10,
                    apply_optimization=self._prune_columns,
                    description="列裁剪优化",
                    estimated_improvement=0.10,
                ),
                OptimizationRule(
                    name="predicate_pushdown",
                    optimization_type=OptimizationType.PREDICATE_OPTIMIZATION,
                    priority=OptimizationPriority.HIGH,
                    condition=lambda q, db: q.join_clauses and q.filters,
                    apply_optimization=self._push_down_predicates,
                    description="谓词下推优化",
                    estimated_improvement=0.25,
                ),
            ]
        )

    async def optimize_query(self, query: DataQuery, target_database: DatabaseType) -> DataQuery:
        """优化查询"""
        start_time = datetime.now()
        current_query = query
        applied_optimizations = []
        total_improvement = 0.0
        recommendations = []
        warnings = []

        # 获取数据库能力
        try:
            # 这里需要一个实际的 IDataAccess 实例来获取能力信息
            # 在实际使用中，应该从调用方传入或通过依赖注入获取
            pass
        except Exception:
            logger.warning("无法获取数据库能力信息，使用通用优化策略")

        # 应用适用的优化规则
        applicable_rules = [rule for rule in self.optimization_rules if rule.condition(current_query, target_database)]

        # 按优先级排序
        applicable_rules.sort(key=lambda x: x.priority.value, reverse=True)

        for rule in applicable_rules:
            try:
                optimized_query = rule.apply_optimization(current_query, target_database)
                if optimized_query != current_query:
                    current_query = optimized_query
                    applied_optimizations.append(rule.name)
                    total_improvement += rule.estimated_improvement

                    # 添加建议
                    if rule.description:
                        recommendations.append(f"应用优化: {rule.description}")

            except Exception as e:
                logger.warning("优化规则应用失败 %s: %s", rule.name, e)
                warnings.append(f"优化规则 '{rule.name}' 应用失败: {str(e)}")

        optimization_time = (datetime.now() - start_time).total_seconds()

        # 创建优化结果
        result = OptimizationResult(
            original_query=query,
            optimized_query=current_query,
            applied_optimizations=applied_optimizations,
            estimated_improvement=min(total_improvement, 0.9),  # 最高90%提升
            optimization_time=optimization_time,
            recommendations=recommendations,
            warnings=warnings,
        )

        # 记录优化历史
        self.optimization_history.append(result)

        # 清理过期的优化历史（保留最近1000条）
        if len(self.optimization_history) > 1000:
            self.optimization_history = self.optimization_history[-1000:]

        logger.info("查询优化完成: 应用了 %s 个优化规则，预估提升 %s", len(applied_optimizations), total_improvement)

        return current_query

    async def analyze_query_plan(self, query: DataQuery, target_database: DatabaseType) -> Dict[str, Any]:
        """分析查询执行计划"""
        # 这里需要实际执行 EXPLAIN 或类似命令
        # 简化实现，返回模拟的计划分析

        plan_details = {
            "operation": query.operation.value,
            "table": query.table_name,
            "estimated_cost": self._estimate_query_cost(query, target_database),
            "estimated_rows": self._estimate_result_rows(query),
            "database_type": target_database.value,
            "optimization_suggestions": [],
        }

        # 根据数据库类型添加特定的计划分析
        if target_database == DatabaseType.POSTGRESQL:
            plan_details.update(
                {
                    "index_usage": self._analyze_postgresql_index_usage(query),
                    "join_order": [join.get("table", "unknown") for join in (query.join_clauses or [])],
                    "parallel_possible": len(query.join_clauses or []) > 1,
                }
            )
        elif target_database == DatabaseType.TDENGINE:
            plan_details.update(
                {
                    "super_table_usage": self._analyze_tdengine_super_table_usage(query),
                    "tag_filtering": self._analyze_tdengine_tag_filtering(query),
                    "time_range_optimization": self._analyze_tdengine_time_range(query),
                }
            )

        return plan_details

    async def suggest_indexes(self, query: DataQuery, target_database: DatabaseType) -> List[IndexRecommendation]:
        """建议索引"""
        cache_key = f"{target_database.value}_{query.table_name}_{hash(str(query.filters or {}))}"

        if cache_key in self.index_cache:
            return self.index_cache[cache_key]

        recommendations = []

        if target_database == DatabaseType.POSTGRESQL:
            recommendations.extend(self._suggest_postgresql_indexes(query))
        elif target_database == DatabaseType.TDENGINE:
            recommendations.extend(self._suggest_tdengine_indexes(query))

        # 缓存结果
        self.index_cache[cache_key] = recommendations

        return recommendations

    async def estimate_query_cost(self, query: DataQuery, target_database: DatabaseType) -> float:
        """估算查询成本"""
        base_cost = 1.0

        # 操作类型成本
        operation_costs = {
            QueryOperation.SELECT: 1.0,
            QueryOperation.INSERT: 2.0,
            QueryOperation.UPDATE: 3.0,
            QueryOperation.DELETE: 2.5,
            QueryOperation.BATCH_INSERT: 1.5,
            QueryOperation.BATCH_UPDATE: 2.0,
        }

        base_cost *= operation_costs.get(query.operation, 1.0)

        # 数据量成本
        estimated_rows = self._estimate_result_rows(query)
        if estimated_rows > 100000:
            base_cost *= 2.0
        elif estimated_rows > 10000:
            base_cost *= 1.5

        # JOIN成本
        if query.join_clauses:
            base_cost *= 1 + len(query.join_clauses) * 0.5

        # 数据库特性调整
        if target_database == DatabaseType.TDENGINE:
            if self._is_time_series_query(query):
                base_cost *= 0.7  # TDengine对时序查询更高效
        elif target_database == DatabaseType.POSTGRESQL:
            if self._is_relational_query(query):
                base_cost *= 0.8  # PostgreSQL对关系型查询更高效

        return base_cost

    def _is_time_series_query(self, query: DataQuery) -> bool:
        """判断是否为时间序列查询"""
        timeseries_patterns = [
            r".*tick_data$",
            r".*minute_data$",
            r".*ohlcv$",
            r".*market_data$",
            r".*time_series$",
        ]

        table_name = query.table_name.lower()
        return any(re.match(pattern, table_name) for pattern in timeseries_patterns)

    def _is_relational_query(self, query: DataQuery) -> bool:
        """判断是否为关系型查询"""
        return bool(query.join_clauses or query.group_by or query.having)

    def _is_large_dataset_query(self, query: DataQuery) -> bool:
        """判断是否为大数据集查询"""
        # 简单启发式：没有LIMIT的大表查询
        large_table_patterns = [
            r".*data$",
            r".*records$",
            r".*log$",
            r".*history$",
            r".*events$",
        ]

        table_name = query.table_name.lower()
        is_large_table = any(re.match(pattern, table_name) for pattern in large_table_patterns)
        no_limit = query.limit is None

        return is_large_table and no_limit

    def _has_complex_subqueries(self, query: DataQuery) -> bool:
        """判断是否有复杂子查询"""
        if not query.filters:
            return False

        for value in query.filters.values():
            if isinstance(value, str) and "SELECT" in value.upper():
                return True

        return False

    def _has_time_filter(self, query: DataQuery) -> bool:
        """判断是否有时间过滤条件"""
        if not query.filters:
            return False

        time_keys = ["time", "timestamp", "date", "created_at", "updated_at"]
        return any(key in str(filter_key).lower() for filter_key in query.filters.keys() for key in time_keys)

    def _estimate_result_rows(self, query: DataQuery) -> int:
        """估算结果行数"""
        base_estimate = 1000  # 默认估算

        if query.limit:
            return min(base_estimate, query.limit)

        if query.filters:
            # 假设每个过滤条件减少50%的结果
            filter_count = len(query.filters)
            base_estimate = int(base_estimate * (0.5**filter_count))

        return max(base_estimate, 1)

    # PostgreSQL 特定优化方法
    def _optimize_postgresql_joins(self, query: DataQuery, db_type: DatabaseType) -> DataQuery:
        """优化PostgreSQL JOIN"""
        # 简化实现：添加JOIN顺序提示
        optimized_query = DataQuery(**query.__dict__)
        # 在实际实现中，这里会重新排序JOIN子句
        return optimized_query

    def _add_postgresql_index_hints(self, query: DataQuery, db_type: DatabaseType) -> DataQuery:
        """添加PostgreSQL索引提示"""
        optimized_query = DataQuery(**query.__dict__)
        # 在实际实现中，这里会添加索引提示
        return optimized_query

    def _optimize_postgresql_cte(self, query: DataQuery, db_type: DatabaseType) -> DataQuery:
        """优化PostgreSQL CTE"""
        optimized_query = DataQuery(**query.__dict__)
        # 在实际实现中，这里会优化CTE结构
        return optimized_query

    def _optimize_postgresql_partition_pruning(self, query: DataQuery, db_type: DatabaseType) -> DataQuery:
        """优化PostgreSQL分区裁剪"""
        optimized_query = DataQuery(**query.__dict__)
        # 在实际实现中，这里会添加分区裁剪提示
        return optimized_query

    def _suggest_postgresql_indexes(self, query: DataQuery) -> List[IndexRecommendation]:
        """建议PostgreSQL索引"""
        recommendations = []

        if query.filters:
            # 为过滤条件建议索引
            filter_columns = list(query.filters.keys())
            if filter_columns:
                recommendations.append(
                    IndexRecommendation(
                        table_name=query.table_name,
                        columns=filter_columns[:2],  # 复合索引
                        index_type="btree",
                        estimated_improvement=0.30,
                        creation_cost=0.1,
                        recommendation_reason=f"为过滤条件 {filter_columns[:2]} 建议B-tree索引",
                    )
                )

        return recommendations

    # TDengine 特定优化方法
    def _optimize_tdengine_super_tables(self, query: DataQuery, db_type: DatabaseType) -> DataQuery:
        """优化TDengine超级表"""
        optimized_query = DataQuery(**query.__dict__)
        # 在实际实现中，这里会优化超级表查询
        return optimized_query

    def _optimize_tdengine_tag_filtering(self, query: DataQuery, db_type: DatabaseType) -> DataQuery:
        """优化TDengine标签过滤"""
        optimized_query = DataQuery(**query.__dict__)
        # 在实际实现中，这里会优化标签过滤
        return optimized_query

    def _optimize_tdengine_time_range(self, query: DataQuery, db_type: DatabaseType) -> DataQuery:
        """优化TDengine时间范围"""
        optimized_query = DataQuery(**query.__dict__)
        # 在实际实现中，这里会优化时间范围查询
        return optimized_query

    def _optimize_tdengine_batch_size(self, query: DataQuery, db_type: DatabaseType) -> DataQuery:
        """优化TDengine批处理大小"""
        optimized_query = DataQuery(**query.__dict__)
        # 在实际实现中，这里会调整批处理大小
        return optimized_query

    def _suggest_tdengine_indexes(self, query: DataQuery) -> List[IndexRecommendation]:
        """建议TDengine索引"""
        recommendations = []

        # TDengine主要使用标签和列索引
        if query.filters:
            tag_columns = [col for col in query.filters.keys() if col in ["symbol", "exchange", "market"]]
            if tag_columns:
                recommendations.append(
                    IndexRecommendation(
                        table_name=query.table_name,
                        columns=tag_columns,
                        index_type="tag",
                        estimated_improvement=0.40,
                        creation_cost=0.05,
                        recommendation_reason=f"为标签列 {tag_columns} 建议标签索引",
                    )
                )

        return recommendations

    # 通用优化方法
    def _add_limit_clause(self, query: DataQuery, db_type: DatabaseType) -> DataQuery:
        """添加LIMIT子句"""
        if query.limit is None:
            optimized_query = DataQuery(**query.__dict__)
            optimized_query.limit = 1000  # 默认限制
            return optimized_query
        return query

    def _prune_columns(self, query: DataQuery, db_type: DatabaseType) -> DataQuery:
        """列裁剪"""
        if query.columns is None:
            # 在实际实现中，这里会分析查询只选择必要的列
            essential_columns = ["id", "timestamp"]  # 简化示例
            optimized_query = DataQuery(**query.__dict__)
            optimized_query.columns = essential_columns
            return optimized_query
        return query

    def _push_down_predicates(self, query: DataQuery, db_type: DatabaseType) -> DataQuery:
        """谓词下推"""
        optimized_query = DataQuery(**query.__dict__)
        # 在实际实现中，这里会将过滤条件尽可能下推到JOIN之前
        return optimized_query

    def _analyze_postgresql_index_usage(self, query: DataQuery) -> List[str]:
        """分析PostgreSQL索引使用"""
        return ["index_scan", "bitmap_index_scan"] if query.filters else ["sequential_scan"]

    def _analyze_tdengine_super_table_usage(self, query: DataQuery) -> bool:
        """分析TDengine超级表使用"""
        return self._is_time_series_query(query)

    def _analyze_tdengine_tag_filtering(self, query: DataQuery) -> List[str]:
        """分析TDengine标签过滤"""
        if query.filters:
            return [col for col in query.filters.keys() if col in ["symbol", "exchange", "market"]]
        return []

    def _analyze_tdengine_time_range(self, query: DataQuery) -> bool:
        """分析TDengine时间范围优化"""
        return self._has_time_filter(query)

    def get_optimization_statistics(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        if not self.optimization_history:
            return {"message": "暂无优化历史"}

        total_optimizations = len(self.optimization_history)
        avg_improvement = sum(r.estimated_improvement for r in self.optimization_history) / total_optimizations
        avg_time = sum(r.optimization_time for r in self.optimization_history) / total_optimizations

        # 最常用的优化规则
        rule_usage = {}
        for result in self.optimization_history:
            for rule_name in result.applied_optimizations:
                rule_usage[rule_name] = rule_usage.get(rule_name, 0) + 1

        return {
            "total_optimizations": total_optimizations,
            "average_improvement": avg_improvement,
            "average_optimization_time": avg_time,
            "most_used_rules": sorted(rule_usage.items(), key=lambda x: x[1], reverse=True)[:5],
            "cache_size": {
                "index_cache": len(self.index_cache),
                "plan_cache": len(self.plan_cache),
            },
        }


# 全局优化器实例
_global_optimizer = None


def get_global_optimizer() -> QueryOptimizer:
    """获取全局优化器实例"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = QueryOptimizer()
    return _global_optimizer
