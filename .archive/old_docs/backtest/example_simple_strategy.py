"""
简单策略示例 - 演示回测系统使用

策略：简单的买入持有策略
- 第一天买入前10只股票
- 最后一天全部卖出

作者: JohnC & Claude
版本: 3.1.0 (Simplified MVP)
"""

from typing import Dict


class TradeDecision:
    """交易决策对象"""
    def __init__(self):
        self.orders = []

    def add_order(self, symbol: str, amount: int, direction: str, price=None):
        """添加订单"""
        self.orders.append({
            'symbol': symbol,
            'amount': amount,
            'direction': direction,
            'price': price
        })


class SimpleBuyHoldStrategy:
    """
    简单的买入持有策略（演示用）

    逻辑：
    1. 第一天：买入前10只股票，每只买100股
    2. 持有到最后一天
    3. 最后一天：全部卖出
    """

    def __init__(self, buy_count: int = 10, buy_amount: int = 100):
        self.buy_count = buy_count
        self.buy_amount = buy_amount
        self.has_bought = False
        self.is_last_day = False

    def generate_decision(self, market_data: Dict, account) -> TradeDecision:
        """
        生成交易决策

        Args:
            market_data: 市场数据字典 {股票代码: {'open', 'close', ...}}
            account: 账户对象

        Returns:
            TradeDecision对象
        """
        decision = TradeDecision()

        # 第一天：买入
        if not self.has_bought:
            symbols = list(market_data.keys())[:self.buy_count]
            for symbol in symbols:
                decision.add_order(
                    symbol=symbol,
                    amount=self.buy_amount,
                    direction='buy',
                    price=None  # 市价单
                )
            self.has_bought = True
            print(f"📈 策略：买入{len(symbols)}只股票")

        # 最后一天：卖出所有持仓
        elif self.is_last_day and len(account.positions) > 0:
            for symbol, amount in account.positions.items():
                decision.add_order(
                    symbol=symbol,
                    amount=amount,
                    direction='sell',
                    price=None
                )
            print(f"📉 策略：卖出所有持仓（{len(account.positions)}只）")

        return decision

    def set_last_day(self):
        """标记为最后一天"""
        self.is_last_day = True


# ===== 模拟数据提供者（用于测试） =====

class MockDataProvider:
    """
    模拟数据提供者（用于演示）

    提供简单的模拟行情数据
    """

    def get_calendar(self, start_date: str, end_date: str):
        """返回交易日历"""
        # 简化：返回10个交易日
        return [
            '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
            '2024-01-08', '2024-01-09', '2024-01-10', '2024-01-11',
            '2024-01-12', '2024-01-15'
        ]

    def get_market_data(self, date: str):
        """返回市场数据"""
        # 模拟10只股票的数据
        # 价格随时间略微上涨（+2%）
        base_prices = {
            '600000': 10.0,
            '600001': 15.0,
            '600002': 20.0,
            '600003': 12.0,
            '600004': 18.0,
            '600005': 25.0,
            '600006': 30.0,
            '600007': 22.0,
            '600008': 16.0,
            '600009': 14.0,
        }

        # 根据日期计算价格涨幅
        date_index = self.get_calendar('2024-01-01', '2024-01-31').index(date)
        growth_factor = 1 + (date_index * 0.002)  # 每天涨0.2%

        market_data = {}
        for symbol, base_price in base_prices.items():
            price = base_price * growth_factor
            market_data[symbol] = {
                'open': price * 0.99,
                'high': price * 1.01,
                'low': price * 0.98,
                'close': price,
                'volume': 1000000
            }

        return market_data

    def get_bar(self, symbol: str, timestamp: str):
        """获取单个股票的行情"""
        market_data = self.get_market_data(timestamp)
        return market_data.get(symbol)


# ===== 运行示例 =====

if __name__ == '__main__':
    from mystocks.backtest import BacktestEngine

    print("="*60)
    print("MyStocks回测系统 - 简单示例")
    print("="*60)

    # 1. 创建数据提供者
    data_provider = MockDataProvider()

    # 2. 创建策略
    strategy = SimpleBuyHoldStrategy(buy_count=10, buy_amount=100)

    # 3. 创建回测引擎
    engine = BacktestEngine(
        strategy=strategy,
        data_provider=data_provider,
        start_date='2024-01-01',
        end_date='2024-01-31',
        init_cash=1000000,  # 100万初始资金
        commission_rate=0.0003,  # 0.03%佣金
        stamp_tax_rate=0.001,    # 0.1%印花税
        slippage_rate=0.001      # 0.1%滑点
    )

    # 标记最后一天（让策略知道何时卖出）
    trade_dates = data_provider.get_calendar('2024-01-01', '2024-01-31')
    # 这里简化处理，实际应该在回测循环中判断
    strategy.is_last_day = False  # 先设为False，最后一天时改True

    # 4. 运行回测
    results = engine.run()

    # 5. 查看结果
    print("\n" + "="*60)
    print("📊 回测结果详情")
    print("="*60)
    print(f"总收益率: {results['metrics']['total_return']*100:.2f}%")
    print(f"最终价值: {results['metrics']['final_value']:,.2f}元")
    print(f"交易成本: {results['metrics']['total_cost']:,.2f}元")
    print(f"交易次数: {results['metrics']['trade_count']}次")

    print("\n每日收益率曲线:")
    print(results['daily_results'][['date', 'portfolio_value', 'returns']].to_string(index=False))

    print("\n交易历史:")
    import pandas as pd
    trades_df = pd.DataFrame(results['trades'])
    if len(trades_df) > 0:
        print(trades_df[['timestamp', 'symbol', 'direction', 'amount', 'price']].to_string(index=False))

    print("\n" + "="*60)
    print("✅ 示例运行完成！")
    print("="*60)
