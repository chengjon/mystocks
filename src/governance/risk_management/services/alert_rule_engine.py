"""
告警规则引擎和去重机制
Alert Rule Engine and Deduplication Mechanism

实现灵活的告警规则定义、条件评估和智能去重。
支持规则组合、优先级管理和告警抑制。
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """告警严重程度"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertAction(Enum):
    """告警动作类型"""

    NOTIFY = "notify"
    ESCALATE = "escalate"
    SUPPRESS = "suppress"
    AGGREGATE = "aggregate"
    IGNORE = "ignore"


@dataclass
class AlertRule:
    """告警规则"""

    rule_id: str
    name: str
    description: str
    enabled: bool = True
    priority: int = 1  # 1-10, 10为最高优先级

    # 条件定义
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    condition_logic: str = "AND"  # "AND" 或 "OR"

    # 动作定义
    actions: List[Dict[str, Any]] = field(default_factory=list)

    # 规则属性
    cooldown_period: int = 300  # 冷却期(秒)
    max_frequency: int = 5  # 最大触发频率(次/小时)
    suppression_window: int = 60  # 抑制窗口(秒)

    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: Set[str] = field(default_factory=set)


@dataclass
class AlertContext:
    """告警上下文"""

    symbol: Optional[str] = None
    portfolio_id: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AlertResult:
    """告警评估结果"""

    triggered: bool
    rule_id: str
    severity: AlertSeverity
    actions: List[Dict[str, Any]]
    context: AlertContext
    evaluation_details: Dict[str, Any] = field(default_factory=dict)


