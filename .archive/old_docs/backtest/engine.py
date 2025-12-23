"""
回测引擎 - Backtest Engine

功能：
1. 整合Exchange和Account
2. 执行策略回测
3. 生成回测报告

作者: JohnC & Claude
版本: 3.1.0 (Simplified MVP)
"""

from typing import Dict, List
import pandas as pd
from .exchange import Exchange
from .account import Account


class BacktestEngine:
    """
    回测引擎（简化版）

    核心功能：
    - 按时间步执行策略
    - 自动撮合订单
    - 追踪账户状态
    - 生成每日报告

    示例：
        >>> engine = BacktestEngine(
        ...     strategy=my_strategy,
        ...     data_provider=data_provider,
        ...     start_date='2024-01-01',
        ...     end_date='2024-12-31'
        ... )
        >>> results = engine.run()
        >>> print(results['metrics'])
    """

    def __init__(
        self,
        strategy,
        data_provider,
        start_date: str,
        end_date: str,
        init_cash: float = 1000000,
        commission_rate: float = 0.0003,
        stamp_tax_rate: float = 0.001,
        slippage_rate: float = 0.001,
    ):
        """
        初始化回测引擎

        Args:
            strategy: 策略对象（需实现generate_decision方法）
            data_provider: 数据提供者
            start_date: 回测开始日期
            end_date: 回测结束日期
            init_cash: 初始资金
            commission_rate: 佣金率
            stamp_tax_rate: 印花税率
            slippage_rate: 滑点率
        """
        self.strategy = strategy
        self.data_provider = data_provider
        self.start_date = start_date
        self.end_date = end_date

        # 创建Exchange和Account
        self.exchange = Exchange(data_provider, slippage_rate)
        self.account = Account(init_cash, commission_rate, stamp_tax_rate)

        # 回测结果
        self.daily_results: List[Dict] = []

    def run(self) -> Dict:
        """
        执行回测

        Returns:
            回测结果字典：{
                'daily_results': DataFrame,
                'trades': List[Dict],
                'metrics': Dict,
                'cost_summary': Dict
            }
        """
        print(f"\n{'='*60}")
        print(f"🚀 开始回测: {self.start_date} → {self.end_date}")
        print(f"💰 初始资金: {self.account.init_cash:,.0f}元")
        print(f"{'='*60}\n")

        # 获取交易日历
        trade_dates = self.data_provider.get_calendar(self.start_date, self.end_date)

        # 逐日回测
        for i, date in enumerate(trade_dates):
            # 1. 获取市场数据
            market_data = self.data_provider.get_market_data(date)
            if market_data is None or len(market_data) == 0:
                continue

            # 2. 策略生成决策
            decision = self.strategy.generate_decision(market_data, self.account)

            # 3. 执行订单
            if decision and hasattr(decision, "orders"):
                for order in decision.orders:
                    try:
                        # 撮合订单
                        filled = self.exchange.match_order(order, date)
                        if filled is None:
                            continue

                        # 执行交易
                        if filled["direction"] == "buy":
                            self.account.buy(
                                filled["symbol"],
                                filled["amount"],
                                filled["price"],
                                date,
                            )
                        else:  # sell
                            self.account.sell(
                                filled["symbol"],
                                filled["amount"],
                                filled["price"],
                                date,
                            )
                    except ValueError as e:
                        print(f"⚠️ 交易失败: {e}")

            # 4. 计算当日组合价值
            current_prices = {
                symbol: market_data[symbol]["close"] for symbol in market_data
            }
            portfolio_value = self.account.get_portfolio_value(current_prices)
            returns = self.account.get_returns(current_prices)

            # 5. 记录每日状态
            self.daily_results.append(
                {
                    "date": date,
                    "cash": self.account.cash,
                    "portfolio_value": portfolio_value,
                    "returns": returns,
                    "positions": self.account.positions.copy(),
                }
            )

            # 进度显示
            if (i + 1) % 50 == 0 or (i + 1) == len(trade_dates):
                print(
                    f"📊 进度: {i+1}/{len(trade_dates)} "
                    f"({(i+1)/len(trade_dates)*100:.1f}%) "
                    f"| 组合价值: {portfolio_value:,.0f}元 "
                    f"| 收益率: {returns*100:.2f}%"
                )

        # 生成回测报告
        return self._generate_report()

    def _generate_report(self) -> Dict:
        """生成回测报告"""
        df = pd.DataFrame(self.daily_results)

        # 获取成本汇总
        cost_summary = self.account.get_cost_summary()

        print(f"\n{'='*60}")
        print("📈 回测完成")
        print(f"{'='*60}")
        print(f"💵 最终资金: {self.account.cash:,.0f}元")
        print(f"📦 持仓品种: {len(self.account.positions)}个")
        print(f"📊 总收益率: {df['returns'].iloc[-1]*100:.2f}%")
        print(f"💸 交易成本: {cost_summary['total_cost']:,.2f}元")
        print(f"   ├─ 佣金: {cost_summary['total_commission']:,.2f}元")
        print(f"   └─ 印花税: {cost_summary['total_stamp_tax']:,.2f}元")
        print(f"🔄 交易次数: {cost_summary['trade_count']}次")
        print(f"{'='*60}\n")

        return {
            "daily_results": df,
            "trades": self.account.history,
            "metrics": {
                "total_return": df["returns"].iloc[-1],
                "final_value": df["portfolio_value"].iloc[-1],
                "total_cost": cost_summary["total_cost"],
                "trade_count": cost_summary["trade_count"],
            },
            "cost_summary": cost_summary,
        }
