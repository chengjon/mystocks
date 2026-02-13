"""
Signal Metrics Aggregation Task

信号指标聚合任务 - 定期计算和更新信号统计指标。

功能：
- 从数据库读取信号执行结果
- 计算准确率、成功率、盈利比率
- 更新Prometheus Gauge指标
- 支持定时任务调度

使用方式：
```python
# 作为定时任务运行
from src.monitoring.signal_aggregation_task import SignalMetricsAggregator

aggregator = SignalMetricsAggregator()
aggregator.run_hourly()  # 每小时执行
aggregator.run_daily()    # 每天执行
```

作者: MyStocks量化交易团队
创建时间: 2026-01-08
版本: 1.0.0
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)

try:
    from src.monitoring.signal_metrics import (
        update_profit_ratio,
        update_signal_accuracy,
        update_signal_success_rate,
        update_strategy_health,
    )

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    logger.warning("Signal metrics module not available")


@dataclass
class AggregationConfig:
    """聚合配置"""

    hourly_batch_size: int = 1000
    daily_batch_size: int = 10000
    accuracy_window_hours: int = 168  # 7天滑动窗口
    profit_window_hours: int = 720  # 30天窗口
    strategies_per_batch: int = 50


class SignalMetricsAggregator:
    """
    信号指标聚合器

    从数据库读取信号执行结果，计算统计指标并更新Prometheus。
    """

    def __init__(self, config: Optional[AggregationConfig] = None):
        self.config = config or AggregationConfig()
        self._last_run: Optional[datetime] = None

    async def run_hourly(self) -> Dict[str, Any]:
        """
        运行小时级聚合任务

        计算：
        - 过去1小时的信号生成统计
        - 活跃信号数量
        - 策略健康状态
        """
        start_time = datetime.now(timezone.utc)
        logger.info("开始小时级信号指标聚合")

        results = {
            "task_type": "hourly",
            "start_time": start_time.isoformat(),
            "strategies_processed": 0,
            "signals_processed": 0,
            "errors": [],
        }

        try:
            # 获取所有活跃策略
            strategies = await self._get_active_strategies()

            for strategy in strategies:
                try:
                    await self._aggregate_hourly(strategy)
                    results["strategies_processed"] += 1
                except Exception as e:
                    error_msg = f"策略 {strategy.get('id', 'unknown')} 聚合失败: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

            # 更新全局健康状态
            await self._update_global_health()

            results["status"] = "success"
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(f"聚合任务失败: {e}")
            logger.error("小时级聚合任务失败: %(e)s")

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        results["elapsed_seconds"] = elapsed
        results["end_time"] = datetime.now(timezone.utc).isoformat()

        logger.info("小时级聚合完成: 处理 {results['strategies_processed']} 个策略, 耗时 {elapsed:.2f}秒")

        return results

    async def run_daily(self) -> Dict[str, Any]:
        """
        运行天级聚合任务

        计算：
        - 过去24小时的准确率
        - 过去30天的盈利比率
        - 策略性能排名
        """
        start_time = datetime.now(timezone.utc)
        logger.info("开始天级信号指标聚合")

        results = {
            "task_type": "daily",
            "start_time": start_time.isoformat(),
            "strategies_processed": 0,
            "signals_processed": 0,
            "accuracy_updates": 0,
            "profit_updates": 0,
            "errors": [],
        }

        try:
            strategies = await self._get_active_strategies()

            for strategy in strategies:
                try:
                    await self._aggregate_daily(strategy)
                    results["strategies_processed"] += 1
                except Exception as e:
                    error_msg = f"策略 {strategy.get('id', 'unknown')} 日聚合失败: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

            results["status"] = "success"
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(f"日级聚合任务失败: {e}")

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        results["elapsed_seconds"] = elapsed
        results["end_time"] = datetime.now(timezone.utc).isoformat()

        logger.info(
            f"天级聚合完成: 处理 {results['strategies_processed']} 个策略, "
            f"准确率更新 {results['accuracy_updates']} 次, "
            f"盈利比率更新 {results['profit_updates']} 次, "
            f"耗时 {elapsed:.2f}秒"
        )

        return results

    async def run_ondemand(
        self, strategy_ids: Optional[List[str]] = None, metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        按需运行聚合任务

        Args:
            strategy_ids: 策略ID列表（None表示所有策略）
            metrics: 要计算的指标列表（None表示所有）
        """
        start_time = datetime.now(timezone.utc)
        logger.info("开始按需聚合: 策略=%(strategy_ids)s, 指标=%(metrics)s")

        results = {
            "task_type": "ondemand",
            "start_time": start_time.isoformat(),
            "strategies_requested": len(strategy_ids) if strategy_ids else "all",
            "metrics_requested": metrics or ["all"],
            "strategies_processed": 0,
            "updates": 0,
        }

        try:
            if strategy_ids:
                strategies = await self._get_strategies_by_ids(strategy_ids)
            else:
                strategies = await self._get_active_strategies()

            for strategy in strategies:
                try:
                    updates = await self._aggregate_strategy(strategy, metrics)
                    results["updates"] += updates
                    results["strategies_processed"] += 1
                except Exception:
                    logger.error("策略 {strategy.get('id')} 按需聚合失败: %(e)s")

            results["status"] = "success"
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(str(e))

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        results["elapsed_seconds"] = elapsed
        results["end_time"] = datetime.now(timezone.utc).isoformat()

        return results

    async def _get_active_strategies(self) -> List[Dict[str, Any]]:
        """获取所有活跃策略"""
        try:
            from src.ml_strategy.strategy.signal_manager import SignalManager

            manager = SignalManager()

            stats = manager.get_manager_stats()
            return [{"id": "default", "name": "Default Strategy"}]
        except Exception:
            logger.warning("获取活跃策略失败: %(e)s")
            return []

    async def _get_strategies_by_ids(self, strategy_ids: List[str]) -> List[Dict[str, Any]]:
        """根据ID获取策略"""
        return [{"id": sid, "name": f"Strategy {sid}"} for sid in strategy_ids]

    async def _aggregate_hourly(self, strategy: Dict[str, Any]) -> None:
        """聚合小时级指标"""
        strategy_id = strategy.get("id", "unknown")

        try:
            # 获取过去1小时的信号
            signals = await self._get_signals(strategy_id=strategy_id, hours=1, limit=self.config.hourly_batch_size)

            if not signals:
                return

            # 计算统计
            signal_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}
            for sig in signals:
                sig_type = sig.get("signal_type", "HOLD")
                signal_counts[sig_type] = signal_counts.get(sig_type, 0) + 1

            total_signals = len(signals)

            # 更新指标
            if METRICS_AVAILABLE:
                for sig_type, count in signal_counts.items():
                    if count > 0:
                        percentage = (count / total_signals) * 100
                        update_signal_accuracy(strategy_id, sig_type, percentage)

            logger.debug("策略 %(strategy_id)s 小时聚合: BUY={signal_counts['BUY']}, SELL=%s")

        except Exception:
            logger.error("策略 %(strategy_id)s 小时聚合失败: %(e)s")
            raise

    async def _aggregate_daily(self, strategy: Dict[str, Any]) -> None:
        """聚合天级指标"""
        strategy_id = strategy.get("id", "unknown")

        try:
            # 获取过去24小时有结果的信号
            completed_signals = await self._get_completed_signals(
                strategy_id=strategy_id, hours=self.config.accuracy_window_hours, limit=self.config.daily_batch_size
            )

            if not completed_signals:
                return

            # 计算准确率
            total = len(completed_signals)
            profitable = sum(1 for s in completed_signals if s.get("profit_loss", 0) > 0)
            accuracy = (profitable / total * 100) if total > 0 else 0

            # 计算盈利比率
            profit_sum = sum(s.get("profit_loss", 0) for s in completed_signals)
            loss_sum = abs(sum(s.get("profit_loss", 0) for s in completed_signals if s.get("profit_loss", 0) < 0))
            profit_ratio = (profit_sum / (profit_sum + loss_sum + 0.001)) * 100

            # 更新指标
            if METRICS_AVAILABLE:
                update_signal_accuracy(strategy_id, "ALL", accuracy)
                update_signal_success_rate(strategy_id, "ALL", accuracy)
                update_profit_ratio(strategy_id, "1d", profit_ratio)

            logger.debug(
                "策略 %s 日聚合: 准确率=%.1f%%, 盈利比率=%.1f%%",
                strategy_id, accuracy, profit_ratio
            )

        except Exception:
            logger.error("策略 %(strategy_id)s 日聚合失败: %(e)s")
            raise

    async def _aggregate_strategy(self, strategy: Dict[str, Any], metrics: Optional[List[str]] = None) -> int:
        """聚合单个策略的所有或指定指标"""
        strategy_id = strategy.get("id", "unknown")
        update_count = 0

        if not metrics or "accuracy" in metrics:
            await self._aggregate_daily(strategy)
            update_count += 1

        if not metrics or "health" in metrics:
            health = await self._check_strategy_health(strategy_id)
            if METRICS_AVAILABLE:
                update_strategy_health(strategy_id, 1 if health["healthy"] else 0)
            update_count += 1

        return update_count

    async def _get_signals(self, strategy_id: str, hours: int, limit: int = 1000) -> List[Dict[str, Any]]:
        """获取信号数据"""
        try:
            from src.ml_strategy.strategy.signal_manager import SignalManager

            manager = SignalManager()

            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(hours=hours)

            signals = manager.query_signals(
                strategy_id=int(strategy_id) if strategy_id.isdigit() else 1,
                start_date=start_date.date(),
                end_date=end_date.date(),
                limit=limit,
            )

            if hasattr(signals, "to_dict"):
                return signals.to_dict("records")
            return signals if isinstance(signals, list) else []

        except Exception:
            logger.debug("获取信号数据失败: %(e)s")
            return []

    async def _get_completed_signals(self, strategy_id: str, hours: int, limit: int = 1000) -> List[Dict[str, Any]]:
        """获取已完成的信号（有盈亏结果）"""
        signals = await self._get_signals(strategy_id, hours, limit)
        return [s for s in signals if s.get("profit_loss") is not None]

    async def _check_strategy_health(self, strategy_id: str) -> Dict[str, Any]:
        """检查策略健康状态"""
        try:
            recent_signals = await self._get_signals(strategy_id, hours=1, limit=10)

            if not recent_signals:
                return {"healthy": True, "reason": "no_signals"}

            # 检查是否有执行失败的信号
            failed = sum(1 for s in recent_signals if s.get("status") == "failed")

            if failed > len(recent_signals) * 0.3:
                return {"healthy": False, "reason": "high_failure_rate"}

            return {"healthy": True, "reason": "ok"}

        except Exception as e:
            return {"healthy": False, "reason": str(e)}

    async def _update_global_health(self) -> None:
        """更新全局健康状态"""
        if METRICS_AVAILABLE:
            # 这里可以添加全局健康检查逻辑
            pass


