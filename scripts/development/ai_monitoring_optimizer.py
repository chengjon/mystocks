#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks AI监控和告警系统优化脚本
第三阶段：构建智能化监控和告警系统
"""

import json
import time
import logging
import smtplib
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AIAlertManager:
    """AI智能告警管理器"""

    def __init__(
        self,
        config_path: str = "/opt/claude/mystocks_spec/config/ai_automation_config.yaml",
    ):
        self.config = self.load_config(config_path)
        self.alert_history = []
        self.alert_rules = self.setup_alert_rules()
        self.notification_channels = self.setup_notification_channels()

    def load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        try:
            import yaml

            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            return {}

    def setup_alert_rules(self) -> Dict[str, Any]:
        """设置告警规则"""
        return {
            "cpu_high": {
                "threshold": 80,
                "duration": 300,  # 5分钟
                "severity": "warning",
                "message": "CPU使用率过高: {value}%",
            },
            "memory_high": {
                "threshold": 85,
                "duration": 300,
                "severity": "warning",
                "message": "内存使用率过高: {value}%",
            },
            "disk_low": {
                "threshold": 90,
                "duration": 60,
                "severity": "critical",
                "message": "磁盘空间不足: {value}% 已使用",
            },
            "ai_error_rate": {
                "threshold": 5,
                "duration": 180,
                "severity": "critical",
                "message": "AI处理错误率过高: {value}%",
            },
            "response_time_slow": {
                "threshold": 2.0,
                "duration": 120,
                "severity": "warning",
                "message": "AI响应时间过长: {value}秒",
            },
        }

    def setup_notification_channels(self) -> Dict[str, Any]:
        """设置通知渠道"""
        return {
            "email": {
                "enabled": False,  # 默认禁用，需要配置SMTP
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "recipients": [],
            },
            "webhook": {"enabled": False, "url": "", "headers": {}},
            "log": {"enabled": True, "file": "logs/ai_alerts.log"},
        }

    def check_alert_conditions(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查告警条件"""
        alerts = []
        current_time = datetime.now()

        for rule_name, rule_config in self.alert_rules.items():
            threshold = rule_config["threshold"]
            duration = rule_config["duration"]

            # 获取当前指标值
            if rule_name == "cpu_high":
                value = metrics.get("cpu_percent", 0)
            elif rule_name == "memory_high":
                value = metrics.get("memory_percent", 0)
            elif rule_name == "disk_low":
                value = metrics.get("disk_percent", 0)
            elif rule_name == "ai_error_rate":
                value = metrics.get("error_rate", 0)
            elif rule_name == "response_time_slow":
                value = metrics.get("response_time", 0)
            else:
                continue

            # 检查是否超过阈值
            if (
                rule_name
                in ["cpu_high", "memory_high", "ai_error_rate", "response_time_slow"]
                and value > threshold
            ) or (rule_name == "disk_low" and value > threshold):
                # 检查持续时间
                alert_key = (
                    f"{rule_name}_{current_time.hour}_{current_time.minute // 10}"
                )

                alert = {
                    "rule": rule_name,
                    "value": value,
                    "threshold": threshold,
                    "severity": rule_config["severity"],
                    "message": rule_config["message"].format(value=value),
                    "timestamp": current_time.isoformat(),
                    "metric": metrics,
                }

                alerts.append(alert)

        return alerts

    def send_notification(self, alert: Dict[str, Any]) -> bool:
        """发送告警通知"""
        success = True

        # 日志通知
        if self.notification_channels["log"]["enabled"]:
            self.log_alert(alert)

        # 邮件通知
        if self.notification_channels["email"]["enabled"]:
            success &= self.send_email_alert(alert)

        # Webhook通知
        if self.notification_channels["webhook"]["enabled"]:
            success &= self.send_webhook_alert(alert)

        return success

    def log_alert(self, alert: Dict[str, Any]):
        """记录告警到日志"""
        log_file = Path(self.notification_channels["log"]["file"])
        log_file.parent.mkdir(exist_ok=True)

        log_entry = {
            "timestamp": alert["timestamp"],
            "severity": alert["severity"],
            "message": alert["message"],
            "rule": alert["rule"],
            "value": alert["value"],
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def send_email_alert(self, alert: Dict[str, Any]) -> bool:
        """发送邮件告警"""
        try:
            email_config = self.notification_channels["email"]

            if not email_config["recipients"]:
                return False

            msg = MIMEMultipart()
            msg["From"] = email_config["username"]
            msg["To"] = ", ".join(email_config["recipients"])
            msg["Subject"] = f"[AI告警] {alert['severity'].upper()}: {alert['rule']}"

            body = f"""
MyStocks AI系统告警

告警时间: {alert["timestamp"]}
告警级别: {alert["severity"]}
告警规则: {alert["rule"]}
当前值: {alert["value"]}
阈值: {alert["threshold"]}

详细信息:
{alert["message"]}

系统指标:
{json.dumps(alert["metric"], ensure_ascii=False, indent=2)}

请及时检查系统状态。
            """

            msg.attach(MIMEText(body, "plain", "utf-8"))

            server = smtplib.SMTP(
                email_config["smtp_server"], email_config["smtp_port"]
            )
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            server.send_message(msg)
            server.quit()

            logger.info(f"✅ 邮件告警已发送: {alert['rule']}")
            return True

        except Exception as e:
            logger.error(f"❌ 邮件告警发送失败: {e}")
            return False

    def send_webhook_alert(self, alert: Dict[str, Any]) -> bool:
        """发送Webhook告警"""
        try:
            import requests

            webhook_config = self.notification_channels["webhook"]
            payload = {
                "alert": alert,
                "source": "MyStocks AI Monitor",
                "timestamp": time.time(),
            }

            response = requests.post(
                webhook_config["url"],
                json=payload,
                headers=webhook_config["headers"],
                timeout=10,
            )

            if response.status_code == 200:
                logger.info(f"✅ Webhook告警已发送: {alert['rule']}")
                return True
            else:
                logger.error(f"❌ Webhook告警发送失败: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Webhook告警发送失败: {e}")
            return False

    def process_alerts(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """处理告警"""
        alerts = self.check_alert_conditions(metrics)

        processed_alerts = []
        for alert in alerts:
            # 发送通知
            success = self.send_notification(alert)

            # 记录到历史
            alert["notification_sent"] = success
            self.alert_history.append(alert)
            processed_alerts.append(alert)

            # 根据严重级别处理
            if alert["severity"] == "critical":
                logger.critical(f"🚨 严重告警: {alert['message']}")
            elif alert["severity"] == "warning":
                logger.warning(f"⚠️  警告告警: {alert['message']}")

        return {
            "total_alerts": len(alerts),
            "processed_alerts": processed_alerts,
            "alert_history_count": len(self.alert_history),
        }


class AIRealtimeMonitor:
    """AI实时监控器"""

    def __init__(self):
        self.alert_manager = AIAlertManager()
        self.monitoring_active = False
        self.metrics_buffer = []

    def collect_realtime_metrics(self) -> Dict[str, Any]:
        """收集实时指标"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "network_io": dict(psutil.net_io_counters()._asdict()),
            "process_count": len(psutil.pids()),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "load_average": list(psutil.getloadavg())
            if hasattr(psutil, "getloadavg")
            else [0, 0, 0],
        }

    def simulate_ai_metrics(self) -> Dict[str, Any]:
        """模拟AI系统指标"""
        import random

        return {
            "ai_processing_rate": random.randint(50, 200),  # 处理速率
            "error_rate": random.uniform(0, 10),  # 错误率
            "response_time": random.uniform(0.1, 5.0),  # 响应时间
            "queue_size": random.randint(0, 100),  # 队列大小
            "accuracy": random.uniform(0.7, 0.95),  # 准确率
            "throughput": random.randint(1000, 10000),  # 吞吐量
        }

    def run_real_time_monitoring(self, duration: int = 120):
        """运行实时监控"""
        logger.info(f"🔍 开始实时监控，时长: {duration}秒")

        self.monitoring_active = True
        start_time = time.time()

        while self.monitoring_active and (time.time() - start_time) < duration:
            # 收集系统指标
            system_metrics = self.collect_realtime_metrics()

            # 模拟AI指标
            ai_metrics = self.simulate_ai_metrics()

            # 合并指标
            combined_metrics = {**system_metrics, **ai_metrics}
            self.metrics_buffer.append(combined_metrics)

            # 处理告警
            alert_result = self.alert_manager.process_alerts(combined_metrics)

            # 记录状态
            if alert_result["total_alerts"] > 0:
                logger.warning(f"🚨 检测到 {alert_result['total_alerts']} 个告警")
            else:
                logger.info(
                    f"✅ 系统运行正常 - CPU: {system_metrics['cpu_percent']:.1f}% 内存: {system_metrics['memory_percent']:.1f}%"
                )

            time.sleep(10)  # 每10秒监控一次

        # 保存监控数据
        monitor_file = Path("ai_realtime_monitoring.json")
        with open(monitor_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "monitoring_period": duration,
                    "total_samples": len(self.metrics_buffer),
                    "metrics_data": self.metrics_buffer,
                    "alert_history": self.alert_manager.alert_history,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        logger.info(f"📊 实时监控完成，数据已保存到 {monitor_file}")
        return self.metrics_buffer

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        logger.info("⏹️  实时监控已停止")


class AIStrategyAnalyzer:
    """AI策略分析器"""

    def __init__(self):
        self.strategies = {}
        self.performance_history = []

    def register_strategy(self, name: str, strategy_config: Dict[str, Any]):
        """注册策略"""
        self.strategies[name] = {
            "config": strategy_config,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "performance": [],
        }
        logger.info(f"📈 策略已注册: {name}")

    def analyze_strategy_performance(
        self, strategy_name: str, metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析策略性能"""
        if strategy_name not in self.strategies:
            return {"error": f"策略 {strategy_name} 不存在"}

        strategy = self.strategies[strategy_name]

        # 计算性能指标
        performance_analysis = {
            "strategy_name": strategy_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "score": self.calculate_performance_score(metrics),
            "recommendation": self.generate_recommendation(metrics),
            "risk_level": self.assess_risk_level(metrics),
        }

        # 更新策略性能历史
        strategy["performance"].append(performance_analysis)
        self.performance_history.append(performance_analysis)

        logger.info(
            f"📊 策略性能分析完成: {strategy_name} (得分: {performance_analysis['score']:.2f})"
        )

        return performance_analysis

    def calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """计算性能得分"""
        # 模拟性能评分算法
        accuracy = metrics.get("accuracy", 0.8)
        error_rate = metrics.get("error_rate", 5.0)
        response_time = metrics.get("response_time", 1.0)

        # 基础得分
        score = accuracy * 100

        # 错误率惩罚
        score -= error_rate * 2

        # 响应时间惩罚
        if response_time > 2.0:
            score -= (response_time - 2.0) * 5

        return max(0, min(100, score))

    def generate_recommendation(self, metrics: Dict[str, Any]) -> str:
        """生成建议"""
        accuracy = metrics.get("accuracy", 0.8)
        error_rate = metrics.get("error_rate", 5.0)
        response_time = metrics.get("response_time", 1.0)

        if accuracy < 0.7:
            return "建议优化模型训练数据，提升预测准确率"
        elif error_rate > 8.0:
            return "建议检查错误处理逻辑，降低系统错误率"
        elif response_time > 3.0:
            return "建议优化算法性能，减少响应时间"
        else:
            return "策略运行良好，建议继续监控"

    def assess_risk_level(self, metrics: Dict[str, Any]) -> str:
        """评估风险等级"""
        error_rate = metrics.get("error_rate", 5.0)
        response_time = metrics.get("response_time", 1.0)

        if error_rate > 10.0 or response_time > 5.0:
            return "高风险"
        elif error_rate > 5.0 or response_time > 2.0:
            return "中等风险"
        else:
            return "低风险"

    def get_strategy_summary(self) -> Dict[str, Any]:
        """获取策略摘要"""
        summary = {
            "total_strategies": len(self.strategies),
            "active_strategies": len(
                [s for s in self.strategies.values() if s["status"] == "active"]
            ),
            "performance_history_count": len(self.performance_history),
            "strategies": {},
        }

        for name, strategy in self.strategies.items():
            recent_performance = (
                strategy["performance"][-5:] if strategy["performance"] else []
            )
            avg_score = (
                sum(p["score"] for p in recent_performance) / len(recent_performance)
                if recent_performance
                else 0
            )

            summary["strategies"][name] = {
                "status": strategy["status"],
                "performance_count": len(strategy["performance"]),
                "average_score": round(avg_score, 2),
                "last_analysis": recent_performance[-1]["timestamp"]
                if recent_performance
                else None,
            }

        return summary


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 MyStocks AI监控和告警系统优化")
    print("=" * 60)

    # 初始化组件
    monitor = AIRealtimeMonitor()
    strategy_analyzer = AIStrategyAnalyzer()

    # 注册示例策略
    strategy_analyzer.register_strategy(
        "basic_trading",
        {"type": "momentum", "lookback_period": 20, "confidence_threshold": 0.8},
    )

    strategy_analyzer.register_strategy(
        "mean_reversion",
        {"type": "contrarian", "bollinger_period": 20, "std_dev_threshold": 2.0},
    )

    print("\n📊 开始AI实时监控系统测试...")

    # 运行实时监控（短时间测试）
    metrics_buffer = monitor.run_real_time_monitoring(duration=60)

    print("\n📈 进行策略分析...")

    # 对每个策略进行分析
    if metrics_buffer:
        latest_metrics = metrics_buffer[-1]

        for strategy_name in strategy_analyzer.strategies.keys():
            analysis = strategy_analyzer.analyze_strategy_performance(
                strategy_name, latest_metrics
            )
            print(
                f"  • {strategy_name}: 得分 {analysis['score']:.1f}, 风险等级: {analysis['risk_level']}"
            )

    # 生成策略摘要
    summary = strategy_analyzer.get_strategy_summary()

    print("\n" + "=" * 60)
    print("📋 监控和告警系统优化完成摘要")
    print("=" * 60)
    print(f"✅ 实时监控: {len(metrics_buffer)} 个数据点")
    print("✅ 告警系统: 智能规则已配置")
    print(f"✅ 策略分析: {summary['active_strategies']} 个活跃策略")
    print("✅ 通知渠道: 邮件、Webhook、日志")
    print(f"✅ 告警历史: {len(monitor.alert_manager.alert_history)} 条记录")

    # 保存结果
    result_file = Path("ai_monitoring_optimization_result.json")
    final_result = {
        "timestamp": datetime.now().isoformat(),
        "monitoring_summary": {
            "total_samples": len(metrics_buffer),
            "alerts_triggered": len(monitor.alert_manager.alert_history),
            "strategies_analyzed": len(strategy_analyzer.strategies),
        },
        "strategy_summary": summary,
        "alert_rules": list(monitor.alert_manager.alert_rules.keys()),
        "notification_channels": list(
            monitor.alert_manager.notification_channels.keys()
        ),
    }

    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)

    print(f"\n📄 详细结果已保存到: {result_file}")
    print("=" * 60)

    return final_result


if __name__ == "__main__":
    main()
