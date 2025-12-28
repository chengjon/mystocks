"""
智能查询路由器
根据查询特征和数据特性自动路由到最优数据库
"""

import re
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

from src.data_access.interfaces.i_data_access import (
    IDataAccess,
    DataQuery,
    QueryOperation,
    DatabaseType,
    IQueryRouter,
)
from ..capabilities.database_detector import (
    DatabaseCapabilityDetector,
    CapabilityProfile,
)

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """路由策略"""

    DATABASE_FEATURE_BASED = "database_feature_based"
    DATA_CHARACTERISTIC_BASED = "data_characteristic_based"
    PERFORMANCE_BASED = "performance_based"
    COST_BASED = "cost_based"
    LOAD_BALANCE_BASED = "load_balance_based"


class DataCharacteristic(Enum):
    """数据特征"""

    TIME_SERIES = "time_series"
    RELATIONAL = "relational"
    HIGH_FREQUENCY = "high_frequency"
    LARGE_DATASET = "large_dataset"
    REAL_TIME = "real_time"
    ANALYTICAL = "analytical"
    TRANSACTIONAL = "transactional"


@dataclass
class RoutingRule:
    """路由规则"""

    name: str
    strategy: RoutingStrategy
    condition: Callable[[DataQuery], bool]
    target_database: DatabaseType
    priority: int = 1
    description: str = ""
    enabled: bool = True


@dataclass
class RoutingDecision:
    """路由决策"""

    target_database: DatabaseType
    selected_adapter: IDataAccess
    confidence: float
    reasoning: str
    alternative_options: List[Tuple[DatabaseType, IDataAccess, str]]
    estimated_cost: Optional[float] = None
    execution_time_estimate: Optional[float] = None


@dataclass
class RoutingMetrics:
    """路由指标"""

    total_routes: int
    database_usage: Dict[DatabaseType, int]
    average_routing_time: float
    cache_hit_rate: float
    failed_routes: int
    fallback_usage: int


