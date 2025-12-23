"""
交易所模拟器 - Exchange Simulator

功能：
1. 提供历史行情数据
2. 订单撮合（考虑滑点）
3. 模拟真实交易环境

作者: JohnC & Claude
版本: 3.1.0 (Simplified MVP)
"""

from typing import Dict, Optional


class Exchange:
    """
    交易所模拟器（简化版）

    核心功能：
    - 获取历史行情
    - 订单撮合（考虑滑点）
    - 支持市价单和限价单

    示例：
        >>> exchange = Exchange(data_provider)
        >>> quote = exchange.get_quote('600000', '2024-01-15')
        >>> filled = exchange.match_order({
        ...     'symbol': '600000',
        ...     'direction': 'buy',
        ...     'amount': 100,
        ...     'price': None  # 市价单
        ... }, '2024-01-15')
    """

    def __init__(self, data_provider, slippage_rate: float = 0.001):
        """
        初始化交易所模拟器

        Args:
            data_provider: 数据提供者（需实现get_bar方法）
            slippage_rate: 滑点比例（默认0.1%）
        """
        self.data_provider = data_provider
        self.slippage_rate = slippage_rate

    def get_quote(self, symbol: str, timestamp: str) -> Optional[Dict]:
        """
        获取指定时刻的行情报价

        Args:
            symbol: 股票代码
            timestamp: 时间戳（日期字符串）

        Returns:
            行情字典：{'open', 'high', 'low', 'close', 'volume'}
            如果无数据返回None
        """
        try:
            return self.data_provider.get_bar(symbol, timestamp)
        except Exception as e:
            print(f"⚠️ 获取行情失败 {symbol}@{timestamp}: {e}")
            return None

    def match_order(self, order: Dict, timestamp: str) -> Optional[Dict]:
        """
        订单撮合（考虑滑点）

        Args:
            order: 订单字典
                {
                    'symbol': str,
                    'direction': 'buy' or 'sell',
                    'amount': int (正数),
                    'price': float or None (None表示市价单)
                }
            timestamp: 撮合时间

        Returns:
            成交字典：{'symbol', 'amount', 'price', 'direction', 'timestamp'}
            如果无法成交返回None
        """
        # 获取当前行情
        quote = self.get_quote(order["symbol"], timestamp)
        if quote is None:
            print(f"⚠️ 无法撮合订单：无行情数据 {order['symbol']}@{timestamp}")
            return None

        # 确定成交价格
        if order["price"] is None:  # 市价单
            # 使用收盘价作为成交价
            filled_price = quote["close"]
        else:  # 限价单
            # 简化处理：直接使用限价
            # 实际可以检查是否在当日价格范围内
            filled_price = order["price"]

        # 应用滑点
        # 买入：价格略高；卖出：价格略低
        if order["direction"] == "buy":
            filled_price *= 1 + self.slippage_rate
        else:  # sell
            filled_price *= 1 - self.slippage_rate

        # 返回成交结果
        return {
            "symbol": order["symbol"],
            "amount": order["amount"],
            "price": round(filled_price, 2),
            "direction": order["direction"],
            "timestamp": timestamp,
            "slippage": self.slippage_rate,
        }

    def get_market_value(self, symbol: str, amount: int, timestamp: str) -> float:
        """
        计算股票市值

        Args:
            symbol: 股票代码
            amount: 持仓数量
            timestamp: 计算时间

        Returns:
            市值（价格×数量）
        """
        quote = self.get_quote(symbol, timestamp)
        if quote is None:
            return 0.0
        return quote["close"] * amount
