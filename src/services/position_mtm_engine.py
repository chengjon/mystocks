"""
持仓市值实时计算引擎
Position Mark-to-Market Engine - Real-time Portfolio Value Calculation

实时计算持仓市值、未实现盈亏、盈亏比例等指标。

Author: Claude Code
Date: 2026-01-09
"""

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger()


class PositionStatus(str, Enum):
    """持仓状态"""

    ACTIVE = "active"  # 活跃
    PENDING = "pending"  # 待成交
    CLOSED = "closed"  # 已平仓
    FROZEN = "frozen"  # 冻结


@dataclass
class PositionSnapshot:
    """持仓快照"""

    position_id: str
    portfolio_id: str
    symbol: str
    quantity: int
    avg_price: float
    market_price: float = 0.0
    market_value: float = 0.0
    unrealized_profit: float = 0.0
    profit_ratio: float = 0.0
    realized_profit: float = 0.0
    total_profit: float = 0.0
    status: PositionStatus = PositionStatus.ACTIVE
    last_update: datetime = field(default_factory=datetime.now)
    price_change: float = 0.0
    price_change_percent: float = 0.0


@dataclass
class PortfolioSnapshot:
    """投资组合快照"""

    portfolio_id: str
    total_market_value: float = 0.0
    total_cost: float = 0.0
    total_unrealized_profit: float = 0.0
    total_realized_profit: float = 0.0
    total_profit: float = 0.0
    profit_ratio: float = 0.0
    cash_balance: float = 0.0
    available_cash: float = 0.0
    position_count: int = 0
    last_update: datetime = field(default_factory=datetime.now)
    positions: Dict[str, PositionSnapshot] = field(default_factory=dict)


@dataclass
class MTMUpdate:
    """市值更新事件"""

    position_id: str
    symbol: str
    old_price: float
    new_price: float
    old_market_value: float
    new_market_value: float
    profit_change: float
    timestamp: datetime = field(default_factory=datetime.now)


