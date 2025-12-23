"""
账户管理器 - Account Manager

功能：
1. 资金管理（现金、持仓）
2. 交易执行（买入、卖出）
3. 成本计算（佣金、印花税）
4. 历史追踪

作者: JohnC & Claude
版本: 3.1.0 (Simplified MVP)
"""

from typing import Dict, List


class Account:
    """
    账户管理器（简化版）

    核心功能：
    - 资金和持仓追踪
    - 真实交易成本（佣金+印花税）
    - 完整交易历史

    示例：
        >>> account = Account(init_cash=1000000)
        >>> account.buy('600000', 100, 10.50, '2024-01-15')
        >>> account.sell('600000', 50, 10.80, '2024-01-16')
        >>> print(account.get_portfolio_value({'600000': 10.90}))
    """

    def __init__(
        self,
        init_cash: float = 1000000,
        commission_rate: float = 0.0003,
        stamp_tax_rate: float = 0.001,
    ):
        """
        初始化账户

        Args:
            init_cash: 初始资金（默认100万）
            commission_rate: 佣金率（默认0.03%，买卖双向）
            stamp_tax_rate: 印花税率（默认0.1%，仅卖出）
        """
        self.init_cash = init_cash
        self.cash = init_cash
        self.commission_rate = commission_rate
        self.stamp_tax_rate = stamp_tax_rate

        # 持仓：{股票代码: 数量}
        self.positions: Dict[str, int] = {}

        # 交易历史
        self.history: List[Dict] = []

        # 统计
        self.total_commission = 0.0
        self.total_stamp_tax = 0.0
        self.trade_count = 0

    def buy(self, symbol: str, amount: int, price: float, timestamp: str):
        """
        买入股票

        Args:
            symbol: 股票代码
            amount: 买入数量（正整数）
            price: 成交价格
            timestamp: 交易时间

        Raises:
            ValueError: 资金不足
        """
        # 计算成本
        stock_value = amount * price
        commission = stock_value * self.commission_rate
        # 佣金有最低5元限制
        commission = max(commission, 5.0)
        total_cost = stock_value + commission

        # 检查资金
        if total_cost > self.cash:
            raise ValueError(
                f"❌ 资金不足: 需要{total_cost:.2f}元, " f"可用{self.cash:.2f}元"
            )

        # 执行买入
        self.cash -= total_cost
        self.positions[symbol] = self.positions.get(symbol, 0) + amount

        # 更新统计
        self.total_commission += commission
        self.trade_count += 1

        # 记录历史
        self.history.append(
            {
                "timestamp": timestamp,
                "symbol": symbol,
                "direction": "buy",
                "amount": amount,
                "price": price,
                "stock_value": stock_value,
                "commission": commission,
                "stamp_tax": 0.0,
                "total_cost": total_cost,
                "cash_after": self.cash,
            }
        )

        print(
            f"✅ 买入 {symbol} {amount}股 @{price:.2f}元 "
            f"成本{total_cost:.2f}元（含佣金{commission:.2f}元）"
        )

    def sell(self, symbol: str, amount: int, price: float, timestamp: str):
        """
        卖出股票

        Args:
            symbol: 股票代码
            amount: 卖出数量（正整数）
            price: 成交价格
            timestamp: 交易时间

        Raises:
            ValueError: 持仓不足
        """
        # 检查持仓
        if symbol not in self.positions or self.positions[symbol] < amount:
            current = self.positions.get(symbol, 0)
            raise ValueError(
                f"❌ 持仓不足: {symbol} 需要{amount}股, " f"持有{current}股"
            )

        # 计算收入
        stock_value = amount * price
        commission = stock_value * self.commission_rate
        commission = max(commission, 5.0)  # 最低5元
        stamp_tax = stock_value * self.stamp_tax_rate  # 印花税（仅卖出）
        total_revenue = stock_value - commission - stamp_tax

        # 执行卖出
        self.cash += total_revenue
        self.positions[symbol] -= amount

        # 如果持仓为0，删除记录
        if self.positions[symbol] == 0:
            del self.positions[symbol]

        # 更新统计
        self.total_commission += commission
        self.total_stamp_tax += stamp_tax
        self.trade_count += 1

        # 记录历史
        self.history.append(
            {
                "timestamp": timestamp,
                "symbol": symbol,
                "direction": "sell",
                "amount": amount,
                "price": price,
                "stock_value": stock_value,
                "commission": commission,
                "stamp_tax": stamp_tax,
                "total_revenue": total_revenue,
                "cash_after": self.cash,
            }
        )

        print(
            f"✅ 卖出 {symbol} {amount}股 @{price:.2f}元 "
            f"收入{total_revenue:.2f}元（扣佣金{commission:.2f}元+印花税{stamp_tax:.2f}元）"
        )

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        计算组合总价值（现金+持仓市值）

        Args:
            current_prices: 当前价格字典 {股票代码: 价格}

        Returns:
            组合总价值
        """
        # 计算持仓市值
        stock_value = sum(
            self.positions[symbol] * current_prices.get(symbol, 0)
            for symbol in self.positions
        )

        return self.cash + stock_value

    def get_returns(self, current_prices: Dict[str, float]) -> float:
        """
        计算收益率

        Args:
            current_prices: 当前价格字典

        Returns:
            收益率（小数，如0.15表示15%）
        """
        current_value = self.get_portfolio_value(current_prices)
        return (current_value - self.init_cash) / self.init_cash

    def get_position_info(self) -> Dict:
        """获取当前持仓信息"""
        return {
            "cash": self.cash,
            "positions": self.positions.copy(),
            "position_count": len(self.positions),
        }

    def get_cost_summary(self) -> Dict:
        """获取交易成本汇总"""
        return {
            "total_commission": self.total_commission,
            "total_stamp_tax": self.total_stamp_tax,
            "total_cost": self.total_commission + self.total_stamp_tax,
            "trade_count": self.trade_count,
            "avg_cost_per_trade": (self.total_commission + self.total_stamp_tax)
            / max(self.trade_count, 1),
        }
