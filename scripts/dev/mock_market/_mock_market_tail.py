"""Tail helpers extracted from `_generate_realistic_stock_price.py`."""

from __future__ import annotations

import datetime
import random
from typing import Dict, List, Optional


def get_etf_list(symbol: Optional[str] = None, keyword: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """获取ETF列表

    Args:
        symbol: Optional[str] - ETF代码
        keyword: Optional[str] - 关键词搜索
        limit: int - 返回数量

    Returns:
        List[Dict]: ETF数据，包含:
                   - symbol: ETF代码
                   - name: ETF名称
                   - price: 最新价
                   - change: 涨跌额
                   - change_pct: 涨跌幅(%)
                   - volume: 成交量
                   - amount: 成交额

    """
    etf_pool = [
        {
            "symbol": "510300",
            "name": "沪深300ETF",
            "base_price": 3.85,
            "volume": 25000000,
        },
        {
            "symbol": "510500",
            "name": "中证500ETF",
            "base_price": 6.12,
            "volume": 18000000,
        },
        {
            "symbol": "159915",
            "name": "创业板ETF",
            "base_price": 2.45,
            "volume": 35000000,
        },
        {
            "symbol": "512880",
            "name": "证券ETF",
            "base_price": 0.95,
            "volume": 120000000,
        },
        {"symbol": "515050", "name": "5G ETF", "base_price": 1.23, "volume": 28000000},
        {"symbol": "159928", "name": "消费ETF", "base_price": 0.87, "volume": 15000000},
        {"symbol": "512690", "name": "酒ETF", "base_price": 0.76, "volume": 22000000},
        {"symbol": "515000", "name": "科技ETF", "base_price": 1.05, "volume": 19000000},
    ]

    # 筛选逻辑
    filtered_etfs = etf_pool
    if symbol:
        filtered_etfs = [etf for etf in etf_pool if etf["symbol"] == symbol]
    elif keyword:
        filtered_etfs = [etf for etf in etf_pool if keyword.lower() in etf["name"].lower()]

    # 生成ETF数据
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
            },
        )

    return result


def get_chip_race(
    race_type: str = "open",
    trade_date: Optional[str] = None,
    min_race_amount: Optional[float] = None,
    limit: int = 100,
) -> List[Dict]:
    """获取竞价抢筹数据

    参考instock实现: /opt/iflow/instock/instock/core/crawling/stock_chip_race.py
    字段名与tablestructure.py一致

    数据字段说明 (instock标准):
    - deal_amount: 开盘金额/收盘金额
    - bid_rate: 抢筹幅度 = (bid_deal_amount - bid_trust_amount) / bid_trust_amount * 100%
    - bid_ratio: 抢筹占比 = bid_deal_amount / deal_amount * 100%
    - change_rate: 涨跌幅 = (new_price / pre_close - 1) * 100%

    Args:
        race_type: str - 抢筹类型: open(早盘) / end(尾盘)
        trade_date: Optional[str] - 交易日期
        min_race_amount: Optional[float] - 最小抢筹金额
        limit: int - 返回数量

    Returns:
        List[Dict]: 竞价抢筹数据，包含:
                   - code: 股票代码
                   - name: 股票名称
                   - date: 交易日期
                   - new_price: 最新价
                   - change_rate: 涨跌幅(%)
                   - pre_close_price: 昨收价
                   - open_price: 今开价
                   - deal_amount: 开盘金额/收盘金额
                   - bid_rate: 抢筹幅度(%)
                   - bid_trust_amount: 抢筹委托金额
                   - bid_deal_amount: 抢筹成交金额
                   - bid_ratio: 抢筹占比(%)

    """
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

        if race_type == "open":
            open_price = round(pre_close_price * (1 + random.uniform(-0.02, 0.02)), 2)
        else:
            open_price = pre_close_price

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
            },
        )

    race_data = sorted(race_data, key=lambda x: x["deal_amount"], reverse=True)

    return race_data[:limit]


def get_lhb_detail(
    symbol: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_net_amount: Optional[float] = None,
    limit: int = 100,
) -> List[Dict]:
    """获取龙虎榜详细数据

    Args:
        symbol: Optional[str] - 股票代码
        start_date: Optional[str] - 开始日期
        end_date: Optional[str] - 结束日期
        min_net_amount: Optional[float] - 最小净买入额
        limit: int - 返回数量

    Returns:
        List[Dict]: 龙虎榜数据，包含:
                   - trade_date: 交易日期
                   - symbol: 股票代码
                   - name: 股票名称
                   - net_amount: 净买入额
                   - buy_amount: 买入金额
                   - sell_amount: 卖出金额
                   - reason: 上榜原因

    """
    if not end_date:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - datetime.timedelta(days=30)).strftime(
            "%Y-%m-%d",
        )

    # 生成龙虎榜数据
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
        # 跳过周末
        if current_date.weekday() < 5:
            for stock in stock_pool:
                # 生成净买入额
                net_amount = random.randint(-50000000, 100000000)

                # 筛选条件
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
                    },
                )

        current_date += datetime.timedelta(days=1)

    # 按日期和净买入额排序
    lhb_data = sorted(lhb_data, key=lambda x: (x["trade_date"], x["net_amount"]), reverse=True)

    return lhb_data[:limit]


def get_stock_list(
    limit: int = 100,
    search: Optional[str] = None,
    exchange: Optional[str] = None,
    security_type: Optional[str] = None,
) -> List[Dict]:
    """获取股票列表

    Args:
        limit: int - 返回记录数限制
        search: Optional[str] - 股票代码或名称搜索关键词
        exchange: Optional[str] - 交易所筛选: SSE/SZSE
        security_type: Optional[str] - 证券类型筛选

    Returns:
        List[Dict]: 股票列表，包含:
                   - symbol: 股票代码
                   - name: 股票名称
                   - exchange: 交易所
                   - security_type: 证券类型
                   - list_date: 上市日期
                   - status: 状态
                   - listing_board: 上市板块
                   - market_cap: 总市值
                   - circulating_market_cap: 流通市值

    """
    stock_pool = [
        {
            "symbol": "600519",
            "name": "贵州茅台",
            "exchange": "SSE",
            "security_type": "股票",
            "market_cap": 2300000000000,
            "circulating_market_cap": 2300000000000,
        },
        {
            "symbol": "600036",
            "name": "招商银行",
            "exchange": "SSE",
            "security_type": "股票",
            "market_cap": 950000000000,
            "circulating_market_cap": 950000000000,
        },
        {
            "symbol": "000001",
            "name": "平安银行",
            "exchange": "SZSE",
            "security_type": "股票",
            "market_cap": 232000000000,
            "circulating_market_cap": 232000000000,
        },
        {
            "symbol": "000002",
            "name": "万科A",
            "exchange": "SZSE",
            "security_type": "股票",
            "market_cap": 95000000000,
            "circulating_market_cap": 95000000000,
        },
        {
            "symbol": "000858",
            "name": "五粮液",
            "exchange": "SZSE",
            "security_type": "股票",
            "market_cap": 580000000000,
            "circulating_market_cap": 580000000000,
        },
        {
            "symbol": "600276",
            "name": "恒瑞医药",
            "exchange": "SSE",
            "security_type": "股票",
            "market_cap": 210000000000,
            "circulating_market_cap": 210000000000,
        },
    ]

    # 筛选逻辑
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

    # 生成上市日期和状态
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
            },
        )

    return result
