"""
Signal Engine Core - 信号引擎核心

实现多指标融合的实时信号生成：
- 事件驱动架构
- 指标调度管理
- 信号融合算法
- 性能监控

作者: Claude Code (Sisyphus)
日期: 2026-01-14
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from web.backend.app.core.event_bus import Event, get_event_bus
from web.backend.app.services.indicators.gpu_adapter import (
    GPUIndicatorFactory,
    IndicatorConfig,
)
from web.backend.app.services.signals.strategies.base_strategies import (
    BollingerBandsStrategy,
    MACDStrategy,
    RSIStrategy,
    SignalStrategy,
    SignalType,
    TradingSignal,
)

logger = logging.getLogger(__name__)

# 集成现有的信号监控系统（不重新实现）
try:
    from src.monitoring.signal_recorder import get_signal_recorder
    from src.monitoring.signal_result_tracker import get_signal_result_tracker

    MONITORING_AVAILABLE = True
    logger.info("✅ Signal monitoring system available")
except ImportError:
    logger.warning("Signal monitoring system not available: %(e)s")
    MONITORING_AVAILABLE = False
    get_signal_recorder = None
    get_signal_result_tracker = None

# 通知管理器（可选集成）- 暂时跳过，避免导入问题
NOTIFICATION_AVAILABLE = False
get_monitored_notification_manager = None
logger.info("ℹ️ Notification system integration deferred (import issues)")


@dataclass
class SignalEngineConfig:
    """信号引擎配置"""

    min_confidence: float = 0.6  # 最小置信度
    max_signals_per_symbol: int = 3  # 每个股票的最大信号数
    signal_cooldown_seconds: int = 300  # 信号冷却时间（秒）
    enable_gpu_acceleration: bool = True  # 启用GPU加速
    batch_size_limit: int = 1000  # 批量处理大小限制


class SignalEngine:
    """
    信号引擎核心

    负责：
    1. 监听市场数据事件
    2. 协调指标计算
    3. 执行信号策略
    4. 生成和发布交易信号
    """

    def __init__(self, config: Optional[SignalEngineConfig] = None):
        """
        初始化信号引擎

        Args:
            config: 引擎配置
        """
        self.config = config or SignalEngineConfig()
        self.event_bus = get_event_bus()

        # 集成现有的信号监控系统（如果可用）
        self.signal_recorder = get_signal_recorder() if MONITORING_AVAILABLE else None
        self.result_tracker = get_signal_result_tracker() if MONITORING_AVAILABLE else None
        self.notification_manager = get_monitored_notification_manager() if NOTIFICATION_AVAILABLE else None

        # 信号策略
        self.strategies: List[SignalStrategy] = []
        self._load_default_strategies()

        # 状态管理
        self.active_signals: Dict[str, List[TradingSignal]] = {}
        self.last_signal_time: Dict[str, datetime] = {}
        self.indicator_cache: Dict[str, Dict[str, Any]] = {}

        # 性能统计
        self.signals_generated = 0
        self.signals_published = 0
        self.processing_time = 0.0

        # 订阅市场事件
        self._setup_event_subscriptions()

        logger.info("✅ Signal Engine initialized with monitoring integration")

    def _load_default_strategies(self):
        """加载默认信号策略"""
        # RSI策略
        rsi_strategy = RSIStrategy(
            {
                "oversold_level": 30,
                "overbought_level": 70,
                "risk_reward_ratio": 2.0,
                "stop_loss_percentage": 0.05,
            }
        )
        self.strategies.append(rsi_strategy)

        # MACD策略
        macd_strategy = MACDStrategy(
            {
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9,
                "risk_reward_ratio": 2.0,
                "stop_loss_percentage": 0.05,
            }
        )
        self.strategies.append(macd_strategy)

        # 布林带策略
        bb_strategy = BollingerBandsStrategy(
            {
                "period": 20,
                "std_dev": 2.0,
                "risk_reward_ratio": 2.0,
                "stop_loss_percentage": 0.05,
            }
        )
        self.strategies.append(bb_strategy)

        logger.info("Loaded {len(self.strategies)} default strategies")

    def _setup_event_subscriptions(self):
        """设置事件订阅"""
        # 订阅市场数据更新事件
        self.event_bus.subscribe("market.tick", self._handle_market_tick)
        self.event_bus.subscribe("market.bar", self._handle_market_bar)

        logger.info("Event subscriptions setup complete")

    async def _handle_market_tick(self, event: Event):
        """
        处理市场tick事件

        Args:
            event: 市场事件
        """
        try:
            symbol = event.data.get("symbol")
            tick_data = event.data.get("data", {})

            if not symbol or not tick_data:
                return

            # 更新指标缓存（实时tick数据）
            await self._update_indicators(symbol, tick_data, "tick")

        except Exception:
            logger.error("Error handling market tick: %(e)s")

    async def _handle_market_bar(self, event: Event):
        """
        处理市场bar事件

        Args:
            event: 市场事件
        """
        try:
            symbol = event.data.get("symbol")
            bar_data = event.data.get("data", {})

            if not symbol or not bar_data:
                return

            # 更新指标缓存
            await self._update_indicators(symbol, bar_data, "bar")

            # 生成信号
            await self._generate_signals(symbol, bar_data)

        except Exception:
            logger.error("Error handling market bar: %(e)s")

    async def _update_indicators(self, symbol: str, market_data: Dict[str, Any], data_type: str):
        """
        更新指标数据

        Args:
            symbol: 股票代码
            market_data: 市场数据
            data_type: 数据类型 ('tick' 或 'bar')
        """
        try:
            if symbol not in self.indicator_cache:
                self.indicator_cache[symbol] = {}

            # 收集所有策略需要的指标
            required_indicators = set()
            for strategy in self.strategies:
                required_indicators.update(strategy.indicators)

            # 计算指标
            for indicator_name in required_indicators:
                try:
                    indicator_data = await self._calculate_indicator(symbol, indicator_name, market_data)
                    if indicator_data:
                        self.indicator_cache[symbol][indicator_name] = indicator_data

                except Exception:
                    logger.error("Error calculating %(indicator_name)s for %(symbol)s: %(e)s")

        except Exception:
            logger.error("Error updating indicators for %(symbol)s: %(e)s")

    async def _calculate_indicator(
        self, symbol: str, indicator_name: str, market_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        计算单个指标

        Args:
            symbol: 股票代码
            indicator_name: 指标名称
            market_data: 市场数据

        Returns:
            指标数据
        """
        try:
            # 创建指标配置
            config = IndicatorConfig(
                name=f"{indicator_name}_{symbol}",
                type=indicator_name,
                parameters=self._get_indicator_params(indicator_name),
            )

            # 获取GPU指标实例
            indicator = GPUIndicatorFactory.create_indicator(indicator_name, config)

            # 执行计算
            result = indicator.calculate(market_data)

            return result.data if hasattr(result, "data") else result

        except Exception:
            logger.error("Error in indicator calculation: %(e)s")
            return None

    def _get_indicator_params(self, indicator_name: str) -> Dict[str, Any]:
        """获取指标参数"""
        param_map = {
            "rsi": {"period": 14},
            "macd": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
            "bbands": {"period": 20, "std_dev": 2.0},
        }
        return param_map.get(indicator_name, {})

    async def _generate_signals(self, symbol: str, market_data: Dict[str, Any]):
        """
        为股票生成交易信号

        Args:
            symbol: 股票代码
            market_data: 市场数据
        """
        start_time = time.time()

        try:
            # 检查冷却时间
            if not self._can_generate_signal(symbol):
                return

            indicator_data = self.indicator_cache.get(symbol, {})
            if not indicator_data:
                return

            signals = []

            # 执行所有策略
            for strategy in self.strategies:
                try:
                    signal = strategy.evaluate(symbol, indicator_data, market_data)
                    if signal and signal.confidence >= self.config.min_confidence:
                        signals.append(signal)

                except Exception:
                    logger.error("Error in strategy {strategy.name}: %(e)s")

            # 信号融合和过滤
            filtered_signals = self._filter_and_rank_signals(signals)

            # 发布信号
            for signal in filtered_signals:
                await self._publish_signal(signal)

            # 更新状态
            processing_time = time.time() - start_time
            self.processing_time += processing_time

            if filtered_signals:
                self.last_signal_time[symbol] = datetime.now()
                self.signals_generated += len(filtered_signals)

        except Exception:
            logger.error("Error generating signals for %(symbol)s: %(e)s")

    def _can_generate_signal(self, symbol: str) -> bool:
        """
        检查是否可以生成信号

        Args:
            symbol: 股票代码

        Returns:
            是否可以生成信号
        """
        if symbol not in self.last_signal_time:
            return True

        time_since_last_signal = (datetime.now() - self.last_signal_time[symbol]).total_seconds()
        return time_since_last_signal >= self.config.signal_cooldown_seconds

    def _filter_and_rank_signals(self, signals: List[TradingSignal]) -> List[TradingSignal]:
        """
        过滤和排序信号

        Args:
            signals: 原始信号列表

        Returns:
            过滤后的信号列表
        """
        if not signals:
            return []

        # 按置信度排序
        signals.sort(key=lambda x: x.confidence, reverse=True)

        # 限制每个股票的信号数量
        filtered_signals = signals[: self.config.max_signals_per_symbol]

        # 信号一致性检查（避免冲突信号）
        buy_signals = [s for s in filtered_signals if s.signal_type == SignalType.BUY]
        sell_signals = [s for s in filtered_signals if s.signal_type == SignalType.SELL]

        # 如果同时有买入和卖出信号，只保留置信度最高的
        if buy_signals and sell_signals:
            best_buy = max(buy_signals, key=lambda x: x.confidence)
            best_sell = max(sell_signals, key=lambda x: x.confidence)

            if best_buy.confidence > best_sell.confidence:
                filtered_signals = [best_buy]
            else:
                filtered_signals = [best_sell]

        return filtered_signals

    async def _publish_signal(self, signal: TradingSignal):
        """
        发布交易信号

        Args:
            signal: 交易信号
        """
        try:
            # 转换为事件数据
            event_data = {
                "signal": signal.to_dict(),
                "timestamp": datetime.now().isoformat(),
            }

            # 发布信号事件
            await self.event_bus.publish_data("signal.alert", event_data)

            # 记录到信号监控系统（异步，不阻塞主流程）
            asyncio.create_task(self._record_signal_to_monitoring(signal))

            # 发送通知（异步）
            asyncio.create_task(self._send_signal_notification(signal))

            # 更新活跃信号
            if signal.symbol not in self.active_signals:
                self.active_signals[signal.symbol] = []

            self.active_signals[signal.symbol].append(signal)
            self.signals_published += 1

            logger.info("Published signal: {signal.signal_id} for {signal.symbol} ({signal.signal_type.value})")

        except Exception:
            logger.error("Error publishing signal {signal.signal_id}: %(e)s")

    async def _record_signal_to_monitoring(self, signal: TradingSignal):
        """记录信号到监控系统"""
        if not self.signal_recorder:
            logger.debug("Signal recorder not available, skipping monitoring")
            return

        try:
            await self.signal_recorder.record_signal(
                strategy_id="signal_engine",  # 使用固定策略ID
                symbol=signal.symbol,
                signal_type=signal.signal_type.value,
                indicator_count=len(signal.indicators),
                execution_time_ms=0,  # 信号生成时间，暂时设为0
                gpu_used=self.config.enable_gpu_acceleration,
                gpu_latency_ms=0,  # GPU处理时间，暂时设为0
                metadata={
                    "confidence": signal.confidence,
                    "reason": signal.reason,
                    "price": signal.price,
                    "strength": signal.strength.value,
                    "indicators": signal.indicators,
                },
            )
        except Exception:
            logger.error("Error recording signal to monitoring: %(e)s")

    async def _send_signal_notification(self, signal: TradingSignal):
        """发送信号通知"""
        if not self.notification_manager:
            logger.debug("Notification manager not available, skipping notification")
            return

        try:
            self.notification_manager.send_signal_notification(
                strategy_name="Signal Engine",
                symbol=signal.symbol,
                signal=signal.signal_type.value,
                price=signal.price,
                context={
                    "confidence": signal.confidence,
                    "reason": signal.reason,
                    "indicators": signal.indicators,
                },
                signal_id=signal.signal_id,
            )
        except Exception:
            logger.error("Error sending signal notification: %(e)s")

    # ================ API规范实现 ================

    async def get_trading_signals(self, stock_code: str) -> Dict[str, Any]:
        """
        获取单个股票的交易信号（符合API规范）

        Args:
            stock_code: 股票代码

        Returns:
            Dict: 交易信号数据，符合data_source_interface.py规范
        """
        try:
            # 获取该股票的活跃信号
            active_signals = self.active_signals.get(stock_code, [])

            if not active_signals:
                return {
                    "stock_code": stock_code,
                    "signals": [],
                    "total_count": 0,
                    "last_updated": datetime.now().isoformat(),
                }

            # 转换为API规范格式
            signals_data = []
            for signal in active_signals[-10:]:  # 最多返回最近10个信号
                signals_data.append(
                    {
                        "signal_id": signal.signal_id,
                        "type": signal.signal_type.value,
                        "confidence": signal.confidence,
                        "price": signal.price,
                        "timestamp": signal.timestamp.isoformat(),
                        "reason": signal.reason,
                        "indicators": signal.indicators,
                        "strength": signal.strength.value,
                    }
                )

            return {
                "stock_code": stock_code,
                "signals": signals_data,
                "total_count": len(signals_data),
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error("Error getting trading signals for %(stock_code)s: %(e)s")
            return {
                "stock_code": stock_code,
                "signals": [],
                "total_count": 0,
                "error": str(e),
                "last_updated": datetime.now().isoformat(),
            }

    async def analyze_trading_signals(
        self,
        user_id: int,
        strategy_ids: Optional[List[int]] = None,
        trade_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        分析交易信号（符合business_data_source.py API规范）

        Args:
            user_id: 用户ID
            strategy_ids: 策略ID列表，None表示所有启用的策略
            trade_date: 交易日期，None表示最新交易日

        Returns:
            List[Dict]: 交易信号列表，符合API规范格式
        """
        try:
            # 获取所有活跃信号
            all_signals = []
            for symbol, signals in self.active_signals.items():
                for signal in signals:
                    # 转换时间格式
                    signal_date = signal.timestamp.date().isoformat()

                    # 如果指定了交易日期，只返回该日期的信号
                    if trade_date and signal_date != trade_date:
                        continue

                    all_signals.append(
                        {
                            "signal_id": signal.signal_id,
                            "strategy_id": 1,  # Signal Engine使用固定策略ID
                            "strategy_name": "Signal Engine",
                            "symbol": signal.symbol,
                            "name": signal.symbol,  # 简化为股票代码
                            "action": signal.signal_type.value.lower(),
                            "confidence": signal.confidence,
                            "price": signal.price,
                            "recommended_quantity": None,  # Signal Engine不提供推荐数量
                            "reason": signal.reason,
                            "generated_at": signal.timestamp.isoformat(),
                        }
                    )

            # 按时间倒序排序
            all_signals.sort(key=lambda x: x["generated_at"], reverse=True)

            # 限制返回数量（避免返回过多数据）
            return all_signals[:100]

        except Exception:
            logger.error("Error analyzing trading signals: %(e)s")
            return []

    def get_active_signals(self, symbol: Optional[str] = None) -> Dict[str, List[TradingSignal]]:
        """
        获取活跃信号

        Args:
            symbol: 股票代码，如果为None则返回所有

        Returns:
            活跃信号字典
        """
        if symbol:
            return {symbol: self.active_signals.get(symbol, [])}
        return self.active_signals.copy()

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return {
            "signals_generated": self.signals_generated,
            "signals_published": self.signals_published,
            "active_symbols": len(self.active_signals),
            "total_active_signals": sum(len(signals) for signals in self.active_signals.values()),
            "average_processing_time": self.processing_time / max(self.signals_generated, 1),
            "strategies_count": len(self.strategies),
        }

    async def cleanup_expired_signals(self):
        """清理过期信号"""
        current_time = datetime.now()
        expired_symbols = []

        for symbol, signals in self.active_signals.items():
            # 移除过期信号
            active_signals = [
                signal for signal in signals if signal.validity_period is None or signal.validity_period > current_time
            ]

            if not active_signals:
                expired_symbols.append(symbol)
            else:
                self.active_signals[symbol] = active_signals

        # 清理空符号
        for symbol in expired_symbols:
            del self.active_signals[symbol]

        if expired_symbols:
            logger.info("Cleaned up expired signals for {len(expired_symbols)} symbols")

    async def shutdown(self):
        """关闭信号引擎"""
        logger.info("Shutting down Signal Engine...")

        # 清理资源
        await self.cleanup_expired_signals()

        logger.info("✅ Signal Engine shutdown complete")
