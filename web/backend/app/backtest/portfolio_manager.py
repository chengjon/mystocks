"""
Portfolio Manager

管理回测过程中的持仓、资金和PnL计算
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.backtest.events import FillEvent, MarketEvent


class Position:
    """持仓信息"""

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity = 0  # 持仓数量（正数=多头，负数=空头）
        self.avg_cost = Decimal("0")  # 平均成本
        self.market_value = Decimal("0")  # 市值
        self.unrealized_pnl = Decimal("0")  # 未实现盈亏
        self.realized_pnl = Decimal("0")  # 已实现盈亏

    def update_market_value(self, current_price: Decimal):
        """更新市值和未实现盈亏"""
        if self.quantity != 0:
            self.market_value = Decimal(self.quantity) * current_price
            self.unrealized_pnl = self.market_value - (Decimal(self.quantity) * self.avg_cost)
        else:
            self.market_value = Decimal("0")
            self.unrealized_pnl = Decimal("0")

    def add_position(self, quantity: int, price: Decimal, commission: Decimal):
        """
        增加持仓

        Args:
            quantity: 数量（正数=买入，负数=卖出）
            price: 价格
            commission: 手续费
        """
        if self.quantity == 0:
            # 新开仓
            self.quantity = quantity
            self.avg_cost = price
        elif (self.quantity > 0 and quantity > 0) or (self.quantity < 0 and quantity < 0):
            # 加仓（同向）
            total_cost = (Decimal(self.quantity) * self.avg_cost) + (Decimal(quantity) * price)
            self.quantity += quantity
            self.avg_cost = total_cost / Decimal(self.quantity)
        else:
            # 减仓或反向开仓
            if abs(quantity) < abs(self.quantity):
                # 减仓
                realized = (price - self.avg_cost) * Decimal(abs(quantity))
                if self.quantity < 0:  # 空头平仓
                    realized = -realized
                self.realized_pnl += realized
                self.quantity += quantity
            elif abs(quantity) == abs(self.quantity):
                # 平仓
                realized = (price - self.avg_cost) * Decimal(abs(self.quantity))
                if self.quantity < 0:
                    realized = -realized
                self.realized_pnl += realized
                self.quantity = 0
                self.avg_cost = Decimal("0")
            else:
                # 平仓后反向开仓
                close_qty = -self.quantity
                realized = (price - self.avg_cost) * Decimal(abs(close_qty))
                if self.quantity < 0:
                    realized = -realized
                self.realized_pnl += realized

                # 反向开仓
                new_qty = quantity + self.quantity
                self.quantity = new_qty
                self.avg_cost = price

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "avg_cost": float(self.avg_cost),
            "market_value": float(self.market_value),
            "unrealized_pnl": float(self.unrealized_pnl),
            "realized_pnl": float(self.realized_pnl),
        }


class PortfolioManager:
    """
    组合管理器

    管理回测过程中的持仓、资金和交易记录
    """

    def __init__(
        self,
        initial_capital: Decimal,
        commission_rate: Decimal = Decimal("0.0003"),
        slippage_rate: Decimal = Decimal("0.001"),
    ):
        """
        初始化组合管理器

        Args:
            initial_capital: 初始资金
            commission_rate: 手续费率（默认0.03%）
            slippage_rate: 滑点率（默认0.1%）
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate

        # 资金状态
        self.cash = initial_capital  # 现金
        self.equity = initial_capital  # 总资产
        self.margin_used = Decimal("0")  # 保证金使用

        # 持仓管理
        self.positions: Dict[str, Position] = {}  # symbol -> Position
        self.current_prices: Dict[str, Decimal] = {}  # symbol -> current_price

        # 历史记录
        self.equity_curve: List[Dict[str, Any]] = []
        self.trades: List[Dict[str, Any]] = []

        # 统计
        self.total_commission = Decimal("0")
        self.total_slippage = Decimal("0")

    def update_market_data(self, market_event: MarketEvent):
        """
        更新市场数据

        Args:
            market_event: 市场数据事件
        """
        self.current_prices[market_event.symbol] = market_event.close

        # 更新持仓的市值
        if market_event.symbol in self.positions:
            self.positions[market_event.symbol].update_market_value(market_event.close)

        # 更新总资产
        self._update_equity()

    def process_fill(self, fill_event: FillEvent) -> bool:
        """
        处理成交事件

        Args:
            fill_event: 成交事件

        Returns:
            是否成功处理
        """
        symbol = fill_event.symbol
        action = fill_event.action
        quantity = fill_event.quantity
        fill_price = fill_event.fill_price
        commission = fill_event.commission

        # 检查资金是否足够
        required_cash = fill_price * Decimal(quantity) + commission
        if action == "BUY" and required_cash > self.cash:
            # 资金不足
            return False

        # 更新持仓
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol)

        position = self.positions[symbol]

        # 计算数量（买入为正，卖出为负）
        qty_change = quantity if action == "BUY" else -quantity

        # 更新持仓
        position.add_position(qty_change, fill_price, commission)

        # 更新现金
        if action == "BUY":
            self.cash -= required_cash
        else:  # SELL
            self.cash += (fill_price * Decimal(quantity)) - commission

        # 统计手续费和滑点
        self.total_commission += commission
        self.total_slippage += fill_event.slippage

        # 记录交易
        self.trades.append(
            {
                "symbol": symbol,
                "trade_date": fill_event.trade_date,
                "action": action,
                "quantity": quantity,
                "price": float(fill_price),
                "amount": float(fill_price * Decimal(quantity)),
                "commission": float(commission),
                "profit_loss": float(position.realized_pnl) if action == "SELL" else None,
            }
        )

        # 更新总资产
        self._update_equity()

        return True

    def _update_equity(self):
        """更新总资产"""
        # 计算持仓市值
        total_market_value = sum(pos.market_value for pos in self.positions.values())

        # 总资产 = 现金 + 持仓市值
        self.equity = self.cash + total_market_value

    def record_equity_curve(self, trade_date: datetime):
        """
        记录资金曲线

        Args:
            trade_date: 交易日期
        """
        # 计算回撤
        if len(self.equity_curve) == 0:
            peak_equity = self.equity
            drawdown = Decimal("0")
        else:
            peak_equity = max(self.equity, max(point["equity"] for point in self.equity_curve))
            drawdown = (peak_equity - self.equity) / peak_equity if peak_equity > 0 else Decimal("0")

        self.equity_curve.append(
            {
                "trade_date": trade_date,
                "equity": self.equity,
                "cash": self.cash,
                "drawdown": drawdown,
                "total_market_value": self.equity - self.cash,
            }
        )

    def get_position(self, symbol: str) -> Optional[Position]:
        """获取持仓"""
        return self.positions.get(symbol)

    def get_all_positions(self) -> List[Dict[str, Any]]:
        """获取所有持仓"""
        return [pos.to_dict() for pos in self.positions.values() if pos.quantity != 0]

    def get_equity_curve(self) -> List[Dict[str, Any]]:
        """获取资金曲线"""
        return self.equity_curve

    def get_trades(self) -> List[Dict[str, Any]]:
        """获取所有交易记录"""
        return self.trades

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """获取组合摘要"""
        total_pnl = self.equity - self.initial_capital
        total_return = (total_pnl / self.initial_capital) if self.initial_capital > 0 else Decimal("0")

        return {
            "initial_capital": float(self.initial_capital),
            "current_equity": float(self.equity),
            "cash": float(self.cash),
            "total_pnl": float(total_pnl),
            "total_return": float(total_return),
            "total_commission": float(self.total_commission),
            "total_slippage": float(self.total_slippage),
            "num_positions": len([p for p in self.positions.values() if p.quantity != 0]),
            "num_trades": len(self.trades),
        }

    def calculate_position_size(
        self,
        symbol: str,
        signal_strength: float,
        max_position_size: float,
        current_price: Decimal,
    ) -> int:
        """
        计算仓位大小

        Args:
            symbol: 股票代码
            signal_strength: 信号强度 (0-1)
            max_position_size: 最大仓位比例
            current_price: 当前价格

        Returns:
            应该买入的数量
        """
        # 可用资金
        available_cash = self.cash * Decimal(max_position_size) * Decimal(signal_strength)

        # 计算数量（向下取整到100的倍数，A股最小交易单位）
        quantity = int(available_cash / current_price / 100) * 100

        return max(0, quantity)

    def can_open_position(self, required_cash: Decimal) -> bool:
        """检查是否有足够资金开仓"""
        return self.cash >= required_cash

    def reset(self):
        """重置组合状态（用于新的回测）"""
        self.cash = self.initial_capital
        self.equity = self.initial_capital
        self.margin_used = Decimal("0")
        self.positions.clear()
        self.current_prices.clear()
        self.equity_curve.clear()
        self.trades.clear()
        self.total_commission = Decimal("0")
        self.total_slippage = Decimal("0")
