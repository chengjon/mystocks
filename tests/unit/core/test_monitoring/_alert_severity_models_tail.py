#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Support model tests extracted from `test_alert_severity.py`."""

from datetime import datetime, timedelta

from src.core.monitoring import Alert, AlertRule, AlertSeverity, MetricType, MetricValue


class TestAlertSeverity:
    """警报严重程度枚举测试"""

    def test_severity_values(self):
        """测试严重程度枚举值"""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"

    def test_severity_enum_properties(self):
        """测试严重程度枚举属性"""
        info = AlertSeverity.INFO
        assert info.name == "INFO"
        assert info.value == "info"
        assert isinstance(info.value, str)


class TestMetricType:
    """指标类型枚举测试"""

    def test_metric_type_values(self):
        """测试指标类型枚举值"""
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.TIMER.value == "timer"

    def test_metric_type_enum_properties(self):
        """测试指标类型枚举属性"""
        counter = MetricType.COUNTER
        assert counter.name == "COUNTER"
        assert counter.value == "counter"
        assert isinstance(counter.value, str)


class TestAlertRule:
    """警报规则测试"""

    def test_alert_rule_creation(self):
        """测试警报规则创建"""
        rule = AlertRule(
            name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            duration=timedelta(minutes=5),
        )

        assert rule.name == "cpu_usage"
        assert rule.condition == ">"
        assert rule.threshold == 80.0
        assert rule.severity == AlertSeverity.WARNING
        assert rule.duration == timedelta(minutes=5)
        assert rule.enabled is True

    def test_alert_rule_defaults(self):
        """测试警报规则默认值"""
        rule = AlertRule(name="test_rule", condition="<", threshold=10.0, severity=AlertSeverity.INFO)

        assert rule.duration is None
        assert rule.enabled is True


class TestMetricValue:
    """指标值测试"""

    def test_metric_value_creation(self):
        """测试指标值创建"""
        timestamp = datetime.now()
        metric = MetricValue(
            name="cpu_usage",
            value=75.5,
            timestamp=timestamp,
            labels={"host": "server1"},
            metric_type=MetricType.GAUGE,
        )

        assert metric.name == "cpu_usage"
        assert metric.value == 75.5
        assert metric.timestamp == timestamp
        assert metric.labels == {"host": "server1"}
        assert metric.metric_type == MetricType.GAUGE

    def test_metric_value_defaults(self):
        """测试指标值默认值"""
        timestamp = datetime.now()
        metric = MetricValue(name="test_metric", value=100.0, timestamp=timestamp)

        assert metric.labels is None
        assert metric.metric_type == MetricType.GAUGE


class TestAlert:
    """警报测试"""

    def test_alert_creation(self):
        """测试警报创建"""
        timestamp = datetime.now()
        alert = Alert(
            id="alert_123",
            rule_name="cpu_usage",
            severity=AlertSeverity.WARNING,
            message="CPU usage exceeds threshold",
            timestamp=timestamp,
        )

        assert alert.id == "alert_123"
        assert alert.rule_name == "cpu_usage"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.message == "CPU usage exceeds threshold"
        assert alert.timestamp == timestamp
        assert alert.resolved is False
        assert alert.resolved_at is None

    def test_alert_resolution(self):
        """测试警报解决"""
        timestamp = datetime.now()
        resolved_at = datetime.now()

        alert = Alert(
            id="alert_456",
            rule_name="memory_usage",
            severity=AlertSeverity.ERROR,
            message="Memory usage high",
            timestamp=timestamp,
        )

        alert.resolved = True
        alert.resolved_at = resolved_at

        assert alert.resolved is True
        assert alert.resolved_at == resolved_at
