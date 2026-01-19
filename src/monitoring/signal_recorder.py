"""
Signal Recorder Service
信号记录服务

负责将信号生成和执行结果持久化到监控数据库。
连接信号生成服务和监控数据库，记录完整信号生命周期。
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SignalRecord:
    """信号记录数据模型"""

    strategy_id: str
    symbol: str
    signal_type: str  # BUY/SELL/HOLD
    indicator_count: int = 1
    execution_time_ms: float = 0.0
    gpu_used: bool = False
    gpu_latency_ms: float = 0.0
    status: str = "generated"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SignalExecutionRecord:
    """信号执行结果记录"""

    signal_id: int
    executed: bool = True
    executed_at: Optional[datetime] = None
    execution_price: float = 0.0
    profit_loss: float = 0.0
    profit_loss_percent: float = 0.0
    mae: float = 0.0  # Maximum Adverse Excursion
    mfe: float = 0.0  # Maximum Favorable Excursion


class SignalRecorder:
    """
    信号记录器 - 负责将信号持久化到监控数据库

    功能：
    - 记录信号生成（signal_records 表）
    - 记录信号执行结果（signal_execution_results 表）
    - 记录信号推送日志（signal_push_logs 表）
    - 批量插入优化
    - 异常处理和重试

    使用示例：
        ```python
        from src.monitoring.signal_recorder import SignalRecorder

        recorder = SignalRecorder()

        # 记录信号生成
        signal_id = await recorder.record_signal(
            strategy_id="macd_strategy",
            symbol="600519.SH",
            signal_type="BUY",
            execution_time_ms=45.5
        )

        # 记录执行结果
        await recorder.record_execution(
            signal_id=signal_id,
            executed=True,
            execution_price=1850.0,
            profit_loss=125.50
        )
        ```
    """

    def __init__(self):
        """初始化信号记录器"""
        self._pg_pool = None
        self._batch_buffer: List[SignalRecord] = []
        self._batch_size = 100  # 批量插入阈值

    async def _get_pg_pool(self):
        """获取 PostgreSQL 连接池（懒加载）"""
        if self._pg_pool is None:
            try:
                from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

                pg = get_postgres_async()
                if not pg.is_connected():
                    logger.warning("监控数据库未连接，信号记录功能将不可用")
                    return None
                self._pg_pool = pg
            except Exception as e:
                logger.error(f"无法获取监控数据库连接: {e}")
                return None
        return self._pg_pool

    async def record_signal(
        self,
        strategy_id: str,
        symbol: str,
        signal_type: str,
        indicator_count: int = 1,
        execution_time_ms: float = 0.0,
        gpu_used: bool = False,
        gpu_latency_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[int]:
        """
        记录单个信号生成

        Args:
            strategy_id: 策略ID
            symbol: 标的代码
            signal_type: 信号类型 (BUY/SELL/HOLD)
            indicator_count: 使用的指标数量
            execution_time_ms: 执行时间（毫秒）
            gpu_used: 是否使用GPU
            gpu_latency_ms: GPU计算延迟（毫秒）
            metadata: 额外元数据（JSONB）

        Returns:
            signal_id (成功时) 或 None (失败时)
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return None

        try:
            async with pg.pool.acquire() as conn:
                signal_id = await conn.fetchval(
                    """
                    INSERT INTO signal_records
                    (strategy_id, symbol, signal_type, indicator_count,
                     execution_time_ms, gpu_used, gpu_latency_ms, status, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING id
                    """,
                    strategy_id,
                    symbol,
                    signal_type,
                    indicator_count,
                    execution_time_ms,
                    gpu_used,
                    gpu_latency_ms,
                    "generated",
                    metadata,
                )

            logger.debug(
                f"记录信号生成: strategy_id={strategy_id}, symbol={symbol}, "
                f"signal_type={signal_type}, signal_id={signal_id}"
            )
            return signal_id

        except Exception as e:
            logger.error(f"记录信号失败: {e}", exc_info=True)
            return None

    async def record_signal_batch(
        self,
        signals: List[SignalRecord],
    ) -> List[int]:
        """
        批量记录信号生成（性能优化）

        Args:
            signals: 信号记录列表

        Returns:
            signal_id 列表
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return []

        signal_ids = []
        try:
            async with pg.pool.acquire() as conn:
                async with conn.transaction():
                    for signal in signals:
                        signal_id = await conn.fetchval(
                            """
                            INSERT INTO signal_records
                            (strategy_id, symbol, signal_type, indicator_count,
                             execution_time_ms, gpu_used, gpu_latency_ms, status, metadata)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                            RETURNING id
                            """,
                            signal.strategy_id,
                            signal.symbol,
                            signal.signal_type,
                            signal.indicator_count,
                            signal.execution_time_ms,
                            signal.gpu_used,
                            signal.gpu_latency_ms,
                            signal.status,
                            signal.metadata,
                        )
                        signal_ids.append(signal_id)

            logger.info(f"批量记录 {len(signal_ids)} 个信号")
            return signal_ids

        except Exception as e:
            logger.error(f"批量记录信号失败: {e}", exc_info=True)
            return []

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
            mae: 最大不利偏移
            mfe: 最大有利偏移

        Returns:
            是否成功
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return False

        try:
            async with pg.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO signal_execution_results
                    (signal_id, executed, executed_at, execution_price,
                     profit_loss, profit_loss_percent, mae, mfe)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    signal_id,
                    executed,
                    executed_at or datetime.now(),
                    execution_price,
                    profit_loss,
                    profit_loss_percent,
                    mae,
                    mfe,
                )

            logger.debug(f"记录执行结果: signal_id={signal_id}, executed={executed}")
            return True

        except Exception as e:
            logger.error(f"记录执行结果失败: {e}", exc_info=True)
            return False

    async def record_push(
        self,
        signal_id: int,
        channel: str,
        status: str,
        push_latency_ms: float = 0.0,
        retry_count: int = 0,
        error_message: str = "",
    ) -> bool:
        """
        记录信号推送日志

        Args:
            signal_id: 信号ID
            channel: 推送渠道 (websocket/email/sms/app)
            status: 推送状态 (success/failed/pending)
            push_latency_ms: 推送延迟（毫秒）
            retry_count: 重试次数
            error_message: 错误信息

        Returns:
            是否成功
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return False

        try:
            async with pg.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO signal_push_logs
                    (signal_id, channel, status, push_latency_ms, retry_count, error_message)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    signal_id,
                    channel,
                    status,
                    push_latency_ms,
                    retry_count,
                    error_message,
                )

            logger.debug(f"记录推送日志: signal_id={signal_id}, channel={channel}, status={status}")
            return True

        except Exception as e:
            logger.error(f"记录推送日志失败: {e}", exc_info=True)
            return False

    async def update_signal_status(
        self,
        signal_id: int,
        status: str,
    ) -> bool:
        """
        更新信号状态

        Args:
            signal_id: 信号ID
            status: 新状态 (generated/executed/cancelled/expired)

        Returns:
            是否成功
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return False

        try:
            async with pg.pool.acquire() as conn:
                await conn.execute(
                    "UPDATE signal_records SET status = $1 WHERE id = $2",
                    status,
                    signal_id,
                )

            logger.debug(f"更新信号状态: signal_id={signal_id}, status={status}")
            return True

        except Exception as e:
            logger.error(f"更新信号状态失败: {e}", exc_info=True)
            return False

    async def get_signal_by_id(
        self,
        signal_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        查询信号详情

        Args:
            signal_id: 信号ID

        Returns:
            信号详情字典 或 None
        """
        pg = await self._get_pg_pool()
        if pg is None:
            return None

        try:
            async with pg.pool.acquire() as conn:
                record = await conn.fetchrow(
                    """
                    SELECT * FROM signal_records
                    WHERE id = $1
                    """,
                    signal_id,
                )

            return dict(record) if record else None

        except Exception as e:
            logger.error(f"查询信号失败: {e}", exc_info=True)
            return None


# 单例实例
_recorder_instance: Optional[SignalRecorder] = None


def get_signal_recorder() -> SignalRecorder:
    """获取信号记录器单例"""
    global _recorder_instance
    if _recorder_instance is None:
        _recorder_instance = SignalRecorder()
    return _recorder_instance


__all__ = [
    "SignalRecorder",
    "SignalRecord",
    "SignalExecutionRecord",
    "get_signal_recorder",
]
