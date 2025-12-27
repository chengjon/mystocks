#!/usr/bin/env python3
"""
# 功能：智能阈值管理器 - 主控制器
# 作者：MyStocks AI开发团队
# 创建日期：2025-12-20
# 版本：2.0.0 (重构版本)
# 说明：重构后的智能阈值管理器主控制器
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 导入模块化组件
from .base_threshold_manager import (
    ThresholdRule,
    ThresholdAdjustment,
    OptimizationResult,
    DataAnalyzer,
)
from .statistical_optimizer import StatisticalOptimizer
from .trend_optimizer import TrendOptimizer
from .clustering_optimizer import ClusteringOptimizer

# 监控组件导入
try:
    from ..performance_monitor import SystemMetrics
    from ..monitoring_database import get_monitoring_database
except ImportError:
    # 兼容模式
    SystemMetrics = Any
    get_monitoring_database = None

logger = logging.getLogger(__name__)


class IntelligentThresholdManager:
    """智能阈值管理器 - 主控制器

    重构改进:
    ✅ 原文件1,282行 → 拆分为5个模块化文件
    ✅ 功能分离：基础管理器、统计优化、趋势分析、聚类分析
    ✅ 更好的代码组织和可维护性
    ✅ 保持完整功能兼容性
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化智能阈值管理器"""
        self.config = config or self._get_default_config()
        self.threshold_rules: Dict[str, ThresholdRule] = {}
        self.adjustment_history: List[ThresholdAdjustment] = []
        self.data_analyzers: Dict[str, DataAnalyzer] = {}

        # 优化器
        self.statistical_optimizer = StatisticalOptimizer()
        self.trend_optimizer = TrendOptimizer()
        self.clustering_optimizer = ClusteringOptimizer()

        # 监控数据库
        self.monitoring_db = None
        if get_monitoring_database:
            try:
                self.monitoring_db = get_monitoring_database()
            except Exception as e:
                logger.warning(f"监控数据库初始化失败: {e}")

        # 初始化默认阈值规则
        self._initialize_default_rules()

        logger.info("✅ 智能阈值管理器初始化完成 (重构版本)")

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "learning_rate": 0.1,
            "adaptation_speed": 0.05,
            "min_data_points": 30,
            "optimization_interval": 3600,  # 1小时
            "max_history_size": 1000,
            "false_positive_threshold": 0.1,
            "false_negative_threshold": 0.05,
            "confidence_threshold": 0.7,
            "trend_analysis_window": 24,  # 24小时
            "anomaly_detection_contamination": 0.1,
        }

    def _initialize_default_rules(self) -> None:
        """初始化默认阈值规则"""
        default_rules = [
            # CPU使用率阈值
            ThresholdRule(
                name="cpu_usage_high",
                metric_name="cpu_usage",
                current_threshold=80.0,
                threshold_type="upper",
                confidence_score=0.8,
            ),
            # 内存使用率阈值
            ThresholdRule(
                name="memory_usage_high",
                metric_name="memory_usage",
                current_threshold=85.0,
                threshold_type="upper",
                confidence_score=0.8,
            ),
            # 磁盘使用率阈值
            ThresholdRule(
                name="disk_usage_high",
                metric_name="disk_usage",
                current_threshold=90.0,
                threshold_type="upper",
                confidence_score=0.8,
            ),
            # 响应时间阈值
            ThresholdRule(
                name="response_time_high",
                metric_name="response_time",
                current_threshold=2000.0,  # 2秒
                threshold_type="upper",
                confidence_score=0.7,
            ),
            # 错误率阈值
            ThresholdRule(
                name="error_rate_high",
                metric_name="error_rate",
                current_threshold=5.0,  # 5%
                threshold_type="upper",
                confidence_score=0.8,
            ),
        ]

        for rule in default_rules:
            self.threshold_rules[rule.name] = rule
            self.data_analyzers[rule.name] = DataAnalyzer()

        logger.info(f"初始化了{len(default_rules)}个默认阈值规则")

    async def optimize_all_thresholds(self) -> Dict[str, OptimizationResult]:
        """优化所有阈值"""
        results = {}

        for rule_name, rule in self.threshold_rules.items():
            try:
                result = await self.optimize_threshold(rule_name)
                results[rule_name] = result
            except Exception as e:
                logger.error(f"优化阈值 {rule_name} 失败: {e}")
                results[rule_name] = OptimizationResult(
                    rule_name=rule_name,
                    optimization_type="error",
                    recommended_threshold=rule.current_threshold,
                    confidence_score=0.0,
                    expected_improvement=0.0,
                    reasoning=f"优化过程出错: {str(e)}",
                    supporting_evidence=[],
                    metadata={"error": True},
                )

        return results

    async def optimize_threshold(self, rule_name: str, optimization_methods: List[str] = None) -> OptimizationResult:
        """优化指定阈值"""
        if rule_name not in self.threshold_rules:
            raise ValueError(f"阈值规则 {rule_name} 不存在")

        rule = self.threshold_rules[rule_name]
        self.data_analyzers[rule_name]

        # 获取历史数据
        values, timestamps = await self._get_metric_history(rule.metric_name)

        if len(values) < self.config["min_data_points"]:
            return OptimizationResult(
                rule_name=rule_name,
                optimization_type="insufficient_data",
                recommended_threshold=rule.current_threshold,
                confidence_score=0.1,
                expected_improvement=0.0,
                reasoning="历史数据不足，无法进行优化",
                supporting_evidence=[f"需要至少{self.config['min_data_points']}个数据点"],
                metadata={"data_points": len(values)},
            )

        # 默认使用所有优化方法
        if optimization_methods is None:
            optimization_methods = ["statistical", "trend", "clustering"]

        results = []

        # 统计优化
        if "statistical" in optimization_methods:
            try:
                stat_result = self.statistical_optimizer.optimize_threshold_statistical(
                    values, rule.current_threshold, rule.threshold_type
                )
                results.append(stat_result)
            except Exception as e:
                logger.error(f"统计优化失败: {e}")

        # 趋势优化
        if "trend" in optimization_methods and timestamps:
            try:
                trend_result = self.trend_optimizer.optimize_threshold_trend(
                    values, timestamps, rule.current_threshold, rule.threshold_type
                )
                results.append(trend_result)
            except Exception as e:
                logger.error(f"趋势优化失败: {e}")

        # 聚类优化
        if "clustering" in optimization_methods:
            try:
                cluster_result = self.clustering_optimizer.optimize_threshold_clustering(
                    values, rule.current_threshold, rule.threshold_type
                )
                results.append(cluster_result)
            except Exception as e:
                logger.error(f"聚类优化失败: {e}")

        if not results:
            return OptimizationResult(
                rule_name=rule_name,
                optimization_type="failed",
                recommended_threshold=rule.current_threshold,
                confidence_score=0.0,
                expected_improvement=0.0,
                reasoning="所有优化方法都失败了",
                supporting_evidence=[],
                metadata={"error": True},
            )

        # 选择最佳结果
        best_result = max(results, key=lambda r: r.confidence_score * r.expected_improvement)

        # 如果置信度足够高，应用新的阈值
        if best_result.confidence_score >= self.config["confidence_threshold"]:
            await self._apply_threshold_optimization(rule_name, best_result)

        return best_result

    async def _apply_threshold_optimization(self, rule_name: str, optimization_result: OptimizationResult) -> None:
        """应用阈值优化结果"""
        if rule_name not in self.threshold_rules:
            return

        rule = self.threshold_rules[rule_name]
        old_threshold = rule.current_threshold

        # 更新阈值
        rule.current_threshold = optimization_result.recommended_threshold
        rule.optimal_threshold = optimization_result.recommended_threshold
        rule.confidence_score = optimization_result.confidence_score
        rule.adjustment_count += 1
        rule.last_adjustment = datetime.now()

        # 记录调整历史
        adjustment = ThresholdAdjustment(
            timestamp=datetime.now(),
            rule_name=rule_name,
            old_threshold=old_threshold,
            new_threshold=optimization_result.recommended_threshold,
            reason=optimization_result.reasoning,
            confidence=optimization_result.confidence_score,
            metrics_snapshot={
                "optimization_type": optimization_result.optimization_type,
                "expected_improvement": optimization_result.expected_improvement,
            },
            predicted_effectiveness=optimization_result.expected_improvement,
        )

        self.adjustment_history.append(adjustment)

        # 限制历史记录数量
        if len(self.adjustment_history) > self.config["max_history_size"]:
            self.adjustment_history = self.adjustment_history[-self.config["max_history_size"] :]

        # 保存到数据库
        if self.monitoring_db:
            try:
                await self._save_adjustment_to_db(adjustment)
            except Exception as e:
                logger.error(f"保存调整记录到数据库失败: {e}")

        logger.info(
            f"阈值优化完成: {rule_name} {old_threshold} -> {optimization_result.recommended_threshold} "
            f"(置信度: {optimization_result.confidence_score:.2f})"
        )

    async def _get_metric_history(self, metric_name: str, hours_back: int = 24) -> tuple[List[float], List[datetime]]:
        """获取指标历史数据"""
        try:
            if self.monitoring_db:
                # 从监控数据库获取数据
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=hours_back)

                data = await self.monitoring_db.get_metrics_history(metric_name, start_time, end_time)

                if data:
                    values = [record["value"] for record in data]
                    timestamps = [record["timestamp"] for record in data]
                    return values, timestamps

            # 如果没有数据库，返回空列表
            return [], []
        except Exception as e:
            logger.error(f"获取指标历史数据失败: {e}")
            return [], []

    async def _save_adjustment_to_db(self, adjustment: ThresholdAdjustment) -> None:
        """保存调整记录到数据库"""
        if self.monitoring_db:
            await self.monitoring_db.save_threshold_adjustment(adjustment)

    def add_threshold_rule(self, rule: ThresholdRule) -> None:
        """添加新的阈值规则"""
        self.threshold_rules[rule.name] = rule
        self.data_analyzers[rule.name] = DataAnalyzer()
        logger.info(f"添加阈值规则: {rule.name}")

    def get_threshold_rule(self, rule_name: str) -> Optional[ThresholdRule]:
        """获取阈值规则"""
        return self.threshold_rules.get(rule_name)

    def get_all_threshold_rules(self) -> Dict[str, ThresholdRule]:
        """获取所有阈值规则"""
        return self.threshold_rules.copy()

    def get_adjustment_history(self, rule_name: Optional[str] = None, limit: int = 100) -> List[ThresholdAdjustment]:
        """获取调整历史"""
        history = self.adjustment_history

        if rule_name:
            history = [adj for adj in history if adj.rule_name == rule_name]

        # 按时间倒序排列，限制数量
        history = sorted(history, key=lambda x: x.timestamp, reverse=True)
        return history[:limit]

    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "total_rules": len(self.threshold_rules),
            "active_rules": len([r for r in self.threshold_rules.values() if r.confidence_score > 0.5]),
            "total_adjustments": len(self.adjustment_history),
            "recent_adjustments": len(
                [adj for adj in self.adjustment_history if (datetime.now() - adj.timestamp).hours < 24]
            ),
            "config": self.config,
            "database_connected": self.monitoring_db is not None,
        }

    async def start_optimization_loop(self) -> None:
        """启动自动优化循环"""
        while True:
            try:
                logger.info("开始自动阈值优化...")

                results = await self.optimize_all_thresholds()

                successful_optimizations = [
                    r for r in results.values() if r.confidence_score >= self.config["confidence_threshold"]
                ]

                logger.info(f"自动优化完成: {len(successful_optimizations)}/{len(results)} 个阈值被优化")

            except Exception as e:
                logger.error(f"自动优化循环出错: {e}")

            # 等待下一次优化
            await asyncio.sleep(self.config["optimization_interval"])

    def analyze_metric_data(self, metric_name: str, values: List[float]) -> Dict[str, Any]:
        """分析指标数据"""
        if metric_name in self.data_analyzers:
            analyzer = self.data_analyzers[metric_name]
        else:
            analyzer = DataAnalyzer()

        try:
            # 基础统计分析
            basic_stats = analyzer.analyze_basic_statistics(values)

            # 异常值检测
            outlier_info = analyzer.detect_outliers_iqr(values)

            # 移动统计
            moving_stats = analyzer.calculate_moving_statistics(values)

            # 波动性分析
            volatility_info = analyzer.analyze_volatility(values)

            # 数据质量
            quality_metrics = analyzer.get_data_quality_metrics(values)

            return {
                "basic_statistics": basic_stats,
                "outlier_detection": outlier_info,
                "moving_statistics": moving_stats,
                "volatility_analysis": volatility_info,
                "data_quality": quality_metrics,
                "data_points": len(values),
            }
        except Exception as e:
            logger.error(f"指标数据分析失败: {e}")
            return {"error": str(e), "data_points": len(values)}