class MetricsScheduler:
    """
    指标聚合调度器

    支持定时调度聚合任务。
    """

    def __init__(self):
        self._hourly_task: Optional[SignalMetricsAggregator] = None
        self._daily_task: Optional[SignalMetricsAggregator] = None
        self._running = False

    async def start(self, hourly_interval: int = 3600, daily_hour: int = 2) -> None:
        """
        启动调度器

        Args:
            hourly_interval: 小时任务间隔（秒），默认1小时
            daily_hour: 每天执行天级任务的小时（UTC），默认2点
        """
        self._running = True
        self._hourly_task = SignalMetricsAggregator()
        self._daily_task = SignalMetricsAggregator()

        logger.info("启动指标聚合调度器: 小时间隔=%(hourly_interval)ss, 天级小时=%(daily_hour)s")

        while self._running:
            try:
                now = datetime.now(timezone.utc)

                # 执行小时级任务
                await self._hourly_task.run_hourly()

                # 检查是否需要执行天级任务
                if now.hour == daily_hour and now.minute < 5:
                    logger.info("执行每日聚合任务")
                    await self._daily_task.run_daily()

            except Exception:
                logger.error("调度任务执行失败: %(e)s")

            await asyncio.sleep(60)  # 每分钟检查一次

    async def stop(self) -> None:
        """停止调度器"""
        self._running = False
        logger.info("指标聚合调度器已停止")


