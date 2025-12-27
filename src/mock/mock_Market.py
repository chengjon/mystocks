"""
Mock数据文件: Market
提供接口:
1. get_market_heatmap() -> List[Dict] - 获取市场热力图数据
2. get_real_time_quotes() -> List[Dict] - 获取实时行情
3. get_fund_flow() -> List[Dict] - 获取资金流向数据
4. get_etf_list() -> List[Dict] - 获取ETF列表
5. get_chip_race() -> List[Dict] - 获取竞价抢筹数据
6. get_lhb_detail() -> List[Dict] - 获取龙虎榜数据
7. get_stock_list() -> List[Dict] - 获取股票列表
8. get_kline_data() -> List[Dict] - 获取K线数据

使用说明:
- 所有函数参数需与真实API接口完全对齐
- 返回值字段名需与前端表格列字段一致
- 股票价格保留2位小数，百分比保留4位小数
- 时间字段使用datetime类型，格式：YYYY-MM-DD HH:MM:SS

作者: Claude Code
生成时间: 2025-11-13
"""

from typing import List, Dict, Optional
import datetime
import random
import numpy as np
import math


def _generate_realistic_stock_price(base_price: float, volatility: float = 0.02) -> float:
    """生成更真实的股票价格，使用对数正态分布

    Args:
        base_price: 基准价格
        volatility: 价格波动率

    Returns:
        float: 生成的股票价格
    """
    # 使用对数正态分布模拟股票价格
    log_return = np.random.normal(0, volatility)
    price = base_price * math.exp(log_return)
    return round(max(price, 0.1), 2)  # 确保价格为正且保留两位小数


def _generate_realistic_volume(market_cap: float) -> int:
    """基于市值生成更真实的成交量

    Args:
        market_cap: 市值(亿元)

    Returns:
        int: 成交量(股)
    """
    # 大市值股票成交量通常更大，使用幂律分布
    base_volume = 1000000  # 100万股
    market_factor = (market_cap / 1000) ** 0.7  # 市值因子
    volume = base_volume * market_factor * random.uniform(0.5, 3.0)
    return int(volume)


def _generate_correlated_change(volatility: float = 0.02) -> tuple:
    """生成相关的价格变动和百分比变动

    Args:
        volatility: 波动率

    Returns:
        tuple: (change_amount, change_percent)
    """
    # 生成正态分布的收益率
    daily_return = np.random.normal(0, volatility)

    # 限制极端值
    daily_return = max(min(daily_return, 0.2), -0.2)  # 限制在±20%范围内

    return round(daily_return * 100, 4)  # 百分比变动(小数形式)


def get_market_heatmap(market: str = "cn", limit: int = 50) -> List[Dict]:
    """获取市场热力图数据

    Args:
        market: str - 市场类型: cn(A股)/hk(港股)
        limit: int - 返回股票数量

    Returns:
        List[Dict]: 市场热力图数据，包含:
                   - symbol: 股票代码
                   - name: 股票名称
                   - price: 实时价格
                   - change: 涨跌额
                   - change_pct: 涨跌幅(%)
                   - volume: 成交量
                   - amount: 成交额
                   - market_cap: 市值
    """
    # 股票池数据
    if market == "cn":
        stock_pool = [
            {
                "symbol": "600519",
                "name": "贵州茅台",
                "base_price": 1800.0,
                "volume": 1200000,
                "market_cap": 2300000000000,
            },
            {
                "symbol": "600036",
                "name": "招商银行",
                "base_price": 35.0,
                "volume": 8900000,
                "market_cap": 950000000000,
            },
            {
                "symbol": "000001",
                "name": "平安银行",
                "base_price": 12.0,
                "volume": 15600000,
                "market_cap": 232000000000,
            },
            {
                "symbol": "000002",
                "name": "万科A",
                "base_price": 8.5,
                "volume": 45000000,
                "market_cap": 95000000000,
            },
            {
                "symbol": "000858",
                "name": "五粮液",
                "base_price": 150.0,
                "volume": 2300000,
                "market_cap": 580000000000,
            },
            {
                "symbol": "600276",
                "name": "恒瑞医药",
                "base_price": 45.0,
                "volume": 6800000,
                "market_cap": 210000000000,
            },
            {
                "symbol": "600000",
                "name": "浦发银行",
                "base_price": 8.0,
                "volume": 12800000,
                "market_cap": 236000000000,
            },
            {
                "symbol": "600887",
                "name": "伊利股份",
                "base_price": 28.0,
                "volume": 5600000,
                "market_cap": 178000000000,
            },
            {
                "symbol": "600104",
                "name": "上汽集团",
                "base_price": 12.5,
                "volume": 3400000,
                "market_cap": 146000000000,
            },
            {
                "symbol": "600585",
                "name": "海螺水泥",
                "base_price": 28.5,
                "volume": 2800000,
                "market_cap": 152000000000,
            },
        ]
    else:  # hk market
        stock_pool = [
            {
                "symbol": "0700",
                "name": "腾讯控股",
                "base_price": 385.0,
                "volume": 12000000,
                "market_cap": 3700000000000,
            },
            {
                "symbol": "0939",
                "name": "建设银行",
                "base_price": 5.8,
                "volume": 89000000,
                "market_cap": 1460000000000,
            },
            {
                "symbol": "0388",
                "name": "港交所",
                "base_price": 285.0,
                "volume": 2300000,
                "market_cap": 362000000000,
            },
            {
                "symbol": "1299",
                "name": "友邦保险",
                "base_price": 68.5,
                "volume": 5600000,
                "market_cap": 810000000000,
            },
            {
                "symbol": "3690",
                "name": "美团",
                "base_price": 168.0,
                "volume": 8900000,
                "market_cap": 1050000000000,
            },
        ]

    result = []
    for stock in stock_pool[:limit]:
        # 使用更真实的价格生成方法
        base_price = stock["base_price"]
        volatility = random.uniform(0.01, 0.05)  # 不同股票有不同的波动率

        # 生成相关的价格变动和百分比变动
        change_pct_decimal = _generate_correlated_change(volatility)
        change_pct = round(change_pct_decimal, 2)

        # 基于价格生成真实的价格变化
        change_amount = round(base_price * change_pct_decimal / 100, 2)
        price = _generate_realistic_stock_price(base_price, volatility)

        # 基于市值生成更真实的成交量
        market_cap_billion = stock["market_cap"] / 1e9  # 转换为亿元
        volume = _generate_realistic_volume(market_cap_billion)

        # 生成成交额
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

    # 按涨跌幅排序
    result = sorted(result, key=lambda x: x["change_pct"], reverse=True)

    return result


