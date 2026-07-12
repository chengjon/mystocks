#!/usr/bin/env python3
"""MyStocks CI/CD监控集成工具
将监控数据集成到CI/CD流程中，实现自动化质量验证
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict

import requests


# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class CICDMonitor:
    """CI/CD监控集成器"""

    def __init__(self):
        self.prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
        self.grafana_url = os.getenv("GRAFANA_URL", "http://localhost:3000")
        self.alert_webhook_url = os.getenv("ALERT_WEBHOOK_URL")

    def query_prometheus(self, query: str, hours: int = 24) -> Dict[str, Any]:
        """查询Prometheus指标"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        params = {
            "query": query,
            "start": start_time.timestamp(),
            "end": end_time.timestamp(),
            "step": "3600",  # 1小时步长
        }

        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/query_range", params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Prometheus查询失败: {e}")
            return {"data": {"result": []}}

    def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统关键指标"""
        print("📊 收集系统性能指标...")

        metrics = {}

        # API响应时间
        api_response_query = "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
        metrics["api_response_time"] = self.query_prometheus(api_response_query)

        # 错误率
        error_rate_query = 'rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100'
        metrics["error_rate"] = self.query_prometheus(error_rate_query)

        # 系统资源使用率
        cpu_query = "system_cpu_usage_percent"
        memory_query = "system_memory_usage_percent"
        disk_query = "system_disk_usage_percent"

        metrics["cpu_usage"] = self.query_prometheus(cpu_query)
        metrics["memory_usage"] = self.query_prometheus(memory_query)
        metrics["disk_usage"] = self.query_prometheus(disk_query)

        # 用户体验指标
        ux_query = "user_experience_health_score"
        metrics["ux_health"] = self.query_prometheus(ux_query)

        return metrics

    def analyze_performance_score(self, metrics: Dict[str, Any]) -> float:
        """分析性能评分"""
        score = 100.0

        # API响应时间评分 (目标: <2秒 95th percentile)
        if metrics.get("api_response_time", {}).get("data", {}).get("result"):
            response_times = []
            for result in metrics["api_response_time"]["data"]["result"]:
                if result.get("values"):
                    response_times.extend([float(v[1]) for v in result["values"]])

            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                if avg_response_time > 2.0:
                    score -= (avg_response_time - 2.0) * 20  # 每超0.1秒减2分
                print(f"📈 平均API响应时间: {avg_response_time:.2f}秒")
            else:
                print("⚠️ 无API响应时间数据")

        # CPU使用率评分 (目标: <80%)
        if metrics.get("cpu_usage", {}).get("data", {}).get("result"):
            cpu_values = []
            for result in metrics["cpu_usage"]["data"]["result"]:
                if result.get("values"):
                    cpu_values.extend([float(v[1]) for v in result["values"]])

            if cpu_values:
                avg_cpu = sum(cpu_values) / len(cpu_values)
                if avg_cpu > 80:
                    score -= (avg_cpu - 80) * 0.5  # 每超1%减0.5分
                print(f"🖥️ 平均CPU使用率: {avg_cpu:.1f}%")
            else:
                print("⚠️ 无CPU使用率数据")

        # 内存使用率评分 (目标: <85%)
        if metrics.get("memory_usage", {}).get("data", {}).get("result"):
            mem_values = []
            for result in metrics["memory_usage"]["data"]["result"]:
                if result.get("values"):
                    mem_values.extend([float(v[1]) for v in result["values"]])

            if mem_values:
                avg_mem = sum(mem_values) / len(mem_values)
                if avg_mem > 85:
                    score -= (avg_mem - 85) * 0.5  # 每超1%减0.5分
                print(f"💾 平均内存使用率: {avg_mem:.1f}%")
            else:
                print("⚠️ 无内存使用率数据")

        return max(0.0, min(100.0, score))

    def analyze_security_score(self, metrics: Dict[str, Any]) -> float:
        """分析安全评分"""
        score = 100.0

        # 错误率评分 (目标: <5%)
        if metrics.get("error_rate", {}).get("data", {}).get("result"):
            error_rates = []
            for result in metrics["error_rate"]["data"]["result"]:
                if result.get("values"):
                    error_rates.extend([float(v[1]) for v in result["values"]])

            if error_rates:
                avg_error_rate = sum(error_rates) / len(error_rates)
                if avg_error_rate > 5.0:
                    score -= (avg_error_rate - 5.0) * 5  # 每超1%减5分
                elif avg_error_rate > 1.0:
                    score -= (avg_error_rate - 1.0) * 2  # 1-5%之间每超1%减2分
                print(f"🚨 平均错误率: {avg_error_rate:.2f}%")
            else:
                print("⚠️ 无错误率数据")

        return max(0.0, min(100.0, score))

    def check_quality_gates(self, performance_score: float, security_score: float) -> Dict[str, Any]:
        """检查质量门禁"""
        results = {
            "passed": True,
            "performance": {
                "score": performance_score,
                "threshold": 70.0,
                "passed": performance_score >= 70.0,
            },
            "security": {
                "score": security_score,
                "threshold": 80.0,
                "passed": security_score >= 80.0,
            },
            "issues": [],
        }

        if not results["performance"]["passed"]:
            results["passed"] = False
            results["issues"].append(
                {
                    "type": "performance",
                    "message": f"性能评分过低: {performance_score:.1f}/100 (需要 >=70)",
                    "severity": "high",
                }
            )

        if not results["security"]["passed"]:
            results["passed"] = False
            results["issues"].append(
                {
                    "type": "security",
                    "message": f"安全评分过低: {security_score:.1f}/100 (需要 >=80)",
                    "severity": "critical",
                }
            )

        return results

    def generate_report(self, metrics: Dict[str, Any], quality_gates: Dict[str, Any]) -> str:
        """生成质量报告"""
        report = []
        report.append("# MyStocks CI/CD 质量报告")
        report.append("")
        report.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # 整体状态
        if quality_gates["passed"]:
            report.append("## ✅ 质量门禁通过")
            report.append("")
            report.append("所有质量检查均已通过，系统运行正常。")
        else:
            report.append("## ❌ 质量门禁失败")
            report.append("")
            report.append("发现以下问题需要立即处理：")
            for issue in quality_gates["issues"]:
                severity_icon = "🔴" if issue["severity"] == "critical" else "🟡"
                report.append(f"- {severity_icon} {issue['message']}")
        report.append("")

        # 详细评分
        report.append("## 📊 详细评分")
        report.append("")
        report.append("### 性能评分")
        perf = quality_gates["performance"]
        status = "✅ 通过" if perf["passed"] else "❌ 未通过"
        report.append(f"- 分数: {perf['score']:.1f}/100")
        report.append(f"- 阈值: ≥{perf['threshold']}")
        report.append(f"- 状态: {status}")
        report.append("")

        report.append("### 安全评分")
        sec = quality_gates["security"]
        status = "✅ 通过" if sec["passed"] else "❌ 未通过"
        report.append(f"- 分数: {sec['score']:.1f}/100")
        report.append(f"- 阈值: ≥{sec['threshold']}")
        report.append(f"- 状态: {status}")
        report.append("")

        # 改进建议
        report.append("## 💡 改进建议")
        report.append("")

        if not quality_gates["performance"]["passed"]:
            report.append("### 性能优化建议")
            report.append("- 优化数据库查询，添加适当的索引")
            report.append("- 实现API响应缓存机制")
            report.append("- 检查并优化系统资源配置")
            report.append("- 考虑使用连接池和异步处理")
            report.append("")

        if not quality_gates["security"]["passed"]:
            report.append("### 安全改进建议")
            report.append("- 改进错误处理逻辑，减少5xx错误")
            report.append("- 添加请求频率限制和DDoS防护")
            report.append("- 加强输入验证和数据清理")
            report.append("- 定期进行安全审计和渗透测试")
            report.append("")

        # 监控建议
        report.append("### 持续监控建议")
        report.append("- 定期监控关键性能指标变化趋势")
        report.append("- 设置自动化告警阈值")
        report.append("- 建立性能基线和回归测试")
        report.append("- 关注用户体验指标和业务健康度")

        return "\n".join(report)

    def send_alert(self, quality_gates: Dict[str, Any], report: str):
        """发送告警通知"""
        if quality_gates["passed"]:
            print("✅ 质量检查通过，无需发送告警")
            return

        alert_message = "🚨 MyStocks 质量门禁告警\n\n"
        alert_message += "❌ 发现质量问题需要立即处理：\n"

        for issue in quality_gates["issues"]:
            severity_icon = "🔴" if issue["severity"] == "critical" else "🟡"
            alert_message += f"{severity_icon} {issue['message']}\n"

        alert_message += f"\n📊 性能评分: {quality_gates['performance']['score']:.1f}/100\n"
        alert_message += f"🔒 安全评分: {quality_gates['security']['score']:.1f}/100\n\n"
        alert_message += "请立即检查系统状态并采取 corrective action。"

        # 发送Webhook通知
        if self.alert_webhook_url:
            try:
                payload = {
                    "text": alert_message,
                    "timestamp": datetime.now().isoformat(),
                }
                response = requests.post(self.alert_webhook_url, json=payload, timeout=10)
                if response.status_code == 200:
                    print("✅ 告警通知发送成功")
                else:
                    print(f"⚠️ 告警通知发送失败: {response.status_code}")
            except Exception as e:
                print(f"⚠️ 发送告警通知时出错: {e}")
        else:
            print("⚠️ 未配置告警Webhook URL")

    def run_validation(self) -> int:
        """运行完整的质量验证"""
        print("🚀 开始MyStocks CI/CD质量验证...")

        try:
            # 1. 收集监控数据
            metrics = self.collect_system_metrics()

            # 2. 分析评分
            performance_score = self.analyze_performance_score(metrics)
            security_score = self.analyze_security_score(metrics)

            print("\n🎯 质量评分:")
            print(f"   性能评分: {performance_score:.1f}/100")
            print(f"   安全评分: {security_score:.1f}/100")
            # 3. 检查质量门禁
            quality_gates = self.check_quality_gates(performance_score, security_score)

            # 4. 生成报告
            report = self.generate_report(metrics, quality_gates)

            # 保存报告
            with open("cicd_quality_report.md", "w", encoding="utf-8") as f:
                f.write(report)

            print("\n📄 详细报告已保存到: cicd_quality_report.md")

            # 5. 发送告警（如果需要）
            if not quality_gates["passed"]:
                self.send_alert(quality_gates, report)

            # 6. 返回退出码
            return 0 if quality_gates["passed"] else 1

        except Exception as e:
            print(f"❌ 质量验证过程中出错: {e}")
            return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MyStocks CI/CD监控集成工具")
    parser.add_argument("--prometheus-url", help="Prometheus服务器URL")
    parser.add_argument("--grafana-url", help="Grafana服务器URL")
    parser.add_argument("--alert-webhook", help="告警Webhook URL")
    parser.add_argument("--output", default="cicd_quality_report.md", help="报告输出文件")

    args = parser.parse_args()

    # 设置环境变量
    if args.prometheus_url:
        os.environ["PROMETHEUS_URL"] = args.prometheus_url
    if args.grafana_url:
        os.environ["GRAFANA_URL"] = args.grafana_url
    if args.alert_webhook:
        os.environ["ALERT_WEBHOOK_URL"] = args.alert_webhook

    # 运行验证
    monitor = CICDMonitor()
    exit_code = monitor.run_validation()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