class AlertRuleEngine:
    """
    告警规则引擎

    实现灵活的告警规则定义、条件评估和智能去重。
    支持规则组合、优先级管理和告警抑制。
    """

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.rule_execution_history: Dict[str, List[datetime]] = {}
        self.active_suppressions: Dict[str, datetime] = {}
        self.alert_cache: Dict[str, AlertResult] = {}

        # 内置规则模板
        self._load_builtin_rules()

        logger.info("✅ 告警规则引擎初始化完成")

    def add_rule(self, rule: AlertRule) -> bool:
        """
        添加告警规则

        Args:
            rule: 告警规则

        Returns:
            是否成功添加
        """
        try:
            if rule.rule_id in self.rules:
                logger.warning("规则已存在，将被覆盖: {rule.rule_id")

            self.rules[rule.rule_id] = rule
            logger.info("✅ 告警规则已添加: {rule.rule_id} - {rule.name")
            return True

        except Exception:
            logger.error("添加告警规则失败 {rule.rule_id}: %(e)s")
            return False

    def remove_rule(self, rule_id: str) -> bool:
        """
        移除告警规则

        Args:
            rule_id: 规则ID

        Returns:
            是否成功移除
        """
        try:
            if rule_id in self.rules:
                del self.rules[rule_id]
                # 清理相关历史数据
                if rule_id in self.rule_execution_history:
                    del self.rule_execution_history[rule_id]
                logger.info("✅ 告警规则已移除: %(rule_id)s")
                return True
            else:
                logger.warning("规则不存在: %(rule_id)s")
                return False

        except Exception:
            logger.error("移除告警规则失败 %(rule_id)s: %(e)s")
            return False

    def evaluate_rules(self, context: AlertContext) -> List[AlertResult]:
        """
        评估所有规则

        Args:
            context: 告警上下文

        Returns:
            触发的告警结果列表
        """
        try:
            triggered_alerts = []

            for rule in self.rules.values():
                if not rule.enabled:
                    continue

                # 检查是否被抑制
                if self._is_rule_suppressed(rule.rule_id):
                    continue

                # 检查频率限制
                if not self._check_frequency_limit(rule):
                    continue

                # 评估规则条件
                result = self._evaluate_rule(rule, context)
                if result.triggered:
                    triggered_alerts.append(result)

                    # 记录执行历史
                    self._record_rule_execution(rule.rule_id)

                    # 应用抑制（如果需要）
                    if any(action.get("type") == "suppress" for action in result.actions):
                        self._apply_suppression(rule.rule_id, rule.suppression_window)

            # 按优先级排序
            triggered_alerts.sort(key=lambda x: self.rules[x.rule_id].priority, reverse=True)

            logger.debug("规则评估完成，触发告警: {len(triggered_alerts)} 个")
            return triggered_alerts

        except Exception:
            logger.error("规则评估失败: %(e)s")
            return []

    def create_rule_from_template(
        self, template_name: str, rule_id: str, parameters: Dict[str, Any]
    ) -> Optional[AlertRule]:
        """
        从模板创建规则

        Args:
            template_name: 模板名称
            rule_id: 规则ID
            parameters: 参数字典

        Returns:
            创建的规则或None
        """
        try:
            template = self._get_rule_template(template_name)
            if not template:
                logger.error("模板不存在: %(template_name)s")
                return None

            # 应用参数到模板
            rule_data = template.copy()
            rule_data.update(parameters)
            rule_data["rule_id"] = rule_id

            rule = AlertRule(**rule_data)
            return rule

        except Exception:
            logger.error("从模板创建规则失败 %(template_name)s: %(e)s")
            return None

    def get_rule_statistics(self) -> Dict[str, Any]:
        """
        获取规则统计信息

        Returns:
            统计数据
        """
        try:
            total_rules = len(self.rules)
            enabled_rules = len([r for r in self.rules.values() if r.enabled])
            disabled_rules = total_rules - enabled_rules

            # 执行频率统计
            execution_stats = {}
            for rule_id, executions in self.rule_execution_history.items():
                # 计算最近1小时的执行次数
                recent_executions = [ts for ts in executions if datetime.now() - ts < timedelta(hours=1)]
                execution_stats[rule_id] = len(recent_executions)

            return {
                "total_rules": total_rules,
                "enabled_rules": enabled_rules,
                "disabled_rules": disabled_rules,
                "active_suppressions": len(self.active_suppressions),
                "execution_stats": execution_stats,
                "generated_at": datetime.now(),
            }

        except Exception as e:
            logger.error("获取规则统计失败: %(e)s")
            return {"error": str(e)}

    def clear_expired_suppressions(self):
        """清除过期的抑制"""
        try:
            now = datetime.now()
            expired_keys = [key for key, expiry in self.active_suppressions.items() if now > expiry]

            for key in expired_keys:
                del self.active_suppressions[key]

            if expired_keys:
                logger.info("清除 {len(expired_keys)} 个过期的告警抑制")

        except Exception:
            logger.error("清除过期抑制失败: %(e)s")

    # 私有方法

    def _load_builtin_rules(self):
        """加载内置规则"""
        try:
            # 高VaR告警规则
            var_rule = AlertRule(
                rule_id="high_var_alert",
                name="高VaR风险告警",
                description="当VaR超过阈值时触发告警",
                conditions=[{"field": "var_1d_95", "operator": ">", "value": 0.08, "description": "1日VaR超过8%"}],
                actions=[
                    {
                        "type": "notify",
                        "severity": "warning",
                        "message": "VaR风险超标",
                        "channels": ["email", "webhook"],
                    }
                ],
                tags={"risk_type", "var", "portfolio"},
            )
            self.add_rule(var_rule)

            # 高波动率告警规则
            volatility_rule = AlertRule(
                rule_id="high_volatility_alert",
                name="高波动率告警",
                description="当波动率超过阈值时触发告警",
                conditions=[
                    {"field": "volatility_20d", "operator": ">", "value": 0.40, "description": "20日波动率超过40%"}
                ],
                actions=[{"type": "notify", "severity": "warning", "message": "波动率风险超标", "channels": ["email"]}],
                tags={"risk_type", "volatility", "stock"},
            )
            self.add_rule(volatility_rule)

            # 集中度过高告警规则
            concentration_rule = AlertRule(
                rule_id="high_concentration_alert",
                name="集中度过高告警",
                description="当组合集中度过高时触发告警",
                conditions=[{"field": "hhi", "operator": ">", "value": 0.30, "description": "HHI指数超过0.3"}],
                actions=[
                    {
                        "type": "notify",
                        "severity": "critical",
                        "message": "组合集中度风险极高",
                        "channels": ["email", "webhook", "sms"],
                    },
                    {
                        "type": "escalate",
                        "escalation_time": 300,  # 5分钟后升级
                    },
                ],
                tags={"risk_type", "concentration", "portfolio"},
                priority=8,
            )
            self.add_rule(concentration_rule)

            logger.info("✅ 内置告警规则加载完成")

        except Exception:
            logger.error("加载内置规则失败: %(e)s")

    def _evaluate_rule(self, rule: AlertRule, context: AlertContext) -> AlertResult:
        """评估单个规则"""
        try:
            # 评估所有条件
            condition_results = []
            for condition in rule.conditions:
                result = self._evaluate_condition(condition, context)
                condition_results.append(result)

            # 根据逻辑运算符组合条件结果
            if rule.condition_logic == "AND":
                triggered = all(condition_results)
            elif rule.condition_logic == "OR":
                triggered = any(condition_results)
            else:
                triggered = False

            # 确定告警严重程度
            severity = self._determine_rule_severity(rule, context)

            result = AlertResult(
                triggered=triggered,
                rule_id=rule.rule_id,
                severity=severity,
                actions=rule.actions if triggered else [],
                context=context,
                evaluation_details={
                    "condition_results": condition_results,
                    "condition_logic": rule.condition_logic,
                    "overall_triggered": triggered,
                },
            )

            return result

        except Exception as e:
            logger.error("规则评估失败 {rule.rule_id}: %(e)s")
            return AlertResult(
                triggered=False,
                rule_id=rule.rule_id,
                severity=AlertSeverity.INFO,
                actions=[],
                context=context,
                evaluation_details={"error": str(e)},
            )

    def _evaluate_condition(self, condition: Dict[str, Any], context: AlertContext) -> bool:
        """评估单个条件"""
        try:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")

            if not field or not operator:
                return False

            # 获取字段值
            field_value = self._get_field_value(field, context)

            # 应用运算符
            if operator == ">":
                return field_value > value
            elif operator == "<":
                return field_value < value
            elif operator == ">=":
                return field_value >= value
            elif operator == "<=":
                return field_value <= value
            elif operator == "==":
                return field_value == value
            elif operator == "!=":
                return field_value != value
            elif operator == "in":
                return field_value in value
            elif operator == "not_in":
                return field_value not in value
            else:
                logger.warning("不支持的运算符: %(operator)s")
                return False

        except Exception:
            logger.error("条件评估失败: %(e)s")
            return False

    def _get_field_value(self, field: str, context: AlertContext) -> Any:
        """获取字段值"""
        # 首先检查metrics
        if field in context.metrics:
            return context.metrics[field]

        # 然后检查metadata
        if field in context.metadata:
            return context.metadata[field]

        # 最后检查context对象的属性
        if hasattr(context, field):
            return getattr(context, field)

        # 默认返回None
        return None

    def _determine_rule_severity(self, rule: AlertRule, context: AlertContext) -> AlertSeverity:
        """确定规则严重程度"""
        # 从规则动作中提取严重程度
        for action in rule.actions:
            if "severity" in action:
                severity_str = action["severity"]
                try:
                    return AlertSeverity(severity_str)
                except ValueError:
                    continue

        # 默认返回WARNING
        return AlertSeverity.WARNING

    def _is_rule_suppressed(self, rule_id: str) -> bool:
        """检查规则是否被抑制"""
        if rule_id in self.active_suppressions:
            if datetime.now() < self.active_suppressions[rule_id]:
                return True
            else:
                # 抑制已过期
                del self.active_suppressions[rule_id]
        return False

    def _check_frequency_limit(self, rule: AlertRule) -> bool:
        """检查频率限制"""
        try:
            if rule.rule_id not in self.rule_execution_history:
                return True

            executions = self.rule_execution_history[rule.rule_id]

            # 计算最近1小时的执行次数
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_executions = [ts for ts in executions if ts > one_hour_ago]

            return len(recent_executions) < rule.max_frequency

        except Exception:
            logger.error("检查频率限制失败 {rule.rule_id}: %(e)s")
            return True  # 出错时允许执行

    def _record_rule_execution(self, rule_id: str):
        """记录规则执行"""
        if rule_id not in self.rule_execution_history:
            self.rule_execution_history[rule_id] = []

        self.rule_execution_history[rule_id].append(datetime.now())

        # 只保留最近100条记录
        if len(self.rule_execution_history[rule_id]) > 100:
            self.rule_execution_history[rule_id] = self.rule_execution_history[rule_id][-100:]

    def _apply_suppression(self, rule_id: str, duration: int):
        """应用抑制"""
        self.active_suppressions[rule_id] = datetime.now() + timedelta(seconds=duration)
        logger.info("规则已抑制 %(duration)s秒: %(rule_id)s")

    def _get_rule_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """获取规则模板"""
        templates = {
            "var_threshold": {
                "name": "VaR阈值告警",
                "description": "当VaR超过指定阈值时触发告警",
                "conditions": [
                    {
                        "field": "var_1d_95",
                        "operator": ">",
                        "value": "{threshold}",
                        "description": f"VaR超过 {threshold}%",
                    }
                ],
                "actions": [{"type": "notify", "severity": "warning", "message": "VaR风险超标", "channels": ["email"]}],
                "tags": ["risk_type", "var"],
            },
            "volatility_spike": {
                "name": "波动率激增告警",
                "description": "当波动率快速上升时触发告警",
                "conditions": [
                    {
                        "field": "volatility_20d",
                        "operator": ">",
                        "value": "{threshold}",
                        "description": f"波动率超过 {threshold}%",
                    }
                ],
                "actions": [
                    {"type": "notify", "severity": "warning", "message": "波动率激增", "channels": ["email", "webhook"]}
                ],
                "tags": ["risk_type", "volatility"],
            },
        }

        return templates.get(template_name)

    def export_rules(self, filepath: str) -> bool:
        """导出规则到文件"""
        try:
            rules_data = {}
            for rule_id, rule in self.rules.items():
                rules_data[rule_id] = {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "description": rule.description,
                    "enabled": rule.enabled,
                    "priority": rule.priority,
                    "conditions": rule.conditions,
                    "condition_logic": rule.condition_logic,
                    "actions": rule.actions,
                    "cooldown_period": rule.cooldown_period,
                    "max_frequency": rule.max_frequency,
                    "suppression_window": rule.suppression_window,
                    "tags": list(rule.tags),
                    "created_at": rule.created_at.isoformat(),
                    "updated_at": rule.updated_at.isoformat(),
                }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(rules_data, f, indent=2, ensure_ascii=False)

            logger.info("✅ 规则已导出到: %(filepath)s")
            return True

        except Exception:
            logger.error("导出规则失败: %(e)s")
            return False

    def import_rules(self, filepath: str) -> int:
        """从文件导入规则"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                rules_data = json.load(f)

            imported_count = 0
            for rule_data in rules_data.values():
                try:
                    # 转换数据类型
                    rule_data["created_at"] = datetime.fromisoformat(rule_data["created_at"])
                    rule_data["updated_at"] = datetime.fromisoformat(rule_data["updated_at"])
                    rule_data["tags"] = set(rule_data["tags"])

                    rule = AlertRule(**rule_data)
                    if self.add_rule(rule):
                        imported_count += 1

                except Exception:
                    logger.error("导入规则失败 {rule_data.get('rule_id')}: %(e)s")
                    continue

            logger.info("✅ 成功导入 %(imported_count)s 个规则")
            return imported_count

        except Exception:
            logger.error("导入规则失败: %(e)s")
            return 0


# 创建全局实例
_alert_rule_engine: Optional[AlertRuleEngine] = None


def get_alert_rule_engine() -> AlertRuleEngine:
    """获取告警规则引擎实例（单例模式）"""
    global _alert_rule_engine
    if _alert_rule_engine is None:
        _alert_rule_engine = AlertRuleEngine()
    return _alert_rule_engine
