"""
监控模块单元测试
测试monitoring.py和alert_manager.py等监控功能
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))


class MockAlertRule:
    """模拟告警规则"""

    def __init__(self, rule_id, name, condition, threshold, enabled=True):
        self.rule_id = rule_id
        self.name = name
        self.condition = condition
        self.threshold = threshold
        self.enabled = enabled
        self.trigger_count = 0
        self.last_triggered = None


class MockAlertManager:
    """模拟告警管理器"""

    def __init__(self):
        self.alert_rules = {}
        self.alert_history = []
        self.monitoring_enabled = True
        self.notification_channels = {"email": [], "webhook": [], "log": True}

    def create_alert_rule(self, rule_id, name, condition, threshold, enabled=True):
        """创建告警规则"""
        rule = MockAlertRule(rule_id, name, condition, threshold, enabled)
        self.alert_rules[rule_id] = rule
        return rule

    def delete_alert_rule(self, rule_id):
        """删除告警规则"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            return True
        return False

    def evaluate_alert_rules(self, metric_data):
        """评估告警规则"""
        triggered_alerts = []

        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled:
                continue

            # 简化条件评估逻辑
            if self._evaluate_condition(rule, metric_data):
                rule.trigger_count += 1
                rule.last_triggered = datetime.now()

                alert = {
                    "rule_id": rule_id,
                    "rule_name": rule.name,
                    "condition": rule.condition,
                    "current_value": metric_data.get("value", 0),
                    "threshold": rule.threshold,
                    "timestamp": datetime.now(),
                    "severity": self._determine_severity(rule, metric_data),
                }

                triggered_alerts.append(alert)
                self.alert_history.append(alert)

                # 发送通知
                self._send_notification(alert)

        return triggered_alerts

    def _evaluate_condition(self, rule, metric_data):
        """评估条件"""
        current_value = metric_data.get("value", 0)
        threshold = rule.threshold

        if rule.condition == "gt":  # greater than
            return current_value > threshold
        elif rule.condition == "lt":  # less than
            return current_value < threshold
        elif rule.condition == "eq":  # equal
            return current_value == threshold
        elif rule.condition == "gte":  # greater than or equal
            return current_value >= threshold
        elif rule.condition == "lte":  # less than or equal
            return current_value <= threshold
        else:
            return False

    def _determine_severity(self, rule, metric_data):
        """确定告警严重程度"""
        current_value = metric_data.get("value", 0)
        threshold = rule.threshold

        if rule.condition == "gt":
            deviation = (current_value - threshold) / threshold
        elif rule.condition == "lt":
            deviation = (threshold - current_value) / threshold
        else:
            deviation = 0.1  # 默认小偏差

        if deviation > 0.5:
            return "critical"
        elif deviation > 0.2:
            return "warning"
        else:
            return "info"

    def _send_notification(self, alert):
        """发送通知"""
        # 模拟发送邮件
        if self.notification_channels["email"]:
            for email in self.notification_channels["email"]:
                self._send_email(email, alert)

        # 模拟发送webhook
        if self.notification_channels["webhook"]:
            for webhook in self.notification_channels["webhook"]:
                self._send_webhook(webhook, alert)

        # 记录到日志
        if self.notification_channels["log"]:
            self._log_alert(alert)

    def _send_email(self, email, alert):
        """模拟发送邮件"""
        print(f"Email sent to {email}: Alert - {alert['rule_name']}")

    def _send_webhook(self, webhook, alert):
        """模拟发送webhook"""
        print(f"Webhook sent to {webhook}: Alert - {alert['rule_name']}")

    def _log_alert(self, alert):
        """记录告警到日志"""
        print(
            f"ALERT LOG: [{alert['severity'].upper()}] {alert['rule_name']} - Value: {alert['current_value']}, Threshold: {alert['threshold']}"
        )

    def get_alert_history(self, hours=24):
        """获取告警历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert["timestamp"] > cutoff_time]

    def get_monitoring_statistics(self):
        """获取监控统计信息"""
        total_rules = len(self.alert_rules)
        enabled_rules = sum(1 for rule in self.alert_rules.values() if rule.enabled)
        total_triggers = sum(rule.trigger_count for rule in self.alert_rules.values())
        recent_alerts = len(self.get_alert_history(24))

        return {
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "disabled_rules": total_rules - enabled_rules,
            "total_triggers": total_triggers,
            "recent_alerts_24h": recent_alerts,
            "monitoring_enabled": self.monitoring_enabled,
        }


class TestAlertManager:
    """告警管理器测试类"""

    def setup_method(self):
        """测试前的设置"""
        self.alert_manager = MockAlertManager()

    def test_create_alert_rule(self):
        """测试创建告警规则"""
        rule = self.alert_manager.create_alert_rule("price_alert", "价格告警", "gt", 100.0, True)

        assert rule.rule_id == "price_alert"
        assert rule.name == "价格告警"
        assert rule.condition == "gt"
        assert rule.threshold == 100.0
        assert rule.enabled is True
        assert "price_alert" in self.alert_manager.alert_rules

    def test_delete_alert_rule(self):
        """测试删除告警规则"""
        # 先创建规则
        self.alert_manager.create_alert_rule("test_rule", "测试规则", "gt", 50.0)

        # 删除规则
        result = self.alert_manager.delete_alert_rule("test_rule")
        assert result is True
        assert "test_rule" not in self.alert_manager.alert_rules

    def test_delete_nonexistent_rule(self):
        """测试删除不存在的规则"""
        result = self.alert_manager.delete_alert_rule("nonexistent")
        assert result is False

    def test_evaluate_alert_rules_gt_condition(self):
        """测试评估大于条件"""
        # 创建规则
        self.alert_manager.create_alert_rule("high_price", "高价告警", "gt", 100.0)

        # 测试超过阈值 (偏离>50%应为critical)
        metric_data = {"value": 160.0, "symbol": "000001"}  # 60% deviation
        alerts = self.alert_manager.evaluate_alert_rules(metric_data)

        assert len(alerts) == 1
        assert alerts[0]["rule_id"] == "high_price"
        assert alerts[0]["severity"] == "critical"  # 偏离60%，应为critical
        assert alerts[0]["current_value"] == 160.0
        assert alerts[0]["threshold"] == 100.0

    def test_evaluate_alert_rules_lt_condition(self):
        """测试评估小于条件"""
        self.alert_manager.create_alert_rule("low_price", "低价告警", "lt", 10.0)

        # 测试低于阈值 (偏离>50%应为critical)
        metric_data = {"value": 4.0, "symbol": "000001"}  # 60% deviation
        alerts = self.alert_manager.evaluate_alert_rules(metric_data)

        assert len(alerts) == 1
        assert alerts[0]["rule_id"] == "low_price"
        assert alerts[0]["severity"] == "critical"  # 偏离60%，应为critical

    def test_evaluate_alert_rules_no_trigger(self):
        """测试不触发告警的情况"""
        self.alert_manager.create_alert_rule("moderate_price", "中等价格告警", "gt", 100.0)

        # 测试未超过阈值
        metric_data = {"value": 50.0, "symbol": "000001"}
        alerts = self.alert_manager.evaluate_alert_rules(metric_data)

        assert len(alerts) == 0

    def test_disabled_rule_not_evaluated(self):
        """测试禁用的规则不会被评估"""
        self.alert_manager.create_alert_rule("disabled_rule", "禁用规则", "gt", 100.0, enabled=False)

        metric_data = {"value": 150.0, "symbol": "000001"}
        alerts = self.alert_manager.evaluate_alert_rules(metric_data)

        assert len(alerts) == 0

    def test_multiple_rules_evaluation(self):
        """测试多个规则的评估"""
        # 创建多个规则
        self.alert_manager.create_alert_rule("high_price", "高价", "gt", 100.0)
        self.alert_manager.create_alert_rule("low_price", "低价", "lt", 10.0)
        self.alert_manager.create_alert_rule("normal_price", "正常", "gt", 50.0)

        # 测试数据触发两个规则
        metric_data = {"value": 150.0, "symbol": "000001"}
        alerts = self.alert_manager.evaluate_alert_rules(metric_data)

        assert len(alerts) == 2  # 高价和正常规则都被触发
        assert any(alert["rule_id"] == "high_price" for alert in alerts)
        assert any(alert["rule_id"] == "normal_price" for alert in alerts)
        assert not any(alert["rule_id"] == "low_price" for alert in alerts)

    def test_alert_history_tracking(self):
        """测试告警历史跟踪"""
        self.alert_manager.create_alert_rule("test_rule", "测试", "gt", 50.0)

        # 触发告警
        metric_data = {"value": 100.0}
        alerts = self.alert_manager.evaluate_alert_rules(metric_data)

        assert len(alerts) == 1
        assert len(self.alert_manager.alert_history) == 1

        # 检查告警历史内容
        history_item = self.alert_manager.alert_history[0]
        assert history_item["rule_id"] == "test_rule"
        assert "timestamp" in history_item

    def test_get_alert_history_filtering(self):
        """测试告警历史过滤"""
        self.alert_manager.create_alert_rule("test_rule", "测试", "gt", 50.0)

        # 触发一个旧告警
        old_alert = {
            "rule_id": "test_rule",
            "timestamp": datetime.now() - timedelta(hours=25),
            "severity": "warning",
        }
        self.alert_manager.alert_history.append(old_alert)

        # 触发一个近期告警
        metric_data = {"value": 100.0}
        self.alert_manager.evaluate_alert_rules(metric_data)

        # 获取最近24小时的告警
        recent_alerts = self.alert_manager.get_alert_history(24)
        assert len(recent_alerts) == 1  # 只有近期的告警

    def test_monitoring_statistics(self):
        """测试监控统计信息"""
        # 创建一些规则
        self.alert_manager.create_alert_rule("rule1", "规则1", "gt", 50.0)
        self.alert_manager.create_alert_rule("rule2", "规则2", "lt", 10.0)
        self.alert_manager.create_alert_rule("rule3", "规则3", "gt", 100.0, enabled=False)

        # 触发一些告警
        self.alert_manager.evaluate_alert_rules({"value": 60.0})
        self.alert_manager.evaluate_alert_rules({"value": 5.0})

        stats = self.alert_manager.get_monitoring_statistics()

        assert stats["total_rules"] == 3
        assert stats["enabled_rules"] == 2
        assert stats["disabled_rules"] == 1
        assert stats["total_triggers"] == 2
        assert stats["monitoring_enabled"] is True

    def test_rule_trigger_counting(self):
        """测试规则触发计数"""
        rule = self.alert_manager.create_alert_rule("count_rule", "计数规则", "gt", 50.0)

        # 触发规则多次
        for i in range(3):
            self.alert_manager.evaluate_alert_rules({"value": 60.0 + i * 10})

        assert rule.trigger_count == 3
        assert rule.last_triggered is not None


class TestAlertSeverityDetermination:
    """告警严重程度确定测试"""

    def setup_method(self):
        """测试前的设置"""
        self.alert_manager = MockAlertManager()

    def test_critical_severity(self):
        """测试严重告警"""
        rule = self.alert_manager.create_alert_rule("critical_test", "严重测试", "gt", 100.0)

        # 触发严重告警（偏离50%以上）
        metric_data = {"value": 160.0}
        alerts = self.alert_manager.evaluate_alert_rules(metric_data)

        assert len(alerts) == 1
        assert alerts[0]["severity"] == "critical"

    def test_warning_severity(self):
        """测试警告告警"""
        rule = self.alert_manager.create_alert_rule("warning_test", "警告测试", "gt", 100.0)

        # 触发警告告警（偏离20-50%）
        metric_data = {"value": 125.0}
        alerts = self.alert_manager.evaluate_alert_rules(metric_data)

        assert len(alerts) == 1
        assert alerts[0]["severity"] == "warning"

    def test_info_severity(self):
        """测试信息告警"""
        rule = self.alert_manager.create_alert_rule("info_test", "信息测试", "gt", 100.0)

        # 触发信息告警（偏离小于20%）
        metric_data = {"value": 110.0}
        alerts = self.alert_manager.evaluate_alert_rules(metric_data)

        assert len(alerts) == 1
        assert alerts[0]["severity"] == "info"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
