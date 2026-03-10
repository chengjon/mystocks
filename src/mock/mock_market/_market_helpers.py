import math
import random

import numpy as np


def _generate_realistic_stock_price(base_price: float, volatility: float = 0.02) -> float:
    """生成更真实的股票价格，使用对数正态分布"""
    log_return = np.random.normal(0, volatility)
    price = base_price * math.exp(log_return)
    return round(max(price, 0.1), 2)


def _generate_realistic_volume(market_cap: float) -> int:
    """基于市值生成更真实的成交量"""
    base_volume = 1000000
    market_factor = (market_cap / 1000) ** 0.7
    volume = base_volume * market_factor * random.uniform(0.5, 3.0)
    return int(volume)


def _generate_correlated_change(volatility: float = 0.02) -> tuple:
    """生成相关的价格变动和百分比变动"""
    daily_return = np.random.normal(0, volatility)
    daily_return = max(min(daily_return, 0.2), -0.2)
    return round(daily_return * 100, 4)
