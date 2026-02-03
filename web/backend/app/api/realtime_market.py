"""
实时行情 WebSocket API
Real-time Market WebSocket API

提供 WebSocket 实时行情订阅和持仓市值推送功能。

Author: Claude Code
Date: 2026-01-09
Phase: 12.4 - Integrated with DDD Architecture
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import structlog
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.services.market_data_parser import get_market_data_parser

# 保留旧接口以兼容性
# Phase 12.4: 使用新的 DDD 架构适配器
from web.backend.app.api.realtime_mtm_adapter import MTMUpdate, get_mtm_engine

logger = structlog.get_logger()

router = APIRouter()


@dataclass
class SubscriptionInfo:
    """订阅信息"""

    symbol: str
    subscribed_at: datetime
    fields: List[str] = None


class WebSocketConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.symbol_subscriptions: Dict[str, set] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """建立连接"""
        await websocket.accept()
        self.active_connections[client_id] = {
            "websocket": websocket,
            "connected_at": datetime.now(),
            "subscriptions": set(),
        }
        logger.info("WebSocket client connected: %(client_id)s")

    def disconnect(self, client_id: str):
        """断开连接"""
        if client_id in self.active_connections:
            subscriptions = self.active_connections[client_id]["subscriptions"]
            for symbol in subscriptions:
                if symbol in self.symbol_subscriptions:
                    self.symbol_subscriptions[symbol].discard(client_id)
                    if not self.symbol_subscriptions[symbol]:
                        del self.symbol_subscriptions[symbol]
            del self.active_connections[client_id]
            logger.info("WebSocket client disconnected: %(client_id)s")

    async def subscribe(self, client_id: str, symbol: str):
        """订阅行情"""
        if client_id not in self.active_connections:
            return False

        self.active_connections[client_id]["subscriptions"].add(symbol)

        if symbol not in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol] = set()
        self.symbol_subscriptions[symbol].add(client_id)

        logger.info("Client %(client_id)s subscribed to %(symbol)s")
        return True

    async def unsubscribe(self, client_id: str, symbol: str):
        """取消订阅"""
        if client_id not in self.active_connections:
            return False

        self.active_connections[client_id]["subscriptions"].discard(symbol)

        if symbol in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol].discard(client_id)
            if not self.symbol_subscriptions[symbol]:
                del self.symbol_subscriptions[symbol]

        logger.info("Client %(client_id)s unsubscribed from %(symbol)s")
        return True

    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """发送个人消息"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]["websocket"]
            await websocket.send_json(message)

    async def broadcast_to_subscribers(self, symbol: str, message: Dict[str, Any]):
        """广播给订阅者"""
        if symbol in self.symbol_subscribers:
            for client_id in self.symbol_subscriptions[symbol]:
                await self.send_personal_message(message, client_id)

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_connections": len(self.active_connections),
            "total_subscriptions": sum(len(s) for s in self.symbol_subscriptions.values()),
            "subscribed_symbols": list(self.symbol_subscriptions.keys()),
        }


manager = WebSocketConnectionManager()


