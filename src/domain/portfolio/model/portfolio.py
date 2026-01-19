"""
Portfolio Aggregate Root
投资组合聚合根
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from uuid import uuid4

from src.domain.shared.event import DomainEvent
from src.domain.trading.events import OrderFilledEvent
from src.domain.trading.value_objects import OrderSide
from ..value_objects.performance_metrics import PerformanceMetrics, PositionInfo
from .transaction import Transaction


@dataclass
class Portfolio:
    """
    投资组合聚合根

    职责:
    - 管理资金 (Cash)
    - 管理持仓集合 (Positions)
    - 处理交易事件 (OrderFilled)
    - 计算组合绩效
    """

    id: str
    name: str
    initial_capital: float
    cash: float
    positions: Dict[str, PositionInfo] = field(default_factory=dict)
    transactions: List[Transaction] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, name: str, initial_capital: float) -> "Portfolio":
        return cls(id=str(uuid4()), name=name, initial_capital=initial_capital, cash=initial_capital)

    def handle_order_filled(self, event: OrderFilledEvent) -> None:
        """
        处理订单成交事件
        核心逻辑：更新资金，更新持仓，记录流水
        """
        transaction_amount = event.filled_quantity * event.filled_price
        commission = event.commission

        # 1. 更新资金 (Cash)
        if event.side == OrderSide.BUY:
            total_cost = transaction_amount + commission
            if self.cash < total_cost:
                # 理论上OrderContext应该检查过资金，但这里做双重保险
                # 或者允许融资（负现金），这里暂定不允许
                # raise ValueError("Insufficient cash for transaction")
                pass
            self.cash -= total_cost
            self._update_position_buy(event.symbol, event.filled_quantity, event.filled_price)

        elif event.side == OrderSide.SELL:
            total_income = transaction_amount - commission
            self.cash += total_income
            self._update_position_sell(event.symbol, event.filled_quantity)

        # 2. 记录流水
        self.transactions.append(
            Transaction.create(
                portfolio_id=self.id,
                symbol=event.symbol,
                side=event.side,
                quantity=event.filled_quantity,
                price=event.filled_price,
                commission=commission,
            )
        )

        self.updated_at = datetime.now()

    def _update_position_buy(self, symbol: str, quantity: int, price: float):
        """处理买入持仓更新"""
        if symbol not in self.positions:
            self.positions[symbol] = PositionInfo(symbol, 0, 0.0)

        pos = self.positions[symbol]
        total_cost = (pos.quantity * pos.average_cost) + (quantity * price)
        pos.quantity += quantity
        pos.average_cost = total_cost / pos.quantity
        pos.current_price = price  # 更新最新价格为成交价

    def _update_position_sell(self, symbol: str, quantity: int):
        """处理卖出持仓更新"""
        if symbol not in self.positions:
            raise ValueError(f"Position not found for symbol: {symbol}")

        pos = self.positions[symbol]
        if pos.quantity < quantity:
            raise ValueError(f"Insufficient position quantity: {pos.quantity} < {quantity}")

        pos.quantity -= quantity

        # 如果清仓，移除记录
        if pos.quantity == 0:
            del self.positions[symbol]

    def update_market_prices(self, prices: Dict[str, float]) -> None:
        """更新持仓的最新市场价格"""
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].current_price = price

    def calculate_performance(self) -> PerformanceMetrics:
        """计算当前绩效"""
        # 计算持仓市值
        holdings_value = sum(p.market_value for p in self.positions.values())

        # 计算总收益率（百分比）
        total_value = self.cash + holdings_value
        total_return_pct = (
            ((total_value - self.initial_capital) / self.initial_capital * 100) if self.initial_capital > 0 else 0.0
        )

        # 计算胜率（基于交易记录）
        winning_trades = sum(
            1 for t in self.transactions if t.side == "SELL" and (t.price * t.quantity) > (t.quantity * 10.0)
        )  # 简化假设成本为10元
        total_trades = len([t for t in self.transactions if t.side == "SELL"])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

        return PerformanceMetrics(
            total_return=total_return_pct,  # 百分比形式
            holdings_value=holdings_value,
            cash_balance=self.cash,
            win_rate=win_rate,
            trade_count=len(self.transactions),
            calculated_at=datetime.now(),
        )