# ============================================================================
# 数据库统计聚合（新增）
# ============================================================================


class SignalStatisticsAggregator:
    """
    信号数据库统计聚合器

    负责将信号统计数据聚合到 signal_statistics_hourly 表。
    与 SignalMetricsAggregator 配合使用：
    - SignalMetricsAggregator: 更新 Prometheus 指标
    - SignalStatisticsAggregator: 更新数据库统计表
    """

    def __init__(self):
        """初始化统计聚合器"""
        self._pg_pool = None

    async def _get_pg_pool(self):
        """获取 PostgreSQL 连接池（懒加载）"""
        if self._pg_pool is None:
            try:
                from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

                pg = get_postgres_async()
                if not pg.is_connected():
                    logger.warning("监控数据库未连接，统计聚合功能将不可用")
                    return None
                self._pg_pool = pg
            except Exception:
                logger.error("无法获取监控数据库连接: %(e)s")
                return None
        return self._pg_pool

    async def aggregate_hourly_statistics(
        self,
        hours_back: int = 2,
    ) -> Dict[str, Any]:
        """
        聚合小时统计数据

        Args:
            hours_back: 聚合最近多少小时的数据

        Returns:
            聚合结果字典
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return {"success": False, "error": "数据库未连接"}

        start_time = datetime.now()
        result = {
            "success": False,
            "hours_back": hours_back,
            "aggregated_count": 0,
            "cleanup_count": 0,
            "error": None,
            "start_time": start_time.isoformat(),
        }

        try:
            # 1. 执行聚合
            async with pg.pool.acquire() as conn:
                aggregated_count = await conn.fetchval(
                    "SELECT aggregate_all_strategies_statistics($1)",
                    hours_back,
                )

            result["aggregated_count"] = aggregated_count or 0
            logger.info("数据库统计聚合完成: {result['aggregated_count']} 条记录")

            # 2. 清理旧数据（90天前）
            cleanup_count = await conn.fetchval("SELECT cleanup_old_signal_statistics()")
            result["cleanup_count"] = cleanup_count or 0

            result["success"] = True
            result["duration_seconds"] = (datetime.now() - start_time).total_seconds()

        except Exception as e:
            logger.error("数据库统计聚合失败: {e}", exc_info=True)
            result["error"] = str(e)

        return result

    async def aggregate_strategy_hour(
        self,
        strategy_id: str,
        hour_timestamp: datetime,
    ) -> bool:
        """
        聚合单个策略的单小时数据

        Args:
            strategy_id: 策略ID
            hour_timestamp: 小时时间戳

        Returns:
            是否成功
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return False

        try:
            async with pg.pool.acquire() as conn:
                success = await conn.fetchval(
                    "SELECT aggregate_signal_statistics($1, $2)",
                    strategy_id,
                    hour_timestamp,
                )

            return bool(success)

        except Exception:
            logger.error("聚合策略 {strategy_id} 失败: {e}", exc_info=True)
            return False

    async def get_recent_statistics(
        self,
        strategy_id: str,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        """
        获取最近的统计数据

        Args:
            strategy_id: 策略ID
            hours: 查询最近多少小时

        Returns:
            统计数据列表
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return []

        try:
            async with pg.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT * FROM signal_statistics_hourly
                    WHERE strategy_id = $1
                      AND hour_timestamp >= NOW() - INTERVAL '%s hours'
                    ORDER BY hour_timestamp DESC
                    """
                    % hours,
                    strategy_id,
                )

            return [dict(row) for row in rows]

        except Exception:
            logger.error("获取统计数据失败: {e}", exc_info=True)
            return []


# ============================================================================
# 便捷函数和CLI入口
# ============================================================================


def run_aggregation(task_type: str = "hourly") -> Dict[str, Any]:
    """
    运行聚合任务（同步入口）

    Args:
        task_type: 任务类型 (hourly/daily/ondemand)

    Returns:
        任务执行结果
    """
    import asyncio

    aggregator = SignalMetricsAggregator()

    if task_type == "hourly":
        return asyncio.run(aggregator.run_hourly())
    elif task_type == "daily":
        return asyncio.run(aggregator.run_daily())
    else:
        return asyncio.run(aggregator.run_ondemand())


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    task_type = sys.argv[1] if len(sys.argv) > 1 else "hourly"
    result = run_aggregation(task_type)
    print(f"聚合任务完成: {result['status']}")
    print(f"处理策略数: {result.get('strategies_processed', 0)}")
    print(f"耗时: {result.get('elapsed_seconds', 0):.2f}秒")
