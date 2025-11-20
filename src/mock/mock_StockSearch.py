"""
Mock数据文件: StockSearch
提供接口:
1. search_stocks() -> List[Dict] - 搜索股票（支持按代码、名称、行业搜索）
2. get_stock_detail() -> Dict - 获取股票详情
3. get_industry_list() -> List[Dict] - 获取行业列表
4. get_stock_concept() -> List[Dict] - 获取概念板块

使用说明:
- 所有函数参数需与真实API接口完全对齐
- 返回值字段名需与前端表格列字段一致
- 股票价格保留2位小数，百分比保留4位小数
- 时间字段使用datetime类型，格式：YYYY-MM-DD HH:MM:SS

作者: Claude Code
生成时间: 2025-11-13
"""

from typing import List, Dict, Optional, Any
import pandas as pd
import datetime
import random
import numpy as np
import math
from decimal import Decimal


def _generate_realistic_market_cap() -> float:
    """生成更真实的市值分布（对数正态分布）"""
    # 市值分布近似对数正态分布
    log_market_cap = np.random.normal(11, 1.5)  # log(市值) ~ N(11, 1.5)
    market_cap = np.exp(log_market_cap)  # e^log(市值)
    return round(market_cap, 0)


def _generate_correlated_price_data(base_price: float) -> Dict[str, float]:
    """生成相关联的价格、涨跌幅、成交量数据"""
    # 生成正态分布的日收益率
    daily_return = np.random.normal(0, 0.025)  # 2.5%日波动率
    daily_return = max(min(daily_return, 0.15), -0.15)  # 限制在±15%范围内
    
    # 计算价格和变动
    price = base_price * (1 + daily_return)
    price = round(max(price, 0.1), 2)  # 确保价格为正
    
    change_amount = round(price - base_price, 2)
    change_pct = round(daily_return * 100, 4)
    
    # 生成与价格相关的成交量（高价股通常成交量较小）
    volume_base = max(1000000, 50000000 / price)  # 反比例关系
    volume = int(volume_base * random.uniform(0.3, 3.0))
    
    return {
        "price": price,
        "change_amount": change_amount,
        "change_pct": change_pct,
        "volume": volume
    }


def search_stocks(keyword: str = "", industry: str = "", market: str = "", limit: int = 20) -> List[Dict]:
    """搜索股票（支持按代码、名称、行业搜索）
    
    Args:
        keyword: str - 搜索关键词（股票代码或名称）
        industry: str - 行业筛选
        market: str - 市场筛选 (SSE/SZSE)
        limit: int - 返回数量限制
        
    Returns:
        List[Dict]: 搜索结果，包含：
                   - symbol: 股票代码
                   - name: 股票名称
                   - industry: 所属行业
                   - market: 市场
                   - current_price: 当前价格
                   - change_pct: 涨跌幅(%)
                   - volume: 成交量
                   - market_cap: 市值
    """
    # 股票数据库
    stock_database = [
        # 上海证券交易所
        {"symbol": "600519", "name": "贵州茅台", "industry": "白酒", "market": "SSE", "base_price": 1800.0},
        {"symbol": "600036", "name": "招商银行", "industry": "银行", "market": "SSE", "base_price": 35.0},
        {"symbol": "600276", "name": "恒瑞医药", "industry": "医药生物", "market": "SSE", "base_price": 45.0},
        {"symbol": "600009", "name": "上海机场", "industry": "机场航运", "market": "SSE", "base_price": 65.0},
        {"symbol": "600000", "name": "浦发银行", "industry": "银行", "market": "SSE", "base_price": 8.0},
        {"symbol": "600887", "name": "伊利股份", "industry": "食品饮料", "market": "SSE", "base_price": 28.0},
        {"symbol": "600104", "name": "上汽集团", "industry": "汽车", "market": "SSE", "base_price": 12.5},
        {"symbol": "600585", "name": "海螺水泥", "industry": "建筑材料", "market": "SSE", "base_price": 28.5},
        
        # 深圳证券交易所
        {"symbol": "000001", "name": "平安银行", "industry": "银行", "market": "SZSE", "base_price": 12.0},
        {"symbol": "000002", "name": "万科A", "industry": "房地产", "market": "SZSE", "base_price": 8.5},
        {"symbol": "000858", "name": "五粮液", "industry": "白酒", "market": "SZSE", "base_price": 150.0},
        {"symbol": "000776", "name": "广发证券", "industry": "非银金融", "market": "SZSE", "base_price": 15.5},
        {"symbol": "000568", "name": "泸州老窖", "industry": "白酒", "market": "SZSE", "base_price": 120.0},
        {"symbol": "000166", "name": "申万宏源", "industry": "非银金融", "market": "SZSE", "base_price": 4.2},
        {"symbol": "000063", "name": "中兴通讯", "industry": "通信", "market": "SZSE", "base_price": 28.0},
        {"symbol": "000100", "name": "TCL科技", "industry": "电子", "market": "SZSE", "base_price": 5.8}
    ]
    
    # 应用筛选条件
    filtered_stocks = stock_database
    
    if keyword:
        keyword = keyword.lower()
        filtered_stocks = [
            stock for stock in filtered_stocks 
            if keyword in stock["symbol"].lower() or keyword in stock["name"].lower()
        ]
    
    if industry:
        filtered_stocks = [stock for stock in filtered_stocks if stock["industry"] == industry]
    
    if market:
        filtered_stocks = [stock for stock in filtered_stocks if stock["market"] == market]
    
    # 生成搜索结果
    results = []
    for stock in filtered_stocks[:limit]:
        # 使用更真实的价格数据生成
        base_price = stock["base_price"]
        price_data = _generate_correlated_price_data(base_price)
        
        # 生成真实的市值分布
        market_cap = _generate_realistic_market_cap()
        
        results.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "industry": stock["industry"],
            "market": stock["market"],
            "current_price": price_data["price"],
            "change_pct": price_data["change_pct"],
            "volume": price_data["volume"],
            "market_cap": market_cap
        })
    
    return results


