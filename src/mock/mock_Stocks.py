"""
Mock数据文件: Stocks
提供接口:
1. get_stock_list() -> List[Dict] - 获取股票列表（支持按交易所筛选，支持分页）
2. get_real_time_quote() -> Dict - 获取实时行情（必填参数：股票代码）
3. get_history_profit() -> pd.DataFrame - 获取历史收益（默认30天，返回DataFrame）

使用说明:
- 所有函数参数需与真实API接口完全对齐
- 返回值字段名需与前端表格列字段一致
- 股票价格保留2位小数，百分比保留4位小数
- 时间字段使用datetime类型，格式：YYYY-MM-DD HH:MM:SS

作者: Claude Code
生成时间: 2025-11-13
"""

from typing import List, Dict, Optional
import pandas as pd
import datetime
import random


def get_stock_list(params: Optional[Dict] = None) -> List[Dict]:
    """获取股票列表（支持按交易所筛选，支持分页）

    Args:
        params: Dict - 查询参数：
                exchange: Optional[str] - 交易所筛选（sh=上交所，sz=深交所）
                limit: int - 每页数量，默认20
                offset: int - 偏移量，默认0

    Returns:
        List[Dict]: 股票列表数据，前端表格所需字段：
                   - symbol: 股票代码
                   - name: 股票名称
                   - industry: 所属行业
                   - area: 地区
                   - market: 市场
                   - list_date: 上市日期
    """
    # 默认参数
    params = params or {}
    exchange = params.get("exchange")
    limit = params.get("limit", 20)
    offset = params.get("offset", 0)

    # 股票基础数据池（包含不同交易所的热门股票）
    stock_pools = {
        "sh": [
            {
                "symbol": "600519",
                "name": "贵州茅台",
                "industry": "白酒",
                "area": "贵州",
                "market": "上交所",
            },
            {
                "symbol": "600036",
                "name": "招商银行",
                "industry": "银行",
                "area": "深圳",
                "market": "上交所",
            },
            {
                "symbol": "600276",
                "name": "恒瑞医药",
                "industry": "医药生物",
                "area": "江苏",
                "market": "上交所",
            },
            {
                "symbol": "600009",
                "name": "上海机场",
                "industry": "机场航运",
                "area": "上海",
                "market": "上交所",
            },
            {
                "symbol": "600000",
                "name": "浦发银行",
                "industry": "银行",
                "area": "上海",
                "market": "上交所",
            },
            {
                "symbol": "600887",
                "name": "伊利股份",
                "industry": "食品饮料",
                "area": "内蒙古",
                "market": "上交所",
            },
            {
                "symbol": "600104",
                "name": "上汽集团",
                "industry": "汽车",
                "area": "上海",
                "market": "上交所",
            },
            {
                "symbol": "600585",
                "name": "海螺水泥",
                "industry": "建筑材料",
                "area": "安徽",
                "market": "上交所",
            },
        ],
        "sz": [
            {
                "symbol": "000001",
                "name": "平安银行",
                "industry": "银行",
                "area": "深圳",
                "market": "深交所",
            },
            {
                "symbol": "000002",
                "name": "万科A",
                "industry": "房地产",
                "area": "深圳",
                "market": "深交所",
            },
            {
                "symbol": "000858",
                "name": "五粮液",
                "industry": "白酒",
                "area": "四川",
                "market": "深交所",
            },
            {
                "symbol": "000776",
                "name": "广发证券",
                "industry": "非银金融",
                "area": "广东",
                "market": "深交所",
            },
            {
                "symbol": "000568",
                "name": "泸州老窖",
                "industry": "白酒",
                "area": "四川",
                "market": "深交所",
            },
            {
                "symbol": "000166",
                "name": "申万宏源",
                "industry": "非银金融",
                "area": "深圳",
                "market": "深交所",
            },
            {
                "symbol": "000063",
                "name": "中兴通讯",
                "industry": "通信",
                "area": "广东",
                "market": "深交所",
            },
            {
                "symbol": "000100",
                "name": "TCL科技",
                "industry": "电子",
                "area": "广东",
                "market": "深交所",
            },
        ],
    }

    # 根据交易所筛选
    if exchange:
        available_stocks = stock_pools.get(exchange, [])
    else:
        available_stocks = stock_pools["sh"] + stock_pools["sz"]

    # 生成分页数据
    total_stocks = len(available_stocks)
    paginated_stocks = available_stocks[offset : offset + limit]

    # 为每个股票生成上市日期和实际数据
    result = []
    base_date = datetime.datetime.now() - datetime.timedelta(
        days=3650
    )  # 约10年前的日期

    for i, stock in enumerate(paginated_stocks):
        list_date = base_date + datetime.timedelta(days=random.randint(0, 3650))
        result.append(
            {
                "symbol": stock["symbol"],
                "name": stock["name"],
                "industry": stock["industry"],
                "area": stock["area"],
                "market": stock["market"],
                "list_date": list_date.strftime("%Y-%m-%d"),
                "total": total_stocks,  # 用于分页的总数量
            }
        )

    return result


