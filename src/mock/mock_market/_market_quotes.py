import datetime
import random
from typing import Dict, List, Optional


def get_real_time_quotes(symbols: Optional[str] = None) -> List[Dict]:
    """获取实时行情"""
    default_symbols = ["000001", "600519", "000858", "601318", "600036"]
    symbol_list = [symbol.strip() for symbol in symbols.split(",")] if symbols else default_symbols

    stock_info = {
        "600519": {"name": "贵州茅台", "base_price": 1800.0},
        "600036": {"name": "招商银行", "base_price": 35.0},
        "000001": {"name": "平安银行", "base_price": 12.0},
        "000002": {"name": "万科A", "base_price": 8.5},
        "000858": {"name": "五粮液", "base_price": 150.0},
        "601318": {"name": "中国平安", "base_price": 45.5},
    }

    quotes = []
    for symbol in symbol_list:
        stock = stock_info.get(symbol, {"name": f"股票{symbol}", "base_price": 100.0})
        base_price = stock["base_price"]
        change_amount = round(random.uniform(-base_price * 0.05, base_price * 0.05), 2)
        change_pct = round((change_amount / base_price) * 100, 2)
        price = round(base_price + change_amount, 2)
        open_price = round(base_price + random.uniform(-base_price * 0.02, base_price * 0.02), 2)
        high_price = round(max(price, open_price) + random.uniform(0, base_price * 0.01), 2)
        low_price = round(min(price, open_price) - random.uniform(0, base_price * 0.01), 2)
        volume = random.randint(1000000, 50000000)
        turnover = round(price * volume, 2)

        quotes.append(
            {
                "symbol": symbol,
                "name": stock["name"],
                "price": price,
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

    return quotes


def get_fund_flow(
    symbol: str,
    timeframe: str = "1",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict]:
    """获取资金流向数据"""
    base_flow = random.randint(-50000000, 50000000)

    if not end_date:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        days = int(timeframe) if timeframe.isdigit() else 1
        start_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - datetime.timedelta(days=days)).strftime(
            "%Y-%m-%d"
        )

    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    fund_flow_data = []
    current_flow = base_flow

    while start_dt <= end_dt:
        if start_dt.weekday() < 5:
            main_inflow = random.randint(1000000, 50000000)
            main_outflow = random.randint(1000000, 50000000)
            retail_inflow = random.randint(500000, 10000000)
            retail_outflow = random.randint(500000, 10000000)
            net_amount = current_flow + random.randint(-10000000, 10000000)

            fund_flow_data.append(
                {
                    "date": start_dt.strftime("%Y-%m-%d"),
                    "main_inflow": main_inflow,
                    "main_outflow": main_outflow,
                    "retail_inflow": retail_inflow,
                    "retail_outflow": retail_outflow,
                    "net_amount": net_amount,
                }
            )

            current_flow = net_amount * 0.8

        start_dt += datetime.timedelta(days=1)

    return fund_flow_data
