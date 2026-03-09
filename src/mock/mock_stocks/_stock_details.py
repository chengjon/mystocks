import datetime
import random
from typing import Dict


def get_stock_detail(params: Dict) -> Dict:
    """获取股票详细信息"""
    stock_code = params.get("stock_code", "600000")
    stock_info = {
        "600519": {"name": "贵州茅台", "industry": "白酒", "area": "贵州", "market": "上交所"},
        "600036": {"name": "招商银行", "industry": "银行", "area": "深圳", "market": "上交所"},
        "000001": {"name": "平安银行", "industry": "银行", "area": "深圳", "market": "深交所"},
        "000002": {"name": "万科A", "industry": "房地产", "area": "深圳", "market": "深交所"},
        "000858": {"name": "五粮液", "industry": "白酒", "area": "四川", "market": "深交所"},
        "600276": {"name": "恒瑞医药", "industry": "医药生物", "area": "江苏", "market": "上交所"},
        "600000": {"name": "浦发银行", "industry": "银行", "area": "上海", "market": "上交所"},
        "600887": {"name": "伊利股份", "industry": "食品饮料", "area": "内蒙古", "market": "上交所"},
    }

    info = stock_info.get(
        stock_code,
        {"name": f"股票{stock_code}", "industry": "未知", "area": "未知", "market": "未知"},
    )

    return {
        "symbol": stock_code,
        "name": info["name"],
        "industry": info["industry"],
        "area": info["area"],
        "market": info["market"],
        "list_date": (datetime.datetime.now() - datetime.timedelta(days=random.randint(1000, 5000))).strftime(
            "%Y-%m-%d"
        ),
        "total_shares": random.randint(100000000, 10000000000),
        "circulating_shares": random.randint(50000000, 8000000000),
        "pe_ratio": round(random.uniform(5, 50), 2),
        "pb_ratio": round(random.uniform(0.5, 5), 2),
    }


def get_stock_financial_data(params: Dict) -> Dict:
    """获取股票财务数据"""
    stock_code = params.get("stock_code", "600000")

    return {
        "symbol": stock_code,
        "name": f"股票{stock_code}",
        "financial_data": {
            "revenue": round(random.uniform(1000000000, 50000000000), 2),
            "net_profit": round(random.uniform(100000000, 10000000000), 2),
            "total_assets": round(random.uniform(5000000000, 100000000000), 2),
            "net_assets": round(random.uniform(2000000000, 50000000000), 2),
            "roa": round(random.uniform(0.01, 0.15), 4),
            "roe": round(random.uniform(0.02, 0.25), 4),
            "debt_ratio": round(random.uniform(0.2, 0.6), 4),
            "current_ratio": round(random.uniform(0.8, 2.5), 2),
            "report_date": (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365))).strftime(
                "%Y-%m-%d"
            ),
        },
    }


def get_stock_indicators(params: Dict) -> Dict:
    """获取股票技术指标"""
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
