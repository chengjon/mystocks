#!/usr/bin/env python3
"""
定时聚合任务启动脚本

用于定时执行信号统计聚合任务，包括：
- 小时级聚合（每小时执行）
- 数据清理（删除90天前的数据）

使用方法：
    python scripts/runtime/run_signal_aggregation.py

作者: Claude Code (Main CLI)
创建日期: 2026-01-08
版本: v1.0
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.monitoring.signal_aggregation_task import SignalStatisticsAggregator, MetricsScheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/signal_aggregation.log')
    ]
)

logger = logging.getLogger(__name__)


async def run_hourly_aggregation():
    """
    运行小时级聚合任务（手动触发）

    聚合最近2小时的数据到 signal_statistics_hourly 表。
    """
    logger.info("=" * 60)
    logger.info("开始小时级信号统计聚合")
    logger.info("=" * 60)

    try:
        aggregator = SignalStatisticsAggregator()
        result = await aggregator.aggregate_hourly_statistics(hours_back=2)

        if result.get("success"):
            logger.info("✅ 聚合成功!")
            logger.info(f"   - 聚合记录数: {result['aggregated_count']}")
            logger.info(f"   - 清理记录数: {result['cleanup_count']}")
            logger.info(f"   - 执行时间: {result['duration_seconds']:.2f}秒")
        else:
            logger.error(f"❌ 聚合失败: {result.get('error')}")

    except Exception as e:
        logger.error(f"❌ 聚合任务执行失败: {e}", exc_info=True)


async def run_scheduler(hourly_interval: int = 3600, daily_hour: int = 2):
    """
    启动定时聚合调度器

    Args:
        hourly_interval: 小时任务间隔（秒），默认1小时
        daily_hour: 每天执行天级任务的小时（UTC），默认2点
    """
    logger.info("=" * 60)
    logger.info("启动信号统计聚合调度器")
    logger.info("=" * 60)
    logger.info("配置:")
    logger.info(f"  - 小时间隔: {hourly_interval}秒 ({hourly_interval//60}分钟)")
    logger.info(f"  - 天级小时: {daily_hour}:00 (UTC)")
    logger.info("=" * 60)

    scheduler = MetricsScheduler()

    try:
        await scheduler.start(hourly_interval=hourly_interval, daily_hour=daily_hour)
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭调度器...")
        await scheduler.stop()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="信号监控统计聚合任务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 手动运行一次聚合
  python scripts/runtime/run_signal_aggregation.py

  # 启动定时调度器（每30分钟执行一次小时聚合）
  python scripts/runtime/run_signal_aggregation.py --scheduler --interval 1800

  # 启动定时调度器（自定义配置）
  python scripts/runtime/run_signal_aggregation.py --scheduler --interval 3600 --daily-hour 3
        """
    )

    parser.add_argument(
        '--scheduler',
        action='store_true',
        help='启动定时调度器（默认只运行一次聚合）'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=3600,
        help='小时任务间隔（秒），默认3600（1小时）'
    )

    parser.add_argument(
        '--daily-hour',
        type=int,
        default=2,
        help='每天执行天级任务的小时（UTC），默认2点'
    )

    args = parser.parse_args()

    # 确保logs目录存在
    Path("logs").mkdir(exist_ok=True)

    if args.scheduler:
        # 启动定时调度器
        asyncio.run(run_scheduler(args.interval, args.daily_hour))
    else:
        # 手动运行一次聚合
        asyncio.run(run_hourly_aggregation())


if __name__ == "__main__":
    main()
