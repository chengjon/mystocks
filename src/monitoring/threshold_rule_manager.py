"""
阈值规则管理器 - 从 intelligent_threshold_manager.py 拆分
职责：阈值规则管理、调整历史、优化记录
遵循 TDD 原则：仅实现满足测试的最小功能
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

# 设置日志
logger = logging.getLogger(__name__)


@dataclass
class ThresholdRule:
    """阈值规则定义"""

    name: str
    metric_name: str
    current_threshold: float
    optimal_threshold: Optional[float] = None
    threshold_type: str = "upper"  # 'upper', 'lower', 'range'
    confidence_score: float = 0.5
    learning_rate: float = 0.1
    adaptation_speed: float = 0.05
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    adjustment_count: int = 0
    last_adjustment: Optional[datetime] = None
    history: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.history is None:
            self.history = []


@dataclass
class ThresholdAdjustment:
    """阈值调整记录"""

    timestamp: datetime
    rule_name: str
    old_threshold: float
    new_threshold: float
    reason: str
    confidence: float
    metrics_snapshot: Dict[str, Any]
    predicted_effectiveness: float = 0.0
    actual_effectiveness: Optional[float] = None


class ThresholdRuleManager:
    """阈值规则管理器 - 专注于阈值规则的生命周期管理"""

    def __init__(self):
        """初始化阈值规则管理器"""
        self.rules: Dict[str, ThresholdRule] = {}
        self.adjustments: List[ThresholdAdjustment] = []
        self.logger = logging.getLogger(__name__)

    def create_threshold_rule(self, rule_data: Dict[str, Any]) -> ThresholdRule:
        """
        创建阈值规则

        Args:
            rule_data: 规则数据

        Returns:
            ThresholdRule: 创建的规则
        """
        rule = ThresholdRule(
            name=rule_data["name"],
            metric_name=rule_data["metric_name"],
            current_threshold=rule_data["current_threshold"],
            threshold_type=rule_data.get("threshold_type", "upper"),
            confidence_score=rule_data.get("confidence_score", 0.5),
            learning_rate=rule_data.get("learning_rate", 0.1),
            adaptation_speed=rule_data.get("adaptation_speed", 0.05),
        )

        self.rules[rule.name] = rule
        logger.info("Created threshold rule: %s", rule.name)

        return rule

    def adjust_threshold(
        self,
        rule_name: str,
        new_threshold: float,
        reason: str,
        confidence: float,
        metrics_snapshot: Optional[Dict[str, Any]] = None,
    ) -> Optional[ThresholdAdjustment]:
        """
        调整阈值

        Args:
            rule_name: 规则名称
            new_threshold: 新阈值
            reason: 调整原因
            confidence: 调整置信度
            metrics_snapshot: 指标快照

        Returns:
            ThresholdAdjustment: 调整记录
        """
        if rule_name not in self.rules:
            logger.warning("Rule not found: %s", rule_name)
            return None

        rule = self.rules[rule_name]
        old_threshold = rule.current_threshold

        # 创建调整记录
        adjustment = ThresholdAdjustment(
            timestamp=datetime.now(),
            rule_name=rule_name,
            old_threshold=old_threshold,
            new_threshold=new_threshold,
            reason=reason,
            confidence=confidence,
            metrics_snapshot=metrics_snapshot or {},
        )

        # 更新规则
        rule.current_threshold = new_threshold
        rule.adjustment_count += 1
        rule.last_adjustment = datetime.now()
        rule.confidence_score = max(0.0, min(1.0, confidence))

        # 添加到历史记录
        rule.history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "action": "adjustment",
                "old_threshold": old_threshold,
                "new_threshold": new_threshold,
                "reason": reason,
                "confidence": confidence,
            }
        )

        # 保存调整记录
        self.adjustments.append(adjustment)

        logger.info("Adjusted threshold for rule %s: %s -> %s", rule_name, old_threshold, new_threshold)

        return adjustment

    def get_rule(self, rule_name: str) -> Optional[ThresholdRule]:
        """
        获取阈值规则

        Args:
            rule_name: 规则名称

        Returns:
            ThresholdRule: 规则对象
        """
        return self.rules.get(rule_name)

    def get_all_rules(self) -> Dict[str, ThresholdRule]:
        """
        获取所有规则

        Returns:
            Dict[str, ThresholdRule]: 所有规则
        """
        return self.rules.copy()

    def delete_rule(self, rule_name: str) -> bool:
        """
        删除阈值规则

        Args:
            rule_name: 规则名称

        Returns:
            bool: 是否成功删除
        """
        if rule_name in self.rules:
            del self.rules[rule_name]
            logger.info("Deleted threshold rule: %s", rule_name)
            return True
        return False

    def get_rule_optimization_history(self, rule_name: str) -> List[Dict[str, Any]]:
        """
        获取规则优化历史

        Args:
            rule_name: 规则名称

        Returns:
            List[Dict[str, Any]]: 优化历史
        """
        if rule_name not in self.rules:
            return []

        rule = self.rules[rule_name]

        # 返回最近的调整历史
        return rule.history[-10:] if rule.history else []

    def get_recent_adjustments(self, count: int = 10, rule_name: Optional[str] = None) -> List[ThresholdAdjustment]:
        """
        获取最近的调整记录

        Args:
            count: 返回数量
            rule_name: 规则名称过滤

        Returns:
            List[ThresholdAdjustment]: 调整记录列表
        """
        adjustments = self.adjustments

        if rule_name:
            adjustments = [adj for adj in adjustments if adj.rule_name == rule_name]

        # 按时间倒序排列
        adjustments.sort(key=lambda x: x.timestamp, reverse=True)

        return adjustments[:count]

    def calculate_rule_effectiveness(self, rule_name: str) -> Dict[str, Any]:
        """
        计算规则有效性

        Args:
            rule_name: 规则名称

        Returns:
            Dict[str, Any]: 有效性分析
        """
        if rule_name not in self.rules:
            return {
                "effectiveness": 0.0,
                "total_adjustments": 0,
                "recent_adjustments": 0,
                "stability_score": 0.0,
            }

        rule = self.rules[rule_name]

        # 计算调整频率
        total_adjustments = rule.adjustment_count

        # 计算最近调整频率（最近30天）
        recent_adjustments = len(
            [
                adj
                for adj in self.adjustments
                if (adj.rule_name == rule_name and (datetime.now() - adj.timestamp).days <= 30)
            ]
        )

        # 计算稳定性（调整频率越低越稳定）
        if total_adjustments > 0:
            stability_score = max(0.0, 1.0 - (recent_adjustments / 10))
        else:
            stability_score = 1.0

        # 综合有效性评分
        effectiveness = rule.confidence_score * 0.4 + stability_score * 0.6

        return {
            "effectiveness": effectiveness,
            "total_adjustments": total_adjustments,
            "recent_adjustments": recent_adjustments,
            "stability_score": stability_score,
            "confidence_score": rule.confidence_score,
            "last_adjustment": rule.last_adjustment.isoformat() if rule.last_adjustment else None,
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        获取性能摘要

        Returns:
            Dict[str, Any]: 性能摘要
        """
        total_rules = len(self.rules)
        total_adjustments = len(self.adjustments)

        if total_adjustments == 0:
            return {
                "total_rules": total_rules,
                "total_adjustments": total_adjustments,
                "avg_adjustments_per_rule": 0.0,
                "most_adjusted_rule": None,
                "least_adjusted_rule": None,
                "recent_activity": False,
            }

        # 计算每个规则的调整次数
        rule_adjustments = {}
        for adj in self.adjustments:
            rule_adjustments[adj.rule_name] = rule_adjustments.get(adj.rule_name, 0) + 1

        if rule_adjustments:
            most_adjusted = max(rule_adjustments.keys(), key=rule_adjustments.get)
            least_adjusted = min(rule_adjustments.keys(), key=rule_adjustments.get)
            avg_adjustments = total_adjustments / total_rules
        else:
            most_adjusted = None
            least_adjusted = None
            avg_adjustments = 0.0

        # 检查最近活动
        recent_activity = len(self.get_recent_adjustments(count=1)) > 0

        return {
            "total_rules": total_rules,
            "total_adjustments": total_adjustments,
            "avg_adjustments_per_rule": avg_adjustments,
            "most_adjusted_rule": most_adjusted,
            "least_adjusted_rule": least_adjusted,
            "recent_activity": recent_activity,
            "rule_effectiveness": {
                rule_name: self.calculate_rule_effectiveness(rule_name) for rule_name in self.rules.keys()
            },
        }

    def export_rules(self) -> List[Dict[str, Any]]:
        """
        导出规则配置

        Returns:
            List[Dict[str, Any]]: 规则配置列表
        """
        return [asdict(rule) for rule in self.rules.values()]

    def import_rules(self, rules_data: List[Dict[str, Any]]) -> int:
        """
        导入规则配置

        Args:
            rules_data: 规则配置数据

        Returns:
            int: 导入的规则数量
        """
        imported_count = 0

        for rule_data in rules_data:
            try:
                if "name" in rule_data and rule_data["name"] not in self.rules:
                    rule = self.create_threshold_rule(rule_data)
                    imported_count += 1
                    logger.info("Imported rule: %s", rule.name)
            except Exception as e:
                logger.error("Failed to import rule %s: %s", rule_data.get("name", "unknown"), str(e))

        return imported_count

    def clear_all_adjustments(self):
        """清空所有调整记录"""
        self.adjustments.clear()
        for rule in self.rules.values():
            rule.adjustment_count = 0
            rule.last_adjustment = None
            rule.history.clear()

        logger.info("Cleared all adjustment records")

    def get_rule_statistics(self, rule_name: str) -> Dict[str, Any]:
        """
        获取规则统计信息

        Args:
            rule_name: 规则名称

        Returns:
            Dict[str, Any]: 统计信息
        """
        if rule_name not in self.rules:
            return {"error": f"Rule {rule_name} not found"}

        self.rules[rule_name]
        rule_adjustments = [adj for adj in self.adjustments if adj.rule_name == rule_name]

        if not rule_adjustments:
            return {
                "rule_name": rule_name,
                "total_adjustments": 0,
                "avg_adjustment_change": 0.0,
                "max_adjustment_change": 0.0,
                "min_adjustment_change": 0.0,
            }

        # 计算调整变化
        changes = [abs(adj.new_threshold - adj.old_threshold) for adj in rule_adjustments]

        return {
            "rule_name": rule_name,
            "total_adjustments": len(rule_adjustments),
            "avg_adjustment_change": np.mean(changes),
            "max_adjustment_change": np.max(changes),
            "min_adjustment_change": np.min(changes),
            "first_adjustment": rule_adjustments[0].timestamp.isoformat(),
            "last_adjustment": rule_adjustments[-1].timestamp.isoformat(),
        }