def get_real_time_quote(stock_codes: List[str]) -> List[Dict]:
    """获取实时行情（必填参数：股票代码列表）

    Args:
        stock_codes: List[str] - 股票代码列表（必填）

    Returns:
        List[Dict]: 实时行情数据列表，每项包含：
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
    # 股票基础信息
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

    # 如果传入的是单个股票代码字符串，转换为列表
    if isinstance(stock_codes, str):
        stock_codes = [stock_codes]

    for code in stock_codes:
        # 获取基础信息
        stock = stock_info.get(code, {"name": f"股票{code}", "base_price": 100.0})

        # 生成实时价格数据
        base_price = stock["base_price"]
        change_amount = round(random.uniform(-10.0, 10.0), 2)  # 涨跌额
        change_pct = round((change_amount / base_price) * 100, 2)  # 涨跌幅

        current_price = round(base_price + change_amount, 2)
        open_price = round(base_price + random.uniform(-3.0, 3.0), 2)
        high_price = round(
            max(base_price, open_price, current_price) + random.uniform(0, 5.0), 2
        )
        low_price = round(
            min(base_price, open_price, current_price) - random.uniform(0, 5.0), 2
        )

        volume = random.randint(1000000, 100000000)  # 成交量
        turnover = round(current_price * volume, 2)  # 成交额

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
    """获取历史收益（默认30天，返回DataFrame）

    Args:
        code: str - 股票代码（必填）
        days: int - 历史天数，默认30天

    Returns:
        pd.DataFrame: 历史收益数据，包含字段：
                     - date: 日期
                     - price: 收盘价
                     - change_amount: 涨跌额
                     - change_pct: 涨跌幅(%)
                     - volume: 成交量
                     - turnover: 成交额
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

    base_price = base_prices.get(code, 100.0)

    # 生成历史数据
    dates = []
    prices = []
    change_amounts = []
    change_pcts = []
    volumes = []
    turnovers = []

    current_price = base_price
    end_date = datetime.datetime.now()

    for i in range(days):
        date = end_date - datetime.timedelta(days=days - 1 - i)

        # 跳过周末（简化处理）
        if date.weekday() >= 5:
            continue

        # 生成价格变化（随机游走）
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


