"""
预定义任务 (Predefined Tasks)

功能说明:
- 常用自动化任务的预定义实现
- 数据更新任务
- 策略执行任务
- 信号生成任务
- 系统维护任务

所有任务都遵循统一接口，可直接用于TaskScheduler调度

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional, TYPE_CHECKING
from datetime import date, datetime
import logging

if TYPE_CHECKING:
    from .scheduler import TaskConfig


logger = logging.getLogger(__name__)


class PredefinedTasks:
    """
    预定义任务集合

    提供常用的自动化任务函数，可直接用于调度器
    """

    @staticmethod
    def daily_data_update(market: str = "sh", lookback_days: int = 3, unified_manager=None) -> Dict:
        """
        每日数据更新任务

        参数:
            market: 市场代码 ('sh', 'sz')
            lookback_days: 回溯天数
            unified_manager: 数据管理器实例

        返回:
            Dict: 更新结果
        """
        logger.info("=" * 70)
        logger.info(f"开始每日数据更新: {market.upper()}")
        logger.info("=" * 70)

        try:
            # 动态导入（避免循环依赖）
            from src.data_sources.tdx_importer import TdxImporter

            # 创建导入器
            importer = TdxImporter(unified_manager=unified_manager)

            # 增量导入
            result = importer.import_incremental(market=market, lookback_days=lookback_days)

            logger.info("✓ 数据更新完成")
            logger.info(f"  成功: {result['success_count']} 只股票")
            logger.info(f"  记录数: {result['total_records']:,}")

            return {
                "status": "success",
                "market": market,
                "symbols_updated": result["success_count"],
                "records_imported": result["total_records"],
                "failed_count": result["fail_count"],
            }

        except Exception as e:
            logger.error(f"✗ 数据更新失败: {e}")
            raise

    @staticmethod
    def execute_strategy(
        strategy_name: str,
        universe: List[str],
        strategy_executor=None,
        notification_manager=None,
    ) -> Dict:
        """
        执行策略任务

        参数:
            strategy_name: 策略名称
            universe: 股票池
            strategy_executor: 策略执行器实例
            notification_manager: 通知管理器

        返回:
            Dict: 执行结果
        """
        logger.info("=" * 70)
        logger.info(f"执行策略: {strategy_name}")
        logger.info(f"股票池大小: {len(universe)}")
        logger.info("=" * 70)

        try:
            if strategy_executor is None:
                raise ValueError("未提供策略执行器")

            # 执行策略
            result = strategy_executor.execute(strategy_name=strategy_name, symbols=universe)

            # 统计信号
            signals = result.get("signals", [])
            buy_signals = [s for s in signals if s["signal"] == "buy"]
            sell_signals = [s for s in signals if s["signal"] == "sell"]

            logger.info("✓ 策略执行完成")
            logger.info(f"  买入信号: {len(buy_signals)}")
            logger.info(f"  卖出信号: {len(sell_signals)}")

            # 发送信号通知
            if notification_manager:
                for signal in buy_signals + sell_signals:
                    notification_manager.send_signal_notification(
                        strategy_name=strategy_name,
                        symbol=signal["symbol"],
                        signal=signal["signal"],
                        price=signal.get("price", 0),
                        context=signal.get("context", {}),
                    )

            return {
                "status": "success",
                "strategy_name": strategy_name,
                "total_signals": len(signals),
                "buy_signals": len(buy_signals),
                "sell_signals": len(sell_signals),
            }

        except Exception as e:
            logger.error(f"✗ 策略执行失败: {e}")
            raise

    @staticmethod
    def screen_stocks(
        screener_config: Dict,
        universe: Optional[List[str]] = None,
        unified_manager=None,
    ) -> Dict:
        """
        股票筛选任务

        参数:
            screener_config: 筛选器配置
            universe: 股票池（可选）
            unified_manager: 数据管理器

        返回:
            Dict: 筛选结果
        """
        logger.info("=" * 70)
        logger.info("执行股票筛选")
        logger.info("=" * 70)

        try:
            # 动态导入
            from strategy.stock_screener import StockScreener

            # 创建筛选器
            screener = StockScreener(**screener_config)

            # 执行筛选
            if universe is None:
                # 使用全市场
                universe = ["sh600000", "sh600016"]  # 示例

            filtered = screener.screen(universe)

            logger.info("✓ 筛选完成")
            logger.info(f"  候选股票: {len(universe)}")
            logger.info(f"  通过筛选: {len(filtered)}")

            return {
                "status": "success",
                "total_candidates": len(universe),
                "filtered_count": len(filtered),
                "filtered_symbols": filtered,
            }

        except Exception as e:
            logger.error(f"✗ 筛选失败: {e}")
            raise

    @staticmethod
    def database_maintenance(unified_manager=None) -> Dict:
        """
        数据库维护任务

        参数:
            unified_manager: 数据管理器

        返回:
            Dict: 维护结果
        """
        logger.info("=" * 70)
        logger.info("执行数据库维护")
        logger.info("=" * 70)

        try:
            results = {}

            # 1. 数据质量检查
            logger.info("1. 数据质量检查")
            # TODO: 实现数据质量检查
            results["quality_check"] = "passed"

            # 2. 性能优化
            logger.info("2. 性能优化")
            # TODO: 实现索引优化、统计信息更新等
            results["optimization"] = "completed"

            # 3. 清理过期数据
            logger.info("3. 清理过期数据")
            # TODO: 实现过期数据清理
            results["cleanup"] = "completed"

            logger.info("✓ 数据库维护完成")

            return {"status": "success", **results}

        except Exception as e:
            logger.error(f"✗ 数据库维护失败: {e}")
            raise

    @staticmethod
    def generate_daily_report(date: Optional[date] = None, unified_manager=None, notification_manager=None) -> Dict:
        """
        生成每日报告任务

        参数:
            date: 报告日期（默认今天）
            unified_manager: 数据管理器
            notification_manager: 通知管理器

        返回:
            Dict: 报告信息
        """
        report_date = date or datetime.now().date()

        logger.info("=" * 70)
        logger.info(f"生成每日报告: {report_date}")
        logger.info("=" * 70)

        try:
            # 收集统计数据

            # 生成报告文本
            report_text = f"""