@router.websocket("/ws/market")
async def websocket_market(websocket: WebSocket, client_id: str = Query(default=None)):
    """
    实时行情 WebSocket 端点

    支持：
    - 订阅/取消订阅股票行情
    - 接收实时价格更新
    - 心跳检测
    """
    client_id = client_id or f"client_{id(websocket)}"
    await manager.connect(websocket, client_id)

    mtm_engine = get_mtm_engine()
    parser = get_market_data_parser()

    try:
        while True:
            data = await websocket.receive_json()

            action = data.get("action")
            if action == "subscribe":
                symbol = data.get("symbol")
                if symbol:
                    await manager.subscribe(client_id, symbol)
                    mtm_engine.update_price(symbol, data.get("price", 0))
                    await manager.send_personal_message(
                        {
                            "action": "subscribed",
                            "symbol": symbol,
                            "status": "success",
                        },
                        client_id,
                    )

            elif action == "unsubscribe":
                symbol = data.get("symbol")
                if symbol:
                    await manager.unsubscribe(client_id, symbol)
                    await manager.send_personal_message(
                        {
                            "action": "unsubscribed",
                            "symbol": symbol,
                            "status": "success",
                        },
                        client_id,
                    )

            elif action == "quote":
                symbol = data.get("symbol")
                price = data.get("price")
                if symbol and price is not None:
                    parsed = parser.parse({"symbol": symbol, "price": price}, "websocket")
                    if parsed:
                        updates = mtm_engine.update_price(symbol, parsed.price)
                        await manager.send_personal_message(
                            {
                                "action": "quote_update",
                                "data": parsed.to_dict(),
                            },
                            client_id,
                        )

            elif action == "ping":
                await manager.send_personal_message(
                    {"action": "pong", "timestamp": datetime.now().isoformat()},
                    client_id,
                )

            else:
                await manager.send_personal_message(
                    {"action": "error", "message": f"Unknown action: {action}"},
                    client_id,
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error("WebSocket error: %(e)s")
        manager.disconnect(client_id)


@router.websocket("/ws/portfolio")
async def websocket_portfolio(
    websocket: WebSocket, portfolio_id: str = Query(default=None), client_id: str = Query(default=None)
):
    """
    持仓市值实时推送 WebSocket 端点

    支持：
    - 注册持仓
    - 接收市值更新
    - 组合快照推送
    """
    client_id = client_id or f"client_{id(websocket)}"
    portfolio_id = portfolio_id or f"portfolio_{client_id}"
    await manager.connect(websocket, client_id)

    mtm_engine = get_mtm_engine()

    try:
        initial_snapshot = mtm_engine.get_portfolio_snapshot(portfolio_id)
        await manager.send_personal_message(
            {
                "action": "connected",
                "portfolio_id": portfolio_id,
                "snapshot": _snapshot_to_dict(initial_snapshot) if initial_snapshot else None,
            },
            client_id,
        )

        while True:
            data = await websocket.receive_json()

            action = data.get("action")

            if action == "register_position":
                position_id = data.get("position_id")
                symbol = data.get("symbol")
                quantity = data.get("quantity")
                avg_price = data.get("avg_price")

                if all([position_id, symbol, quantity is not None, avg_price is not None]):
                    mtm_engine.register_position(
                        position_id=position_id,
                        portfolio_id=portfolio_id,
                        symbol=symbol,
                        quantity=int(quantity),
                        avg_price=float(avg_price),
                    )
                    await manager.send_personal_message(
                        {"action": "position_registered", "position_id": position_id},
                        client_id,
                    )

            elif action == "update_price":
                symbol = data.get("symbol")
                price = data.get("price")

                if symbol and price is not None:
                    updates = mtm_engine.update_price(symbol, float(price))

                    snapshot = mtm_engine.get_portfolio_snapshot(portfolio_id)

                    await manager.send_personal_message(
                        {
                            "action": "portfolio_update",
                            "snapshot": _snapshot_to_dict(snapshot),
                            "updates": [_update_to_dict(u) for u in updates],
                        },
                        client_id,
                    )

            elif action == "get_snapshot":
                snapshot = mtm_engine.get_portfolio_snapshot(portfolio_id)
                await manager.send_personal_message(
                    {"action": "snapshot", "snapshot": _snapshot_to_dict(snapshot)},
                    client_id,
                )

            elif action == "ping":
                await manager.send_personal_message(
                    {"action": "pong", "timestamp": datetime.now().isoformat()},
                    client_id,
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error("Portfolio WebSocket error: %(e)s")
        manager.disconnect(client_id)


@router.get("/api/realtime/quote/{symbol}")
async def get_realtime_quote(symbol: str):
    """
    获取股票实时行情

    通过 akshare 或其他数据源获取实时行情
    """
    try:
        parser = get_market_data_parser()

        try:
            import akshare as ak

            stock_zh_a_spot_df = ak.stock_zh_a_spot(symbol=symbol)
            if not stock_zh_a_spot_df.empty:
                row = stock_zh_a_spot_df.iloc[0]
                data = {
                    "symbol": symbol,
                    "name": row.get("名称", ""),
                    "price": row.get("最新价", 0),
                    "open": row.get("开盘", 0),
                    "high": row.get("最高", 0),
                    "low": row.get("最低", 0),
                    "pre_close": row.get("昨收", 0),
                    "volume": row.get("成交量", 0),
                    "amount": row.get("成交额", 0),
                    "change": row.get("涨跌额", 0),
                    "change_percent": row.get("涨跌幅", 0),
                }
                return {"success": True, "data": data}
        except Exception as e:
            logger.warning("Failed to fetch quote via akshare: %(e)s")

        return {"success": False, "error": "Failed to fetch quote"}

    except Exception as e:
        logger.error("Error fetching quote: %(e)s")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/realtime/quotes")
async def get_realtime_quotes(symbols: str = Query(..., description="股票代码列表，逗号分隔")):
    """
    批量获取股票实时行情
    """
    try:
        symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
        results = {}

        try:
            import akshare as ak

            stock_zh_a_spot_df = ak.stock_zh_a_spot()
            if not stock_zh_a_spot_df.empty:
                for symbol in symbol_list:
                    row = stock_zh_a_spot_df[stock_zh_a_spot_df["代码"] == symbol]
                    if not row.empty:
                        r = row.iloc[0]
                        results[symbol] = {
                            "symbol": symbol,
                            "name": r.get("名称", ""),
                            "price": r.get("最新价", 0),
                            "change_percent": r.get("涨跌幅", 0),
                        }
        except Exception as e:
            logger.warning("Failed to fetch quotes via akshare: %(e)s")

        return {"success": True, "data": results}

    except Exception as e:
        logger.error("Error fetching quotes: %(e)s")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/mtm/portfolio/{portfolio_id}")
async def get_portfolio_mtm(portfolio_id: str):
    """
    获取投资组合市值快照
    """
    try:
        mtm_engine = get_mtm_engine()
        snapshot = mtm_engine.get_portfolio_snapshot(portfolio_id)

        if not snapshot:
            return {"success": False, "error": "Portfolio not found"}

        return {"success": True, "data": _snapshot_to_dict(snapshot)}

    except Exception as e:
        logger.error("Error getting portfolio MTM: %(e)s")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/mtm/position/{position_id}")
async def get_position_mtm(position_id: str):
    """
    获取单个持仓市值快照
    """
    try:
        mtm_engine = get_mtm_engine()
        position = mtm_engine.get_position_snapshot(position_id)

        if not position:
            return {"success": False, "error": "Position not found"}

        return {
            "success": True,
            "data": {
                "position_id": position.position_id,
                "symbol": position.symbol,
                "quantity": position.quantity,
                "avg_price": position.avg_price,
                "market_price": position.market_price,
                "market_value": position.market_value,
                "unrealized_profit": position.unrealized_profit,
                "profit_ratio": position.profit_ratio,
                "total_profit": position.total_profit,
                "last_update": position.last_update.isoformat(),
            },
        }

    except Exception as e:
        logger.error("Error getting position MTM: %(e)s")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/mtm/stats")
async def get_mtm_stats():
    """
    获取 MTM 引擎统计信息
    """
    try:
        mtm_engine = get_mtm_engine()
        return {
            "success": True,
            "data": {
                "engine_metrics": mtm_engine.get_metrics(),
                "connection_stats": manager.get_stats(),
            },
        }
    except Exception as e:
        logger.error("Error getting MTM stats: %(e)s")
        raise HTTPException(status_code=500, detail=str(e))


def _snapshot_to_dict(snapshot) -> Dict[str, Any]:
    """转换组合快照为字典"""
    if not snapshot:
        return None
    return {
        "portfolio_id": snapshot.portfolio_id,
        "total_market_value": round(snapshot.total_market_value, 2),
        "total_cost": round(snapshot.total_cost, 2),
        "total_unrealized_profit": round(snapshot.total_unrealized_profit, 2),
        "total_realized_profit": round(snapshot.total_realized_profit, 2),
        "total_profit": round(snapshot.total_profit, 2),
        "profit_ratio": round(snapshot.profit_ratio, 2),
        "cash_balance": round(snapshot.cash_balance, 2),
        "available_cash": round(snapshot.available_cash, 2),
        "position_count": snapshot.position_count,
        "last_update": snapshot.last_update.isoformat(),
        "positions": {
            pid: {
                "position_id": p.position_id,
                "symbol": p.symbol,
                "quantity": p.quantity,
                "avg_price": round(p.avg_price, 2),
                "market_price": round(p.market_price, 2),
                "market_value": round(p.market_value, 2),
                "unrealized_profit": round(p.unrealized_profit, 2),
                "profit_ratio": round(p.profit_ratio, 2),
            }
            for pid, p in snapshot.positions.items()
        },
    }


def _update_to_dict(update: MTMUpdate) -> Dict[str, Any]:
    """转换更新事件为字典"""
    return {
        "position_id": update.position_id,
        "symbol": update.symbol,
        "old_price": round(update.old_price, 2),
        "new_price": round(update.new_price, 2),
        "profit_change": round(update.profit_change, 2),
        "timestamp": update.timestamp.isoformat(),
    }
