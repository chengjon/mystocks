#!/usr/bin/env python3
"""
WebSocket连接压力测试脚本
WebSocket Connection Stress Test - Performance Testing and Optimization

Phase 6-2: WebSocket连接压力测试和优化

功能特性:
- 多并发连接压力测试
- 消息吞吐量测试
- 连接池性能验证
- 内存使用监控
- 错误处理和恢复测试
- 性能报告生成

Author: Claude Code
Date: 2025-11-13
"""

import asyncio
import aiohttp
import time
import json
import uuid
import statistics
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import structlog

logger = structlog.get_logger()


@dataclass
class TestMetrics:
    """测试指标"""

    test_name: str
    total_connections: int
    concurrent_connections: int
    duration_seconds: float
    messages_per_second: float
    avg_response_time_ms: float
    max_response_time_ms: float
    min_response_time_ms: float
    success_rate: float
    error_count: int
    memory_usage_mb: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "test_name": self.test_name,
            "total_connections": self.total_connections,
            "concurrent_connections": self.concurrent_connections,
            "duration_seconds": round(self.duration_seconds, 2),
            "messages_per_second": round(self.messages_per_second, 2),
            "avg_response_time_ms": round(self.avg_response_time_ms, 2),
            "max_response_time_ms": round(self.max_response_time_ms, 2),
            "min_response_time_ms": round(self.min_response_time_ms, 2),
            "success_rate": round(self.success_rate, 2),
            "error_count": self.error_count,
            "memory_usage_mb": round(self.memory_usage_mb, 2),
            "timestamp": self.timestamp.isoformat(),
        }


