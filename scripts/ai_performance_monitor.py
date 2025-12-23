#!/usr/bin/env python3
"""
MyStocks AI性能监控器
实时监控AI系统性能和异常
"""

import time
import psutil
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIPerformanceMonitor:
    def __init__(self):
        self.monitoring_data = []
        self.alert_thresholds = {
            "cpu_usage": 80,
            "memory_usage": 85,
            "error_rate": 5,
            "response_time": 2.0,
        }

    def collect_metrics(self) -> dict:
        """收集性能指标"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "process_count": len(psutil.pids()),
            "load_average": psutil.getloadavg()[0]
            if hasattr(psutil, "getloadavg")
            else 0,
        }

    def check_alerts(self, metrics: dict) -> list:
        """检查告警条件"""
        alerts = []

        for metric, value in metrics.items():
            if metric in self.alert_thresholds:
                threshold = self.alert_thresholds[metric]
                if (
                    metric == "cpu_usage"
                    or metric == "memory_usage"
                    or metric == "disk_percent"
                ) and value > threshold:
                    alerts.append(f"⚠️  {metric}: {value:.1f}% 超过阈值 {threshold}%")
                elif metric == "response_time" and value > threshold:
                    alerts.append(f"⚠️  {metric}: {value:.2f}秒 超过阈值 {threshold}秒")

        return alerts

    def run_monitoring(self, duration: int = 60):
        """运行监控"""
        logger.info(f"🔍 开始AI性能监控，时长: {duration}秒")

        start_time = time.time()

        while time.time() - start_time < duration:
            metrics = self.collect_metrics()
            alerts = self.check_alerts(metrics)

            self.monitoring_data.append({"metrics": metrics, "alerts": alerts})

            if alerts:
                for alert in alerts:
                    logger.warning(alert)
            else:
                logger.info(
                    f"✅ 系统运行正常 - CPU: {metrics['cpu_percent']:.1f}% 内存: {metrics['memory_percent']:.1f}%"
                )

            time.sleep(10)

        # 保存监控数据
        monitor_file = Path("ai_performance_monitor.json")
        with open(monitor_file, "w", encoding="utf-8") as f:
            json.dump(self.monitoring_data, f, ensure_ascii=False, indent=2)

        logger.info(f"📊 监控完成，数据已保存到 {monitor_file}")
        return self.monitoring_data


if __name__ == "__main__":
    monitor = AIPerformanceMonitor()
    monitor.run_monitoring(duration=30)  # 监控30秒作为测试
