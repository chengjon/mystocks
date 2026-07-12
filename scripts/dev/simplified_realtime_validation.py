#!/usr/bin/env python3
"""简化版实时数据流验证工具
Simplified Real-Time Streaming Validation Tool

Phase 7-1: 实时数据流完整性验证 (简化版)

功能特性:
- HTTP API可用性验证
- WebSocket连接基本测试
- 数据源完整性检查
- 实时数据获取测试
- 基础流媒体功能验证

Author: Claude Code
Date: 2025-11-13
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, List

import requests
import websockets


class SimplifiedRealtimeValidator:
    """简化版实时数据流验证器"""

    def __init__(self):
        self.backend_port = int(os.getenv("BACKEND_PORT", "8020"))
        self.base_url = os.getenv("BACKEND_URL", f"http://localhost:{self.backend_port}")
        self.ws_base_url = os.getenv("BACKEND_WS_URL", f"ws://localhost:{self.backend_port}")
        self.test_symbols = ["600519", "000001", "600036"]
        self.results = []

    def validate_all(self) -> Dict[str, any]:
        """执行所有验证测试"""
        print("🔧 开始简化版实时数据流完整性验证")
        print("=" * 60)

        # 1. HTTP API健康检查
        print("\n1️⃣ HTTP API健康检查")
        http_result = self._test_http_health()
        self._print_result(http_result)
        self.results.append(http_result)

        # 2. 实时数据获取测试
        if http_result.get("success"):
            print("\n2️⃣ 实时数据获取测试")
            data_result = self._test_realtime_data()
            self._print_result(data_result)
            self.results.append(data_result)
        else:
            print("\n2️⃣ 跳过实时数据测试 (API不可用)")
            self.results.append(
                {"test": "Realtime Data", "success": False, "error": "API unavailable"},
            )

        # 3. 数据源完整性检查
        print("\n3️⃣ 数据源完整性检查")
        source_result = self._test_data_sources()
        self._print_result(source_result)
        self.results.append(source_result)

        # 4. WebSocket基础连接测试
        print("\n4️⃣ WebSocket基础连接测试")
        ws_result = self._test_basic_websocket()
        self._print_result(ws_result)
        self.results.append(ws_result)

        # 生成摘要
        return self._generate_summary()

    def _test_http_health(self) -> Dict[str, any]:
        """测试HTTP API健康状态"""
        start_time = time.time()

        try:
            # 测试健康检查端点
            health_url = f"{self.base_url}/api/market/health"
            response = requests.get(health_url, timeout=(5, 10))

            if response.status_code == 200:
                data = response.json()
                return {
                    "test": "HTTP API Health",
                    "success": True,
                    "duration": time.time() - start_time,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "status": data.get("status", "unknown"),
                    "service": data.get("service", "unknown"),
                }
            return {
                "test": "HTTP API Health",
                "success": False,
                "duration": time.time() - start_time,
                "error": f"HTTP {response.status_code}",
            }

        except Exception as e:
            return {
                "test": "HTTP API Health",
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
            }

    def _test_realtime_data(self) -> Dict[str, any]:
        """测试实时数据获取"""
        start_time = time.time()

        try:
            # 测试实时行情端点
            quotes_url = f"{self.base_url}/api/market/quotes"
            response = requests.get(quotes_url, timeout=(5, 10))

            if response.status_code == 200:
                data = response.json()

                # 验证响应格式
                if "data" in data and "total" in data:
                    total_count = data["total"]
                    success = total_count > 0

                    return {
                        "test": "Realtime Data",
                        "success": success,
                        "duration": time.time() - start_time,
                        "data_points": total_count,
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                        "timestamp": data.get("timestamp", ""),
                    }
                return {
                    "test": "Realtime Data",
                    "success": False,
                    "duration": time.time() - start_time,
                    "error": "Invalid response format",
                }
            return {
                "test": "Realtime Data",
                "success": False,
                "duration": time.time() - start_time,
                "error": f"HTTP {response.status_code}",
            }

        except Exception as e:
            return {
                "test": "Realtime Data",
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
            }

    def _test_data_sources(self) -> Dict[str, any]:
        """测试数据源完整性"""
        start_time = time.time()
        sources_tested = 0
        sources_working = 0

        # 测试股票列表API
        try:
            stocks_url = f"{self.base_url}/api/market/stocks"
            response = requests.get(stocks_url, timeout=(5, 10))
            sources_tested += 1

            if response.status_code == 200:
                sources_working += 1
        except:
            pass

        # 测试K线数据API
        try:
            kline_url = f"{self.base_url}/api/market/kline"
            params = {
                "stock_code": "600519",
                "period": "daily",
                "start_date": "2024-11-01",
                "end_date": "2024-11-13",
            }
            response = requests.get(kline_url, params=params, timeout=(5, 10))
            sources_tested += 1

            if response.status_code == 200:
                sources_working += 1
        except:
            pass

        # 测试热力图API
        try:
            heatmap_url = f"{self.base_url}/api/market/heatmap"
            response = requests.get(heatmap_url, timeout=(5, 10))
            sources_tested += 1

            if response.status_code == 200:
                sources_working += 1
        except:
            pass

        success_rate = (sources_working / sources_tested * 100) if sources_tested > 0 else 0

        return {
            "test": "Data Sources",
            "success": success_rate >= 50,  # 至少50%的数据源可用
            "duration": time.time() - start_time,
            "sources_tested": sources_tested,
            "sources_working": sources_working,
            "success_rate": success_rate,
        }

    def _test_basic_websocket(self) -> Dict[str, any]:
        """测试WebSocket基础连接"""
        start_time = time.time()

        # 测试基本的WebSocket连接能力
        ws_endpoints = ["/api/v1/ws/realtime", "/ws", "/api/websocket"]

        connections_tested = 0
        connections_working = 0

        async def test_single_endpoint(endpoint):
            nonlocal connections_tested, connections_working
            connections_tested += 1

            try:
                ws_url = f"{self.ws_base_url}{endpoint}"
                async with websockets.connect(ws_url) as websocket:
                    connections_working += 1
                    return True
            except:
                return False

        # 运行WebSocket测试
        try:

            async def run_ws_tests():
                tasks = [test_single_endpoint(endpoint) for endpoint in ws_endpoints]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return results

            asyncio.run(run_ws_tests())

            success_rate = (connections_working / connections_tested * 100) if connections_tested > 0 else 0

            return {
                "test": "WebSocket Connection",
                "success": success_rate > 0,  # 至少有一个端点可以连接
                "duration": time.time() - start_time,
                "endpoints_tested": connections_tested,
                "endpoints_working": connections_working,
                "success_rate": success_rate,
                "note": "WebSocket测试显示连接状态，需要适当的认证配置",
            }

        except Exception as e:
            return {
                "test": "WebSocket Connection",
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
            }

    def _print_result(self, result: Dict[str, any]):
        """打印结果"""
        status_icon = "✅" if result.get("success", False) else "❌"
        test_name = result.get("test", "Unknown")
        duration = result.get("duration", 0)

        print(f"   {status_icon} {test_name}: {duration:.2f}s")

        if result.get("success"):
            if "response_time_ms" in result:
                print(f"      📊 响应时间: {result['response_time_ms']:.1f}ms")
            if "data_points" in result:
                print(f"      📊 数据点: {result['data_points']}")
            if "success_rate" in result:
                print(f"      📊 成功率: {result['success_rate']:.1f}%")
            if "sources_working" in result:
                print(
                    f"      📊 可用数据源: {result['sources_working']}/{result['sources_tested']}",
                )
        else:
            error = result.get("error", "Unknown error")
            print(f"      ❌ 错误: {error}")

    def _generate_summary(self) -> Dict[str, any]:
        """生成摘要报告"""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.get("success", False))
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        total_duration = sum(r.get("duration", 0) for r in self.results)

        # 性能指标
        avg_response_time = 0
        data_sources_working = 0

        for result in self.results:
            if "response_time_ms" in result:
                avg_response_time = max(avg_response_time, result["response_time_ms"])
            if "sources_working" in result:
                data_sources_working = max(
                    data_sources_working,
                    result["sources_working"],
                )

        summary = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": success_rate,
                "total_duration": total_duration,
            },
            "performance_metrics": {
                "average_response_time_ms": avg_response_time,
                "working_data_sources": data_sources_working,
            },
            "detailed_results": self.results,
            "recommendations": self._generate_recommendations(),
        }

        # 打印摘要
        print("\n" + "=" * 60)
        print("📊 实时数据流完整性验证报告 (简化版)")
        print("=" * 60)
        print(f"✅ 成功测试: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"⏱️  总用时: {total_duration:.2f}秒")

        if avg_response_time > 0:
            print(f"📈 平均响应时间: {avg_response_time:.1f}ms")

        if data_sources_working > 0:
            print(f"📊 可用数据源: {data_sources_working}")

        # 保存详细报告
        report_file = f"/opt/claude/mystocks_spec/var/log/simplified_realtime_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n💾 详细报告已保存: {report_file}")

        return summary

    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if not any(r.get("success") for r in self.results):
            recommendations.append("Web服务可能未完全启动，检查端口8888是否可用")
            recommendations.append("验证API路由配置是否正确")

        if not any("WebSocket" in r.get("test", "") and r.get("success") for r in self.results):
            recommendations.append("WebSocket连接需要适当的认证配置")
            recommendations.append("检查WebSocket端点路径是否正确")

        if not any("Realtime Data" in r.get("test", "") and r.get("success") for r in self.results):
            recommendations.append("实时数据API可能需要数据源配置")
            recommendations.append("验证数据库连接和缓存配置")

        if not recommendations:
            recommendations.append("实时数据流系统基本可用，建议进行性能优化")
            recommendations.append("考虑添加更多监控和告警机制")

        return recommendations


def main():
    """主函数"""
    print("🔧 简化版实时数据流完整性验证工具")
    print("Phase 7-1: 实时数据流完整性验证 (简化版)")
    print("=" * 60)

    # 创建验证器
    validator = SimplifiedRealtimeValidator()

    # 执行验证
    report = validator.validate_all()

    # 返回结果
    return report["summary"]["success_rate"]


if __name__ == "__main__":
    success_rate = main()
    print(f"\n🎯 验证完成，整体成功率: {success_rate:.1f}%")