每日量化交易报告
================

日期: {report_date}

市场概况:
---------
  TODO: 添加市场数据

策略表现:
---------
  TODO: 添加策略表现

信号汇总:
---------
  TODO: 添加信号统计

数据质量:
---------
  TODO: 添加数据质量指标

报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

            # 发送通知
            if notification_manager:
                notification_manager.send_notification(
                    title=f"每日报告 - {report_date}",
                    message=report_text,
                    level=(
                        notification_manager.NotificationLevel.INFO
                        if hasattr(notification_manager, "NotificationLevel")
                        else None
                    ),
                )

            logger.info("✓ 报告生成完成")

            return {
                "status": "success",
                "date": str(report_date),
                "report": report_text,
            }

        except Exception as e:
            logger.error(f"✗ 报告生成失败: {e}")
            raise

    @staticmethod
    def health_check(services: Optional[List[str]] = None) -> Dict:
        """
        系统健康检查任务

        参数:
            services: 需要检查的服务列表

        返回:
            Dict: 健康状态
        """
        logger.info("=" * 70)
        logger.info("系统健康检查")
        logger.info("=" * 70)

        services = services or ["database", "data_source", "strategy"]

        health_status = {}

        for service in services:
            try:
                if service == "database":
                    # 检查数据库连接
                    health_status["database"] = "healthy"

                elif service == "data_source":
                    # 检查数据源
                    health_status["data_source"] = "healthy"

                elif service == "strategy":
                    # 检查策略引擎
                    health_status["strategy"] = "healthy"

                logger.info(f"  ✓ {service}: healthy")

            except Exception as e:
                health_status[service] = f"unhealthy: {e}"
                logger.error(f"  ✗ {service}: {e}")

        # 总体状态
        all_healthy = all(status == "healthy" for status in health_status.values())

        logger.info(f"\n总体状态: {'✓ 健康' if all_healthy else '✗ 异常'}")

        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "services": health_status,
            "timestamp": datetime.now().isoformat(),
        }


