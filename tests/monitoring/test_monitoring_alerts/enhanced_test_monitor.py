"""
测试监控告警系统

提供全面的测试监控、告警管理和通知功能。
"""

import json
import logging
import queue
import smtplib
import statistics
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import psutil
import requests
from jinja2 import Template
from pydantic import BaseModel, Field
from prometheus_client import Counter, Gauge, Histogram, start_http_server

from ...ai.test_data_manager import DataManager as AIDataManager

class EnhancedTestMonitor:
    """增强的测试监控器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.real_time_monitor = RealTimeMonitor(config.get("real_time_monitor", {}))
        self.performance_analyzer = IntelligentPerformanceAnalyzer(config.get("performance_analyzer", {}))
        self.performance_optimizer = DynamicPerformanceOptimizer(config.get("performance_optimizer", {}))

        # 测试结果历史
        self.test_results: List[TestExecutionResult] = []
        self.test_stats = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "error": 0,
        }

    def start_monitoring(self):
        """启动监控"""
        self.real_time_monitor.start_monitoring()
        logging.info("增强的测试监控已启动")

    def stop_monitoring(self):
        """停止监控"""
        self.real_time_monitor.stop_monitoring()
        logging.info("增强的测试监控已停止")

    def record_test_result(self, result: TestExecutionResult):
        """记录测试结果"""
        # 添加到历史
        self.test_results.append(result)

        # 更新统计
        self.test_stats["total"] += 1
        if result.status == "passed":
            self.test_stats["passed"] += 1
        elif result.status == "failed":
            self.test_stats["failed"] += 1
        elif result.status == "skipped":
            self.test_stats["skipped"] += 1
        elif result.status == "error":
            self.test_stats["error"] += 1

        # 更新Prometheus指标
        self._update_test_metrics(result)

        # 分析性能
        metrics = self._build_metrics_from_result(result)
        analysis_result = self.performance_analyzer.analyze_performance_patterns(metrics)

        # 优化性能
        if analysis_result["anomalies"]:
            optimization_result = self.performance_optimizer.optimize_performance(analysis_result)
            logging.info(f"性能优化完成，改进: {optimization_result['performance_improvement']:.2%}")

        # 限制历史大小
        max_history = self.config.get("max_test_history", 1000)
        if len(self.test_results) > max_history:
            self.test_results = self.test_results[-max_history:]

    def _update_test_metrics(self, result: TestExecutionResult):
        """更新测试指标"""
        try:
            # 更新测试执行计数
            self.real_time_monitor.prometheus_metrics["test_executions_total"].labels(
                status=result.status, test_type=result.test_type
            ).inc()

            # 更新执行时间直方图
            self.real_time_monitor.prometheus_metrics["test_execution_duration"].labels(
                test_type=result.test_type
            ).observe(result.execution_time)

        except Exception as e:
            logging.error(f"更新测试指标失败: {e}")

    def _build_metrics_from_result(self, result: TestExecutionResult) -> Dict[str, Any]:
        """从测试结果构建指标"""
        return {
            "cpu_usage": result.cpu_usage / 100.0,
            "memory_usage": result.memory_usage / 100.0,
            "test_execution_time": result.execution_time,
            "test_result": 1.0 if result.status == "passed" else 0.0,
            "timestamp": result.timestamp,
        }

    def get_comprehensive_dashboard_data(self) -> Dict[str, Any]:
        """获取综合仪表板数据"""
        dashboard_data = self.real_time_monitor.get_dashboard_data()

        # 添加测试统计
        dashboard_data["test_statistics"] = self.test_stats.copy()
        dashboard_data["test_statistics"]["pass_rate"] = (
            self.test_stats["passed"] / self.test_stats["total"] if self.test_stats["total"] > 0 else 0
        )

        # 添加最近的测试结果
        recent_tests = self.test_results[-10:]
        dashboard_data["recent_tests"] = [
            {
                "name": test.test_name,
                "status": test.status,
                "execution_time": test.execution_time,
                "timestamp": test.timestamp.isoformat(),
            }
            for test in recent_tests
        ]

        # 添加性能分析结果
        if self.performance_analyzer.pattern_history:
            latest_analysis = self.performance_analyzer.pattern_history[-1]
            dashboard_data["performance_analysis"] = {
                "anomalies_count": len(latest_analysis["anomalies"]),
                "recommendations": latest_analysis["recommendations"],
            }

        # 添加优化历史
        dashboard_data["optimization_history"] = self.performance_optimizer.optimization_history[-5:]

        return dashboard_data


def demo_test_monitoring():
    """演示测试监控告警功能"""
    print("🚀 演示测试监控告警系统")

    # 创建告警管理器
    alert_manager = TestAlertManager()

    # 启动监控
    alert_manager.start_monitoring()

    # 模拟测试执行
    for i in range(10):
        import random

        test_name = f"test_{i + 1}"
        execution_time = random.uniform(10, 300)
        passed = random.choice([True, True, False])  # 66.7% 通过率
        memory_mb = random.uniform(100, 2000)
        cpu_percent = random.uniform(20, 90)

        alert_manager.record_test_metrics(
            test_name=test_name,
            execution_time=execution_time,
            passed=passed,
            memory_mb=memory_mb,
            cpu_percent=cpu_percent,
        )

        time.sleep(2)

    # 获取仪表板数据
    dashboard_data = alert_manager.get_dashboard_data()
    print("\n📊 仪表板数据:")
    print(f"告警摘要: {dashboard_data['alerts']}")
    print(f"指标摘要: {list(dashboard_data['metrics'].keys())}")

    # 导出告警数据
    alert_manager.export_alerts("test_alerts.json", "json")

    # 停止监控
    alert_manager.stop_monitoring()