def get_stock_detail(symbol: str) -> Dict:
    """获取股票详情
    
    Args:
        symbol: str - 股票代码
        
    Returns:
        Dict: 股票详情，包含：
             - basic_info: 基本信息
             - financial_info: 财务信息
             - price_info: 价格信息
             - business_scope: 经营范围
    """
    # 股票详细信息数据库
    stock_detail_db = {
        "600519": {
            "name": "贵州茅台",
            "industry": "白酒",
            "area": "贵州",
            "market": "SSE",
            "list_date": "2001-08-27",
            "business_scope": "茅台酒及系列产品生产、销售",
            "employees": 28000,
            "reg_capital": 25185.0,  # 亿元
            "total_shares": 251850.0,  # 万股
        },
        "600036": {
            "name": "招商银行",
            "industry": "银行",
            "area": "深圳",
            "market": "SSE",
            "list_date": "2002-04-09",
            "business_scope": "银行业务",
            "employees": 92000,
            "reg_capital": 252.2,
            "total_shares": 252200.0,
        },
        "000001": {
            "name": "平安银行",
            "industry": "银行",
            "area": "深圳",
            "market": "SZSE",
            "list_date": "1991-04-03",
            "business_scope": "银行业务",
            "employees": 38000,
            "reg_capital": 194.1,
            "total_shares": 194100.0,
        }
    }
    
    # 获取股票基础信息
    detail_info = stock_detail_db.get(symbol, {
        "name": f"股票{symbol}",
        "industry": "未知",
        "area": "未知",
        "market": "未知",
        "list_date": "2000-01-01",
        "business_scope": "未披露",
        "employees": 0,
        "reg_capital": 0.0,
        "total_shares": 0.0,
    })
    
    # 生成财务信息
    base_price = random.uniform(10.0, 100.0)
    current_price = round(base_price * (1 + random.uniform(-0.1, 0.1)), 2)
    
    financial_info = {
        "market_cap": int(current_price * detail_info["total_shares"] * 10000),
        "pe_ratio": round(random.uniform(8.0, 50.0), 2),
        "pb_ratio": round(random.uniform(0.5, 3.0), 2),
        "roe": round(random.uniform(5.0, 25.0), 2),
        "debt_ratio": round(random.uniform(30.0, 90.0), 2),
        "revenue_growth": round(random.uniform(-20.0, 30.0), 2),
        "net_profit_growth": round(random.uniform(-30.0, 40.0), 2),
    }
    
    # 生成价格信息
    change_amount = round(random.uniform(-5.0, 5.0), 2)
    change_pct = round((change_amount / base_price) * 100, 2)
    
    price_info = {
        "current_price": current_price,
        "open_price": round(base_price + random.uniform(-2.0, 2.0), 2),
        "high_price": round(max(base_price, current_price) + random.uniform(0, 3.0), 2),
        "low_price": round(min(base_price, current_price) - random.uniform(0, 3.0), 2),
        "pre_close": round(base_price, 2),
        "change": change_amount,
        "change_pct": change_pct,
        "volume": random.randint(1000000, 50000000),
        "amount": round(current_price * random.randint(1000000, 50000000), 2),
        "turnover_rate": round(random.uniform(0.1, 10.0), 2),
    }
    
    return {
        "symbol": symbol,
        "basic_info": {
            "name": detail_info["name"],
            "industry": detail_info["industry"],
            "area": detail_info["area"],
            "market": detail_info["market"],
            "list_date": detail_info["list_date"],
            "business_scope": detail_info["business_scope"],
            "employees": detail_info["employees"],
            "reg_capital": detail_info["reg_capital"],
            "total_shares": detail_info["total_shares"],
        },
        "financial_info": financial_info,
        "price_info": price_info,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def get_industry_list() -> List[Dict]:
    """获取行业列表
    
    Returns:
        List[Dict]: 行业列表，包含：
                   - industry: 行业名称
                   - stock_count: 股票数量
                   - avg_change_pct: 平均涨跌幅
                   - total_market_cap: 总市值
    """
    industries = [
        {"name": "银行", "base_count": 42, "base_cap": 8500000000000},
        {"name": "白酒", "base_count": 18, "base_cap": 2800000000000},
        {"name": "房地产", "base_count": 125, "base_cap": 1800000000000},
        {"name": "医药生物", "base_count": 320, "base_cap": 4500000000000},
        {"name": "汽车", "base_count": 185, "base_cap": 2100000000000},
        {"name": "电子", "base_count": 520, "base_cap": 3800000000000},
        {"name": "通信", "base_count": 95, "base_cap": 1600000000000},
        {"name": "食品饮料", "base_count": 88, "base_cap": 2200000000000},
        {"name": "非银金融", "base_count": 68, "base_cap": 3500000000000},
        {"name": "建筑材料", "base_count": 65, "base_cap": 1200000000000},
        {"name": "机场航运", "base_count": 25, "base_cap": 850000000000},
    ]
    
    industry_list = []
    for industry in industries:
        # 生成行业数据
        stock_count = industry["base_count"] + random.randint(-20, 50)
        avg_change_pct = round(random.uniform(-3.0, 3.0), 2)
        total_market_cap = int(industry["base_cap"] * (1 + random.uniform(-0.2, 0.5)))
        
        industry_list.append({
            "industry": industry["name"],
            "stock_count": stock_count,
            "avg_change_pct": avg_change_pct,
            "total_market_cap": total_market_cap,
            "leading_stocks": get_leading_stocks_by_industry(industry["name"])
        })
    
    return industry_list


def get_stock_concept(concept_name: str = "") -> List[Dict]:
    """获取概念板块
    
    Args:
        concept_name: str - 概念名称（可选）
        
    Returns:
        List[Dict]: 概念板块数据，包含：
                   - concept_name: 概念名称
                   - stock_count: 股票数量
                   - avg_change_pct: 平均涨跌幅
                   - leading_stocks: 龙头股票
    """
    concepts = [
        {"name": "人工智能", "stocks": ["000063", "002230", "300674", "600588"], "base_change": 2.5},
        {"name": "新能源汽车", "stocks": ["002594", "300750", "600104", "000625"], "base_change": 1.8},
        {"name": "5G概念", "stocks": ["000063", "600050", "002396", "300496"], "base_change": 0.9},
        {"name": "芯片概念", "stocks": ["600460", "002049", "300661", "688981"], "base_change": -1.2},
        {"name": "白酒概念", "stocks": ["600519", "000858", "000568", "603589"], "base_change": 3.2},
        {"name": "碳中和", "stocks": ["002714", "300750", "600885", "002129"], "base_change": 0.5},
        {"name": "光伏概念", "stocks": ["300750", "002459", "601012", "300274"], "base_change": -0.8},
        {"name": "医药生物", "stocks": ["600276", "000661", "300015", "002821"], "base_change": 1.1},
    ]
    
    if concept_name:
        concepts = [c for c in concepts if concept_name.lower() in c["name"].lower()]
    
    concept_list = []
    for concept in concepts:
        # 生成概念数据
        stock_count = len(concept["stocks"])
        avg_change_pct = round(concept["base_change"] + random.uniform(-2.0, 2.0), 2)
        leading_stocks = []
        
        for stock_symbol in concept["stocks"][:3]:  # 取前3只作为龙头
            stock_name = get_stock_name_by_symbol(stock_symbol)
            current_price = round(random.uniform(10.0, 100.0), 2)
            change_pct = round(avg_change_pct + random.uniform(-1.0, 1.0), 2)
            
            leading_stocks.append({
                "symbol": stock_symbol,
                "name": stock_name,
                "price": current_price,
                "change_pct": change_pct
            })
        
        concept_list.append({
            "concept_name": concept["name"],
            "stock_count": stock_count,
            "avg_change_pct": avg_change_pct,
            "leading_stocks": leading_stocks
        })
    
    return concept_list


def get_stock_name_by_symbol(symbol: str) -> str:
    """根据股票代码获取股票名称"""
    stock_names = {
        "000063": "中兴通讯",
        "002230": "科大讯飞", 
        "300674": "宇信科技",
        "600588": "用友网络",
        "002594": "比亚迪",
        "300750": "宁德时代",
        "600104": "上汽集团",
        "000625": "长安汽车",
        "600050": "中国联通",
        "002396": "星网锐捷",
        "300496": "中科创达",
        "600460": "士兰微",
        "002049": "紫光国微",
        "300661": "美格智能",
        "688981": "纳芯微",
        "600519": "贵州茅台",
        "000858": "五粮液",
        "000568": "泸州老窖",
        "603589": "金种子酒",
        "002714": "牧原股份",
        "600885": "宏发股份",
        "002129": "中环股份",
        "002459": "晶澳科技",
        "601012": "隆基绿能",
        "300274": "阳光电源",
        "000661": "长春高新",
        "300015": "爱尔眼科",
        "002821": "凯莱英"
    }
    return stock_names.get(symbol, f"股票{symbol}")


def get_leading_stocks_by_industry(industry: str) -> List[Dict]:
    """根据行业获取龙头股票"""
    industry_leaders = {
        "银行": [
            {"symbol": "600036", "name": "招商银行", "market_cap": 950000000000},
            {"symbol": "000001", "name": "平安银行", "market_cap": 232000000000},
            {"symbol": "600000", "name": "浦发银行", "market_cap": 236000000000}
        ],
        "白酒": [
            {"symbol": "600519", "name": "贵州茅台", "market_cap": 2300000000000},
            {"symbol": "000858", "name": "五粮液", "market_cap": 580000000000},
            {"symbol": "000568", "name": "泸州老窖", "market_cap": 480000000000}
        ],
        "房地产": [
            {"symbol": "000002", "name": "万科A", "market_cap": 95000000000},
            {"symbol": "000001", "name": "平安银行", "market_cap": 232000000000},  # 示例
            {"symbol": "600048", "name": "保利发展", "market_cap": 85000000000}
        ]
    }
    
    return industry_leaders.get(industry, [])


if __name__ == "__main__":
    # 测试函数
    print("Mock StockSearch模块测试")
    print("=" * 50)
    
    print("1. 测试股票搜索:")
    search_results = search_stocks(keyword="银行", limit=5)
    print(f"   搜索'银行'关键词，返回 {len(search_results)} 条结果")
    
    print("\n2. 测试股票详情:")
    stock_detail = get_stock_detail("600519")
    print(f"   获取股票600519详情，包含字段: {list(stock_detail.keys())}")
    
    print("\n3. 测试行业列表:")
    industries = get_industry_list()
    print(f"   返回 {len(industries)} 个行业")
    
    print("\n4. 测试概念板块:")
    concepts = get_stock_concept("人工智能")
    print(f"   人工智能概念，包含 {len(concepts)} 个相关概念")
    
    print("\n测试完成！")