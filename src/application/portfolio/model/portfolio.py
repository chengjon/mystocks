"""
Portfolio Management Aggregate Roots
组合管理聚合根
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.domain.portfolio.value_objects import PerformanceMetrics


@dataclass
class Portfolio:
    """
    投资组合聚合根
    """

    id: str
    name: str
    portfolio_type: str  # real/simulation/research
    description: str = ""
    initial_capital: float = 0.0
    current_value: float = 0.0
    cash: float = 0.0
    holdings: Dict[str, "Holding"] = field(default_factory=dict)
    transactions: List["Transaction"] = field(default_factory=list)
    benchmark_index: str = "000300"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls,
        name: str,
        portfolio_type: str,
        initial_capital: float,
        description: str = "",
        benchmark_index: str = "000300",
    ) -> "Portfolio":
        return cls(
            id=str(uuid4()),
            name=name,
            portfolio_type=portfolio_type,
            initial_capital=initial_capital,
            cash=initial_capital,
            current_value=initial_capital,
            description=description,
            benchmark_index=benchmark_index,
        )

    def add_holding(self, symbol: str, quantity: int, price: float, side: str = "LONG") -> "Holding":
        if symbol in self.holdings:
            raise ValueError(f"持仓 {symbol} 已存在")

        if side == "LONG":
            cost = quantity * price
            if self.cash < cost:
                raise ValueError(f"现金不足，需要 {cost}，可用 {self.cash}")
            self.cash -= cost
        else:
            self.cash += quantity * price

        holding = Holding.create(portfolio_id=self.id, symbol=symbol, quantity=quantity, average_cost=price, side=side)
        self.holdings[symbol] = holding
        self._recalculate_value()
        self.updated_at = datetime.now()
        return holding

    def update_holding(
        self, symbol: str, quantity_change: int, price: float, side: str = "LONG"
    ) -> Optional["Holding"]:
        if symbol not in self.holdings:
            return None

        holding = self.holdings[symbol]
        if side != holding.side:
            raise ValueError("不能改变持仓方向")

        if quantity_change > 0:
            cost = quantity_change * price
            if self.cash < cost:
                raise ValueError("现金不足")
            self.cash -= cost
            holding.add_quantity(quantity_change, price)
        else:
            self.cash += abs(quantity_change) * price
            holding.reduce_quantity(abs(quantity_change))

        self._recalculate_value()
        self.updated_at = datetime.now()
        return holding

    def remove_holding(self, symbol: str) -> bool:
        if symbol not in self.holdings:
            return False

        holding = self.holdings[symbol]
        if holding.quantity > 0:
            self.cash += holding.quantity * holding.current_price
        del self.holdings[symbol]
        self._recalculate_value()
        self.updated_at = datetime.now()
        return True

    def _recalculate_value(self) -> None:
        total_value = self.cash
        for holding in self.holdings.values():
            total_value += holding.market_value
        self.current_value = total_value

    def get_holding(self, symbol: str) -> Optional["Holding"]:
        return self.holdings.get(symbol)

    def get_all_holdings(self) -> List["Holding"]:
        return list(self.holdings.values())

    def get_performance_metrics(self) -> PerformanceMetrics:
        total_return = (
            (self.current_value - self.initial_capital) / self.initial_capital * 100 if self.initial_capital > 0 else 0
        )
        holdings_value = self.current_value - self.cash

        winning_trades = sum(1 for t in self.transactions if t.pnl and t.pnl > 0)
        total_trades = len([t for t in self.transactions if t.pnl is not None])
        win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0

        return PerformanceMetrics(
            total_return=total_return,
            holdings_value=holdings_value,
            cash_balance=self.cash,
            win_rate=win_rate,
            trade_count=total_trades,
        )

    def get_sector_allocation(self) -> Dict[str, float]:
        """获取行业配置占比"""
        sector_map = {}
        for holding in self.holdings.values():
            sector = holding.sector
            value = holding.market_value
            sector_map[sector] = sector_map.get(sector, 0) + value

        total = self.current_value if self.current_value > 0 else 1
        return {k: (v / total * 100) for k, v in sector_map.items()}

    def get_position_concentration(self) -> Dict[str, Any]:
        """获取真实的持仓集中度 (基于资产占比)"""
        if not self.holdings:
            return {"max_position": 0, "top5_concentration": 0}

        # 计算每只票的资产占比
        total = self.current_value if self.current_value > 0 else 1
        weights = sorted([h.market_value / total * 100 for h in self.holdings.values()], reverse=True)

        return {"max_position": weights[0], "top5_concentration": sum(weights[:5])}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.portfolio_type,
            "current_value": self.current_value,
            "cash": self.cash,
            "holdings_count": len(self.holdings),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Holding:
    """持仓实体"""

    id: str
    portfolio_id: str
    symbol: str
    quantity: int
    average_cost: float
    current_price: float = 0.0
    side: str = "LONG"
    sector: str = "未分类"
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> float:
        return self.quantity * self.average_cost

    @property
    def unrealized_pnl(self) -> float:
        return self.market_value - self.cost_basis

    @classmethod
    def create(
        cls, portfolio_id: str, symbol: str, quantity: int, average_cost: float, side: str = "LONG"
    ) -> "Holding":
        return cls(
            id=str(uuid4()),
            portfolio_id=portfolio_id,
            symbol=symbol,
            quantity=quantity,
            average_cost=average_cost,
            side=side,
        )

    def add_quantity(self, quantity: int, price: float) -> None:
        total_cost = self.quantity * self.average_cost + quantity * price
        self.quantity += quantity
        self.average_cost = total_cost / self.quantity
        self.last_updated = datetime.now()

    def reduce_quantity(self, quantity: int) -> None:
        self.quantity = max(0, self.quantity - quantity)
        self.last_updated = datetime.now()

    def update_price(self, price: float) -> None:
        self.current_price = price
        self.last_updated = datetime.now()

    def to_dict(self, total_portfolio_value: float = 0) -> Dict[str, Any]:
        """增强：支持传入总资产以计算权重"""
        weight = (self.market_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "average_cost": self.average_cost,
            "current_price": self.current_price,
            "market_value": self.market_value,
            "unrealized_pnl": self.unrealized_pnl,
            "weight": weight,
            "sector": self.sector,
        }


@dataclass
class Transaction:
    """交易流水"""

    id: str
    portfolio_id: str
    symbol: str
    side: str
    quantity: int
    price: float
    commission: float = 0.0
    pnl: float = None
    timestamp: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls,
        portfolio_id: str,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        commission: float = 0.0,
        pnl: float = None,
    ) -> "Transaction":
        return cls(
            id=str(uuid4()),
            portfolio_id=portfolio_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            commission=commission,
            pnl=pnl,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.price,
            "pnl": self.pnl,
            "timestamp": self.timestamp.isoformat(),
        }
