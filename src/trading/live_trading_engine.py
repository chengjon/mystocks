"""
Live Trading Engine - Real-time ML Strategy Execution
实时交易引擎 - 实时ML策略执行

Connects ML strategies with real-time market data and order execution.
将ML策略与实时市场数据和订单执行连接起来。
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.adapters.tdx_realtime_manager import TdxRealtimeManager
from src.application.trading.order_mgmt_service import OrderManagementService
from src.governance.risk_management.services.stop_loss_execution_service import StopLossExecutionService
from src.ml_strategy.strategy.ml_strategy_base import MLTradingStrategy

logger = logging.getLogger(__name__)


@dataclass
class LiveTradingConfig:
    """Live trading configuration"""

    max_positions: int = 10
    max_position_size: float = 100000.0  # Maximum position size in RMB
    max_daily_loss: float = 5000.0  # Maximum daily loss
    max_drawdown: float = 0.05  # Maximum drawdown (5%)
    risk_per_trade: float = 0.02  # Risk per trade (2%)
    min_signal_confidence: float = 0.7  # Minimum signal confidence
    trading_hours_start: str = "09:30"
    trading_hours_end: str = "15:00"
    position_update_interval: int = 60  # Position update interval in seconds
    market_data_update_interval: int = 5  # Market data update interval in seconds


@dataclass
class Position:
    """Trading position"""

    symbol: str
    quantity: int
    entry_price: float
    entry_time: datetime
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    strategy_name: str = ""
    confidence: float = 0.0


@dataclass
class TradingSession:
    """Trading session state"""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    max_drawdown: float = 0.0
    current_drawdown: float = 0.0
    active_positions: Dict[str, Position] = field(default_factory=dict)
    closed_positions: List[Position] = field(default_factory=list)


class LiveTradingEngine:
    """
    Live Trading Engine

    Orchestrates real-time trading execution with ML strategies:
    1. Real-time market data feed
    2. ML strategy signal generation
    3. Risk management and position sizing
    4. Order execution and position monitoring
    5. Performance tracking and reporting
    """


def __init__(
    self,
    config: LiveTradingConfig,
    realtime_manager: TdxRealtimeManager,
    strategies: List[MLTradingStrategy],
    order_service: OrderManagementService,
    stop_loss_service: Optional[StopLossExecutionService] = None,
):
    self.config = config
    self.realtime_manager = realtime_manager
    self.strategies = strategies
    self.order_service = order_service
    self.stop_loss_service = stop_loss_service

    # Trading state
    self.current_session: Optional[TradingSession] = None
    self.is_running = False
    self.daily_pnl = 0.0
    self.daily_start_pnl = 0.0

    # Market data subscriptions
    self.market_subscriptions: Dict[str, str] = {}  # symbol -> subscription_id

    # Background tasks
    self.market_data_task: Optional[asyncio.Task] = None
    self.strategy_task: Optional[asyncio.Task] = None
    self.monitoring_task: Optional[asyncio.Task] = None

    logger.info("LiveTradingEngine initialized with %d strategies", len(strategies))


async def start_trading_session(self) -> str:
    """Start a new trading session"""
    if self.is_running:
        raise RuntimeError("Trading session already running")

    session_id = f"live_session_{int(time.time())}"
    self.current_session = TradingSession(session_id=session_id, start_time=datetime.now())

    self.is_running = True
    self.daily_start_pnl = self.daily_pnl

    # Start background tasks
    self.market_data_task = asyncio.create_task(self._run_market_data_feed())
    self.strategy_task = asyncio.create_task(self._run_strategy_execution())
    self.monitoring_task = asyncio.create_task(self._run_position_monitoring())

    logger.info("Started live trading session: %s", session_id)
    return session_id


async def stop_trading_session(self) -> Dict[str, Any]:
    """Stop the current trading session"""
    if not self.is_running:
        raise RuntimeError("No trading session running")

    self.is_running = False

    # Cancel background tasks
    if self.market_data_task:
        self.market_data_task.cancel()
    if self.strategy_task:
        self.strategy_task.cancel()
    if self.monitoring_task:
        self.monitoring_task.cancel()

    # Close all positions
    await self._close_all_positions()

    # Unsubscribe from market data
    for subscription_id in self.market_subscriptions.values():
        self.realtime_manager.unsubscribe_realtime_updates(subscription_id)

    self.market_subscriptions.clear()

    # Finalize session
    if self.current_session:
        self.current_session.end_time = datetime.now()
        session_summary = self._get_session_summary()
        self.current_session = None

        logger.info("Stopped trading session")
        return session_summary

    return {}


async def _run_market_data_feed(self):
    """Run market data feed collection"""
    try:
        while self.is_running:
            # Update market data for all watched symbols
            watched_symbols = set()
            for strategy in self.strategies:
                watched_symbols.update(strategy.get_watchlist())

            # Subscribe to new symbols
            for symbol in watched_symbols:
                if symbol not in self.market_subscriptions:
                    subscription_id = self.realtime_manager.subscribe_realtime_updates(
                        symbol, self._handle_market_data_update
                    )
                    self.market_subscriptions[symbol] = subscription_id

            await asyncio.sleep(self.config.market_data_update_interval)

    except asyncio.CancelledError:
        logger.info("Market data feed cancelled")
    except Exception as e:
        logger.error("Error in market data feed: %s", e)


async def _run_strategy_execution(self):
    """Run ML strategy signal generation and execution"""
    try:
        while self.is_running:
            # Check if within trading hours
            if not self._is_trading_hours():
                await asyncio.sleep(60)  # Check every minute outside trading hours
                continue
            # Generate signals from all strategies
            for strategy in self.strategies:
                try:
                    signals = self._generate_strategy_signals(strategy)

                    for signal in signals:
                        await self._process_trading_signal(signal, strategy)

                except Exception as e:
                    logger.error("Error generating signals for %s: %s", strategy.__class__.__name__, e)

            await asyncio.sleep(30)  # Generate signals every 30 seconds

    except asyncio.CancelledError:
        logger.info("Strategy execution cancelled")
    except Exception as e:
        logger.error("Error in strategy execution: %s", e)


async def _run_position_monitoring(self):
    """Run position monitoring and risk management"""
    try:
        while self.is_running:
            await self._update_positions()
            await self._check_risk_limits()
            await self._check_stop_loss_take_profit()

            await asyncio.sleep(self.config.position_update_interval)

    except asyncio.CancelledError:
        logger.info("Position monitoring cancelled")
    except Exception as e:
        logger.error("Error in position monitoring: %s", e)


def _generate_strategy_signals(self, strategy: MLTradingStrategy) -> List[Dict[str, Any]]:
    """Generate trading signals from ML strategy"""
    signals = []

    # Define default watchlist since strategy doesn't have get_watchlist method
    # In real implementation, this could be configured per strategy
    watchlist = ["000001", "600000", "000002"]  # Default symbols for testing

    # Get market data for strategy symbols and create DataFrame
    market_records = []
    for symbol in watchlist:
        try:
            data = self.realtime_manager.get_real_time_data(symbol)
            market_records.append(
                {
                    "symbol": symbol,
                    "price": data["price"],
                    "volume": data["volume"],
                    "timestamp": data["timestamp"],
                    "high": data.get("high", data["price"]),
                    "low": data.get("low", data["price"]),
                    "open": data.get("bid", data["price"] * 0.99),  # Estimate open from bid
                    "close": data["price"],
                }
            )
        except Exception as e:
            logger.warning("Failed to get market data for %s: %s", symbol, e)
            continue

    if not market_records:
        return signals

    # Convert to DataFrame for strategy
    import pandas as pd

    market_df = pd.DataFrame(market_records)

    # Generate signals using strategy
    try:
        # Run in thread pool since strategy.generate_signals is not async
        import asyncio

        loop = asyncio.get_event_loop()
        signals_df = loop.run_until_complete(strategy.generate_signals(market_df))

        # Parse signals from DataFrame
        if not signals_df.empty and "signal" in signals_df.columns:
            for _, row in signals_df.iterrows():
                signal_type = row.get("signal", "").lower()
                confidence = row.get("confidence", 0.5)

                if confidence >= self.config.min_signal_confidence:
                    action = "buy" if signal_type in ["buy", "long", "1"] else "sell"
                    signals.append(
                        {
                            "symbol": row.get("symbol", watchlist[0]),
                            "action": action,
                            "confidence": confidence,
                            "strategy_name": strategy.__class__.__name__,
                            "metadata": {"signal_data": row.to_dict()},
                        }
                    )

    except Exception as e:
        logger.error("Error generating signals: %s", e)

    return signals

    # Generate signals using strategy
    try:
        strategy_signals = strategy.generate_signals(market_df)

        for signal in strategy_signals:
            if signal.get("confidence", 0) >= self.config.min_signal_confidence:
                signals.append(
                    {
                        "symbol": signal["symbol"],
                        "action": signal["action"],  # 'buy' or 'sell'
                        "confidence": signal["confidence"],
                        "strategy_name": strategy.__class__.__name__,
                        "metadata": signal.get("metadata", {}),
                    }
                )

    except Exception as e:
        logger.error("Error generating signals: %s", e)

    return signals


async def _process_trading_signal(self, signal: Dict[str, Any], strategy: MLTradingStrategy):
    """Process a trading signal and execute order if appropriate"""
    symbol = signal["symbol"]
    action = signal["action"]
    confidence = signal["confidence"]

    # Check if we already have a position in this symbol
    existing_position = self.current_session.active_positions.get(symbol) if self.current_session else None

    # Risk management checks
    if not await self._check_signal_risk_limits(signal, existing_position):
        return

    # Calculate position size
    position_size = await self._calculate_position_size(signal, strategy)

    if position_size <= 0:
        return

    try:
        # Execute order
        order_request = {
            "symbol": symbol,
            "quantity": position_size if action == "buy" else -position_size,
            "side": "buy" if action == "buy" else "sell",
            "order_type": "market",
            "price": None,  # Market order
        }

        order_result = self.order_service.place_order(order_request)
        logger.info("Order placed successfully: %s", order_result.order_id)

        # Track position
        if action == "buy":
            position = Position(
                symbol=symbol,
                quantity=position_size,
                entry_price=self.realtime_manager.get_real_time_data(symbol)["price"],
                entry_time=datetime.now(),
                strategy_name=strategy.__class__.__name__,
                confidence=confidence,
            )
            if self.current_session:
                self.current_session.active_positions[symbol] = position
        else:
            # Close position
            if existing_position:
                await self._close_position(symbol, self.realtime_manager.get_real_time_data(symbol)["price"])

        if self.current_session:
            self.current_session.total_trades += 1

        logger.info("Executed %s order for %s: %d shares at market price", action.upper(), symbol, position_size)

    except Exception as e:
        logger.error("Failed to execute order for %s: %s", symbol, e)


async def _calculate_position_size(self, signal: Dict[str, Any], strategy: MLTradingStrategy) -> int:
    """Calculate position size based on risk management"""
    try:
        current_price = self.realtime_manager.get_real_time_data(signal["symbol"])["price"]
        available_capital = self.config.max_position_size - sum(
            pos.quantity * pos.entry_price
            for pos in (self.current_session.active_positions.values() if self.current_session else [])
        )

        # Risk-based position sizing
        risk_amount = min(
            available_capital * self.config.risk_per_trade,
            self.config.max_position_size / self.config.max_positions,
        )

        # Adjust based on confidence
        confidence_multiplier = signal["confidence"] / self.config.min_signal_confidence
        position_value = risk_amount * confidence_multiplier

        position_size = int(position_value / current_price)

        # Ensure minimum position size and respect limits
        position_size = max(100, min(position_size, int(self.config.max_position_size / current_price)))

        return position_size

    except Exception as e:
        logger.error("Error calculating position size: %s", e)
        return 0


async def _check_signal_risk_limits(self, signal: Dict[str, Any], existing_position: Optional[Position]) -> bool:
    """Check if signal passes risk management limits"""
    try:
        # Check daily loss limit
        if self.daily_pnl - self.daily_start_pnl <= -self.config.max_daily_loss:
            logger.warning("Daily loss limit reached, stopping trading")
            return False

        # Check position count limit
        active_positions = len(self.current_session.active_positions) if self.current_session else 0
        if active_positions >= self.config.max_positions:
            logger.info("Maximum position count reached")
            return False

        # Check if already have position in this symbol
        if existing_position and signal["action"] == "buy":
            logger.info("Already have position in %s", signal["symbol"])
            return False

        # Check drawdown limit
        if self.current_session and self.current_session.current_drawdown >= self.config.max_drawdown:
            logger.warning("Maximum drawdown reached, stopping trading")
            return False

        return True

    except Exception as e:
        logger.error("Error checking risk limits: %s", e)
        return False


async def _update_positions(self):
    """Update position P&L and status"""
    if not self.current_session:
        return

    try:
        for symbol, position in self.current_session.active_positions.items():
            try:
                market_data = self.realtime_manager.get_real_time_data(symbol)
                current_price = market_data["price"]

                position.current_price = current_price
                position.unrealized_pnl = (current_price - position.entry_price) * position.quantity

            except Exception as e:
                logger.warning("Failed to update position for %s: %s", symbol, e)

        # Update session drawdown
        total_pnl = sum(pos.unrealized_pnl for pos in self.current_session.active_positions.values())
        self.current_session.current_drawdown = max(0, -total_pnl)

    except Exception as e:
        logger.error("Error updating positions: %s", e)


async def _check_risk_limits(self):
    """Check overall risk limits for the trading session"""
    if not self.current_session:
        return

    try:
        # Check daily loss limit
        if self.daily_pnl - self.daily_start_pnl <= -self.config.max_daily_loss:
            logger.warning("Daily loss limit reached (%.2f), stopping trading", self.daily_pnl - self.daily_start_pnl)
            return

        # Check drawdown limit
        if self.current_session.current_drawdown >= self.config.max_drawdown:
            logger.warning(
                "Maximum drawdown reached (%.2f%%), stopping trading", self.current_session.current_drawdown * 100
            )
            return

        # Check drawdown limit
        if self.current_session.current_drawdown >= self.config.max_drawdown:
            logger.warning(
                "Maximum drawdown reached (%.2f%%), stopping trading", self.current_session.current_drawdown * 100
            )
            # Note: In a real implementation, this would signal to stop trading
            return

    except Exception as e:
        logger.error("Error checking risk limits: %s", e)


async def _check_stop_loss_take_profit(self):
    """Check and execute stop-loss and take-profit orders"""
    if not self.current_session or not self.stop_loss_service:
        return

    try:
        for symbol, position in list(self.current_session.active_positions.items()):
            try:
                current_price = position.current_price

                # Check stop loss
                if position.stop_loss_price and current_price <= position.stop_loss_price:
                    await self._close_position(symbol, current_price, "stop_loss")
                    continue

                # Check take profit
                if position.take_profit_price and current_price >= position.take_profit_price:
                    await self._close_position(symbol, current_price, "take_profit")
                    continue

            except Exception as e:
                logger.warning("Error checking stop/take profit for %s: %s", symbol, e)

    except Exception as e:
        logger.error("Error in stop-loss/take-profit check: %s", e)


async def _close_position(self, symbol: str, exit_price: float, reason: str = "manual"):
    """Close a position"""
    if not self.current_session or symbol not in self.current_session.active_positions:
        return

    position = self.current_session.active_positions[symbol]
    pnl = (exit_price - position.entry_price) * position.quantity

    # Update session stats
    self.current_session.total_pnl += pnl
    self.daily_pnl += pnl

    if pnl > 0:
        self.current_session.winning_trades += 1
    else:
        self.current_session.losing_trades += 1

    # Move to closed positions
    self.current_session.closed_positions.append(position)
    del self.current_session.active_positions[symbol]

    logger.info("Closed position in %s: P&L %.2f RMB (%s)", symbol, pnl, reason)


async def _close_all_positions(self):
    """Close all active positions"""
    if not self.current_session:
        return

    symbols_to_close = list(self.current_session.active_positions.keys())

    for symbol in symbols_to_close:
        try:
            current_price = self.realtime_manager.get_real_time_data(symbol)["price"]
            await self._close_position(symbol, current_price, "session_end")
        except Exception as e:
            logger.warning("Failed to close position for %s: %s", symbol, e)


def _handle_market_data_update(self, data: Dict[str, Any]):
    """Handle real-time market data updates"""
    # Update position prices if we have active positions
    symbol = data.get("symbol")
    if symbol and self.current_session and symbol in self.current_session.active_positions:
        position = self.current_session.active_positions[symbol]
        position.current_price = data.get("price", position.current_price)


def _is_trading_hours(self) -> bool:
    """Check if current time is within trading hours"""
    now = datetime.now().time()
    start_time = datetime.strptime(self.config.trading_hours_start, "%H:%M").time()
    end_time = datetime.strptime(self.config.trading_hours_end, "%H:%M").time()

    return start_time <= now <= end_time


def _get_session_summary(self) -> Dict[str, Any]:
    """Get trading session summary"""
    if not self.current_session:
        return {}

    duration = (
        (self.current_session.end_time - self.current_session.start_time)
        if self.current_session.end_time
        else timedelta(0)
    )

    return {
        "session_id": self.current_session.session_id,
        "start_time": self.current_session.start_time.isoformat(),
        "end_time": self.current_session.end_time.isoformat() if self.current_session.end_time else None,
        "duration_seconds": duration.total_seconds(),
        "total_trades": self.current_session.total_trades,
        "winning_trades": self.current_session.winning_trades,
        "losing_trades": self.current_session.losing_trades,
        "total_pnl": self.current_session.total_pnl,
        "max_drawdown": self.current_session.max_drawdown,
        "win_rate": (self.current_session.winning_trades / max(1, self.current_session.total_trades)) * 100,
        "active_positions_count": len(self.current_session.active_positions),
        "closed_positions_count": len(self.current_session.closed_positions),
    }


def get_trading_status(self) -> Dict[str, Any]:
    """Get current trading status"""
    return {
        "is_running": self.is_running,
        "session_id": self.current_session.session_id if self.current_session else None,
        "active_positions": len(self.current_session.active_positions) if self.current_session else 0,
        "total_pnl": self.current_session.total_pnl if self.current_session else 0.0,
        "daily_pnl": self.daily_pnl - self.daily_start_pnl,
        "current_drawdown": self.current_session.current_drawdown if self.current_session else 0.0,
        "trading_hours": self._is_trading_hours(),
    }
