import random
from typing import Dict


def search_stocks(params: Dict) -> Dict:
    """搜索股票"""
    keyword = params.get("q", "")
    limit = params.get("limit", 20)

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

    results = []
    for stock in all_stocks:
        if keyword.lower() in stock["symbol"].lower() or keyword.lower() in stock["name"].lower():
            results.append(stock)

    if not results:
        results = all_stocks

    results = results[:limit]
    return {"results": results, "total": len(results), "keyword": keyword}


def get_stock_by_industry(params: Dict) -> Dict:
    """按行业获取股票"""
    industry_name = params.get("industry_name", "")
    page = params.get("page", 1)
    limit = params.get("limit", 20)

    industry_stocks = {
        "白酒": [
            {"symbol": "600519", "name": "贵州茅台", "price": round(random.uniform(1500, 2000), 2)},
            {"symbol": "000858", "name": "五粮液", "price": round(random.uniform(130, 250), 2)},
            {"symbol": "000568", "name": "泸州老窖", "price": round(random.uniform(150, 250), 2)},
            {"symbol": "002304", "name": "洋河股份", "price": round(random.uniform(80, 180), 2)},
        ],
        "银行": [
            {"symbol": "600036", "name": "招商银行", "price": round(random.uniform(30, 50), 2)},
            {"symbol": "000001", "name": "平安银行", "price": round(random.uniform(10, 20), 2)},
            {"symbol": "601398", "name": "工商银行", "price": round(random.uniform(4, 7), 2)},
            {"symbol": "601939", "name": "建设银行", "price": round(random.uniform(5, 8), 2)},
        ],
        "医药": [
            {"symbol": "600276", "name": "恒瑞医药", "price": round(random.uniform(35, 60), 2)},
            {"symbol": "300142", "name": "沃森生物", "price": round(random.uniform(20, 50), 2)},
            {"symbol": "300122", "name": "智飞生物", "price": round(random.uniform(70, 150), 2)},
        ],
    }

    stocks = industry_stocks.get(industry_name, industry_stocks.get("白酒", []))
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
