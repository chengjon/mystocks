"""
GPU API 系统主服务器
GPU API System Main Server
"""

import logging
import signal
import sys
import time
from concurrent import futures
import grpc

from src.utils.gpu_utils import GPUResourceManager
from src.utils.redis_utils import RedisQueue
from src.utils.monitoring import MetricsCollector
from services.integrated_backtest_service import IntegratedBacktestService
from services.integrated_realtime_service import IntegratedRealTimeService
from services.integrated_ml_service import IntegratedMLService
from config.system_config import SystemConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "/opt/claude/mystocks_spec/gpu_api_system/logs/gpu_api_server.log"
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class GPUAPIServer:
    """GPU API 系统主服务器"""

    def __init__(self, config: SystemConfig):
        self.config = config
        self.server = None
        self.services = {}

        # 核心组件
        self.gpu_manager = None
        self.redis_queue = None
        self.metrics_collector = None

        # 集成服务
        self.backtest_service = None
        self.realtime_service = None
        self.ml_service = None

        logger.info("GPU API 服务器初始化")

    def initialize(self):
        """初始化服务器"""
        logger.info("正在初始化GPU API服务器...")

        try:
            # 初始化核心组件
            self._initialize_core_components()

            # 初始化集成服务
            self._initialize_services()

            # 创建gRPC服务器
            self._create_grpc_server()

            logger.info("GPU API服务器初始化完成")

        except Exception as e:
            logger.error(f"初始化GPU API服务器失败: {e}")
            raise e

    def _initialize_core_components(self):
        """初始化核心组件"""
        logger.info("初始化核心组件...")

        # GPU资源管理器
        self.gpu_manager = GPUResourceManager()
        self.gpu_manager.initialize()
        logger.info("GPU资源管理器初始化完成")

        # Redis队列
        self.redis_queue = RedisQueue(
            host=self.config.redis_config["host"],
            port=self.config.redis_config["port"],
            db=self.config.redis_config["db"],
        )
        logger.info("Redis队列初始化完成")

        # 指标收集器
        self.metrics_collector = MetricsCollector()
        self.metrics_collector.start()
        logger.info("指标收集器初始化完成")

    def _initialize_services(self):
        """初始化集成服务"""
        logger.info("初始化集成服务...")

        # 回测服务
        self.backtest_service = IntegratedBacktestService(
            self.gpu_manager, self.redis_queue, self.metrics_collector
        )
        self.backtest_service.initialize()
        logger.info("集成回测服务初始化完成")

        # 实时数据处理服务
        self.realtime_service = IntegratedRealTimeService(
            self.gpu_manager, self.redis_queue, self.metrics_collector
        )
        self.realtime_service.initialize()
        logger.info("集成实时数据处理服务初始化完成")

        # ML训练服务
        self.ml_service = IntegratedMLService(
            self.gpu_manager, self.redis_queue, self.metrics_collector
        )
        self.ml_service.initialize()
        logger.info("集成ML训练服务初始化完成")

    def _create_grpc_server(self):
        """创建gRPC服务器"""
        logger.info("创建gRPC服务器...")

        # 创建服务器
        self.server = grpc.server(
            futures.ThreadPoolExecutor(
                max_workers=self.config.grpc_config["max_workers"]
            ),
            options=[
                (
                    "grpc.max_send_message_length",
                    self.config.grpc_config["max_message_size"],
                ),
                (
                    "grpc.max_receive_message_length",
                    self.config.grpc_config["max_message_size"],
                ),
                ("grpc.keepalive_time_ms", 30000),
                ("grpc.keepalive_timeout_ms", 10000),
                ("grpc.keepalive_permit_without_calls", True),
                ("grpc.http2.max_pings_without_data", 0),
                ("grpc.http2.min_time_between_pings_ms", 10000),
                ("grpc.http2.min_ping_interval_without_data_ms", 5000),
            ],
        )

        # 注册服务
        from api_proto.backtest_pb2_grpc import add_BacktestServiceServicer_to_server
        from api_proto.realtime_pb2_grpc import add_RealTimeServiceServicer_to_server
        from api_proto.ml_pb2_grpc import add_MLServiceServicer_to_server

        add_BacktestServiceServicer_to_server(self.backtest_service, self.server)
        add_RealTimeServiceServicer_to_server(self.realtime_service, self.server)
        add_MLServiceServicer_to_server(self.ml_service, self.server)

        # 添加端口
        server_address = (
            f"{self.config.grpc_config['host']}:{self.config.grpc_config['port']}"
        )
        self.server.add_insecure_port(server_address)

        logger.info(f"gRPC服务器创建完成，监听地址: {server_address}")

    def start(self):
        """启动服务器"""
        logger.info("正在启动GPU API服务器...")

        try:
            # 启动gRPC服务器
            self.server.start()
            logger.info(
                f"GPU API服务器已启动，监听端口: {self.config.grpc_config['port']}"
            )

            # 注册信号处理
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            # 打印服务状态
            self._print_server_status()

            # 保持服务器运行
            try:
                while True:
                    time.sleep(86400)  # 24小时
            except KeyboardInterrupt:
                logger.info("接收到中断信号")

        except Exception as e:
            logger.error(f"启动GPU API服务器失败: {e}")
            raise e

    def _signal_handler(self, signum, frame):
        """信号处理"""
        logger.info(f"接收到信号: {signum}")
        self.stop()
        sys.exit(0)

    def _print_server_status(self):
        """打印服务器状态"""
        logger.info("=" * 80)
        logger.info("GPU API 系统服务器状态")
        logger.info("=" * 80)

        # GPU状态
        gpu_stats = self.gpu_manager.get_gpu_stats()
        logger.info(f"GPU状态: {gpu_stats}")

        # 服务状态
        logger.info("集成服务:")
        logger.info(f"  - 回测服务: 已启动")
        logger.info(f"  - 实时数据处理服务: 已启动")
        logger.info(f"  - ML训练服务: 已启动")

        # 服务器配置
        logger.info("服务器配置:")
        logger.info(f"  - gRPC端口: {self.config.grpc_config['port']}")
        logger.info(f"  - 最大工作线程: {self.config.grpc_config['max_workers']}")
        logger.info(
            f"  - Redis地址: {self.config.redis_config['host']}:{self.config.redis_config['port']}"
        )

        logger.info("=" * 80)

    def stop(self):
        """停止服务器"""
        logger.info("正在停止GPU API服务器...")

        try:
            # 停止集成服务
            if self.backtest_service:
                self.backtest_service.stop()
                logger.info("集成回测服务已停止")

            if self.realtime_service:
                self.realtime_service.stop()
                logger.info("集成实时数据处理服务已停止")

            if self.ml_service:
                self.ml_service.stop()
                logger.info("集成ML训练服务已停止")

            # 停止核心组件
            if self.metrics_collector:
                self.metrics_collector.stop()
                logger.info("指标收集器已停止")

            # 停止gRPC服务器
            if self.server:
                self.server.stop(grace=5)
                logger.info("gRPC服务器已停止")

            logger.info("GPU API服务器已完全停止")

        except Exception as e:
            logger.error(f"停止GPU API服务器失败: {e}")


def main():
    """主函数"""
    logger.info("启动GPU API系统主服务器...")

    # 加载配置
    config = SystemConfig()

    # 创建服务器
    server = GPUAPIServer(config)

    try:
        # 初始化服务器
        server.initialize()

        # 启动服务器
        server.start()

    except Exception as e:
        logger.error(f"服务器运行失败: {e}")
        server.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
