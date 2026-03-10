import datetime
import random
from typing import Dict, List, Optional


def get_chip_race(
    race_type: str = "open",
    trade_date: Optional[str] = None,
    min_race_amount: Optional[float] = None,
    limit: int = 100,
) -> List[Dict]:
    """获取竞价抢筹数据"""
    if not trade_date:
        trade_date = datetime.datetime.now().strftime("%Y-%m-%d")

    race_data = []
    stock_pool = [
        {"code": "600519", "name": "贵州茅台", "base_price": 1800.0},
        {"code": "600036", "name": "招商银行", "base_price": 35.0},
        {"code": "000001", "name": "平安银行", "base_price": 12.0},
        {"code": "000858", "name": "五粮液", "base_price": 150.0},
        {"code": "600276", "name": "恒瑞医药", "base_price": 45.0},
        {"code": "601398", "name": "工商银行", "base_price": 15.0},
        {"code": "601988", "name": "中国银行", "base_price": 10.0},
        {"code": "600016", "name": "民生银行", "base_price": 8.0},
        {"code": "600015", "name": "华夏银行", "base_price": 6.0},
        {"code": "601229", "name": "上海银行", "base_price": 7.0},
    ]

    for stock in stock_pool:
        base_price = stock["base_price"]
        pre_close_price = round(base_price + random.uniform(-0.5, 0.5), 2)
        change_rate = round(random.uniform(-5.0, 5.0), 2)
        new_price = round(pre_close_price * (1 + change_rate / 100), 2)
        open_price = round(pre_close_price * (1 + random.uniform(-0.02, 0.02)), 2) if race_type == "open" else pre_close_price
        bid_trust_amount = round(random.uniform(1000000, 50000000), 2)
        bid_deal_amount = round(bid_trust_amount * (1 + random.uniform(-0.3, 0.5)), 2)
        deal_amount = open_price * random.randint(10000, 100000)
        bid_rate = round((bid_deal_amount - bid_trust_amount) / bid_trust_amount * 100, 2)
        bid_ratio = round(bid_deal_amount / deal_amount * 100, 2)

        if min_race_amount and deal_amount < min_race_amount:
            continue

        race_data.append(
            {
                "code": stock["code"],
                "name": stock["name"],
                "date": trade_date,
                "new_price": new_price,
                "change_rate": change_rate,
                "pre_close_price": pre_close_price,
                "open_price": open_price,
                "deal_amount": deal_amount,
                "bid_rate": bid_rate,
                "bid_trust_amount": bid_trust_amount,
                "bid_deal_amount": bid_deal_amount,
                "bid_ratio": bid_ratio,
            }
        )

    race_data = sorted(race_data, key=lambda item: item["deal_amount"], reverse=True)
    return race_data[:limit]


def get_lhb_detail(
    symbol: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_net_amount: Optional[float] = None,
    limit: int = 100,
) -> List[Dict]:
    """获取龙虎榜详细数据"""
    if not end_date:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - datetime.timedelta(days=30)).strftime(
            "%Y-%m-%d"
        )

    lhb_data = []
    stock_pool = [
        {"symbol": "600519", "name": "贵州茅台"},
        {"symbol": "000858", "name": "五粮液"},
        {"symbol": "600036", "name": "招商银行"},
        {"symbol": "000001", "name": "平安银行"},
    ]
    reason_pool = ["日涨幅偏离值达7%", "日跌幅偏离值达7%", "换手率达20%", "振幅达15%"]

    current_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    while current_date <= end_dt:
        if current_date.weekday() < 5:
            for stock in stock_pool:
                net_amount = random.randint(-50000000, 100000000)

                if symbol and stock["symbol"] != symbol:
                    continue
                if min_net_amount and net_amount < min_net_amount:
                    continue

                buy_amount = max(0, net_amount) + random.randint(0, 50000000)
                sell_amount = max(0, -net_amount) + random.randint(0, 50000000)
                reason = random.choice(reason_pool)

                lhb_data.append(
                    {
                        "trade_date": current_date.strftime("%Y-%m-%d"),
                        "symbol": stock["symbol"],
                        "name": stock["name"],
                        "net_amount": net_amount,
                        "buy_amount": buy_amount,
                        "sell_amount": sell_amount,
                        "reason": reason,
                    }
                )

        current_date += datetime.timedelta(days=1)

    lhb_data = sorted(lhb_data, key=lambda item: (item["trade_date"], item["net_amount"]), reverse=True)
    return lhb_data[:limit]
