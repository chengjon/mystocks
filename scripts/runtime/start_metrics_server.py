#!/usr/bin/env python3
"""
启动数据源Prometheus监控指标服务器

功能：
1. 启动Prometheus metrics HTTP服务器（端口8001）
2. 初始化所有已注册数据源的metrics
3. 提供持续的指标暴露给Prometheus抓取

使用方法：
    # 启动服务器
    python scripts/runtime/start_metrics_server.py

    # 后台运行
    nohup python scripts/runtime/start_metrics_server.py > logs/metrics_server.log 2>&1 &

    # 使用PM2管理（推荐）
    pm2 start scripts/runtime/start_metrics_server.py --name mystocks-metrics

端口：
    默认 8001，可通过环境变量 METRICS_PORT 配置

访问：
    http://localhost:8001/metrics

作者：Claude Code
版本：v2.0
创建时间：2026-01-02
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.monitoring.data_source_metrics import (
    DataSourceMetricsExporter,
    start_metrics_server
)
from src.core.data_source_manager_v2 import DataSourceManagerV2


def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/metrics_server.log')
        ]
    )


def initialize_data_source_metrics():
    """
    初始化所有数据源的metrics

    从PostgreSQL注册表加载所有数据源，为每个数据源初始化Prometheus metrics
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("初始化数据源监控指标")
    logger.info("=" * 60)

    try:
        # 创建V2管理器（会自动加载注册表）
        manager = DataSourceManagerV2()

        # 获取所有注册的数据源
        all_sources = manager.registry

        logger.info(f"找到 {len(all_sources)} 个已注册的数据源")

        # 初始化每个数据源的metrics
        exporter = DataSourceMetricsExporter.get_instance()

        initialized = 0
        for endpoint_name, source_data in all_sources.items():
            try:
                config = source_data.get('config', {})

                # 初始化metrics
                exporter.init_source_metrics(
                    endpoint_name=endpoint_name,
                    source_name=config.get('source_name', ''),
                    data_category=config.get('data_category', ''),
                    source_type=config.get('source_type', ''),
                    classification_level=config.get('classification_level', ''),
                    target_db=config.get('target_db', ''),
                    table_name=config.get('table_name', ''),
                    description=config.get('description', ''),
                    priority=config.get('priority', 10),
                    status=config.get('status', 'unknown')
                )

                initialized += 1
                logger.info(f"✓ {endpoint_name}: {config.get('source_name')} - {config.get('data_category')}")

            except Exception as e:
                logger.error(f"✗ {endpoint_name}: 初始化失败 - {e}")

        logger.info(f"\n成功初始化 {initialized}/{len(all_sources)} 个数据源的metrics")

        # 更新健康状态metrics
        exporter.update_all_from_registry(all_sources)

        logger.info("✓ 所有健康状态指标已更新")

        return exporter

    except Exception as e:
        logger.error(f"初始化数据源metrics失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)

    # 确保日志目录存在
    Path('logs').mkdir(exist_ok=True)

    logger.info("")
    logger.info("╔══════════════════════════════════════════════════════╗")
    logger.info("║   MyStocks 数据源监控指标服务器 v2.0                  ║")
    logger.info("╚══════════════════════════════════════════════════════╝")
    logger.info("")

    # 获取端口配置
    metrics_port = int(os.getenv('METRICS_PORT', '8001'))

    logger.info("配置信息:")
    logger.info(f"  - Metrics端口: {metrics_port}")
    logger.info("  - Prometheus地址: http://localhost:9090")
    logger.info("  - Grafana地址: http://localhost:3000")
    logger.info(f"  - Metrics端点: http://localhost:{metrics_port}/metrics")
    logger.info("")

    # 初始化数据源metrics
    exporter = initialize_data_source_metrics()

    if exporter is None:
        logger.error("无法初始化数据源metrics，退出...")
        sys.exit(1)

    logger.info("")
    logger.info("启动Prometheus metrics服务器...")
    logger.info(f"访问 http://localhost:{metrics_port}/metrics 查看指标")
    logger.info("")
    logger.info("按 Ctrl+C 停止服务器")
    logger.info("")

    try:
        # 启动metrics服务器（阻塞）
        start_metrics_server(port=metrics_port)

    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 60)
        logger.info("收到停止信号，正在关闭服务器...")
        logger.info("=" * 60)
        logger.info("✓ 服务器已停止")
        sys.exit(0)

    except Exception as e:
        logger.error(f"服务器错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
