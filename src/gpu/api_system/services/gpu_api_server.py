#!/usr/bin/env python3
"""
MyStocks GPU API系统 - 主服务
MyStocks GPU API System - Main Service
"""

import logging
import signal
import sys
import time

import grpc
import prometheus_client
from concurrent import futures
from prometheus_client import Counter, Histogram, Gauge

# 导入gRPC服务
from api_proto import realtime_pb2_grpc
from api_proto import backtest_pb2_grpc

# 导入自定义模块
from src.utils.gpu_utils import GPUResourceManager
from src.utils.redis_utils import RedisQueue
from src.utils.monitoring import MetricsCollector
from services.realtime_service import RealTimeService
from services.backtest_service import BacktestService
from services.resource_scheduler import ResourceScheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/opt/mystocks_gpu_api/logs/api.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Prometheus指标
REQUEST_COUNT = Counter("api_requests_total", "Total API requests", ["method", "status"])
REQUEST_DURATION = Histogram("api_request_duration_seconds", "API request duration")
ACTIVE_CONNECTIONS = Gauge("active_connections", "Number of active connections")
GPU_UTILIZATION = Gauge("gpu_utilization", "GPU utilization percentage")
GPU_MEMORY_USAGE = Gauge("gpu_memory_usage", "GPU memory usage percentage")
TASK_QUEUE_LENGTH = Gauge("task_queue_length", "Number of tasks in queue")


class GPUServer:
    def __init__(self):
        self.server = None
        self.gpu_manager = GPUResourceManager()
        self.redis_queue = RedisQueue()
        self.metrics_collector = MetricsCollector()
        self.resource_scheduler = ResourceScheduler()
        self.realtime_service = RealTimeService(self.gpu_manager, self.redis_queue, self.metrics_collector)
        self.backtest_service = BacktestService(self.gpu_manager, self.redis_queue, self.metrics_collector)
        self.running = True

    def initialize(self):
        """初始化服务器"""
        try:
            logger.info("正在初始化GPU API服务器...")

            # 初始化GPU资源管理器
            self.gpu_manager.initialize()
            logger.info("GPU资源管理器初始化完成")

            # 初始化Redis队列
            self.redis_queue.connect()
            logger.info("Redis队列连接成功")

            # 初始化资源调度器
            self.resource_scheduler.initialize()
            logger.info("资源调度器初始化完成")

            logger.info("GPU API服务器初始化完成")

        except Exception as e:
            logger.error("服务器初始化失败: %s", e)
            raise

    def create_server(self):
        """创建gRPC服务器"""
        self.server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=100),
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),  # 50MB
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),  # 50MB
                ("grpc.max_concurrent_calls", 100),
                ("grpc.keepalive_timeout_ms", 10000),
                ("grpc.http2_max_pings_without_data", 0),
            ],
        )

        # 添加服务
        realtime_pb2_grpc.add_RealTimeServiceServicer_to_server(self.realtime_service, self.server)
        backtest_pb2_grpc.add_BacktestServiceServicer_to_server(self.backtest_service, self.server)

        # 添加监控指标
        prometheus_client.start_http_server(8000)
        logger.info("监控指标服务已启动在端口8000")

    def start(self):
        """启动服务器"""
        try:
            self.create_server()

            # 启动服务器
            self.server.add_insecure_port("[::]:50051")
            self.server.add_insecure_port("[::]:50052")
            self.server.add_insecure_port("[::]:50053")

            logger.info("正在启动gRPC服务器...")
            self.server.start()

            logger.info("gRPC服务器已启动")
            logger.info("gRPC端口: 50051 (实时数据), 50052 (WebSocket), 50053 (REST)")
            logger.info("监控端口: 8000")

            # 启动监控
            self.start_monitoring()

        except Exception as e:
            logger.error("服务器启动失败: %s", e)
            raise

    def start_monitoring(self):
        """启动监控线程"""

        def monitor_loop():
            while self.running:
                try:
                    # 更新GPU指标
                    gpu_stats = self.gpu_manager.get_gpu_stats()
                    if gpu_stats:
                        GPU_UTILIZATION.set(gpu_stats["utilization"])
                        GPU_MEMORY_USAGE.set(gpu_stats["memory_usage"])

                    # 更新队列长度
                    queue_length = self.redis_queue.get_queue_length()
                    TASK_QUEUE_LENGTH.set(queue_length)

                    # 更新连接数
                    active_connections = self.metrics_collector.get_active_connections()
                    ACTIVE_CONNECTIONS.set(active_connections)

                    time.sleep(5)

                except Exception as e:
                    logger.error("监控更新失败: %s", e)
                    time.sleep(10)

        import threading

        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("监控线程已启动")

    def stop(self):
        """停止服务器"""
        logger.info("正在停止服务器...")
        self.running = False

        if self.server:
            self.server.stop(grace=10)
            logger.info("服务器已停止")

        # 清理资源
        self.gpu_manager.cleanup()
        self.redis_queue.disconnect()
        logger.info("资源已清理")

    def setup_signal_handlers(self):
        """设置信号处理器"""

        def signal_handler(signum, frame):
            logger.info("收到信号 %s，正在关闭服务器...", signum)
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def run(self):
        """运行服务器"""
        try:
            self.setup_signal_handlers()
            self.initialize()
            self.start()

            # 保持服务器运行
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("收到键盘中断，正在停止服务器...")
        except Exception as e:
            logger.error("服务器运行异常: %s", e)
        finally:
            self.stop()


def main():
    """主函数"""
    logger.info("=========================================")
    logger.info("MyStocks GPU API系统启动中...")
    logger.info("=========================================")

    server = GPUServer()

    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("用户中断，正在关闭服务器...")
    except Exception as e:
        logger.error("服务器启动失败: %s", e)
        sys.exit(1)
    finally:
        logger.info("服务器已关闭")


if __name__ == "__main__":
    main()