def get_stock_detail(params: Dict) -> Dict:
    """获取股票详细信息

    Args:
        params: Dict - 查询参数：
                stock_code: str - 股票代码

    Returns:
        Dict: 股票详细信息
    """
    stock_code = params.get("stock_code", "600000")

    # 股票基础信息
    stock_info = {
        "600519": {
            "name": "贵州茅台",
            "industry": "白酒",
            "area": "贵州",
            "market": "上交所",
        },
        "600036": {
            "name": "招商银行",
            "industry": "银行",
            "area": "深圳",
            "market": "上交所",
        },
        "000001": {
            "name": "平安银行",
            "industry": "银行",
            "area": "深圳",
            "market": "深交所",
        },
        "000002": {
            "name": "万科A",
            "industry": "房地产",
            "area": "深圳",
            "market": "深交所",
        },
        "000858": {
            "name": "五粮液",
            "industry": "白酒",
            "area": "四川",
            "market": "深交所",
        },
        "600276": {
            "name": "恒瑞医药",
            "industry": "医药生物",
            "area": "江苏",
            "market": "上交所",
        },
        "600000": {
            "name": "浦发银行",
            "industry": "银行",
            "area": "上海",
            "market": "上交所",
        },
        "600887": {
            "name": "伊利股份",
            "industry": "食品饮料",
            "area": "内蒙古",
            "market": "上交所",
        },
    }

    info = stock_info.get(
        stock_code,
        {
            "name": f"股票{stock_code}",
            "industry": "未知",
            "area": "未知",
            "market": "未知",
        },
    )

    return {
        "symbol": stock_code,
        "name": info["name"],
        "industry": info["industry"],
        "area": info["area"],
        "market": info["market"],
        "list_date": (
            datetime.datetime.now()
            - datetime.timedelta(days=random.randint(1000, 5000))
        ).strftime("%Y-%m-%d"),
        "total_shares": random.randint(100000000, 10000000000),
        "circulating_shares": random.randint(50000000, 8000000000),
        "pe_ratio": round(random.uniform(5, 50), 2),
        "pb_ratio": round(random.uniform(0.5, 5), 2),
    }


def get_stock_financial_data(params: Dict) -> Dict:
    """获取股票财务数据

    Args:
        params: Dict - 查询参数：
                stock_code: str - 股票代码

    Returns:
        Dict: 股票财务数据
    """
    stock_code = params.get("stock_code", "600000")

    return {
        "symbol": stock_code,
        "name": f"股票{stock_code}",
        "financial_data": {
            "revenue": round(random.uniform(1000000000, 50000000000), 2),  # 收入
            "net_profit": round(random.uniform(100000000, 10000000000), 2),  # 净利润
            "total_assets": round(
                random.uniform(5000000000, 100000000000), 2
            ),  # 总资产
            "net_assets": round(random.uniform(2000000000, 50000000000), 2),  # 净资产
            "roa": round(random.uniform(0.01, 0.15), 4),  # 总资产收益率
            "roa": round(random.uniform(0.02, 0.25), 4),  # 净资产收益率
            "debt_ratio": round(random.uniform(0.2, 0.6), 4),  # 资产负债率
            "current_ratio": round(random.uniform(0.8, 2.5), 2),  # 流动比率
            "report_date": (
                datetime.datetime.now()
                - datetime.timedelta(days=random.randint(0, 365))
            ).strftime("%Y-%m-%d"),  # 报告日期
        },
    }


def get_stock_indicators(params: Dict) -> Dict:
    """获取股票技术指标

    Args:
        params: Dict - 查询参数：
                stock_code: str - 股票代码

    Returns:
        Dict: 股票技术指标
    """
    stock_code = params.get("stock_code", "600000")

    return {
        "symbol": stock_code,
        "indicators": {
            "ma5": round(random.uniform(50, 200), 2),
            "ma10": round(random.uniform(50, 200), 2),
            "ma20": round(random.uniform(50, 200), 2),
            "rsi": round(random.uniform(20, 80), 2),
            "macd": round(random.uniform(-5, 5), 3),
            "kdj_k": round(random.uniform(20, 80), 2),
            "kdj_d": round(random.uniform(20, 80), 2),
            "kdj_j": round(random.uniform(20, 80), 2),
            "boll_upper": round(random.uniform(55, 210), 2),
            "boll_middle": round(random.uniform(50, 200), 2),
            "boll_lower": round(random.uniform(45, 190), 2),
            "atr": round(random.uniform(1, 10), 2),
            "volume_ratio": round(random.uniform(0.5, 3), 2),
        },
    }


