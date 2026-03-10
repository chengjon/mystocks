import random
from typing import Dict, List

from ._market_helpers import (
    _generate_correlated_change,
    _generate_realistic_stock_price,
    _generate_realistic_volume,
)


def get_market_heatmap(market: str = "cn", limit: int = 50) -> List[Dict]:
    """获取市场热力图数据"""
    if market == "cn":
        stock_pool = [
            {"symbol": "600519", "name": "贵州茅台", "base_price": 1800.0, "volume": 1200000, "market_cap": 2300000000000},
            {"symbol": "600036", "name": "招商银行", "base_price": 35.0, "volume": 8900000, "market_cap": 950000000000},
            {"symbol": "000001", "name": "平安银行", "base_price": 12.0, "volume": 15600000, "market_cap": 232000000000},
            {"symbol": "000002", "name": "万科A", "base_price": 8.5, "volume": 45000000, "market_cap": 95000000000},
            {"symbol": "000858", "name": "五粮液", "base_price": 150.0, "volume": 2300000, "market_cap": 580000000000},
            {"symbol": "600276", "name": "恒瑞医药", "base_price": 45.0, "volume": 6800000, "market_cap": 210000000000},
            {"symbol": "600000", "name": "浦发银行", "base_price": 8.0, "volume": 12800000, "market_cap": 236000000000},
            {"symbol": "600887", "name": "伊利股份", "base_price": 28.0, "volume": 5600000, "market_cap": 178000000000},
            {"symbol": "600104", "name": "上汽集团", "base_price": 12.5, "volume": 3400000, "market_cap": 146000000000},
            {"symbol": "600585", "name": "海螺水泥", "base_price": 28.5, "volume": 2800000, "market_cap": 152000000000},
        ]
    else:
        stock_pool = [
            {"symbol": "0700", "name": "腾讯控股", "base_price": 385.0, "volume": 12000000, "market_cap": 3700000000000},
            {"symbol": "0939", "name": "建设银行", "base_price": 5.8, "volume": 89000000, "market_cap": 1460000000000},
            {"symbol": "0388", "name": "港交所", "base_price": 285.0, "volume": 2300000, "market_cap": 362000000000},
            {"symbol": "1299", "name": "友邦保险", "base_price": 68.5, "volume": 5600000, "market_cap": 810000000000},
            {"symbol": "3690", "name": "美团", "base_price": 168.0, "volume": 8900000, "market_cap": 1050000000000},
        ]

    result = []
    for stock in stock_pool[:limit]:
        base_price = stock["base_price"]
        volatility = random.uniform(0.01, 0.05)
        change_pct_decimal = _generate_correlated_change(volatility)
        change_pct = round(change_pct_decimal, 2)
        change_amount = round(base_price * change_pct_decimal / 100, 2)
        price = _generate_realistic_stock_price(base_price, volatility)
        market_cap_billion = stock["market_cap"] / 1e9
        volume = _generate_realistic_volume(market_cap_billion)
        amount = round(price * volume, 0)

        result.append(
            {
                "symbol": stock["symbol"],
                "name": stock["name"],
                "price": price,
                "change": change_amount,
                "change_pct": change_pct,
                "volume": volume,
                "amount": amount,
                "market_cap": stock["market_cap"],
            }
        )

    result = sorted(result, key=lambda item: item["change_pct"], reverse=True)
    return result
