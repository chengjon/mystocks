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

import datetime
import random
from typing import Dict, List, Optional


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


