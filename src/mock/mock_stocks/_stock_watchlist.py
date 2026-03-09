import datetime
import random
from typing import Dict


def get_watchlist() -> Dict:
    """获取自选股列表"""
    watchlist_stocks = [
        {"symbol": "600519", "name": "贵州茅台", "price": round(random.uniform(1500, 2000), 2), "change": round(random.uniform(-5, 5), 2)},
        {"symbol": "300750", "name": "宁德时代", "price": round(random.uniform(200, 500), 2), "change": round(random.uniform(-5, 5), 2)},
        {"symbol": "688981", "name": "中芯国际", "price": round(random.uniform(50, 100), 2), "change": round(random.uniform(-5, 5), 2)},
        {"symbol": "000858", "name": "五粮液", "price": round(random.uniform(130, 250), 2), "change": round(random.uniform(-5, 5), 2)},
    ]

    return {
        "watchlist": watchlist_stocks,
        "total": len(watchlist_stocks),
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def add_to_watchlist(params: Dict) -> Dict:
    """添加到自选股"""
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
    """从自选股移除"""
    stock_code = params.get("stock_code", "")

    return {
        "success": True,
        "message": f"股票{stock_code}已从自选股移除",
        "stock_code": stock_code,
        "removed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