def get_real_time_quotes(symbols: Optional[str] = None) -> List[Dict]:
    """获取实时行情

    Args:
        symbols: Optional[str] - 股票代码列表，逗号分隔

    Returns:
        List[Dict]: 实时行情列表，包含:
                   - symbol: 股票代码
                   - name: 股票名称
                   - price: 实时价格
                   - change: 涨跌额
                   - change_pct: 涨跌幅(%)
                   - volume: 成交量
                   - turnover: 成交额
                   - open: 开盘价
                   - high: 最高价
                   - low: 最低价
                   - close: 昨收价
    """
    # 默认股票列表
    default_symbols = ["000001", "600519", "000858", "601318", "600036"]

    if symbols:
        symbol_list = [s.strip() for s in symbols.split(",")]
    else:
        symbol_list = default_symbols

    # 股票基础信息
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

        # 生成价格数据
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
    """获取资金流向数据

    Args:
        symbol: str - 股票代码
        timeframe: str - 时间维度: 1/3/5/10天
        start_date: Optional[str] - 开始日期
        end_date: Optional[str] - 结束日期

    Returns:
        List[Dict]: 资金流向数据，包含:
                   - date: 日期
                   - main_inflow: 主力净流入
                   - main_outflow: 主力净流出
                   - retail_inflow: 散户净流入
                   - retail_outflow: 散户净流出
                   - net_amount: 净流入额
    """
    # 基础资金流向数据
    base_flow = random.randint(-50000000, 50000000)  # 基础净流入

    # 生成日期序列
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
        # 跳过周末
        if start_dt.weekday() < 5:
            # 生成资金流向数据
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

            # 更新基础流向（模拟趋势）
            current_flow = net_amount * 0.8  # 减少趋势影响

        start_dt += datetime.timedelta(days=1)

    return fund_flow_data


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
            }
        )

    return result


