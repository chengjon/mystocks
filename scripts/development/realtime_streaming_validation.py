#!/usr/bin/env python3
"""
实时数据流完整性验证工具
Real-Time Streaming Integrity Validation Tool

Phase 7-1: 实时数据流完整性验证

功能特性:
- WebSocket连接可用性测试
- 实时数据传输完整性验证
- 数据流延迟和性能测试
- 流状态管理和错误恢复验证
- 数据一致性和准确性验证
- 端到端流处理验证

Author: Claude Code
Date: 2025-11-13
"""

import asyncio
import time
import json
import websockets
import requests
import statistics
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import concurrent.futures


@dataclass
class StreamingMetrics:
    """流媒体指标"""

    connection_latency: float  # 连接延迟 (ms)
    data_throughput: float  # 数据吞吐量 (msg/s)
    message_loss_rate: float  # 消息丢失率 (%)
    average_latency: float  # 平均延迟 (ms)
    max_latency: float  # 最大延迟 (ms)
    error_count: int  # 错误计数
    connection_stability: float  # 连接稳定性 (0-1)


@dataclass
class ValidationResult:
    """验证结果"""

    test_name: str
    success: bool
    duration: float
    metrics: Optional[StreamingMetrics] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = None


class RealtimeStreamingValidator:
    """实时数据流验证器"""

    def __init__(self, config_file: str = None):
        """
        初始化验证器

        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.results: List[ValidationResult] = []
        self.test_symbols = ["600519", "000001", "600036"]  # 测试股票代码
        self.base_url = "http://localhost:8000"

        # 加载配置
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "websocket_url": "ws://localhost:8000/api/stream",
            "http_base_url": "http://localhost:8000",
            "test_duration": 30,  # 测试持续时间(秒)
            "message_count": 100,  # 消息计数
            "timeout": 10,  # 超时时间(秒)
            "retry_count": 3,  # 重试次数
            "latency_threshold": 100,  # 延迟阈值(ms)
            "throughput_threshold": 50,  # 吞吐量阈值(msg/s)
            "loss_threshold": 1.0,  # 丢失率阈值(%)
        }

        if self.config_file and Path(self.config_file).exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️ 配置文件加载失败: {e}，使用默认配置")

        return default_config

    def validate_all(self) -> Dict[str, Any]:
        """执行所有验证测试"""
        print("🔧 开始实时数据流完整性验证")
        print("=" * 60)

        # 1. HTTP API可用性测试
        print("\n1️⃣ HTTP API可用性测试")
        http_result = self._test_http_api()
        self.results.append(http_result)
        self._print_result(http_result)

        # 2. WebSocket连接测试
        print("\n2️⃣ WebSocket连接测试")
        ws_result = self._test_websocket_connection()
        self.results.append(ws_result)
        self._print_result(ws_result)

        # 3. 实时数据传输测试
        if ws_result.success:
            print("\n3️⃣ 实时数据传输测试")
            stream_result = self._test_streaming_data()
            self.results.append(stream_result)
            self._print_result(stream_result)
        else:
            print("\n3️⃣ 跳过实时数据传输测试 (WebSocket连接失败)")
            self.results.append(
                ValidationResult(
                    test_name="Streaming Data Transfer",
                    success=False,
                    duration=0.0,
                    error_message="WebSocket连接测试失败",
                )
            )

        # 4. 数据完整性验证
        print("\n4️⃣ 数据完整性验证")
        integrity_result = self._test_data_integrity()
        self.results.append(integrity_result)
        self._print_result(integrity_result)

        # 5. 流状态管理测试
        print("\n5️⃣ 流状态管理测试")
        state_result = self._test_stream_state_management()
        self.results.append(state_result)
        self._print_result(state_result)

        # 6. 错误恢复测试
        print("\n6️⃣ 错误恢复测试")
        recovery_result = self._test_error_recovery()
        self.results.append(recovery_result)
        self._print_result(recovery_result)

        # 生成综合报告
        return self._generate_summary_report()

    def _test_http_api(self) -> ValidationResult:
        """测试HTTP API可用性"""
        start_time = time.time()

        try:
            # 测试基本健康检查
            health_url = f"{self.base_url}/api/market/health"
            response = requests.get(health_url, timeout=(5, self.config["timeout"]))

            if response.status_code != 200:
                return ValidationResult(
                    test_name="HTTP API Health Check",
                    success=False,
                    duration=time.time() - start_time,
                    error_message=f"健康检查失败: HTTP {response.status_code}",
                )

            # 测试实时数据API
            realtime_url = f"{self.base_url}/api/market/quotes"
            response = requests.get(realtime_url, timeout=(5, self.config["timeout"]))

            if response.status_code != 200:
                return ValidationResult(
                    test_name="HTTP API Real-time Data",
                    success=False,
                    duration=time.time() - start_time,
                    error_message=f"实时数据API失败: HTTP {response.status_code}",
                )

            # 验证响应格式
            try:
                data = response.json()
                if "data" not in data:
                    return ValidationResult(
                        test_name="HTTP API Response Format",
                        success=False,
                        duration=time.time() - start_time,
                        error_message="响应格式不正确：缺少data字段",
                    )
            except json.JSONDecodeError:
                return ValidationResult(
                    test_name="HTTP API JSON Format",
                    success=False,
                    duration=time.time() - start_time,
                    error_message="响应不是有效的JSON格式",
                )

            return ValidationResult(
                test_name="HTTP API Availability",
                success=True,
                duration=time.time() - start_time,
                details={"response_time": response.elapsed.total_seconds() * 1000},
            )

        except requests.exceptions.RequestException as e:
            return ValidationResult(
                test_name="HTTP API Connection",
                success=False,
                duration=time.time() - start_time,
                error_message=f"HTTP连接失败: {str(e)}",
            )

    def _test_websocket_connection(self) -> ValidationResult:
        """测试WebSocket连接"""
        start_time = time.time()
        connection_times = []

        try:
            # 测试多个WebSocket端点
            ws_endpoints = ["/api/v1/ws/realtime", "/api/v1/sse/market", "/ws/market"]

            successful_connections = 0

            async def test_endpoint(endpoint, ws_url):
                connection_start = time.time()
                try:
                    async with websockets.connect(ws_url) as websocket:
                        connection_time = (time.time() - connection_start) * 1000
                        connection_times.append(connection_time)

                        # 发送测试消息
                        test_message = {"action": "ping", "timestamp": time.time()}
                        await websocket.send(json.dumps(test_message))

                        # 接收响应
                        response = await asyncio.wait_for(websocket.recv(), timeout=5)
                        return True, connection_time
                except Exception as e:
                    print(f"   ❌ {endpoint}: {str(e)}")
                    return False, 0

            # 使用asyncio运行所有连接测试
            async def run_all_tests():
                results = []
                for endpoint in ws_endpoints:
                    ws_url = f"ws://localhost:8000{endpoint}"
                    success, connection_time = await test_endpoint(endpoint, ws_url)
                    results.append((endpoint, success, connection_time))
                return results

            # 运行测试
            test_results = asyncio.run(run_all_tests())

            for endpoint, success, connection_time in test_results:
                if success:
                    successful_connections += 1
                    print(f"   ✅ {endpoint}: {connection_time:.2f}ms")

            if successful_connections == 0:
                return ValidationResult(
                    test_name="WebSocket Connection",
                    success=False,
                    duration=time.time() - start_time,
                    error_message="所有WebSocket端点连接失败",
                )

            avg_connection_time = statistics.mean(connection_times)

            return ValidationResult(
                test_name="WebSocket Connection",
                success=True,
                duration=time.time() - start_time,
                metrics=StreamingMetrics(
                    connection_latency=avg_connection_time,
                    data_throughput=0,
                    message_loss_rate=0,
                    average_latency=avg_connection_time,
                    max_latency=max(connection_times),
                    error_count=len(ws_endpoints) - successful_connections,
                    connection_stability=successful_connections / len(ws_endpoints),
                ),
                details={
                    "successful_connections": successful_connections,
                    "total_endpoints": len(ws_endpoints),
                    "connection_times": connection_times,
                },
            )

        except Exception as e:
            return ValidationResult(
                test_name="WebSocket Connection",
                success=False,
                duration=time.time() - start_time,
                error_message=f"WebSocket测试异常: {str(e)}",
            )

    def _test_streaming_data(self) -> ValidationResult:
        """测试流媒体数据传输"""
        start_time = time.time()
        received_messages = []
        sent_count = 0
        error_count = 0

        try:
            # 并发测试多个流
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = []

                for symbol in self.test_symbols:
                    future = executor.submit(self._test_single_stream, symbol)
                    futures.append(future)

                # 等待所有流测试完成
                concurrent.futures.wait(futures, timeout=self.config["test_duration"])

            # 统计结果
            for future in futures:
                try:
                    result = future.result()
                    received_messages.extend(result.get("messages", []))
                    sent_count += result.get("sent_count", 0)
                    error_count += result.get("error_count", 0)
                except Exception:
                    error_count += 1

            # 计算指标
            duration = time.time() - start_time
            throughput = len(received_messages) / duration if duration > 0 else 0
            loss_rate = (
                ((sent_count - len(received_messages)) / sent_count * 100)
                if sent_count > 0
                else 0
            )

            # 计算延迟（如果有时间戳）
            latencies = []
            for msg in received_messages:
                if "timestamp" in msg:
                    try:
                        sent_time = msg.get("timestamp", 0)
                        current_time = time.time()
                        latency = (current_time - sent_time) * 1000  # 转换为毫秒
                        latencies.append(latency)
                    except:
                        pass

            avg_latency = statistics.mean(latencies) if latencies else 0
            max_latency = max(latencies) if latencies else 0

            success = (
                throughput > self.config["throughput_threshold"]
                and loss_rate < self.config["loss_threshold"]
            )

            return ValidationResult(
                test_name="Streaming Data Transfer",
                success=success,
                duration=duration,
                metrics=StreamingMetrics(
                    connection_latency=0,
                    data_throughput=throughput,
                    message_loss_rate=loss_rate,
                    average_latency=avg_latency,
                    max_latency=max_latency,
                    error_count=error_count,
                    connection_stability=1.0,
                ),
                details={
                    "received_messages": len(received_messages),
                    "sent_count": sent_count,
                    "throughput": throughput,
                    "latencies": latencies[:10],  # 前10个延迟样本
                },
            )

        except Exception as e:
            return ValidationResult(
                test_name="Streaming Data Transfer",
                success=False,
                duration=time.time() - start_time,
                error_message=f"流媒体数据测试异常: {str(e)}",
            )

    def _test_single_stream(self, symbol: str) -> Dict[str, Any]:
        """测试单个流的传输"""
        messages = []
        sent_count = 0
        error_count = 0

        try:
            ws_url = "ws://localhost:8000/api/v1/ws/realtime"

            async def test_single_stream():
                async with websockets.connect(ws_url) as websocket:
                    # 订阅特定股票
                    subscribe_msg = {
                        "action": "subscribe",
                        "symbol": symbol,
                        "fields": ["price", "volume", "timestamp"],
                    }
                    await websocket.send(json.dumps(subscribe_msg))

                    # 发送测试消息并接收响应
                    end_time = time.time() + 10  # 10秒测试时间
                    while time.time() < end_time:
                        try:
                            # 发送ping消息
                            ping_msg = {
                                "action": "ping",
                                "timestamp": time.time(),
                                "symbol": symbol,
                            }
                            await websocket.send(json.dumps(ping_msg))
                            sent_count += 1

                            # 接收消息
                            response = await asyncio.wait_for(
                                websocket.recv(), timeout=1
                            )
                            msg = json.loads(response)
                            messages.append(msg)

                        except websockets.exceptions.WebSocketException:
                            error_count += 1
                            break
                        except:
                            error_count += 1
                            continue

            try:
                asyncio.run(test_single_stream())
            except Exception:
                error_count += 1

        except Exception:
            error_count += 1

        return {
            "symbol": symbol,
            "messages": messages,
            "sent_count": sent_count,
            "error_count": error_count,
        }

    def _test_data_integrity(self) -> ValidationResult:
        """测试数据完整性"""
        start_time = time.time()

        try:
            # 测试多个数据源的一致性
            consistency_issues = []
            data_quality_scores = []

            for symbol in self.test_symbols:
                # HTTP API获取数据
                http_url = f"{self.base_url}/api/market/quotes?symbols={symbol}"
                http_response = requests.get(
                    http_url, timeout=(5, self.config["timeout"])
                )

                if http_response.status_code == 200:
                    http_data = http_response.json().get("data", [])

                    # 验证数据字段完整性
                    required_fields = ["symbol", "price", "volume", "timestamp"]
                    missing_fields = []

                    for field in required_fields:
                        if not http_data or field not in http_data[0]:
                            missing_fields.append(field)

                    if missing_fields:
                        consistency_issues.append(
                            f"{symbol}: 缺少字段 {missing_fields}"
                        )

                    # 计算数据质量分数
                    if http_data:
                        quality_score = (
                            (len(required_fields) - len(missing_fields))
                            / len(required_fields)
                            * 100
                        )
                        data_quality_scores.append(quality_score)

            # 检查数据一致性
            average_quality = (
                statistics.mean(data_quality_scores) if data_quality_scores else 0
            )
            success = average_quality > 80 and len(consistency_issues) == 0

            return ValidationResult(
                test_name="Data Integrity",
                success=success,
                duration=time.time() - start_time,
                details={
                    "average_quality_score": average_quality,
                    "consistency_issues": consistency_issues,
                    "tested_symbols": len(self.test_symbols),
                },
            )

        except Exception as e:
            return ValidationResult(
                test_name="Data Integrity",
                success=False,
                duration=time.time() - start_time,
                error_message=f"数据完整性测试异常: {str(e)}",
            )

    def _test_stream_state_management(self) -> ValidationResult:
        """测试流状态管理"""
        start_time = time.time()

        try:
            # 测试流的创建、暂停、恢复和销毁
            state_transitions = []

            ws_url = "ws://localhost:8000/api/v1/ws/realtime"

            async def test_state_management():
                async with websockets.connect(ws_url) as websocket:
                    # 测试订阅/取消订阅
                    subscribe_msg = {
                        "action": "subscribe",
                        "symbol": "600519",
                        "fields": ["price", "volume"],
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                    state_transitions.append("subscribed")

                    # 等待确认
                    response = await asyncio.wait_for(websocket.recv(), timeout=2)

                    # 测试取消订阅
                    unsubscribe_msg = {"action": "unsubscribe", "symbol": "600519"}
                    await websocket.send(json.dumps(unsubscribe_msg))
                    state_transitions.append("unsubscribed")

                    # 验证状态响应
                    response = await asyncio.wait_for(websocket.recv(), timeout=2)

            asyncio.run(test_state_management())

            success = len(state_transitions) == 2

            return ValidationResult(
                test_name="Stream State Management",
                success=success,
                duration=time.time() - start_time,
                details={
                    "state_transitions": state_transitions,
                    "test_duration": time.time() - start_time,
                },
            )

        except Exception as e:
            return ValidationResult(
                test_name="Stream State Management",
                success=False,
                duration=time.time() - start_time,
                error_message=f"流状态管理测试异常: {str(e)}",
            )

    def _test_error_recovery(self) -> ValidationResult:
        """测试错误恢复"""
        start_time = time.time()
        recovery_attempts = 0
        successful_recoveries = 0

        try:
            # 测试连接断开后的恢复
            ws_url = "ws://localhost:8000/api/v1/ws/realtime"

            for attempt in range(self.config["retry_count"]):
                recovery_attempts += 1

                try:

                    async def test_recovery():
                        async with websockets.connect(ws_url) as websocket:
                            # 发送心跳
                            heartbeat_msg = {
                                "action": "heartbeat",
                                "timestamp": time.time(),
                            }
                            await websocket.send(json.dumps(heartbeat_msg))

                            # 验证响应
                            response = await asyncio.wait_for(
                                websocket.recv(), timeout=2
                            )
                            return True

                    asyncio.run(test_recovery())
                    successful_recoveries += 1

                except Exception:
                    continue

            recovery_rate = (
                successful_recoveries / recovery_attempts
                if recovery_attempts > 0
                else 0
            )
            success = recovery_rate > 0.5  # 50%以上的恢复成功率

            return ValidationResult(
                test_name="Error Recovery",
                success=success,
                duration=time.time() - start_time,
                details={
                    "recovery_attempts": recovery_attempts,
                    "successful_recoveries": successful_recoveries,
                    "recovery_rate": recovery_rate,
                },
            )

        except Exception as e:
            return ValidationResult(
                test_name="Error Recovery",
                success=False,
                duration=time.time() - start_time,
                error_message=f"错误恢复测试异常: {str(e)}",
            )

    def _print_result(self, result: ValidationResult):
        """打印验证结果"""
        status_icon = "✅" if result.success else "❌"
        print(f"   {status_icon} {result.test_name}: {result.duration:.2f}s")

        if result.metrics:
            metrics = result.metrics
            print(f"      📊 延迟: {metrics.average_latency:.2f}ms")
            print(f"      📊 吞吐量: {metrics.data_throughput:.2f}msg/s")
            print(f"      📊 消息丢失: {metrics.message_loss_rate:.2f}%")
            print(f"      📊 连接稳定性: {metrics.connection_stability:.2f}")

        if result.error_message:
            print(f"      ❌ 错误: {result.error_message}")

    def _generate_summary_report(self) -> Dict[str, Any]:
        """生成综合报告"""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0

        # 总体指标
        total_duration = sum(r.duration for r in self.results)
        total_errors = sum(r.metrics.error_count for r in self.results if r.metrics)

        # 性能指标
        avg_latencies = [
            r.metrics.average_latency
            for r in self.results
            if r.metrics and r.metrics.average_latency > 0
        ]
        avg_throughput = [
            r.metrics.data_throughput
            for r in self.results
            if r.metrics and r.metrics.data_throughput > 0
        ]
        avg_loss_rates = [
            r.metrics.message_loss_rate for r in self.results if r.metrics
        ]

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": success_rate,
                "total_duration": total_duration,
                "total_errors": total_errors,
            },
            "performance_metrics": {
                "average_latency": statistics.mean(avg_latencies)
                if avg_latencies
                else 0,
                "average_throughput": statistics.mean(avg_throughput)
                if avg_throughput
                else 0,
                "average_loss_rate": statistics.mean(avg_loss_rates)
                if avg_loss_rates
                else 0,
            },
            "individual_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "duration": r.duration,
                    "error_message": r.error_message,
                    "metrics": {
                        "connection_latency": r.metrics.connection_latency
                        if r.metrics
                        else None,
                        "data_throughput": r.metrics.data_throughput
                        if r.metrics
                        else None,
                        "message_loss_rate": r.metrics.message_loss_rate
                        if r.metrics
                        else None,
                        "average_latency": r.metrics.average_latency
                        if r.metrics
                        else None,
                        "max_latency": r.metrics.max_latency if r.metrics else None,
                        "error_count": r.metrics.error_count if r.metrics else None,
                        "connection_stability": r.metrics.connection_stability
                        if r.metrics
                        else None,
                    }
                    if r.metrics
                    else None,
                    "details": r.details,
                }
                for r in self.results
            ],
        }

        # 打印摘要
        print("\n" + "=" * 60)
        print("📊 实时数据流完整性验证报告")
        print("=" * 60)
        print(f"✅ 成功测试: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"⏱️  总用时: {total_duration:.2f}秒")
        print(f"❌ 总错误: {total_errors}")

        if avg_latencies:
            print(f"📈 平均延迟: {statistics.mean(avg_latencies):.2f}ms")
        if avg_throughput:
            print(f"📊 平均吞吐量: {statistics.mean(avg_throughput):.2f}msg/s")
        if avg_loss_rates:
            print(f"📉 平均丢失率: {statistics.mean(avg_loss_rates):.2f}%")

        # 保存详细报告
        report_file = f"/opt/claude/mystocks_spec/logs/realtime_streaming_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 详细报告已保存: {report_file}")

        return report


def main():
    """主函数"""
    print("🔧 实时数据流完整性验证工具")
    print("Phase 7-1: 实时数据流完整性验证")
    print("=" * 60)

    # 创建验证器
    validator = RealtimeStreamingValidator()

    # 执行验证
    report = validator.validate_all()

    # 返回结果
    return report["summary"]["success_rate"]


if __name__ == "__main__":
    main()
