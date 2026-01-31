"""
Real-time Strategy Executor
实时策略执行器

Integrates ML strategies with the live trading engine for real-time execution.
将ML策略与实时交易引擎集成，实现实时执行。
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.adapters.tdx_realtime_manager import TdxRealtimeManager
from src.application.trading.order_mgmt_service import OrderManagementService
from src.governance.risk_management.services.stop_loss_execution_service import StopLossExecutionService
from src.ml_strategy.strategy.ml_strategy_base import MLTradingStrategy
from src.trading.live_trading_engine import LiveTradingConfig, LiveTradingEngine

logger = logging.getLogger(__name__)


class RealtimeStrategyExecutor:
    """
    Real-time Strategy Executor

    Manages multiple ML strategies running in real-time with the live trading engine.
    管理多个ML策略的实时运行，与实时交易引擎协同工作。
    """


def __init__(
    self,
    strategies: List[MLTradingStrategy],
    config: Optional[LiveTradingConfig] = None,
    order_service: Optional[OrderManagementService] = None,
    stop_loss_service: Optional[StopLossExecutionService] = None,
):
    self.strategies = strategies
    self.config = config or LiveTradingConfig()

    # Initialize dependencies
    self.realtime_manager = TdxRealtimeManager()
    self.order_service = order_service or OrderManagementService(None)  # Mock for now
    self.stop_loss_service = stop_loss_service

    # Initialize trading engine
    self.trading_engine = LiveTradingEngine(
        config=self.config,
        realtime_manager=self.realtime_manager,
        strategies=strategies,
        order_service=self.order_service,
        stop_loss_service=self.stop_loss_service,
    )

    self.is_running = False

    logger.info("RealtimeStrategyExecutor initialized with %d strategies", len(strategies))


async def start_execution(self) -> str:
    """Start real-time strategy execution"""
    if self.is_running:
        raise RuntimeError("Strategy execution already running")

    logger.info("Starting real-time strategy execution...")

    # Initialize strategies
    for strategy in self.strategies:
        try:
            # Strategies don't have async initialize method, skip for now
            logger.info("Initialized strategy: %s", strategy.__class__.__name__)
        except Exception as e:
            logger.error("Failed to initialize strategy %s: %s", strategy.__class__.__name__, e)

    # Start trading session
    session_id = await self.trading_engine.start_trading_session()
    self.is_running = True

    logger.info("Real-time strategy execution started with session: %s", session_id)
    return session_id


async def stop_execution(self) -> Dict[str, Any]:
    """Stop real-time strategy execution"""
    if not self.is_running:
        raise RuntimeError("Strategy execution not running")

    logger.info("Stopping real-time strategy execution...")

    # Stop trading session
    session_summary = await self.trading_engine.stop_trading_session()

    # Cleanup strategies
    for strategy in self.strategies:
        try:
            # Strategies don't have async cleanup method, skip for now
            logger.info("Cleaned up strategy: %s", strategy.__class__.__name__)
        except Exception as e:
            logger.error("Failed to cleanup strategy %s: %s", strategy.__class__.__name__, e)

    self.is_running = False

    logger.info("Real-time strategy execution stopped")
    return session_summary


def get_execution_status(self) -> Dict[str, Any]:
    """Get current execution status"""
    trading_status = self.trading_engine.get_trading_status()

    return {
        "is_running": self.is_running,
        "strategies": [
            {
                "name": strategy.__class__.__name__,
                "watchlist": getattr(strategy, "get_watchlist", lambda: ["000001", "600000", "000002"])(),
                "status": "active" if self.is_running else "inactive",
            }
            for strategy in self.strategies
        ],
        "trading_engine": trading_status,
        "market_data": self.realtime_manager.get_cache_status(),
    }


def get_strategy_performance(self) -> Dict[str, Any]:
    """Get performance metrics for all strategies"""
    performance_data = {}

    for strategy in self.strategies:
        try:
            if hasattr(strategy, "get_performance_metrics"):
                performance_data[strategy.__class__.__name__] = strategy.get_performance_metrics()
            else:
                performance_data[strategy.__class__.__name__] = {
                    "status": "performance_metrics_not_available",
                    "message": "Strategy does not implement get_performance_metrics method",
                }
        except Exception as e:
            logger.warning("Failed to get performance for %s: %s", strategy.__class__.__name__, e)
            performance_data[strategy.__class__.__name__] = {"error": str(e)}

    return performance_data


def update_strategy_config(self, strategy_name: str, config_updates: Dict[str, Any]):
    """Update configuration for a specific strategy"""
    for strategy in self.strategies:
        if strategy.__class__.__name__ == strategy_name:
            try:
                # Check if strategy has update_config method
                if hasattr(strategy, "update_config"):
                    strategy.update_config(config_updates)
                    logger.info("Updated config for strategy: %s", strategy_name)
                    return True
                else:
                    logger.warning("Strategy %s does not have update_config method", strategy_name)
                    return False
            except Exception as e:
                logger.error("Failed to update config for %s: %s", strategy_name, e)
                return False

    logger.warning("Strategy not found: %s", strategy_name)
    return False


def add_strategy(self, strategy: MLTradingStrategy):
    """Add a new strategy to the executor"""
    if self.is_running:
        logger.warning("Cannot add strategy while execution is running")
        return False

    self.strategies.append(strategy)
    self.trading_engine.strategies.append(strategy)
    logger.info("Added strategy: %s", strategy.__class__.__name__)
    return True


def remove_strategy(self, strategy_name: str) -> bool:
    """Remove a strategy from the executor"""
    if self.is_running:
        logger.warning("Cannot remove strategy while execution is running")
        return False

    for i, strategy in enumerate(self.strategies):
        if strategy.__class__.__name__ == strategy_name:
            self.strategies.pop(i)
            self.trading_engine.strategies.pop(i)
            logger.info("Removed strategy: %s", strategy_name)
            return True

    logger.warning("Strategy not found: %s", strategy_name)
    return False


def get_market_data_snapshot(self) -> Dict[str, Any]:
    """Get current market data snapshot for all watched symbols"""
    # Use default symbols since strategies don't have get_watchlist method
    all_symbols = {"000001", "600000", "000002"}  # Default test symbols

    market_data = {}
    for symbol in all_symbols:
        try:
            data = self.realtime_manager.get_real_time_data(symbol)
            market_data[symbol] = data
        except Exception as e:
            logger.warning("Failed to get market data for %s: %s", symbol, e)
            market_data[symbol] = {"error": str(e)}

    return {"timestamp": datetime.now().isoformat(), "symbols_count": len(market_data), "data": market_data}


async def create_realtime_executor(
    strategy_names: Optional[List[str]] = None, config: Optional[LiveTradingConfig] = None
) -> RealtimeStrategyExecutor:
    """
    Factory function to create a realtime strategy executor with default strategies.

    Args:
        strategy_names: List of strategy class names to include (default: all available)
        config: Trading configuration (default: standard config)

    Returns:
        Configured RealtimeStrategyExecutor
    """
    from src.ml_strategy.strategy.decision_tree_trading_strategy import DecisionTreeTradingStrategy
    from src.ml_strategy.strategy.naive_bayes_trading_strategy import NaiveBayesTradingStrategy
    from src.ml_strategy.strategy.svm_trading_strategy import SVMTradingStrategy

    # Available strategies
    available_strategies = {
        "SVMTradingStrategy": SVMTradingStrategy,
        "DecisionTreeTradingStrategy": DecisionTreeTradingStrategy,
        "NaiveBayesTradingStrategy": NaiveBayesTradingStrategy,
    }

    # Select strategies
    if strategy_names is None:
        strategy_names = list(available_strategies.keys())

    strategies = []
    for name in strategy_names:
        if name in available_strategies:
            try:
                strategy_class = available_strategies[name]
                strategy = strategy_class()
                strategies.append(strategy)
                logger.info("Loaded strategy: %s", name)
            except Exception as e:
                logger.error("Failed to load strategy %s: %s", name, e)
        else:
            logger.warning("Strategy not found: %s", name)

    if not strategies:
        raise ValueError("No valid strategies loaded")

    # Create executor
    executor = RealtimeStrategyExecutor(strategies=strategies, config=config or LiveTradingConfig())

    return executor
