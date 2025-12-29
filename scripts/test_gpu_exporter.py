#!/usr/bin/env python3
"""
GPU监控 - Prometheus Exporter测试脚本
Test script for GPU Metrics Prometheus Exporter
"""

import sys
import os
import time
import requests
import signal

sys.path.insert(0, os.path.abspath("."))

from src.gpu_monitoring.prometheus_exporter import GPUMetricsExporter


class ExporterTester:
    """Exporter测试器"""

    def __init__(self, port=9100):
        self.port = port
        self.exporter = None
        self.running = False

    def test_metrics_collection(self):
        """测试指标采集"""
        print("🔍 测试GPU指标采集...")

        try:
            result = self.exporter.collect_metrics()
            if result:
                print("✅ GPU指标采集成功")
            else:
                print("❌ GPU指标采集失败")
                return False
        except Exception as e:
            print(f"❌ GPU指标采集异常: {e}")
            return False

        return True

    def test_metrics_endpoint(self):
        """测试/metrics端点"""
        print(f"\n🔍 测试Prometheus metrics端点 (http://localhost:{self.port}/metrics)...")

        try:
            response = requests.get(f"http://localhost:{self.port}/metrics", timeout=5)
            if response.status_code == 200:
                print(f"✅ Metrics端点响应成功 (状态码: {response.status_code})")

                # 统计GPU指标数量
                metrics_content = response.text
                gpu_metrics_count = metrics_content.count("gpu_")
                print(f"✅ 找到 {gpu_metrics_count} 个GPU相关指标")

                # 显示前20行
                lines = metrics_content.split("\n")[:20]
                print("\n前20行指标预览:")
                for line in lines:
                    if line.strip():
                        print(f"  {line}")

                return True
            else:
                print(f"❌ Metrics端点响应失败 (状态码: {response.status_code})")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Metrics端点请求失败: {e}")
            return False

    def test_prometheus_scrape(self):
        """测试Prometheus抓取"""
        print(f"\n🔍 测试Prometheus抓取...")

        # 检查Prometheus是否运行
        try:
            prometheus_response = requests.get("http://localhost:9090/-/healthy", timeout=5)
            print("✅ Prometheus正在运行")
        except requests.exceptions.RequestException:
            print("⚠️  Prometheus未运行或无法访问")
            print("   提示: 启动Prometheus后可验证抓取")
            return None

        # 查询GPU指标
        try:
            query_response = requests.get("http://localhost:9090/api/v1/query?query=gpu_utilization_percent", timeout=5)

            if query_response.status_code == 200:
                data = query_response.json()
                if data["status"] == "success":
                    print("✅ Prometheus成功抓取GPU指标")
                    print(f"   查询结果: {data['data']}")
                    return True
                else:
                    print(f"❌ Prometheus查询失败: {data}")
                    return False
            else:
                print(f"❌ Prometheus查询失败 (状态码: {query_response.status_code})")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Prometheus查询失败: {e}")
            return False

    def test_grafana_dashboard(self):
        """测试Grafana Dashboard"""
        print(f"\n🔍 测试Grafana Dashboard...")

        # 检查Grafana是否运行
        try:
            grafana_response = requests.get("http://localhost:3000/api/health", timeout=5)
            print("✅ Grafana正在运行")
        except requests.exceptions.RequestException:
            print("⚠️  Grafana未运行或无法访问")
            print("   提示: 启动Grafana后可验证Dashboard")
            return None

        # 检查Grafana数据源
        try:
            datasources_response = requests.get("http://localhost:3000/api/datasources", timeout=5)

            if datasources_response.status_code == 200:
                datasources = datasources_response.json()
                print(f"✅ 找到 {len(datasources)} 个Grafana数据源")

                for ds in datasources:
                    if ds.get("type") == "prometheus":
                        print(f"   - {ds.get('name')}: {ds.get('type')}")
                        if ds.get("isDefault"):
                            print("     (默认数据源)")
                return True
            else:
                print(f"❌ 获取Grafana数据源失败 (状态码: {datasources_response.status_code})")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取Grafana数据源失败: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("╔══════════════════════════════════════════════════════╗")
        print("║         GPU Metrics Prometheus Exporter 测试      ║")
        print("╚══════════════════════════════════════════════════════╝")
        print("")

        results = {
            "metrics_collection": None,
            "metrics_endpoint": False,
            "prometheus_scrape": None,
            "grafana_dashboard": None,
        }

        # 测试1: 指标采集
        if self.test_metrics_collection():
            results["metrics_collection"] = True

        # 等待Exporter启动
        print("\n⏳ 等待Exporter启动...")
        time.sleep(3)

        # 测试2: Metrics端点
        results["metrics_endpoint"] = self.test_metrics_endpoint()

        # 测试3: Prometheus抓取
        results["prometheus_scrape"] = self.test_prometheus_scrape()

        # 测试4: Grafana Dashboard
        results["grafana_dashboard"] = self.test_grafana_dashboard()

        # 显示测试结果
        print("\n╔══════════════════════════════════════════════════════╗")
        print("║                   测试结果                            ║")
        print("╚══════════════════════════════════════════════════════╝")
        print("")

        test_names = [
            ("GPU指标采集", "metrics_collection"),
            ("Metrics端点", "metrics_endpoint"),
            ("Prometheus抓取", "prometheus_scrape"),
            ("Grafana Dashboard", "grafana_dashboard"),
        ]

        for name, key in test_names:
            if results[key] is True:
                print(f"✅ {name}: 通过")
            elif results[key] is False:
                print(f"❌ {name}: 失败")
            else:
                print(f"⚠️  {name}: 未测试")

        # 统计
        passed = sum(1 for v in results.values() if v is True)
        failed = sum(1 for v in results.values() if v is False)
        skipped = sum(1 for v in results.values() if v is None)

        print("\n测试统计:")
        print(f"  通过: {passed}")
        print(f"  失败: {failed}")
        print(f"  未测试: {skipped}")

        if failed == 0:
            print("\n🎉 所有测试通过！")
            return 0
        else:
            print(f"\n❌ {failed} 个测试失败")
            return 1


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="GPU Metrics Exporter测试脚本")
    parser.add_argument("--port", type=int, default=9100, help="Exporter端口 (默认: 9100)")
    parser.add_argument("--no-exporter", action="store_true", help="不启动Exporter，仅测试已运行的服务")

    args = parser.parse_args()

    if not args.no_exporter:
        print("启动GPU Metrics Exporter...")
        print(f"端口: {args.port}")
        print("")

        exporter = GPUMetricsExporter()

        # 注册信号处理器
        def signal_handler(signum, frame):
            print(f"\n收到信号 {signum}，停止Exporter...")
            exporter.running = False
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 启动Exporter（后台）
        import asyncio

        async def start_and_test():
            # 启动Exporter
            from prometheus_client import start_http_server

            start_http_server(args.port)
            print(f"✅ Prometheus Exporter已启动 (http://localhost:{args.port}/metrics)")

            # 运行测试
            tester = ExporterTester(port=args.port)
            tester.exporter = exporter
            return tester.run_all_tests()

        try:
            exit_code = asyncio.run(start_and_test())
            sys.exit(exit_code)
        except KeyboardInterrupt:
            print("\n\n🛑 测试已取消")
            sys.exit(1)
    else:
        print("测试模式: 不启动Exporter")
        print(f"端口: {args.port}")
        print("")

        tester = ExporterTester(port=args.port)
        sys.exit(tester.run_all_tests())


if __name__ == "__main__":
    main()