class QueryRouter(IQueryRouter):
    """智能查询路由器"""

    def __init__(self):
        self.adapters: Dict[DatabaseType, List[IDataAccess]] = {}
        self.routing_rules: List[RoutingRule] = []
        self.capability_detector = DatabaseCapabilityDetector()
        self.capability_cache: Dict[DatabaseType, CapabilityProfile] = {}
        self.routing_metrics = RoutingMetrics(
            total_routes=0,
            database_usage={},
            average_routing_time=0.0,
            cache_hit_rate=0.0,
            failed_routes=0,
            fallback_usage=0,
        )
        self._initialize_default_rules()

    def register_adapter(self, adapter: IDataAccess):
        """注册数据访问适配器"""
        db_type = adapter.get_database_type()
        if db_type not in self.adapters:
            self.adapters[db_type] = []
        self.adapters[db_type].append(adapter)
        logger.info(f"注册适配器: {db_type.value}, 总数: {len(self.adapters[db_type])}")

    def _initialize_default_rules(self):
        """初始化默认路由规则"""
        # 时间序列数据路由到TDengine
        self.routing_rules.append(
            RoutingRule(
                name="time_series_to_tdengine",
                strategy=RoutingStrategy.DATA_CHARACTERISTIC_BASED,
                condition=self._is_time_series_query,
                target_database=DatabaseType.TDENGINE,
                priority=2,
                description="时间序列查询路由到TDengine",
            )
        )

        # 高频写入路由到TDengine
        self.routing_rules.append(
            RoutingRule(
                name="high_frequency_write_to_tdengine",
                strategy=RoutingStrategy.DATA_CHARACTERISTIC_BASED,
                condition=self._is_high_frequency_write,
                target_database=DatabaseType.TDENGINE,
                priority=3,
                description="高频写入操作路由到TDengine",
            )
        )

        # 关系型查询路由到PostgreSQL
        self.routing_rules.append(
            RoutingRule(
                name="relational_to_postgresql",
                strategy=RoutingStrategy.DATA_CHARACTERISTIC_BASED,
                condition=self._is_relational_query,
                target_database=DatabaseType.POSTGRESQL,
                priority=2,
                description="关系型查询路由到PostgreSQL",
            )
        )

        # 事务操作路由到PostgreSQL
        self.routing_rules.append(
            RoutingRule(
                name="transactional_to_postgresql",
                strategy=RoutingStrategy.DATABASE_FEATURE_BASED,
                condition=self._requires_acid_transaction,
                target_database=DatabaseType.POSTGRESQL,
                priority=5,
                description="事务操作路由到PostgreSQL",
            )
        )

        # 复杂查询路由到PostgreSQL
        self.routing_rules.append(
            RoutingRule(
                name="complex_query_to_postgresql",
                strategy=RoutingStrategy.DATABASE_FEATURE_BASED,
                condition=self._is_complex_query,
                target_database=DatabaseType.POSTGRESQL,
                priority=4,
                description="复杂查询路由到PostgreSQL",
            )
        )

        # 按表名规则路由
        self.routing_rules.append(
            RoutingRule(
                name="table_based_routing",
                strategy=RoutingStrategy.DATA_CHARACTERISTIC_BASED,
                condition=self._is_timeseries_table,
                target_database=DatabaseType.TDENGINE,
                priority=1,
                description="时序表路由到TDengine",
            )
        )

    async def route_query(self, query: DataQuery) -> IDataAccess:
        """路由查询到合适的数据访问实例"""
        start_time = datetime.now()

        try:
            decision = await self._make_routing_decision(query)
            self._update_metrics(start_time, success=True)

            logger.info(f"查询路由到: {decision.target_database.value}, 置信度: {decision.confidence:.2f}")
            logger.debug(f"路由原因: {decision.reasoning}")

            return decision.selected_adapter

        except Exception as e:
            self._update_metrics(start_time, success=False)
            logger.error(f"查询路由失败: {e}")
            raise

    async def route_operation(self, operation: QueryOperation, table_name: str) -> IDataAccess:
        """路由操作到合适的数据库"""
        # 创建简单查询用于路由
        query = DataQuery(operation=operation, table_name=table_name)
        return await self.route_query(query)

    def add_routing_rule(self, rule: Callable[[DataQuery], bool], target: IDataAccess):
        """添加路由规则"""
        db_type = target.get_database_type()
        routing_rule = RoutingRule(
            name=f"custom_rule_{len(self.routing_rules)}",
            strategy=RoutingStrategy.DATABASE_FEATURE_BASED,
            condition=rule,
            target_database=db_type,
            priority=len(self.routing_rules),
        )
        self.routing_rules.append(routing_rule)
        logger.info(f"添加自定义路由规则: {routing_rule.name}")

    def remove_routing_rule(self, rule: Callable):
        """移除路由规则"""
        self.routing_rules = [r for r in self.routing_rules if r.condition != rule]
        logger.info("移除路由规则")

    async def _make_routing_decision(self, query: DataQuery) -> RoutingDecision:
        """做出路由决策"""
        applicable_rules = []

        # 评估所有路由规则
        for rule in self.routing_rules:
            if rule.enabled and rule.condition(query):
                try:
                    confidence = self._calculate_rule_confidence(rule, query)
                    applicable_rules.append((rule, confidence))
                except Exception as e:
                    logger.warning(f"评估路由规则失败 {rule.name}: {e}")

        # 按优先级和置信度排序
        applicable_rules.sort(key=lambda x: (x[0].priority, -x[1]))

        if not applicable_rules:
            # 无适用规则，使用默认策略
            return await self._fallback_routing(query)

        # 选择最佳规则
        best_rule, best_confidence = applicable_rules[0]
        target_db = best_rule.target_database

        # 选择适配器
        selected_adapter = await self._select_adapter(target_db)

        # 生成替代方案
        alternatives = await self._generate_alternatives(query, target_db, applicable_rules[1:3])

        return RoutingDecision(
            target_database=target_db,
            selected_adapter=selected_adapter,
            confidence=best_confidence,
            reasoning=f"匹配规则: {best_rule.name} - {best_rule.description}",
            alternative_options=alternatives,
            estimated_cost=self._estimate_routing_cost(query, target_db),
        )

    async def _select_adapter(self, target_db: DatabaseType) -> IDataAccess:
        """选择适配器"""
        if target_db not in self.adapters or not self.adapters[target_db]:
            raise ValueError(f"没有可用的 {target_db.value} 适配器")

        # 简单的负载均衡：选择连接数最少的适配器
        # 在实际实现中，应该考虑更复杂的负载均衡策略
        adapters = self.adapters[target_db]

        # 这里可以添加更复杂的选择逻辑
        # 例如：基于连接池状态、响应时间、错误率等
        return adapters[0]

    async def _generate_alternatives(
        self,
        query: DataQuery,
        primary_db: DatabaseType,
        other_rules: List[Tuple[RoutingRule, float]],
    ) -> List[Tuple[DatabaseType, IDataAccess, str]]:
        """生成替代方案"""
        alternatives = []

        for rule, confidence in other_rules:
            try:
                if rule.target_database in self.adapters and self.adapters[rule.target_database]:
                    adapter = await self._select_adapter(rule.target_database)
                    reason = f"替代规则: {rule.name} (置信度: {confidence:.2f})"
                    alternatives.append((rule.target_database, adapter, reason))
            except Exception:
                continue

        return alternatives

    async def _fallback_routing(self, query: DataQuery) -> RoutingDecision:
        """回退路由策略"""
        logger.warning("使用回退路由策略")

        # 优先使用PostgreSQL
        if DatabaseType.POSTGRESQL in self.adapters and self.adapters[DatabaseType.POSTGRESQL]:
            adapter = await self._select_adapter(DatabaseType.POSTGRESQL)
            return RoutingDecision(
                target_database=DatabaseType.POSTGRESQL,
                selected_adapter=adapter,
                confidence=0.5,
                reasoning="回退路由：使用PostgreSQL作为默认数据库",
                alternative_options=[],
            )

        # 其次使用TDengine
        elif DatabaseType.TDENGINE in self.adapters and self.adapters[DatabaseType.TDENGINE]:
            adapter = await self._select_adapter(DatabaseType.TDENGINE)
            return RoutingDecision(
                target_database=DatabaseType.TDENGINE,
                selected_adapter=adapter,
                confidence=0.5,
                reasoning="回退路由：使用TDengine作为默认数据库",
                alternative_options=[],
            )

        else:
            raise ValueError("没有可用的数据访问适配器")

    def _calculate_rule_confidence(self, rule: RoutingRule, query: DataQuery) -> float:
        """计算规则置信度"""
        # 基于规则优先级和查询特征的置信度计算
        base_confidence = 0.7

        # 根据优先级调整
        priority_adjustment = min(rule.priority * 0.05, 0.2)

        # 根据查询特征调整
        feature_adjustment = 0.0

        if rule.strategy == RoutingStrategy.DATA_CHARACTERISTIC_BASED:
            feature_adjustment = self._calculate_feature_confidence(query)
        elif rule.strategy == RoutingStrategy.DATABASE_FEATURE_BASED:
            feature_adjustment = self._calculate_feature_confidence(query)

        confidence = base_confidence + priority_adjustment + feature_adjustment
        return min(confidence, 1.0)

    def _calculate_feature_confidence(self, query: DataQuery) -> float:
        """计算特征置信度"""
        confidence = 0.0

        # 时间序列特征
        if self._is_time_series_query(query):
            confidence += 0.2

        # 高频写入特征
        if self._is_high_frequency_write(query):
            confidence += 0.15

        # 关系型查询特征
        if self._is_relational_query(query):
            confidence += 0.15

        # 复杂查询特征
        if self._is_complex_query(query):
            confidence += 0.1

        return confidence

    def _is_time_series_query(self, query: DataQuery) -> bool:
        """判断是否为时间序列查询"""
        # 检查表名模式
        timeseries_patterns = [
            r".*tick_data$",
            r".*minute_data$",
            r".*ohlcv$",
            r".*market_data$",
            r".*time_series$",
            r".*stream$",
        ]

        table_name = query.table_name.lower()
        for pattern in timeseries_patterns:
            if re.match(pattern, table_name):
                return True

        # 检查列名是否包含时间特征
        if query.columns:
            time_columns = [
                "timestamp",
                "time",
                "created_at",
                "updated_at",
                "trade_time",
            ]
            for col in time_columns:
                if col in query.columns:
                    return True

        # 检查过滤器中的时间条件
        if query.filters:
            for key, value in query.filters.items():
                if any(time_key in key.lower() for time_key in ["time", "date", "timestamp"]):
                    return True

        return False

    def _is_high_frequency_write(self, query: DataQuery) -> bool:
        """判断是否为高频写入操作"""
        return query.operation in [
            QueryOperation.INSERT,
            QueryOperation.BATCH_INSERT,
            QueryOperation.UPSERT,
        ]

    def _is_relational_query(self, query: DataQuery) -> bool:
        """判断是否为关系型查询"""
        # 包含JOIN操作
        if query.join_clauses and len(query.join_clauses) > 0:
            return True

        # 包含GROUP BY和HAVING
        if query.group_by or query.having:
            return True

        # 包含窗口函数
        if query.window_functions and len(query.window_functions) > 0:
            return True

        return False

    def _requires_acid_transaction(self, query: DataQuery) -> bool:
        """判断是否需要ACID事务"""
        transactional_operations = [QueryOperation.UPDATE, QueryOperation.DELETE]

        # 多个操作需要事务
        if query.operation in transactional_operations:
            return True

        # 批量操作通常需要事务保护
        if query.operation in [
            QueryOperation.BATCH_INSERT,
            QueryOperation.BATCH_UPDATE,
        ]:
            return True

        return False

    def _is_complex_query(self, query: DataQuery) -> bool:
        """判断是否为复杂查询"""
        complexity_score = 0

        # JOIN操作增加复杂度
        if query.join_clauses:
            complexity_score += len(query.join_clauses) * 2

        # 子查询增加复杂度
        if query.filters:
            for key, value in query.filters.items():
                if isinstance(value, (list, dict)) or "SELECT" in str(value).upper():
                    complexity_score += 3

        # 聚合操作增加复杂度
        if query.group_by:
            complexity_score += len(query.group_by)

        # 窗口函数增加复杂度
        if query.window_functions:
            complexity_score += len(query.window_functions) * 2

        # 大量列可能增加复杂度
        if query.columns and len(query.columns) > 10:
            complexity_score += 1

        return complexity_score >= 3

    def _is_timeseries_table(self, query: DataQuery) -> bool:
        """根据表名判断是否为时序表"""
        timeseries_table_patterns = [
            r".*_tick$",
            r".*_minute$",
            r".*_hourly$",
            r".*_daily$",
            r".*_ohlcv$",
            r".*_market$",
            r".*_price$",
            r".*_volume$",
            r".*_stream$",
            r".*_series$",
        ]

        table_name = query.table_name.lower()
        for pattern in timeseries_table_patterns:
            if re.match(pattern, table_name):
                return True

        return False

    def _estimate_routing_cost(self, query: DataQuery, target_db: DatabaseType) -> float:
        """估算路由成本"""
        # 简化的成本估算
        base_cost = 1.0

        if target_db == DatabaseType.TDENGINE:
            if self._is_time_series_query(query):
                base_cost *= 0.5  # TDengine对时序数据更高效
            else:
                base_cost *= 1.5  # 对非时序数据效率较低

        elif target_db == DatabaseType.POSTGRESQL:
            if self._is_relational_query(query):
                base_cost *= 0.7  # PostgreSQL对关系型查询更高效
            elif self._is_time_series_query(query):
                base_cost *= 1.2  # 时序数据查询效率相对较低

        return base_cost

    def _update_metrics(self, start_time: datetime, success: bool):
        """更新路由指标"""
        execution_time = (datetime.now() - start_time).total_seconds()

        self.routing_metrics.total_routes += 1

        if not success:
            self.routing_metrics.failed_routes += 1

        # 更新平均路由时间
        if self.routing_metrics.total_routes == 1:
            self.routing_metrics.average_routing_time = execution_time
        else:
            total_time = self.routing_metrics.average_routing_time * (self.routing_metrics.total_routes - 1)
            self.routing_metrics.average_routing_time = (
                total_time + execution_time
            ) / self.routing_metrics.total_routes

    def get_routing_metrics(self) -> RoutingMetrics:
        """获取路由指标"""
        return self.routing_metrics

    def reset_metrics(self):
        """重置路由指标"""
        self.routing_metrics = RoutingMetrics(
            total_routes=0,
            database_usage={},
            average_routing_time=0.0,
            cache_hit_rate=0.0,
            failed_routes=0,
            fallback_usage=0,
        )

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            "router_status": "healthy",
            "registered_adapters": {},
            "active_rules": len([r for r in self.routing_rules if r.enabled]),
            "metrics": self.routing_metrics,
            "timestamp": datetime.now().isoformat(),
        }

        # 检查适配器状态
        for db_type, adapters in self.adapters.items():
            health_status["registered_adapters"][db_type.value] = {
                "count": len(adapters),
                "status": "available" if adapters else "unavailable",
            }

        return health_status


# 全局路由器实例
_global_router = None


def get_global_router() -> QueryRouter:
    """获取全局路由器实例"""
    global _global_router
    if _global_router is None:
        _global_router = QueryRouter()
    return _global_router
