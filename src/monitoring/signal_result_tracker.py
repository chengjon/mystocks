"""
Signal Result Tracker Service
信号结果追踪服务

追踪信号执行后的盈亏情况，计算风险指标，更新策略健康状态。
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SignalStatus(Enum):
    """信号状态枚举"""

    GENERATED = "generated"  # 已生成
    EXECUTED = "executed"  # 已执行
    CANCELLED = "cancelled"  # 已取消
    EXPIRED = "expired"  # 已过期
    FAILED = "failed"  # 执行失败


@dataclass
class ExecutionResult:
    """执行结果数据模型"""

    signal_id: int
    executed: bool
    executed_at: datetime
    execution_price: float
    profit_loss: float = 0.0
    profit_loss_percent: float = 0.0
    mae: float = 0.0  # Maximum Adverse Excursion（最大不利偏移）
    mfe: float = 0.0  # Maximum Favorable Excursion（最大有利偏移）


class SignalResultTracker:
    """
    信号结果追踪器

    功能：
    - 记录信号执行结果（价格、盈亏）
    - 计算风险指标（MAE/MFE）
    - 更新策略健康状态
    - 自动计算信号准确率
    - 盈利比率统计

    使用示例：
        ```python
        from src.monitoring.signal_result_tracker import SignalResultTracker

        tracker = SignalResultTracker()

        # 记录执行结果
        await tracker.record_execution(
            signal_id=123,
            executed=True,
            execution_price=1850.0,
            profit_loss=125.50
        )
        ```
    """

    def __init__(self):
        """初始化结果追踪器"""
        self._pg_pool = None

    async def _get_pg_pool(self):
        """获取 PostgreSQL 连接池（懒加载）"""
        if self._pg_pool is None:
            try:
                from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

                pg = get_postgres_async()
                if not pg.is_connected():
                    logger.warning("监控数据库未连接，结果追踪功能将不可用")
                    return None
                self._pg_pool = pg
            except Exception as e:
                logger.error(f"无法获取监控数据库连接: {e}")
                return None
        return self._pg_pool

    async def record_execution(
        self,
        signal_id: int,
        executed: bool = True,
        executed_at: Optional[datetime] = None,
        execution_price: float = 0.0,
        profit_loss: float = 0.0,
        profit_loss_percent: float = 0.0,
        mae: float = 0.0,
        mfe: float = 0.0,
    ) -> bool:
        """
        记录信号执行结果

        Args:
            signal_id: 信号ID
            executed: 是否执行
            executed_at: 执行时间
            execution_price: 执行价格
            profit_loss: 盈亏金额
            profit_loss_percent: 盈亏百分比
            mae: 最大不利偏移（浮亏）
            mfe: 最大有利偏移（浮盈）

        Returns:
            是否成功
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return False

        try:
            from src.monitoring.signal_recorder import get_signal_recorder

            recorder = get_signal_recorder()
            success = await recorder.record_execution(
                signal_id=signal_id,
                executed=executed,
                executed_at=executed_at,
                execution_price=execution_price,
                profit_loss=profit_loss,
                profit_loss_percent=profit_loss_percent,
                mae=mae,
                mfe=mfe,
            )

            if success:
                # 更新信号状态
                await recorder.update_signal_status(
                    signal_id=signal_id,
                    status="executed" if executed else "failed",
                )

                # 更新 Prometheus 指标
                await self._update_prometheus_metrics(signal_id)

                logger.info(f"记录执行结果成功: signal_id={signal_id}, executed={executed}")
            return success

        except Exception as e:
            logger.error(f"记录执行结果失败: {e}", exc_info=True)
            return False

    async def _update_prometheus_metrics(self, signal_id: int) -> None:
        """更新 Prometheus 指标"""
        try:
            # 查询信号详情
            from src.monitoring.signal_recorder import get_signal_recorder

            recorder = get_signal_recorder()
            signal = await recorder.get_signal_by_id(signal_id)

            if signal is None:
                return

            strategy_id = signal["strategy_id"]
            signal_type = signal["signal_type"]

            # 更新信号准确率（基于盈亏）
            from src.monitoring.signal_metrics import update_signal_accuracy

            # 这里简化处理：盈亏为正则准确
            # 实际应该根据策略目标判断（例如：BUY信号应该价格上涨）
            await self._calculate_and_update_accuracy(strategy_id, signal_type)

        except Exception as e:
            logger.warning(f"更新 Prometheus 指标失败: {e}")

    async def _calculate_and_update_accuracy(
        self,
        strategy_id: str,
        signal_type: str,
        days: int = 7,
    ) -> None:
        """
        计算并更新信号准确率

        Args:
            strategy_id: 策略ID
            signal_type: 信号类型
            days: 统计天数
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return

        try:
            from src.monitoring.signal_metrics import update_signal_accuracy

            # 查询最近N天的执行结果
            async with pg.pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE profit_loss > 0) as profitable,
                        COUNT(*) FILTER (WHERE executed = true) as executed
                    FROM signal_execution_results ser
                    JOIN signal_records sr ON ser.signal_id = sr.id
                    WHERE sr.strategy_id = $1
                      AND sr.signal_type = $2
                      AND sr.generated_at > CURRENT_TIMESTAMP - INTERVAL '%s days'
                    """
                    % days,
                    strategy_id,
                    signal_type,
                )

            if row and row["executed"] > 0:
                accuracy = (row["profitable"] / row["executed"]) * 100
                update_signal_accuracy(
                    strategy_id=strategy_id,
                    signal_type=signal_type,
                    accuracy_percentage=accuracy,
                )
                logger.debug(
                    f"更新准确率: strategy_id={strategy_id}, signal_type={signal_type}, " f"accuracy={accuracy:.2f}%"
                )

        except Exception as e:
            logger.warning(f"计算准确率失败: {e}")

    async def calculate_profit_ratio(
        self,
        strategy_id: str,
        time_window: str = "1d",
    ) -> float:
        """
        计算盈利比率

        Args:
            strategy_id: 策略ID
            time_window: 时间窗口 (1d/7d/30d)

        Returns:
            盈利比率（0-100）
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return 0.0

        try:
            # 映射时间窗口到SQL INTERVAL
            interval_map = {
                "1d": "1 day",
                "7d": "7 days",
                "30d": "30 days",
            }
            interval_str = interval_map.get(time_window, "1 day")

            async with pg.pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT
                        COUNT(*) FILTER (WHERE profit_loss > 0) as profitable,
                        COUNT(*) as total
                    FROM signal_execution_results ser
                    JOIN signal_records sr ON ser.signal_id = sr.id
                    WHERE sr.strategy_id = $1
                      AND sr.generated_at > CURRENT_TIMESTAMP - INTERVAL '%s'
                    """
                    % interval_str,
                    strategy_id,
                )

            if row and row["total"] > 0:
                ratio = (row["profitable"] / row["total"]) * 100
                return ratio

            return 0.0

        except Exception as e:
            logger.error(f"计算盈利比率失败: {e}", exc_info=True)
            return 0.0

    async def update_strategy_health_status(
        self,
        strategy_id: str,
    ) -> Dict[str, Any]:
        """
        更新策略健康状态

        Args:
            strategy_id: 策略ID

        Returns:
            健康状态字典
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return {}

        try:
            from src.monitoring.signal_metrics import update_strategy_health

            # 计算最近1小时的指标
            async with pg.pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT
                        COUNT(*) FILTER (WHERE executed = true) as executed_count,
                        COUNT(*) FILTER (WHERE profit_loss > 0) as profitable_count,
                        COUNT(*) as total_count,
                        AVG(execution_time_ms) as avg_latency
                    FROM signal_records sr
                    LEFT JOIN signal_execution_results ser ON sr.id = ser.signal_id
                    WHERE sr.strategy_id = $1
                      AND sr.generated_at > CURRENT_TIMESTAMP - INTERVAL '1 hour'
                    """,
                    strategy_id,
                )

            if row is None or row["total_count"] == 0:
                return {"status": "no_data"}

            # 计算指标
            success_rate = (row["executed_count"] / row["total_count"]) * 100 if row["total_count"] > 0 else 0
            accuracy = (row["profitable_count"] / row["executed_count"]) * 100 if row["executed_count"] > 0 else 0

            # 判断健康状态
            # 1=healthy, 0=degraded, -1=unhealthy
            if success_rate >= 80 and accuracy >= 70:
                health_status = 1
                status_text = "healthy"
            elif success_rate >= 60 and accuracy >= 50:
                health_status = 0
                status_text = "degraded"
            else:
                health_status = -1
                status_text = "unhealthy"

            # 更新 Prometheus 指标
            update_strategy_health(strategy_id=strategy_id, status=health_status)

            # 记录到数据库（持久化）
            await conn.execute(
                """
                INSERT INTO strategy_health
                (strategy_id, health_status, signal_success_rate, signal_accuracy, avg_execution_time_ms)
                VALUES ($1, $2, $3, $4, $5)
                """,
                strategy_id,
                health_status,
                success_rate,
                accuracy,
                row["avg_latency"] or 0,
            )

            return {
                "strategy_id": strategy_id,
                "health_status": health_status,
                "status_text": status_text,
                "success_rate": success_rate,
                "accuracy": accuracy,
                "avg_latency_ms": row["avg_latency"] or 0,
            }

        except Exception as e:
            logger.error(f"更新策略健康状态失败: {e}", exc_info=True)
            return {}

    async def get_signal_performance_summary(
        self,
        strategy_id: str,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        获取信号性能摘要

        Args:
            strategy_id: 策略ID
            days: 统计天数

        Returns:
            性能摘要字典
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return {}

        try:
            async with pg.pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT
                        COUNT(*) as total_signals,
                        COUNT(*) FILTER (WHERE executed = true) as executed_signals,
                        COUNT(*) FILTER (WHERE profit_loss > 0) as profitable_signals,
                        COALESCE(SUM(profit_loss), 0) as total_profit_loss,
                        AVG(CASE WHEN profit_loss > 0 THEN profit_loss_percent ELSE 0 END) as avg_profit_percent,
                        AVG(CASE WHEN profit_loss < 0 THEN profit_loss_percent ELSE 0 END) as avg_loss_percent
                    FROM signal_records sr
                    LEFT JOIN signal_execution_results ser ON sr.id = ser.signal_id
                    WHERE sr.strategy_id = $1
                      AND sr.generated_at > CURRENT_TIMESTAMP - INTERVAL '%s days'
                    """
                    % days,
                    strategy_id,
                )

            if row is None:
                return {}

            return {
                "strategy_id": strategy_id,
                "period_days": days,
                "total_signals": row["total_signals"] or 0,
                "executed_signals": row["executed_signals"] or 0,
                "profitable_signals": row["profitable_signals"] or 0,
                "total_profit_loss": float(row["total_profit_loss"] or 0),
                "avg_profit_percent": float(row["avg_profit_percent"] or 0),
                "avg_loss_percent": float(row["avg_loss_percent"] or 0),
            }

        except Exception as e:
            logger.error(f"获取性能摘要失败: {e}", exc_info=True)
            return {}


# 单例实例
_tracker_instance: Optional[SignalResultTracker] = None


def get_signal_result_tracker() -> SignalResultTracker:
    """获取结果追踪器单例"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = SignalResultTracker()
    return _tracker_instance


__all__ = [
    "SignalResultTracker",
    "SignalStatus",
    "ExecutionResult",
    "get_signal_result_tracker",
]
