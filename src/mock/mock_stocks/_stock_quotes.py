import datetime
import random
from typing import Dict, List

import pandas as pd


def get_real_time_quote(stock_codes: List[str]) -> List[Dict]:
    """获取实时行情（必填参数：股票代码列表）"""
    stock_info = {
        "600519": {"name": "贵州茅台", "base_price": 1800.0},
        "600036": {"name": "招商银行", "base_price": 35.0},
        "000001": {"name": "平安银行", "base_price": 12.0},
        "000002": {"name": "万科A", "base_price": 8.5},
        "000858": {"name": "五粮液", "base_price": 150.0},
        "600276": {"name": "恒瑞医药", "base_price": 45.0},
        "600000": {"name": "浦发银行", "base_price": 8.0},
        "600887": {"name": "伊利股份", "base_price": 28.0},
    }

    result = []
    if isinstance(stock_codes, str):
        stock_codes = [stock_codes]

    for code in stock_codes:
        stock = stock_info.get(code, {"name": f"股票{code}", "base_price": 100.0})
        base_price = stock["base_price"]
        change_amount = round(random.uniform(-10.0, 10.0), 2)
        change_pct = round((change_amount / base_price) * 100, 2)
        current_price = round(base_price + change_amount, 2)
        open_price = round(base_price + random.uniform(-3.0, 3.0), 2)
        high_price = round(max(base_price, open_price, current_price) + random.uniform(0, 5.0), 2)
        low_price = round(min(base_price, open_price, current_price) - random.uniform(0, 5.0), 2)
        volume = random.randint(1000000, 100000000)
        turnover = round(current_price * volume, 2)

        result.append(
            {
                "symbol": code,
                "name": stock["name"],
                "price": current_price,
                "change": change_amount,
                "change_pct": change_pct,
                "volume": volume,
                "turnover": turnover,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": round(base_price, 2),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    return result


def get_history_profit(code: str, days: int = 30) -> pd.DataFrame:
    """获取历史收益（默认30天，返回DataFrame）"""
    base_prices = {
        "600519": 1800.0,
        "600036": 35.0,
        "000001": 12.0,
        "000002": 8.5,
        "000858": 150.0,
        "600276": 45.0,
        "600000": 8.0,
        "600887": 28.0,
    }

    base_price = base_prices.get(code, 100.0)
    dates = []
    prices = []
    change_amounts = []
    change_pcts = []
    volumes = []
    turnovers = []

    current_price = base_price
    end_date = datetime.datetime.now()

    for index in range(days):
        date = end_date - datetime.timedelta(days=days - 1 - index)
        if date.weekday() >= 5:
            continue

        change = round(random.uniform(-3.0, 3.0), 2)
        current_price = round(current_price + change, 2)
        change_amount = round(change, 2)
        change_pct = round((change_amount / (current_price - change_amount)) * 100, 4)
        volume = random.randint(1000000, 50000000)
        turnover = round(current_price * volume, 2)

        dates.append(date.strftime("%Y-%m-%d"))
        prices.append(current_price)
        change_amounts.append(change_amount)
        change_pcts.append(change_pct)
        volumes.append(volume)
        turnovers.append(turnover)

    return pd.DataFrame(
        {
            "date": dates,
            "price": prices,
            "change_amount": change_amounts,
            "change_pct": change_pcts,
            "volume": volumes,
            "turnover": turnovers,
        }
    )


def get_realtime_quotes() -> List[Dict]:
    """获取实时行情数据"""
    stock_codes = ["600519", "600036", "000001", "000858", "300750", "688981", "600276", "002594"]
    stock_names = ["贵州茅台", "招商银行", "平安银行", "五粮液", "宁德时代", "中芯国际", "恒瑞医药", "比亚迪"]

    result = []
    for index, code in enumerate(stock_codes):
        base_price = random.uniform(20, 2000) if index < 2 else random.uniform(10, 100)
        change_pct = round(random.uniform(-5, 5), 2)
        current_price = round(base_price * (1 + change_pct / 100), 2)

        result.append(
            {
                "symbol": code,
                "name": stock_names[index],
                "price": current_price,
                "change": round(current_price - base_price, 2),
                "change_pct": change_pct,
                "volume": random.randint(1000000, 100000000),
                "turnover": round(current_price * random.randint(1000000, 100000000), 2),
                "high": round(current_price * (1 + random.uniform(0, 0.05)), 2),
                "low": round(current_price * (1 - random.uniform(0, 0.05)), 2),
                "open": round(base_price + random.uniform(-2, 2), 2),
                "pre_close": round(base_price, 2),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    return result


def generate_realistic_price(base_price: float = 100.0, volatility: float = 0.02) -> float:
    """生成真实感的价格数据"""
    change_rate = random.uniform(-volatility, volatility)
    price = base_price * (1 + change_rate)
    return round(price, 2)