def get_chip_race(
    race_type: str = "open",
    trade_date: Optional[str] = None,
    min_race_amount: Optional[float] = None,
    limit: int = 100,
) -> List[Dict]:
    """获取竞价抢筹数据

    Args:
        race_type: str - 抢筹类型: open/end
        trade_date: Optional[str] - 交易日期
        min_race_amount: Optional[float] - 最小抢筹金额
        limit: int - 返回数量

    Returns:
        List[Dict]: 竞价抢筹数据，包含:
                   - symbol: 股票代码
                   - name: 股票名称
                   - race_amount: 抢筹金额
                   - race_ratio: 抢筹比例
                   - open_price: 开盘价
                   - close_price: 收盘价
                   - change_pct: 涨跌幅
    """
    if not trade_date:
        trade_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # 生成抢筹数据
    race_data = []
    stock_pool = [
        {"symbol": "600519", "name": "贵州茅台", "base_price": 1800.0},
        {"symbol": "600036", "name": "招商银行", "base_price": 35.0},
        {"symbol": "000001", "name": "平安银行", "base_price": 12.0},
        {"symbol": "000858", "name": "五粮液", "base_price": 150.0},
        {"symbol": "600276", "name": "恒瑞医药", "base_price": 45.0},
    ]

    for stock in stock_pool:
        # 生成抢筹金额
        race_amount = random.randint(1000000, 100000000)
        race_ratio = round(random.uniform(0.1, 15.0), 2)

        # 生成价格数据
        base_price = stock["base_price"]
        change_pct = round(random.uniform(-5.0, 5.0), 2)
        close_price = round(base_price * (1 + change_pct / 100), 2)

        if race_type == "open":
            # 开盘竞价
            open_price = round(close_price * (1 + random.uniform(-0.02, 0.02)), 2)
        else:
            # 收盘竞价
            open_price = round(base_price, 2)

        # 筛选条件
        if min_race_amount and race_amount < min_race_amount:
            continue

        race_data.append(
            {
                "symbol": stock["symbol"],
                "name": stock["name"],
                "race_amount": race_amount,
                "race_ratio": race_ratio,
                "open_price": open_price,
                "close_price": close_price,
                "change_pct": change_pct,
                "trade_date": trade_date,
            }
        )

    # 按抢筹金额排序
    race_data = sorted(race_data, key=lambda x: x["race_amount"], reverse=True)

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
            "%Y-%m-%d"
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
                    }
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
            }
        )

    return result


def get_kline_data(
    stock_code: str,
    period: str = "daily",
    adjust: str = "qfq",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict]:
    """获取K线数据

    Args:
        stock_code: str - 股票代码
        period: str - 时间周期: daily/weekly/monthly
        adjust: str - 复权类型: qfq/hfq/空字符串
        start_date: Optional[str] - 开始日期
        end_date: Optional[str] - 结束日期

    Returns:
        List[Dict]: K线数据，包含:
                   - date: 日期
                   - open: 开盘价
                   - high: 最高价
                   - low: 最低价
                   - close: 收盘价
                   - volume: 成交量
                   - amount: 成交额
    """
    # 股票基础价格
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

    base_price = base_prices.get(stock_code, 100.0)

    # 设置默认日期
    if not end_date:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - datetime.timedelta(days=60)).strftime(
            "%Y-%m-%d"
        )

    # 根据周期调整日期间隔
    if period == "weekly":
        days_interval = 7
    elif period == "monthly":
        days_interval = 30
    else:
        days_interval = 1

    # 生成K线数据
    kline_data = []
    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    current_price = base_price
    current_date = start_dt

    while current_date <= end_dt:
        # 跳过周末
        if current_date.weekday() < 5:
            # 生成OHLC数据
            open_price = round(current_price + random.uniform(-2.0, 2.0), 2)
            daily_change = random.uniform(-0.03, 0.03)
            high_price = round(max(open_price, current_price) * (1 + random.uniform(0, 0.02)), 2)
            low_price = round(min(open_price, current_price) * (1 - random.uniform(0, 0.02)), 2)
            close_price = round(open_price * (1 + daily_change), 2)
            volume = random.randint(1000000, 50000000)
            amount = round(close_price * volume, 2)

            kline_data.append(
                {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": volume,
                    "amount": amount,
                }
            )

            # 更新价格
            current_price = close_price

        current_date += datetime.timedelta(days=days_interval)

    return kline_data


def generate_realistic_price(base_price: float = 100.0, volatility: float = 0.02) -> float:
    """生成真实感的价格数据

    Args:
        base_price: 基准价格
        volatility: 波动率

    Returns:
        float: 生成的价格（保留2位小数）
    """
    change_rate = random.uniform(-volatility, volatility)
    price = base_price * (1 + change_rate)
    return round(price, 2)


def generate_realistic_volume() -> int:
    """生成真实感的成交量数据

    Returns:
        int: 成交量（股）
    """
    return random.randint(1000000, 100000000)


if __name__ == "__main__":
    # 测试函数
    print("Mock Market模块测试")
    print("=" * 50)

    print("1. 测试市场热力图:")
    heatmap_data = get_market_heatmap(market="cn", limit=5)
    print(f"   返回 {len(heatmap_data)} 条数据")

    print("\n2. 测试实时行情:")
    quotes_data = get_real_time_quotes(symbols="600519,000001")
    print(f"   返回 {len(quotes_data)} 条数据")

    print("\n3. 测试资金流向:")
    fund_flow_data = get_fund_flow(symbol="600519", timeframe="5")
    print(f"   返回 {len(fund_flow_data)} 条数据")

    print("\n4. 测试ETF列表:")
    etf_data = get_etf_list(limit=3)
    print(f"   返回 {len(etf_data)} 条数据")

    print("\n测试完成！")