class PositionMTMEngine:
    """
    持仓市值实时计算引擎

    负责：
    1. 接收实时行情数据
    2. 计算持仓市值（Mark-to-Market）
    3. 计算未实现盈亏和盈亏比例
    4. 生成市值更新事件
    5. 批量更新和性能优化
    """

    def __init__(
        self,
        update_interval: float = 0.1,
        enable_batching: bool = True,
        batch_size: int = 100,
        batch_timeout: float = 0.05,
    ):
        """
        初始化 MTM 引擎

        Args:
            update_interval: 更新间隔（秒）
            enable_batching: 是否启用批量更新
            batch_size: 批量大小
            batch_timeout: 批量超时时间
        """
        self.update_interval = update_interval
        self.enable_batching = enable_batching
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout

        self.positions: Dict[str, PositionSnapshot] = {}
        self.portfolios: Dict[str, PortfolioSnapshot] = {}
        self.symbol_to_position: Dict[str, str] = {}

        self.price_cache: Dict[str, float] = {}
        self.price_history: Dict[str, List[float]] = defaultdict(list)

        self.listeners: List[callable] = []

        self._update_queue: List[MTMUpdate] = []
        self._last_flush: datetime = datetime.now()

        self._lock = asyncio.Lock()

        self.metrics = {
            "total_updates": 0,
            "batches_processed": 0,
            "listeners_notified": 0,
            "last_update_time": None,
        }

        logger.info(
            "✅ MTM Engine initialized",
            update_interval=update_interval,
            batching_enabled=enable_batching,
        )

    def register_position(
        self,
        position_id: str,
        portfolio_id: str,
        symbol: str,
        quantity: int,
        avg_price: float,
        realized_profit: float = 0.0,
    ) -> PositionSnapshot:
        """注册持仓"""
        snapshot = PositionSnapshot(
            position_id=position_id,
            portfolio_id=portfolio_id,
            symbol=symbol,
            quantity=quantity,
            avg_price=avg_price,
            realized_profit=realized_profit,
            market_price=avg_price,
        )

        self.positions[position_id] = snapshot
        self.symbol_to_position[symbol] = position_id

        if portfolio_id not in self.portfolios:
            self.portfolios[portfolio_id] = PortfolioSnapshot(portfolio_id=portfolio_id)

        self.portfolios[portfolio_id].positions[position_id] = snapshot

        logger.info(
            "✅ Position registered",
            position_id=position_id,
            symbol=symbol,
            quantity=quantity,
            avg_price=avg_price,
        )

        return snapshot

    def unregister_position(self, position_id: str) -> bool:
        """注销持仓"""
        if position_id not in self.positions:
            return False

        position = self.positions.pop(position_id)
        self.symbol_to_position.pop(position.symbol, None)

        if position.portfolio_id in self.portfolios:
            portfolio = self.portfolios[position.portfolio_id]
            portfolio.positions.pop(position_id, None)

        logger.info("✅ Position unregistered", position_id=position_id)
        return True

    def update_price(self, symbol: str, price: float) -> List[MTMUpdate]:
        """
        更新持仓价格

        Args:
            symbol: 股票代码
            price: 最新价格

        Returns:
            List[MTMUpdate]: 市值更新列表
        """
        updates = []

        self.price_cache[symbol] = price

        if symbol in self.price_history:
            self.price_history[symbol].append(price)
            if len(self.price_history[symbol]) > 100:
                self.price_history[symbol].pop(0)

        position_id = self.symbol_to_position.get(symbol)
        if position_id and position_id in self.positions:
            position = self.positions[position_id]
            old_price = position.market_price
            old_market_value = position.market_value

            position.market_price = price
            position.market_value = abs(position.quantity) * price
            position.last_update = datetime.now()

            if position.quantity > 0:
                position.unrealized_profit = (price - position.avg_price) * position.quantity
                position.profit_ratio = (
                    ((price - position.avg_price) / position.avg_price) * 100 if position.avg_price > 0 else 0
                )
            else:
                position.unrealized_profit = (position.avg_price - price) * abs(position.quantity)
                position.profit_ratio = (
                    ((position.avg_price - price) / position.avg_price) * 100 if position.avg_price > 0 else 0
                )

            position.total_profit = position.realized_profit + position.unrealized_profit
            position.price_change = price - old_price
            position.price_change_percent = (price - old_price) / old_price * 100 if old_price > 0 else 0

            update = MTMUpdate(
                position_id=position_id,
                symbol=symbol,
                old_price=old_price,
                new_price=price,
                old_market_value=old_market_value,
                new_market_value=position.market_value,
                profit_change=position.unrealized_profit - (old_market_value - abs(position.quantity) * old_price),
            )
            updates.append(update)

            self.metrics["total_updates"] += 1
            self.metrics["last_update_time"] = datetime.now()

        return updates

    async def update_price_batch(self, prices: Dict[str, float]) -> List[MTMUpdate]:
        """
        批量更新价格

        Args:
            prices: 股票代码 -> 价格 映射

        Returns:
            List[MTMUpdate]: 市值更新列表
        """
        all_updates = []

        async with self._lock:
            for symbol, price in prices.items():
                updates = self.update_price(symbol, price)
                all_updates.extend(updates)

            if all_updates and self.enable_batching:
                self._update_queue.extend(all_updates)

                now = datetime.now()
                if (
                    len(self._update_queue) >= self.batch_size
                    or (now - self._last_flush).total_seconds() >= self.batch_timeout
                ):
                    await self._flush_updates()

        return all_updates

    async def _flush_updates(self):
        """刷新更新队列"""
        if not self._update_queue:
            return

        updates = list(self._update_queue)
        self._update_queue.clear()
        self._last_flush = datetime.now()

        self.metrics["batches_processed"] += 1

        for listener in self.listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(updates)
                else:
                    listener(updates)
                self.metrics["listeners_notified"] += 1
            except Exception as e:
                logger.error("Error notifying listener: %(e)s")

    def add_listener(self, listener: callable):
        """添加市值更新监听器"""
        self.listeners.append(listener)
        logger.info("✅ Listener added: {listener.__name__")

    def remove_listener(self, listener: callable):
        """移除市值更新监听器"""
        if listener in self.listeners:
            self.listeners.remove(listener)

    def get_position_snapshot(self, position_id: str) -> Optional[PositionSnapshot]:
        """获取持仓快照"""
        return self.positions.get(position_id)

    def get_portfolio_snapshot(self, portfolio_id: str) -> Optional[PortfolioSnapshot]:
        """获取投资组合快照"""
        if portfolio_id not in self.portfolios:
            return None

        portfolio = self.portfolios[portfolio_id]

        total_market_value = sum(p.market_value for p in portfolio.positions.values())
        total_cost = sum(abs(p.quantity) * p.avg_price for p in portfolio.positions.values())
        total_unrealized_profit = sum(p.unrealized_profit for p in portfolio.positions.values())
        total_realized_profit = sum(p.realized_profit for p in portfolio.positions.values())

        portfolio.total_market_value = total_market_value
        portfolio.total_cost = total_cost
        portfolio.total_unrealized_profit = total_unrealized_profit
        portfolio.total_realized_profit = total_realized_profit
        portfolio.total_profit = total_realized_profit + total_unrealized_profit
        portfolio.profit_ratio = (portfolio.total_profit / total_cost * 100) if total_cost > 0 else 0
        portfolio.position_count = len(portfolio.positions)
        portfolio.last_update = datetime.now()

        return portfolio

    def get_all_portfolio_snapshots(self) -> Dict[str, PortfolioSnapshot]:
        """获取所有投资组合快照"""
        return {portfolio_id: self.get_portfolio_snapshot(portfolio_id) for portfolio_id in self.portfolios}

    def get_metrics(self) -> Dict[str, Any]:
        """获取引擎指标"""
        return {
            **self.metrics,
            "position_count": len(self.positions),
            "portfolio_count": len(self.portfolios),
            "cached_symbols": len(self.price_cache),
            "queue_size": len(self._update_queue),
        }

    def get_positions_by_symbol(self, symbol: str) -> List[PositionSnapshot]:
        """根据股票代码获取持仓"""
        position_id = self.symbol_to_position.get(symbol)
        if position_id and position_id in self.positions:
            return [self.positions[position_id]]
        return []


_global_mtm_engine: Optional[PositionMTMEngine] = None


def get_mtm_engine() -> PositionMTMEngine:
    """获取全局 MTM 引擎实例"""
    global _global_mtm_engine
    if _global_mtm_engine is None:
        _global_mtm_engine = PositionMTMEngine()
    return _global_mtm_engine


def reset_mtm_engine() -> None:
    """重置 MTM 引擎（仅用于测试）"""
    global _global_mtm_engine
    _global_mtm_engine = None
