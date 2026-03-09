import datetime
import random
from typing import Dict, List, Optional


def get_stock_list(params: Optional[Dict] = None) -> List[Dict]:
    """获取股票列表（支持按交易所筛选，支持分页）"""
    params = params or {}
    exchange = params.get("exchange")
    limit = params.get("limit", 20)
    offset = params.get("offset", 0)

    stock_pools = {
        "sh": [
            {"symbol": "600519", "name": "贵州茅台", "industry": "白酒", "area": "贵州", "market": "上交所"},
            {"symbol": "600036", "name": "招商银行", "industry": "银行", "area": "深圳", "market": "上交所"},
            {"symbol": "600276", "name": "恒瑞医药", "industry": "医药生物", "area": "江苏", "market": "上交所"},
            {"symbol": "600009", "name": "上海机场", "industry": "机场航运", "area": "上海", "market": "上交所"},
            {"symbol": "600000", "name": "浦发银行", "industry": "银行", "area": "上海", "market": "上交所"},
            {"symbol": "600887", "name": "伊利股份", "industry": "食品饮料", "area": "内蒙古", "market": "上交所"},
            {"symbol": "600104", "name": "上汽集团", "industry": "汽车", "area": "上海", "market": "上交所"},
            {"symbol": "600585", "name": "海螺水泥", "industry": "建筑材料", "area": "安徽", "market": "上交所"},
        ],
        "sz": [
            {"symbol": "000001", "name": "平安银行", "industry": "银行", "area": "深圳", "market": "深交所"},
            {"symbol": "000002", "name": "万科A", "industry": "房地产", "area": "深圳", "market": "深交所"},
            {"symbol": "000858", "name": "五粮液", "industry": "白酒", "area": "四川", "market": "深交所"},
            {"symbol": "000776", "name": "广发证券", "industry": "非银金融", "area": "广东", "market": "深交所"},
            {"symbol": "000568", "name": "泸州老窖", "industry": "白酒", "area": "四川", "market": "深交所"},
            {"symbol": "000166", "name": "申万宏源", "industry": "非银金融", "area": "深圳", "market": "深交所"},
            {"symbol": "000063", "name": "中兴通讯", "industry": "通信", "area": "广东", "market": "深交所"},
            {"symbol": "000100", "name": "TCL科技", "industry": "电子", "area": "广东", "market": "深交所"},
        ],
    }

    if exchange:
        available_stocks = stock_pools.get(exchange, [])
    else:
        available_stocks = stock_pools["sh"] + stock_pools["sz"]

    total_stocks = len(available_stocks)
    paginated_stocks = available_stocks[offset : offset + limit]

    result = []
    base_date = datetime.datetime.now() - datetime.timedelta(days=3650)

    for stock in paginated_stocks:
        list_date = base_date + datetime.timedelta(days=random.randint(0, 3650))
        result.append(
            {
                "symbol": stock["symbol"],
                "name": stock["name"],
                "industry": stock["industry"],
                "area": stock["area"],
                "market": stock["market"],
                "list_date": list_date.strftime("%Y-%m-%d"),
                "total": total_stocks,
            }
        )

    return result
