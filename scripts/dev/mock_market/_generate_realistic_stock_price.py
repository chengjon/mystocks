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



from scripts.dev.mock_market._mock_market_tail import get_chip_race, get_etf_list, get_lhb_detail, get_stock_list