def get_realtime_quotes() -> List[Dict]:
    """获取实时行情数据

    Returns:
        List[Dict]: 实时行情数据列表
    """
    stock_codes = [
        "600519",
        "600036",
        "000001",
        "000858",
        "300750",
        "688981",
        "600276",
        "002594",
    ]
    stock_names = [
        "贵州茅台",
        "招商银行",
        "平安银行",
        "五粮液",
        "宁德时代",
        "中芯国际",
        "恒瑞医药",
        "比亚迪",
    ]

    result = []
    for i, code in enumerate(stock_codes):
        base_price = random.uniform(20, 2000) if i < 2 else random.uniform(10, 100)
        change_pct = round(random.uniform(-5, 5), 2)
        current_price = round(base_price * (1 + change_pct / 100), 2)

        result.append(
            {
                "symbol": code,
                "name": stock_names[i],
                "price": current_price,
                "change": round(current_price - base_price, 2),
                "change_pct": change_pct,
                "volume": random.randint(1000000, 100000000),
                "turnover": round(
                    current_price * random.randint(1000000, 100000000), 2
                ),
                "high": round(current_price * (1 + random.uniform(0, 0.05)), 2),
                "low": round(current_price * (1 - random.uniform(0, 0.05)), 2),
                "open": round(base_price + random.uniform(-2, 2), 2),
                "pre_close": round(base_price, 2),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    return result


def search_stocks(params: Dict) -> Dict:
    """搜索股票

    Args:
        params: Dict - 查询参数：
                q: str - 搜索关键词
                limit: int - 搜索结果数量

    Returns:
        Dict: 搜索结果
    """
    keyword = params.get("q", "")
    limit = params.get("limit", 20)

    # 模拟搜索结果
    all_stocks = [
        {"symbol": "600519", "name": "贵州茅台", "industry": "白酒"},
        {"symbol": "600036", "name": "招商银行", "industry": "银行"},
        {"symbol": "000001", "name": "平安银行", "industry": "银行"},
        {"symbol": "000858", "name": "五粮液", "industry": "白酒"},
        {"symbol": "600276", "name": "恒瑞医药", "industry": "医药生物"},
        {"symbol": "300750", "name": "宁德时代", "industry": "电池"},
        {"symbol": "002594", "name": "比亚迪", "industry": "新能源汽车"},
        {"symbol": "688981", "name": "中芯国际", "industry": "半导体"},
    ]

    # 根据关键词筛选
    results = []
    for stock in all_stocks:
        if (
            keyword.lower() in stock["symbol"].lower()
            or keyword.lower() in stock["name"].lower()
        ):
            results.append(stock)

    # 如果没有匹配结果，返回所有股票
    if not results:
        results = all_stocks

    # 限制数量
    results = results[:limit]

    return {"results": results, "total": len(results), "keyword": keyword}


def get_stock_by_industry(params: Dict) -> Dict:
    """按行业获取股票

    Args:
        params: Dict - 查询参数：
                industry_name: str - 行业名称
                page: int - 页码
                limit: int - 每页数量

    Returns:
        Dict: 行业股票列表
    """
    industry_name = params.get("industry_name", "")
    page = params.get("page", 1)
    limit = params.get("limit", 20)

    # 模拟各行业股票数据
    industry_stocks = {
        "白酒": [
            {
                "symbol": "600519",
                "name": "贵州茅台",
                "price": round(random.uniform(1500, 2000), 2),
            },
            {
                "symbol": "000858",
                "name": "五粮液",
                "price": round(random.uniform(130, 250), 2),
            },
            {
                "symbol": "000568",
                "name": "泸州老窖",
                "price": round(random.uniform(150, 250), 2),
            },
            {
                "symbol": "002304",
                "name": "洋河股份",
                "price": round(random.uniform(80, 180), 2),
            },
        ],
        "银行": [
            {
                "symbol": "600036",
                "name": "招商银行",
                "price": round(random.uniform(30, 50), 2),
            },
            {
                "symbol": "000001",
                "name": "平安银行",
                "price": round(random.uniform(10, 20), 2),
            },
            {
                "symbol": "601398",
                "name": "工商银行",
                "price": round(random.uniform(4, 7), 2),
            },
            {
                "symbol": "601939",
                "name": "建设银行",
                "price": round(random.uniform(5, 8), 2),
            },
        ],
        "医药": [
            {
                "symbol": "600276",
                "name": "恒瑞医药",
                "price": round(random.uniform(35, 60), 2),
            },
            {
                "symbol": "300142",
                "name": "沃森生物",
                "price": round(random.uniform(20, 50), 2),
            },
            {
                "symbol": "300122",
                "name": "智飞生物",
                "price": round(random.uniform(70, 150), 2),
            },
        ],
    }

    # 获取指定行业的股票
    stocks = industry_stocks.get(industry_name, industry_stocks.get("白酒", []))

    # 分页
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_stocks = stocks[start_idx:end_idx]

    return {
        "industry": industry_name,
        "stocks": paginated_stocks,
        "total": len(stocks),
        "page": page,
        "limit": limit,
        "total_pages": (len(stocks) + limit - 1) // limit,
    }


def get_watchlist() -> Dict:
    """获取自选股列表

    Returns:
        Dict: 自选股列表
    """
    watchlist_stocks = [
        {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": round(random.uniform(1500, 2000), 2),
            "change": round(random.uniform(-5, 5), 2),
        },
        {
            "symbol": "300750",
            "name": "宁德时代",
            "price": round(random.uniform(200, 500), 2),
            "change": round(random.uniform(-5, 5), 2),
        },
        {
            "symbol": "688981",
            "name": "中芯国际",
            "price": round(random.uniform(50, 100), 2),
            "change": round(random.uniform(-5, 5), 2),
        },
        {
            "symbol": "000858",
            "name": "五粮液",
            "price": round(random.uniform(130, 250), 2),
            "change": round(random.uniform(-5, 5), 2),
        },
    ]

    return {
        "watchlist": watchlist_stocks,
        "total": len(watchlist_stocks),
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def add_to_watchlist(params: Dict) -> Dict:
    """添加到自选股

    Args:
        params: Dict - 请求参数：
                stock_code: str - 股票代码
                notes: str - 备注（可选）

    Returns:
        Dict: 添加结果
    """
    stock_code = params.get("stock_code", "")
    notes = params.get("notes", "")

    return {
        "success": True,
        "message": f"股票{stock_code}已添加到自选股",
        "stock_code": stock_code,
        "notes": notes,
        "added_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def remove_from_watchlist(params: Dict) -> Dict:
    """从自选股移除

    Args:
        params: Dict - 查询参数：
                stock_code: str - 股票代码

    Returns:
        Dict: 移除结果
    """
    stock_code = params.get("stock_code", "")

    return {
        "success": True,
        "message": f"股票{stock_code}已从自选股移除",
        "stock_code": stock_code,
        "removed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def generate_realistic_price(
    base_price: float = 100.0, volatility: float = 0.02
) -> float:
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
    print("Mock文件模板测试")
    print("=" * 50)
    print("get_stock_list() 调用测试:")
    result1 = get_stock_list(exchange="sh")
    print(f"返回数据: {result1}")

    print("\nget_stock_detail() 调用测试:")
    result2 = get_stock_detail({"stock_code": "600000"})
    print(f"返回数据: {result2}")

    print("\nget_stock_indicators() 调用测试:")
    result3 = get_stock_indicators({"stock_code": "600000"})
    print(f"返回数据: {result3}")