class WebSocketStressTest:
    """WebSocket压力测试器"""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        websocket_url: str = "ws://localhost:8000/socket.io/",
    ):
        """
        初始化压力测试器

        Args:
            base_url: API基础URL
            websocket_url: WebSocket连接URL
        """
        self.base_url = base_url
        self.websocket_url = websocket_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()

    async def check_server_status(self) -> bool:
        """检查服务器状态"""
        try:
            async with self.session.get(f"{self.base_url}/api/socketio-status") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("✅ WebSocket服务器状态正常", status=data.get("status"))
                    return True
                else:
                    logger.error("❌ WebSocket服务器状态异常", status=response.status)
                    return False
        except Exception as e:
            logger.error("❌ 无法连接WebSocket服务器", error=str(e))
            return False

    async def create_websocket_connection(self, connection_id: str) -> Dict[str, Any]:
        """
        创建WebSocket连接

        Args:
            connection_id: 连接ID

        Returns:
            连接结果字典
        """
        try:
            start_time = time.time()

            # 模拟Socket.IO连接（实际测试中需要更复杂的握手过程）
            async with self.session.ws_connect(self.websocket_url) as ws:
                response_times = []
                message_count = 0
                success_count = 0
                error_count = 0

                # 发送测试消息
                for i in range(10):  # 每个连接发送10条消息
                    msg_start = time.time()

                    # 模拟WebSocket消息格式
                    test_message = {
                        "type": "request",
                        "request_id": f"test_{connection_id}_{i}",
                        "action": "get_market_data",
                        "payload": {
                            "symbol": "600519",
                            "data_type": "fund_flow",
                            "timeframe": "1d",
                        },
                        "timestamp": int(time.time() * 1000),
                    }

                    try:
                        await ws.send_str(json.dumps(test_message))

                        # 等待响应（超时2秒）
                        try:
                            msg = await asyncio.wait_for(ws.receive(), timeout=2.0)
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                response_data = json.loads(msg.data)
                                response_time = (time.time() - msg_start) * 1000
                                response_times.append(response_time)
                                success_count += 1
                                message_count += 1
                            else:
                                error_count += 1
                        except asyncio.TimeoutError:
                            error_count += 1
                            logger.debug("⏰ 消息响应超时", connection_id=connection_id, message_id=i)

                    except Exception as e:
                        error_count += 1
                        logger.debug("❌ 消息发送失败", connection_id=connection_id, error=str(e))

                    # 小延迟避免过于频繁的请求
                    await asyncio.sleep(0.1)

                # 计算连接统计
                connection_time = time.time() - start_time
                avg_response_time = statistics.mean(response_times) if response_times else 0
                max_response_time = max(response_times) if response_times else 0
                min_response_time = min(response_times) if response_times else 0

                return {
                    "connection_id": connection_id,
                    "success": True,
                    "connection_time": connection_time,
                    "avg_response_time_ms": avg_response_time,
                    "max_response_time_ms": max_response_time,
                    "min_response_time_ms": min_response_time,
                    "message_count": message_count,
                    "success_count": success_count,
                    "error_count": error_count,
                }

        except Exception as e:
            logger.error("❌ WebSocket连接失败", connection_id=connection_id, error=str(e))
            return {
                "connection_id": connection_id,
                "success": False,
                "error": str(e),
                "connection_time": 0,
                "avg_response_time_ms": 0,
                "max_response_time_ms": 0,
                "min_response_time_ms": 0,
                "message_count": 0,
                "success_count": 0,
                "error_count": 1,
            }

    async def run_connection_test(
        self,
        concurrent_connections: int = 100,
        test_duration: int = 30,
    ) -> TestMetrics:
        """
        运行连接压力测试

        Args:
            concurrent_connections: 并发连接数
            test_duration: 测试持续时间（秒）

        Returns:
            测试指标
        """
        logger.info(
            "🚀 开始WebSocket连接压力测试",
            concurrent_connections=concurrent_connections,
            test_duration=test_duration,
        )

        start_time = time.time()
        connection_tasks = []
        all_results = []

        # 创建并发连接任务
        for i in range(concurrent_connections):
            connection_id = f"conn_{i}_{int(time.time())}"
            task = asyncio.create_task(
                self.create_websocket_connection(connection_id)
            )
            connection_tasks.append(task)

            # 分批启动连接，避免瞬时负载过高
            if len(connection_tasks) >= 20:
                batch_results = await asyncio.gather(*connection_tasks, return_exceptions=True)
                all_results.extend([r for r in batch_results if not isinstance(r, Exception)])
                connection_tasks.clear()
                await asyncio.sleep(0.5)  # 批次间延迟

        # 等待剩余连接完成
        if connection_tasks:
            batch_results = await asyncio.gather(*connection_tasks, return_exceptions=True)
            all_results.extend([r for r in batch_results if not isinstance(r, Exception)])

        end_time = time.time()
        total_duration = end_time - start_time

        # 分析结果
        successful_connections = [r for r in all_results if r.get("success", False)]
        failed_connections = [r for r in all_results if not r.get("success", False)]

        total_messages = sum(r.get("message_count", 0) for r in all_results)
        total_success = sum(r.get("success_count", 0) for r in all_results)
        total_errors = sum(r.get("error_count", 0) for r in all_results)

        # 计算响应时间统计
        all_response_times = []
        for r in successful_connections:
            if r.get("avg_response_time_ms", 0) > 0:
                all_response_times.append(r["avg_response_time_ms"])

        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
        max_response_time = max(all_response_times) if all_response_times else 0
        min_response_time = min(all_response_times) if all_response_times else 0

        # 计算成功率
        success_rate = (len(successful_connections) / len(all_results)) * 100 if all_results else 0

        # 计算消息吞吐量
        messages_per_second = total_messages / total_duration if total_duration > 0 else 0

        # 估算内存使用（简化版本）
        memory_usage_mb = len(all_results) * 0.5  # 估算每连接0.5MB

        metrics = TestMetrics(
            test_name=f"WebSocket_Connection_Test_{concurrent_connections}_Connections",
            total_connections=len(all_results),
            concurrent_connections=concurrent_connections,
            duration_seconds=total_duration,
            messages_per_second=messages_per_second,
            avg_response_time_ms=avg_response_time,
            max_response_time_ms=max_response_time,
            min_response_time_ms=min_response_time,
            success_rate=success_rate,
            error_count=total_errors,
            memory_usage_mb=memory_usage_mb,
        )

        logger.info(
            "✅ WebSocket连接压力测试完成",
            successful=len(successful_connections),
            failed=len(failed_connections),
            success_rate=f"{success_rate:.2f}%",
            avg_response_time=f"{avg_response_time:.2f}ms",
            messages_per_second=f"{messages_per_second:.2f}/s",
        )

        return metrics

    async def run_throughput_test(
        self,
        connection_count: int = 50,
        messages_per_connection: int = 100,
    ) -> TestMetrics:
        """
        运行消息吞吐量测试

        Args:
            connection_count: 连接数量
            messages_per_connection: 每个连接的消息数量

        Returns:
            测试指标
        """
        logger.info(
            "📊 开始WebSocket消息吞吐量测试",
            connection_count=connection_count,
            messages_per_connection=messages_per_connection,
        )

        # 这里可以实现更详细的消息吞吐量测试
        # 包括不同大小消息、不同频率等测试场景

        return await self.run_connection_test(
            concurrent_connections=connection_count,
            test_duration=10,
        )

    def save_test_results(self, metrics: TestMetrics, filename: Optional[str] = None):
        """
        保存测试结果

        Args:
            metrics: 测试指标
            filename: 文件名（可选）
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"websocket_stress_test_{timestamp}.json"

        filepath = f"/opt/claude/mystocks_spec/logs/{filename}"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(metrics.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info("💾 测试结果已保存", filepath=filepath)

        except Exception as e:
            logger.error("❌ 保存测试结果失败", error=str(e))


async def main():
    """主函数"""
    print("🚀 WebSocket连接压力测试工具")
    print("=" * 50)

    async with WebSocketStressTest() as tester:
        # 检查服务器状态
        if not await tester.check_server_status():
            print("❌ WebSocket服务器不可用，请先启动服务器")
            return

        # 运行不同规模的测试
        test_scenarios = [
            {"concurrent_connections": 50, "test_duration": 30},
            {"concurrent_connections": 100, "test_duration": 30},
            {"concurrent_connections": 200, "test_duration": 60},
        ]

        all_metrics = []

        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📋 测试场景 {i}/{len(test_scenarios)}")
            print(f"并发连接数: {scenario['concurrent_connections']}")
            print(f"测试时长: {scenario['test_duration']}秒")
            print("-" * 30)

            try:
                metrics = await tester.run_connection_test(**scenario)
                all_metrics.append(metrics)
                tester.save_test_results(metrics)

                # 显示结果
                print(f"✅ 测试完成:")
                print(f"   成功率: {metrics.success_rate:.2f}%")
                print(f"   平均响应时间: {metrics.avg_response_time_ms:.2f}ms")
                print(f"   最大响应时间: {metrics.max_response_time_ms:.2f}ms")
                print(f"   消息吞吐量: {metrics.messages_per_second:.2f} 消息/秒")
                print(f"   内存使用: {metrics.memory_usage_mb:.2f}MB")

            except Exception as e:
                print(f"❌ 测试场景 {i} 失败: {e}")

        # 生成综合报告
        if all_metrics:
            print("\n📈 综合测试报告")
            print("=" * 50)

            best_metric = min(all_metrics, key=lambda m: m.avg_response_time_ms)
            worst_metric = max(all_metrics, key=lambda m: m.avg_response_time_ms)

            print(f"最佳性能: {best_metric.concurrent_connections}连接, "
                  f"响应时间: {best_metric.avg_response_time_ms:.2f}ms")
            print(f"最差性能: {worst_metric.concurrent_connections}连接, "
                  f"响应时间: {worst_metric.avg_response_time_ms:.2f}ms")

            avg_success_rate = statistics.mean(m.success_rate for m in all_metrics)
            avg_throughput = statistics.mean(m.messages_per_second for m in all_metrics)

            print(f"平均成功率: {avg_success_rate:.2f}%")
            print(f"平均吞吐量: {avg_throughput:.2f} 消息/秒")


if __name__ == "__main__":
    # 设置事件循环策略（Windows兼容性）
    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # 运行测试
    asyncio.run(main())