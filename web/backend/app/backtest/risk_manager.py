"""
Risk Manager

风险管理器，负责仓位控制、止损止盈检查等风险管理功能
"""

from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from app.backtest.events import OrderEvent
from app.backtest.portfolio_manager import PortfolioManager, Position


class RiskManager:
    """
    风险管理器

    检查和控制交易风险
    """

    def __init__(
        self,
        max_position_size: float = 0.1,  # 单个股票最大仓位比例
        max_total_position: float = 0.95,  # 总仓位上限
        stop_loss_pct: Optional[float] = None,  # 止损比例
        take_profit_pct: Optional[float] = None,  # 止盈比例
        max_daily_loss: Optional[float] = None,  # 单日最大亏损
        max_drawdown: Optional[float] = None,  # 最大回撤限制
    ):
        """
        初始化风险管理器

        Args:
            max_position_size: 单个股票最大仓位比例（默认10%）
            max_total_position: 总仓位上限（默认95%）
            stop_loss_pct: 止损比例（如0.05表示5%止损）
            take_profit_pct: 止盈比例（如0.10表示10%止盈）
            max_daily_loss: 单日最大亏损比例
            max_drawdown: 最大回撤限制
        """
        self.max_position_size = max_position_size
        self.max_total_position = max_total_position
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown

        # 每日统计
        self.daily_pnl: Dict[datetime, Decimal] = {}
        self.current_date: Optional[datetime] = None

    def validate_order(
        self, order: OrderEvent, portfolio: PortfolioManager, current_price: Decimal
    ) -> tuple[bool, Optional[str]]:
        """
        验证订单是否符合风险控制要求

        Args:
            order: 订单事件
            portfolio: 组合管理器
            current_price: 当前价格

        Returns:
            (是否通过, 拒绝原因)
        """
        # 1. 检查仓位限制
        if order.action == "BUY":
            position_check = self._check_position_limit(order, portfolio, current_price)
            if not position_check[0]:
                return position_check

        # 2. 检查资金是否充足
        if order.action == "BUY":
            cash_check = self._check_cash_available(order, portfolio, current_price)
            if not cash_check[0]:
                return cash_check

        # 3. 检查每日亏损限制
        if self.max_daily_loss:
            daily_loss_check = self._check_daily_loss_limit(portfolio)
            if not daily_loss_check[0]:
                return daily_loss_check

        # 4. 检查最大回撤限制
        if self.max_drawdown:
            drawdown_check = self._check_max_drawdown(portfolio)
            if not drawdown_check[0]:
                return drawdown_check

        return True, None

    def _check_position_limit(
        self, order: OrderEvent, portfolio: PortfolioManager, current_price: Decimal
    ) -> tuple[bool, Optional[str]]:
        """检查仓位限制"""
        # 计算订单金额
        order_value = current_price * Decimal(order.quantity)

        # 单个股票仓位限制
        max_single_value = portfolio.equity * Decimal(self.max_position_size)
        current_position = portfolio.get_position(order.symbol)
        current_value = current_position.market_value if current_position else Decimal("0")

        if current_value + order_value > max_single_value:
            return False, f"超过单股票最大仓位限制 ({self.max_position_size * 100}%)"

        # 总仓位限制
        total_position_value = sum(pos.market_value for pos in portfolio.positions.values())
        max_total_value = portfolio.equity * Decimal(self.max_total_position)

        if total_position_value + order_value > max_total_value:
            return False, f"超过总仓位上限 ({self.max_total_position * 100}%)"

        return True, None

    def _check_cash_available(
        self, order: OrderEvent, portfolio: PortfolioManager, current_price: Decimal
    ) -> tuple[bool, Optional[str]]:
        """检查现金是否充足"""
        # 估算手续费
        estimated_commission = current_price * Decimal(order.quantity) * portfolio.commission_rate
        required_cash = current_price * Decimal(order.quantity) + estimated_commission

        if portfolio.cash < required_cash:
            return (
                False,
                f"现金不足（需要{float(required_cash):.2f}，可用{float(portfolio.cash):.2f}）",
            )

        return True, None

    def _check_daily_loss_limit(self, portfolio: PortfolioManager) -> tuple[bool, Optional[str]]:
        """检查每日亏损限制"""
        if not self.max_daily_loss:
            return True, None

        # 计算今日盈亏
        today_equity = portfolio.equity
        if len(portfolio.equity_curve) > 0:
            yesterday_equity = portfolio.equity_curve[-1]["equity"]
            daily_pnl = today_equity - yesterday_equity
            daily_return = daily_pnl / yesterday_equity if yesterday_equity > 0 else Decimal("0")

            if daily_return < Decimal(-self.max_daily_loss):
                return False, f"触发单日最大亏损限制 ({self.max_daily_loss * 100}%)"

        return True, None

    def _check_max_drawdown(self, portfolio: PortfolioManager) -> tuple[bool, Optional[str]]:
        """检查最大回撤限制"""
        if not self.max_drawdown or len(portfolio.equity_curve) == 0:
            return True, None

        # 计算当前回撤
        peak_equity = max(point["equity"] for point in portfolio.equity_curve)
        current_drawdown = (peak_equity - portfolio.equity) / peak_equity if peak_equity > 0 else Decimal("0")

        if current_drawdown > Decimal(self.max_drawdown):
            return False, f"触发最大回撤限制 ({self.max_drawdown * 100}%)"

        return True, None

    def check_stop_loss_take_profit(self, symbol: str, position: Position, current_price: Decimal) -> Optional[str]:
        """
        检查止损止盈

        Args:
            symbol: 股票代码
            position: 持仓信息
            current_price: 当前价格

        Returns:
            如果需要平仓，返回原因；否则返回None
        """
        if position.quantity == 0:
            return None

        # 计算收益率
        price_change = (current_price - position.avg_cost) / position.avg_cost
        if position.quantity < 0:  # 空头
            price_change = -price_change

        # 检查止损
        if self.stop_loss_pct and price_change < Decimal(-self.stop_loss_pct):
            return f"触发止损 ({self.stop_loss_pct * 100}%)"

        # 检查止盈
        if self.take_profit_pct and price_change > Decimal(self.take_profit_pct):
            return f"触发止盈 ({self.take_profit_pct * 100}%)"

        return None

    def should_force_close_position(
        self, symbol: str, position: Position, current_price: Decimal
    ) -> tuple[bool, Optional[str]]:
        """
        判断是否应该强制平仓

        Args:
            symbol: 股票代码
            position: 持仓信息
            current_price: 当前价格

        Returns:
            (是否需要平仓, 原因)
        """
        reason = self.check_stop_loss_take_profit(symbol, position, current_price)
        if reason:
            return True, reason

        return False, None

    def update_risk_metrics(self, portfolio: PortfolioManager, trade_date: datetime):
        """
        更新风险指标

        Args:
            portfolio: 组合管理器
            trade_date: 交易日期
        """
        # 更新每日盈亏
        if len(portfolio.equity_curve) > 1:
            yesterday_equity = portfolio.equity_curve[-2]["equity"]
            daily_pnl = portfolio.equity - yesterday_equity
            self.daily_pnl[trade_date] = daily_pnl

        self.current_date = trade_date

    def get_risk_summary(self, portfolio: PortfolioManager) -> Dict[str, Any]:
        """
        获取风险摘要

        Args:
            portfolio: 组合管理器

        Returns:
            风险指标摘要
        """
        # 计算当前仓位比例
        total_position_value = sum(pos.market_value for pos in portfolio.positions.values())
        position_ratio = float(total_position_value / portfolio.equity) if portfolio.equity > 0 else 0.0

        # 计算当前回撤
        if len(portfolio.equity_curve) > 0:
            peak_equity = max(point["equity"] for point in portfolio.equity_curve)
            current_drawdown = float(
                (peak_equity - portfolio.equity) / peak_equity if peak_equity > 0 else Decimal("0")
            )
        else:
            current_drawdown = 0.0

        # 计算今日盈亏
        if len(portfolio.equity_curve) > 1:
            yesterday_equity = portfolio.equity_curve[-2]["equity"]
            daily_pnl = float(portfolio.equity - yesterday_equity)
            daily_return = float(daily_pnl / yesterday_equity) if yesterday_equity > 0 else 0.0
        else:
            daily_pnl = 0.0
            daily_return = 0.0

        return {
            "current_position_ratio": round(position_ratio, 4),
            "max_position_size": self.max_position_size,
            "max_total_position": self.max_total_position,
            "current_drawdown": round(current_drawdown, 4),
            "max_drawdown_limit": self.max_drawdown,
            "daily_pnl": round(daily_pnl, 2),
            "daily_return": round(daily_return, 4),
            "max_daily_loss": self.max_daily_loss,
            "stop_loss_pct": self.stop_loss_pct,
            "take_profit_pct": self.take_profit_pct,
            "num_positions": len([p for p in portfolio.positions.values() if p.quantity != 0]),
        }

    def reset(self):
        """重置风险管理器状态"""
        self.daily_pnl.clear()
        self.current_date = None