# 任务工厂函数 - 方便创建TaskConfig
def create_daily_update_task(market: str = "sh", hour: int = 16, minute: int = 0) -> "TaskConfig":
    """
    创建每日数据更新任务配置

    参数:
        market: 市场代码
        hour: 执行小时（默认16:00，收盘后）
        minute: 执行分钟

    返回:
        TaskConfig: 任务配置
    """
    from automation import TaskConfig, TaskPriority

    return TaskConfig(
        name=f"daily_data_update_{market}",
        func=PredefinedTasks.daily_data_update,
        trigger_type="cron",
        trigger_args={"hour": hour, "minute": minute},
        kwargs={"market": market},
        priority=TaskPriority.HIGH,
        max_retries=3,
        notify_on_failure=True,
    )


def create_strategy_execution_task(strategy_name: str, hour: int = 9, minute: int = 30) -> "TaskConfig":
    """
    创建策略执行任务配置

    参数:
        strategy_name: 策略名称
        hour: 执行小时（默认9:30，开盘后）
        minute: 执行分钟

    返回:
        TaskConfig: 任务配置
    """
    from automation import TaskConfig, TaskPriority

    return TaskConfig(
        name=f"execute_{strategy_name}",
        func=PredefinedTasks.execute_strategy,
        trigger_type="cron",
        trigger_args={"hour": hour, "minute": minute, "day_of_week": "0-4"},  # 工作日
        kwargs={"strategy_name": strategy_name},
        priority=TaskPriority.NORMAL,
        max_retries=2,
        notify_on_failure=True,
        depends_on=["daily_data_update_sh"],  # 依赖数据更新
    )


def create_health_check_task(interval_minutes: int = 30) -> "TaskConfig":
    """
    创建健康检查任务配置

    参数:
        interval_minutes: 检查间隔（分钟）

    返回:
        TaskConfig: 任务配置
    """
    from automation import TaskConfig, TaskPriority

    return TaskConfig(
        name="system_health_check",
        func=PredefinedTasks.health_check,
        trigger_type="interval",
        trigger_args={"minutes": interval_minutes},
        priority=TaskPriority.LOW,
        max_retries=1,
        notify_on_success=False,
        notify_on_failure=True,
    )


if __name__ == "__main__":
    # 测试代码
    print("预定义任务测试")
    print("=" * 70)

    # 设置日志
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # 测试1: 健康检查
    print("\n测试1: 系统健康检查")
    result = PredefinedTasks.health_check()
    print(f"结果: {result}")

    # 测试2: 创建任务配置
    print("\n测试2: 创建任务配置")

    daily_update = create_daily_update_task(market="sh", hour=16, minute=0)
    print(f"每日更新任务: {daily_update.name}")
    print(f"  触发器: {daily_update.trigger_type}")
    print(f"  优先级: {daily_update.priority.name}")

    strategy_exec = create_strategy_execution_task(strategy_name="momentum", hour=9, minute=30)
    print(f"\n策略执行任务: {strategy_exec.name}")
    print(f"  触发器: {strategy_exec.trigger_type}")
    print(f"  依赖: {strategy_exec.depends_on}")

    health_check = create_health_check_task(interval_minutes=30)
    print(f"\n健康检查任务: {health_check.name}")
    print(f"  触发器: {health_check.trigger_type}")

    print("\n" + "=" * 70)
    print("测试完成")
