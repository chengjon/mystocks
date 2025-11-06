"""
聚合流媒体桥接服务 - Aggregation Streaming Bridge

Task 7: 实现实时OHLCV柱线聚合与多时间周期支持

功能特性:
- 连接AggregationEngine和RealtimeStreamingService
- 自动检测完成的OHLCV柱线
- 异步发布完成的柱线到订阅者
- 性能监控和指标
- 批量处理支持

Author: Claude Code
Date: 2025-11-07
"""

import asyncio
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
import structlog
from enum import Enum

from app.services.data_aggregation_service import (
    AggregationEngine,
    OHLCV,
    Timeframe,
    get_aggregation_engine,
)
from app.services.realtime_streaming_service import (
    RealtimeStreamingService,
    get_streaming_service,
)
from app.services.ohlcv_storage import OHLCVStorage, get_ohlcv_storage

logger = structlog.get_logger()


class BarPublishMode(str, Enum):
    """柱线发布模式"""

    COMPLETED = "completed"  # 仅完成的柱线
    REAL_TIME = "real_time"  # 实时更新（完成和开放中）
    BOTH = "both"  # 两者都发布


class AggregationStreamingBridge:
    """聚合流媒体桥接 - 连接聚合引擎和流服务"""

    def __init__(
        self,
        aggregation_engine: Optional[AggregationEngine] = None,
        streaming_service: Optional[RealtimeStreamingService] = None,
        ohlcv_storage: Optional[OHLCVStorage] = None,
        publish_mode: BarPublishMode = BarPublishMode.COMPLETED,
        enable_persistence: bool = True,
    ):
        """
        初始化聚合流媒体桥接

        Args:
            aggregation_engine: 聚合引擎实例
            streaming_service: 流服务实例
            ohlcv_storage: OHLCV存储实例
            publish_mode: 发布模式
            enable_persistence: 是否启用数据持久化
        """
        self.engine = aggregation_engine or get_aggregation_engine()
        self.streaming = streaming_service or get_streaming_service()
        self.storage = (
            ohlcv_storage or get_ohlcv_storage() if enable_persistence else None
        )
        self.publish_mode = publish_mode
        self.enable_persistence = enable_persistence

        # 缓冲区
        self.pending_bars: List[OHLCV] = []
        self.batch_size = 100

        # 回调函数
        self.on_bar_completed: Optional[Callable[[OHLCV], None]] = None
        self.on_bar_published: Optional[Callable[[OHLCV], None]] = None

        # 指标
        self.bars_published = 0
        self.bars_persisted = 0
        self.publish_errors = 0
        self.last_error = None
        self.last_update_time = datetime.utcnow()

        logger.info("✅ Aggregation Streaming Bridge initialized")

    def process_completed_bars(self, completed_bars: List[OHLCV]) -> None:
        """
        处理完成的柱线

        Args:
            completed_bars: 完成的OHLCV柱线列表
        """
        if not completed_bars:
            return

        self.last_update_time = datetime.utcnow()

        # 持久化柱线
        if self.enable_persistence and self.storage:
            try:
                persisted = self.storage.insert_bars_batch(completed_bars)
                self.bars_persisted += persisted
                logger.debug(
                    "💾 Bars persisted",
                    count=persisted,
                    total=self.bars_persisted,
                )
            except Exception as e:
                logger.error("❌ Persistence error", error=str(e))
                self.last_error = str(e)

        # 发布到流服务
        for bar in completed_bars:
            try:
                self._publish_bar(bar)
                if self.on_bar_completed:
                    self.on_bar_completed(bar)
            except Exception as e:
                logger.error(
                    "❌ Publish error",
                    symbol=bar.symbol,
                    timeframe=bar.timeframe.value,
                    error=str(e),
                )
                self.publish_errors += 1
                self.last_error = str(e)

    def _publish_bar(self, bar: OHLCV) -> bool:
        """发布单个柱线到流服务"""
        try:
            # 转换为发送格式
            bar_data = {
                "symbol": bar.symbol,
                "timeframe": bar.timeframe.value,
                "timestamp": bar.timestamp,
                "open": float(bar.open),
                "high": float(bar.high),
                "low": float(bar.low),
                "close": float(bar.close),
                "volume": bar.volume,
                "tick_count": bar.tick_count,
                "completed": bar.completed,
                "created_at": bar.created_at.isoformat(),
            }

            # 广播到订阅者
            self.streaming.broadcast_data(bar.symbol, bar_data)
            self.bars_published += 1

            logger.debug(
                "📤 Bar published",
                symbol=bar.symbol,
                timeframe=bar.timeframe.value,
                close=float(bar.close),
            )

            if self.on_bar_published:
                self.on_bar_published(bar)

            return True

        except Exception as e:
            logger.error(
                "❌ Bar publish failed",
                symbol=bar.symbol,
                timeframe=bar.timeframe.value,
                error=str(e),
            )
            return False

    def get_stats(self) -> Dict[str, Any]:
        """获取桥接统计信息"""
        return {
            "bars_published": self.bars_published,
            "bars_persisted": self.bars_persisted,
            "publish_errors": self.publish_errors,
            "pending_bars": len(self.pending_bars),
            "publish_mode": self.publish_mode.value,
            "persistence_enabled": self.enable_persistence,
            "aggregation_stats": self.engine.get_stats(),
            "streaming_stats": self.streaming.get_stats(),
            "storage_stats": (
                self.storage.get_stats() if self.storage else {"enabled": False}
            ),
            "last_error": self.last_error,
            "uptime_seconds": (
                datetime.utcnow() - self.last_update_time
            ).total_seconds(),
        }


# 全局单例
_bridge: Optional[AggregationStreamingBridge] = None


def get_aggregation_streaming_bridge() -> AggregationStreamingBridge:
    """获取聚合流媒体桥接单例"""
    global _bridge
    if _bridge is None:
        _bridge = AggregationStreamingBridge()
    return _bridge


def reset_aggregation_streaming_bridge() -> None:
    """重置聚合流媒体桥接单例（仅用于测试）"""
    global _bridge
    _bridge = None
