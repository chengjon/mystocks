import datetime
import random
from typing import Dict, List, Optional


def get_etf_list(symbol: Optional[str] = None, keyword: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """获取ETF列表"""
    etf_pool = [
        {"symbol": "510300", "name": "沪深300ETF", "base_price": 3.85, "volume": 25000000},
        {"symbol": "510500", "name": "中证500ETF", "base_price": 6.12, "volume": 18000000},
        {"symbol": "159915", "name": "创业板ETF", "base_price": 2.45, "volume": 35000000},
        {"symbol": "512880", "name": "证券ETF", "base_price": 0.95, "volume": 120000000},
        {"symbol": "515050", "name": "5G ETF", "base_price": 1.23, "volume": 28000000},
        {"symbol": "159928", "name": "消费ETF", "base_price": 0.87, "volume": 15000000},
        {"symbol": "512690", "name": "酒ETF", "base_price": 0.76, "volume": 22000000},
        {"symbol": "515000", "name": "科技ETF", "base_price": 1.05, "volume": 19000000},
    ]

    filtered_etfs = etf_pool
    if symbol:
        filtered_etfs = [etf for etf in etf_pool if etf["symbol"] == symbol]
    elif keyword:
        filtered_etfs = [etf for etf in etf_pool if keyword.lower() in etf["name"].lower()]

    result = []
    for etf in filtered_etfs[:limit]:
        change_pct = round(random.uniform(-3.0, 3.0), 2)
        change_amount = round(etf["base_price"] * change_pct / 100, 3)
        price = round(etf["base_price"] + change_amount, 3)
        volume_variation = random.uniform(0.5, 3.0)
        volume = int(etf["volume"] * volume_variation)
        amount = round(price * volume, 2)

        result.append(
            {
                "symbol": etf["symbol"],
                "name": etf["name"],
                "price": price,
                "change": change_amount,
                "change_pct": change_pct,
                "volume": volume,
                "amount": amount,
            }
        )

    return result


def get_stock_list(
    limit: int = 100,
    search: Optional[str] = None,
    exchange: Optional[str] = None,
    security_type: Optional[str] = None,
) -> List[Dict]:
    """获取股票列表"""
    stock_pool = [
        {"symbol": "600519", "name": "贵州茅台", "exchange": "SSE", "security_type": "股票", "market_cap": 2300000000000, "circulating_market_cap": 2300000000000},
        {"symbol": "600036", "name": "招商银行", "exchange": "SSE", "security_type": "股票", "market_cap": 950000000000, "circulating_market_cap": 950000000000},
        {"symbol": "000001", "name": "平安银行", "exchange": "SZSE", "security_type": "股票", "market_cap": 232000000000, "circulating_market_cap": 232000000000},
        {"symbol": "000002", "name": "万科A", "exchange": "SZSE", "security_type": "股票", "market_cap": 95000000000, "circulating_market_cap": 95000000000},
        {"symbol": "000858", "name": "五粮液", "exchange": "SZSE", "security_type": "股票", "market_cap": 580000000000, "circulating_market_cap": 580000000000},
        {"symbol": "600276", "name": "恒瑞医药", "exchange": "SSE", "security_type": "股票", "market_cap": 210000000000, "circulating_market_cap": 210000000000},
    ]

    filtered_stocks = stock_pool
    if exchange:
        filtered_stocks = [stock for stock in filtered_stocks if stock["exchange"] == exchange]
    if security_type:
        filtered_stocks = [stock for stock in filtered_stocks if stock["security_type"] == security_type]
    if search:
        filtered_stocks = [
            stock
            for stock in filtered_stocks
            if search.lower() in stock["symbol"].lower() or search.lower() in stock["name"].lower()
        ]

    result = []
    base_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(1000, 8000))

    for stock in filtered_stocks[:limit]:
        list_date = base_date + datetime.timedelta(days=random.randint(0, 7000))
        result.append(
            {
                "symbol": stock["symbol"],
                "name": stock["name"],
                "exchange": stock["exchange"],
                "security_type": stock["security_type"],
                "list_date": list_date.strftime("%Y-%m-%d"),
                "status": "上市",
                "listing_board": "主板" if stock["exchange"] == "SSE" else "主板",
                "market_cap": stock["market_cap"],
                "circulating_market_cap": stock["circulating_market_cap"],
            }
        )

    return result
