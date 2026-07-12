"""自选股 mock 数据辅助函数。"""

from datetime import datetime
from typing import Any, Dict


def get_watchlist_mock_data(manager, **kwargs) -> Dict[str, Any]:
    """生成自选股相关 mock 响应。"""
    user_id = kwargs.get("user_id", 1)
    action = kwargs.get("action", "list")

    if action in {"list", "/list"}:
        watchlist_data = manager._generate_watchlist_data(user_id)
        return {
            "success": True,
            "data": watchlist_data,
            "total": len(watchlist_data),
            "message": "获取自选股列表成功",
            "timestamp": datetime.now().isoformat(),
        }

    if action in {"symbols", "/symbols"}:
        watchlist_data = manager._generate_watchlist_data(user_id)
        symbols = [item["symbol"] for item in watchlist_data]
        return {
            "success": True,
            "data": symbols,
            "total": len(symbols),
            "message": "获取自选股代码列表成功",
            "timestamp": datetime.now().isoformat(),
        }

    if action in {"count", "/count"}:
        watchlist_data = manager._generate_watchlist_data(user_id)
        return {
            "success": True,
            "data": {"count": len(watchlist_data)},
            "message": "获取自选股数量成功",
            "timestamp": datetime.now().isoformat(),
        }

    if action.startswith("add/"):
        symbol = kwargs.get("symbol", "")
        return {
            "success": True,
            "message": f"成功添加 {symbol} 到自选股",
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
        }

    if action.startswith("remove/"):
        symbol = kwargs.get("symbol", "")
        return {
            "success": True,
            "message": f"成功从自选股移除 {symbol}",
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
        }

    if action == "check":
        symbol = kwargs.get("symbol", "")
        watchlist_data = manager._generate_watchlist_data(user_id)
        is_in_watchlist = any(item["symbol"] == symbol for item in watchlist_data)
        return {
            "success": True,
            "data": {"symbol": symbol, "is_in_watchlist": is_in_watchlist},
            "timestamp": datetime.now().isoformat(),
        }

    if action == "update_notes":
        symbol = kwargs.get("symbol", "")
        notes = kwargs.get("notes", "")
        return {
            "success": True,
            "message": f"成功更新 {symbol} 的备注",
            "symbol": symbol,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
        }

    if action == "clear":
        return {
            "success": True,
            "message": "自选股列表已清空",
            "timestamp": datetime.now().isoformat(),
        }

    raise ValueError(f"不支持的watchlist操作: {action}")
