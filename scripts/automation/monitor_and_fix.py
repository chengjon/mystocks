#!/usr/bin/env python3
"""
MyStocks 自动化监控和故障恢复脚本
实现服务健康检查、系统资源监控、自动故障恢复和告警通知系统

版本: 1.0
作者: MyStocks开发团队
创建日期: 2026-01-27
"""

import os
import sys
import time
import json
import logging
import subprocess
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("/tmp/monitoring.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ServiceHealthChecker:
    """服务健康检查器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.services_status = {}
        self.error_counts = {}
        self.last_restart_time = {}
        self.cooldown_period = config.get("alert_cooldown", 300)  # 5分钟冷却期

    def check_service_health(self, service_name: str, health_config: Dict[str, Any]) -> bool:
        """检查单个服务健康状态"""
        try:
            url = health_config["url"]
            timeout = health_config.get("timeout", 5000)
            expected_status = health_config.get("expected_status", 200)

            logger.info(f"检查 {service_name} 健康状态: {url}")

            response = requests.get(url, timeout=timeout / 1000)
            is_healthy = response.status_code == expected_status

            if is_healthy:
                logger.info(f"{service_name} 健康: {response.status_code}")
                # 重置错误计数
                if service_name in self.error_counts:
                    self.error_counts[service_name] = 0
            else:
                logger.warning(f"{service_name} 不健康: {response.status_code}")
                self.error_counts[service_name] = self.error_counts.get(service_name, 0) + 1

            return is_healthy

        except requests.RequestException as e:
            logger.error(f"{service_name} 健康检查失败: {e}")
            self.error_counts[service_name] = self.error_counts.get(service_name, 0) + 1
            return False
        except Exception as e:
            logger.error(f"{service_name} 健康检查异常: {e}")
            return False

    def check_database_connection(self, db_config: Dict[str, Any]) -> bool:
        """检查数据库连接"""
        try:
            query = db_config.get("query", "SELECT 1")
            timeout = db_config.get("timeout", 5000)

            # 这里应该根据实际数据库类型进行连接检查
            # 暂时返回True，实际应该执行数据库连接测试
            logger.info(f"检查数据库连接: {query}")
            return True

        except Exception as e:
            logger.error(f"数据库连接检查失败: {e}")
            return False

    def should_restart_service(self, service_name: str) -> bool:
        """判断是否应该重启服务"""
        error_count = self.error_counts.get(service_name, 0)
        failure_threshold = self.config.get("failure_threshold", 3)

        # 检查是否在冷却期
        if service_name in self.last_restart_time:
            time_since_restart = time.time() - self.last_restart_time[service_name]
            if time_since_restart < self.cooldown_period:
                logger.info(f"{service_name} 在冷却期内，跳过重启")
                return False

        return error_count >= failure_threshold

    def restart_service(self, service_name: str) -> bool:
        """重启服务"""
        try:
            logger.info(f"重启服务: {service_name}")

            # 使用PM2重启服务
            result = subprocess.run(["pm2", "restart", service_name], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.info(f"{service_name} 重启成功")
                self.last_restart_time[service_name] = time.time()
                self.error_counts[service_name] = 0  # 重置错误计数
                return True
            else:
                logger.error(f"{service_name} 重启失败: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"重启服务 {service_name} 时发生异常: {e}")
            return False


class SystemResourceMonitor:
    """系统资源监控器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_thresholds = {
            "cpu": config.get("cpu_threshold", 80),
            "memory": config.get("memory_threshold", 85),
            "disk": config.get("disk_threshold", 90),
        }

    def get_system_stats(self) -> Dict[str, float]:
        """获取系统资源使用率"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)

            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 磁盘使用率
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent

            return {"cpu": cpu_percent, "memory": memory_percent, "disk": disk_percent, "timestamp": time.time()}

        except Exception as e:
            logger.error(f"获取系统资源状态失败: {e}")
            return {}

    def check_resource_alerts(self, stats: Dict[str, float]) -> List[str]:
        """检查资源告警"""
        alerts = []

        for resource, threshold in self.alert_thresholds.items():
            current_value = stats.get(resource, 0)
            if current_value > threshold:
                alerts.append(f"{resource.upper()}使用率 {current_value:.1f}% 超过阈值 {threshold}%")
                logger.warning(f"资源告警: {resource.upper()}使用率 {current_value:.1f}% > {threshold}%")

        return alerts

    def get_process_stats(self, service_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """获取进程资源使用统计"""
        process_stats = {}

        for service_name in service_names:
            try:
                # 使用PM2获取进程信息
                result = subprocess.run(
                    ["pm2", "show", service_name, "--monit"], capture_output=True, text=True, timeout=10
                )

                if result.returncode == 0:
                    # 解析PM2输出获取进程信息
                    lines = result.stdout.strip().split("\n")
                    for line in lines:
                        if "memory usage" in line.lower():
                            # 提取内存使用信息
                            memory_usage = line.split("memory usage")[-1].strip()
                        elif "cpu usage" in line.lower():
                            # 提取CPU使用信息
                            cpu_usage = line.split("cpu usage")[-1].strip()

                    process_stats[service_name] = {
                        "status": "running",
                        "memory_usage": memory_usage if "memory_usage" in locals() else "N/A",
                        "cpu_usage": cpu_usage if "cpu_usage" in locals() else "N/A",
                    }
                else:
                    process_stats[service_name] = {
                        "status": "unknown",
                        "error": result.stderr.strip() if result.stderr else "PM2命令失败",
                    }

            except Exception as e:
                logger.error(f"获取 {service_name} 进程信息失败: {e}")
                process_stats[service_name] = {"status": "error", "error": str(e)}

        return process_stats


class AlertManager:
    """告警管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.last_alert_time = {}
        self.webhook_url = config.get("webhook_url", "")

    def send_alert(self, alert_type: str, message: str, level: str = "warning") -> bool:
        """发送告警通知"""
        try:
            # 检查冷却期
            current_time = time.time()
            alert_key = f"{alert_type}_{message}"

            if alert_key in self.last_alert_time:
                time_since_last = current_time - self.last_alert_time[alert_key]
                cooldown_period = self.config.get("alert_cooldown", 300)  # 5分钟

                if time_since_last < cooldown_period:
                    logger.info(f"告警在冷却期内，跳过发送: {message}")
                    return False

            # 记录告警时间
            self.last_alert_time[alert_key] = current_time

            # 构建告警消息
            alert_data = {
                "timestamp": datetime.now().isoformat(),
                "type": alert_type,
                "level": level,
                "message": message,
                "service": "MyStocks监控系统",
            }

            # 记录到日志文件
            logger.warning(f"告警: [{level}] {message}")

            # 发送Webhook通知（如果配置了）
            if self.webhook_url:
                try:
                    response = requests.post(
                        self.webhook_url, json=alert_data, timeout=10, headers={"Content-Type": "application/json"}
                    )
                    if response.status_code == 200:
                        logger.info(f"Webhook告警发送成功: {message}")
                        return True
                    else:
                        logger.error(f"Webhook告警发送失败: {response.status_code}")
                        return False
                except Exception as e:
                    logger.error(f"发送Webhook告警异常: {e}")
                    return False
            else:
                logger.info(f"告警记录（无Webhook）: {message}")
                return True

        except Exception as e:
            logger.error(f"发送告警异常: {e}")
            return False


class MonitoringSystem:
    """主监控系统"""

    def __init__(self, config_path: str = "/opt/claude/mystocks_spec/scripts/automation/monitor_config.json"):
        self.config = self.load_config(config_path)
        self.health_checker = ServiceHealthChecker(self.config)
        self.resource_monitor = SystemResourceMonitor(self.config)
        self.alert_manager = AlertManager(self.config)
        self.running = False

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载监控配置"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件不存在，使用默认配置: {config_path}")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "check_interval": 60,  # 检查间隔60秒
            "alert_cooldown": 300,  # 告警冷却期5分钟
            "max_restart_attempts": 3,  # 最大重启尝试次数
            "webhook_url": os.getenv("ALERT_WEBHOOK_URL", ""),
            "services": {
                "mystocks-frontend": {"url": "http://localhost:3002", "timeout": 5000, "expected_status": 200},
                "mystocks-backend": {
                    "url": "http://localhost:8000/api/health",
                    "timeout": 3000,
                    "expected_status": 200,
                    "database_check": {"enabled": True, "query": "SELECT 1", "timeout": 5000},
                },
            },
            "thresholds": {"cpu": 80, "memory": 85, "disk": 90},
            "log_level": "info",
        }

    def save_config(self, config_path: str):
        """保存配置"""
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("配置已保存")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")

    def check_all_services(self) -> Dict[str, Any]:
        """检查所有服务健康状态"""
        results = {}
        services_config = self.config.get("services", {})

        for service_name, health_config in services_config.items():
            is_healthy = self.health_checker.check_service_health(service_name, health_config)
            results[service_name] = {"healthy": is_healthy, "timestamp": time.time()}

            # 检查是否需要重启
            if not is_healthy and self.health_checker.should_restart_service(service_name):
                logger.info(f"准备重启 {service_name}")
                restart_success = self.health_checker.restart_service(service_name)
                results[service_name]["restarted"] = restart_success

        return results

    def check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源"""
        stats = self.resource_monitor.get_system_stats()
        alerts = self.resource_monitor.check_resource_alerts(stats)

        return {"stats": stats, "alerts": alerts, "timestamp": time.time()}

    def get_service_processes(self) -> List[str]:
        """获取需要监控的服务列表"""
        return list(self.config.get("services", {}).keys())

    def run_once(self) -> Dict[str, Any]:
        """执行一次完整的监控检查"""
        logger.info("开始执行监控检查...")

        # 检查服务健康状态
        service_results = self.check_all_services()

        # 检查系统资源
        resource_results = self.check_system_resources()

        # 检查进程状态
        service_names = self.get_service_processes()
        process_results = self.resource_monitor.get_process_stats(service_names)

        # 发送资源告警
        for alert in resource_results.get("alerts", []):
            self.alert_manager.send_alert("resource", alert, "warning")

        # 综合结果
        monitoring_result = {
            "timestamp": time.time(),
            "services": service_results,
            "resources": resource_results,
            "processes": process_results,
        }

        logger.info("监控检查完成")
        return monitoring_result

    def start_monitoring(self):
        """启动持续监控"""
        logger.info("启动自动化监控系统...")
        self.running = True

        check_interval = self.config.get("check_interval", 60)

        try:
            while self.running:
                start_time = time.time()

                # 执行监控检查
                result = self.run_once()

                # 保存监控结果
                self.save_monitoring_result(result)

                # 计算下次检查时间
                elapsed = time.time() - start_time
                sleep_time = max(0, check_interval - elapsed)

                logger.info(f"下次检查时间: {sleep_time}秒后")
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("监控停止")
            self.running = False
        except Exception as e:
            logger.error(f"监控异常: {e}")
            self.running = False

    def stop_monitoring(self):
        """停止监控"""
        logger.info("停止监控...")
        self.running = False

    def save_monitoring_result(self, result: Dict[str, Any]):
        """保存监控结果"""
        try:
            # 确保目录存在
            os.makedirs("/tmp/monitoring_results", exist_ok=True)

            # 保存到JSON文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/monitoring_results/monitoring_{timestamp}.json"

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"监控结果已保存: {filename}")

        except Exception as e:
            logger.error(f"保存监控结果失败: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="MyStocks 自动化监控和故障恢复系统")
    parser.add_argument(
        "--config",
        "-c",
        default="/opt/claude/mystocks_spec/scripts/automation/monitor_config.json",
        help="监控配置文件路径",
    )
    parser.add_argument("--daemon", "-d", action="store_true", help="以守护进程模式运行")
    parser.add_argument("--check-once", action="store_true", help="只执行一次检查")
    parser.add_argument("--services", nargs="+", help="指定要监控的服务名称")

    args = parser.parse_args()

    # 创建监控系统
    monitoring = MonitoringSystem(args.config)

    if args.check_once:
        # 只执行一次检查
        result = monitoring.run_once()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # 启动持续监控
        if args.daemon:
            # TODO: 实现真正的守护进程（使用double fork）
            logger.info("守护进程模式暂未实现，使用前台模式")

        if args.services:
            # 过滤服务
            services_config = monitoring.config.get("services", {})
            filtered_services = {k: v for k, v in services_config.items() if k in args.services}
            monitoring.config["services"] = filtered_services
            logger.info(f"监控指定服务: {args.services}")

        signal.signal(signal.SIGTERM, lambda sign, frame: monitoring.stop_monitoring())
        signal.signal(signal.SIGINT, lambda sign, frame: monitoring.stop_monitoring())

        monitoring.start_monitoring()


if __name__ == "__main__":
    main()
