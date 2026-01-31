"""
交易数据API模块

提供订单、持仓、历史、策略执行等交易相关数据获取功能
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = __import__("logging").getLogger(__name__)


class OrderStatus(Enum):
    """订单状态枚举"""

    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderType(Enum):
    """订单类型"""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    CANCEL = "cancel"
    COVERED_CALL = "covered_call"
    EXERCISE = "exercise"


class OrderSide(Enum):
    """订单方向"""

    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    """订单数据类"""

    order_id: str = ""
    symbol: str = ""
    side: OrderSide = OrderSide.BUY
    order_type: OrderType = OrderType.MARKET
    quantity: float = 0.0
    price: float = 0.0
    amount: float = 0.0
    status: OrderStatus = OrderStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    filled_quantity: float = 0.0
    filled_price: float = 0.0
    commission: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "type": self.order_type.value,
            "quantity": self.quantity,
            "price": self.price,
            "amount": self.amount,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "filled_at": self.filled_at.isoformat() if self.filled_at else None,
            "filled_quantity": self.filled_quantity,
            "filled_price": self.filled_price,
            "commission": self.commission,
        }


@dataclass
class Position:
    """持仓数据类"""

    position_id: str = ""
    symbol: str = ""
    quantity: float = 0.0
    avg_cost: float = 0.0
    current_price: float = 0.0
    market_value: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "position_id": self.position_id,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "avg_cost": self.avg_cost,
            "current_price": self.current_price,
            "market_value": self.market_value,
            "unrealized_pnl": self.unrealized_pnl,
            "realized_pnl": self.realized_pnl,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class Trade:
    """交易记录类"""

    trade_id: str = ""
    order_id: str = ""
    symbol: str = ""
    side: OrderSide = OrderSide.BUY
    quantity: float = 0.0
    price: float = 0.0
    amount: float = 0.0
    commission: float = 0.0
    pnl: float = 0.0
    pnl_percent: float = 0.0
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "trade_id": self.trade_id,
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "quantity": self.quantity,
            "price": self.price,
            "amount": self.amount,
            "commission": self.commission,
            "pnl": self.pnl,
            "pnl_percent": self.pnl_percent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TradingDataService:
    """交易数据服务"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_ttl = 60

        logger.info("交易数据API模块初始化")

    async def create_order(
        self, symbol: str, side: OrderSide, order_type: OrderType, quantity: float, price: Optional[float] = None
    ) -> str:
        """创建订单"""
        try:
            from app.core.database import db_service

            order_id = f"order_{datetime.now().isoformat()}_{symbol}"

            sql = f"""
            INSERT INTO orders
            (order_id, symbol, side, order_type, quantity, price, status, created_at, updated_at)
            VALUES ('{order_id}', '{symbol}', '{side.value}', '{order_type.value}', {quantity}, {price if price else "NULL"}, 'pending', NOW(), NOW())
            """

            await db_service.execute(sql)

            self.logger.info(f"创建订单: {order_id}")
            return order_id

        except Exception as e:
            self.logger.error(f"创建订单失败: {e}")
            raise

    async def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        try:
            from app.core.database import db_service

            sql = f"""
            UPDATE orders
            SET status = 'cancelled', updated_at = NOW()
            WHERE order_id = '{order_id}'
            AND status = 'pending'
            """

            result = await db_service.execute(sql)

            if result:
                self.logger.info(f"取消订单: {order_id}")
                return True
            else:
                self.logger.warning(f"订单不存在或已处理: {order_id}")
                return False

        except Exception as e:
            self.logger.error(f"取消订单失败: {order_id}: {e}")
            return False

    async def get_order_status(self, order_id: str) -> Optional[Dict]:
        """获取订单状态"""
        try:
            from app.core.database import db_service

            sql = f"""
            SELECT 
                order_id, symbol, side, order_type, quantity, price,
                status, created_at, updated_at, filled_at
            FROM orders
            WHERE order_id = '{order_id}'
            """

            result = await db_service.fetch_one(sql)

            if result:
                return {
                    "order_id": result["order_id"],
                    "symbol": result["symbol"],
                    "side": result["side"],
                    "type": result["order_type"],
                    "quantity": result["quantity"],
                    "price": result["price"],
                    "status": result["status"],
                    "created_at": result["created_at"].isoformat(),
                    "updated_at": result["updated_at"].isoformat(),
                    "filled_at": result["filled_at"].isoformat() if result["filled_at"] else None,
                }

            return None

        except Exception as e:
            self.logger.error(f"获取订单状态失败: {order_id}: {e}")
            return None

    async def get_positions(self, user_id: str) -> List[Dict]:
        """获取持仓列表"""
        try:
            from app.core.database import db_service

            sql = f"""
            SELECT 
                position_id, symbol, quantity, avg_cost,
                current_price, market_value, unrealized_pnl, realized_pnl,
                created_at, updated_at
            FROM positions
            WHERE user_id = '{user_id}'
            ORDER BY market_value DESC
            """

            results = await db_service.fetch_many(sql)

            if not results:
                return []

            positions = []
            for result in results:
                positions.append(
                    {
                        "position_id": result["position_id"],
                        "symbol": result["symbol"],
                        "quantity": result["quantity"],
                        "avg_cost": result["avg_cost"],
                        "current_price": result["current_price"],
                        "market_value": result["market_value"],
                        "unrealized_pnl": result["unrealized_pnl"],
                        "realized_pnl": result["realized_pnl"],
                        "created_at": result["created_at"].isoformat(),
                        "updated_at": result["updated_at"].isoformat(),
                    }
                )

            self.logger.info(f"获取{len(positions)}个持仓")
            return positions

        except Exception as e:
            self.logger.error(f"获取持仓列表失败: {e}")
            return []

    async def get_trades(self, user_id: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """获取交易历史"""
        try:
            from app.core.database import db_service

            sql = f"""
            SELECT 
                trade_id, order_id, symbol, side, quantity,
                price, amount, commission, pnl, pnl_percent,
                created_at
            FROM trades
            WHERE user_id = '{user_id}'
            ORDER BY created_at DESC
            LIMIT {limit} OFFSET {offset}
            """

            results = await db_service.fetch_many(sql)

            if not results:
                return []

            trades = []
            for result in results:
                trades.append(
                    {
                        "trade_id": result["trade_id"],
                        "order_id": result["order_id"],
                        "symbol": result["symbol"],
                        "side": result["side"],
                        "quantity": result["quantity"],
                        "price": result["price"],
                        "amount": result["amount"],
                        "commission": result["commission"],
                        "pnl": result["pnl"],
                        "pnl_percent": result["pnl_percent"],
                        "created_at": result["created_at"].isoformat(),
                    }
                )

            self.logger.info(f"获取{len(trades)}条交易记录")
            return trades

        except Exception as e:
            self.logger.error(f"获取交易历史失败: {e}")
            return []

    async def get_trading_summary(self, user_id: str) -> Dict:
        """获取交易汇总"""
        try:
            positions = await self.get_positions(user_id)
            trades = await self.get_trades(user_id)

            total_market_value = sum(pos["market_value"] for pos in positions)
            total_unrealized_pnl = sum(pos["unrealized_pnl"] for pos in positions)
            total_realized_pnl = sum(pos["realized_pnl"] for pos in positions)
            total_pnl = total_unrealized_pnl + total_realized_pnl

            summary = {
                "user_id": user_id,
                "total_positions": len(positions),
                "total_trades": len(trades),
                "total_market_value": total_market_value,
                "total_unrealized_pnl": total_unrealized_pnl,
                "total_realized_pnl": total_realized_pnl,
                "total_pnl": total_pnl,
                "generated_at": datetime.now().isoformat(),
            }

            self.logger.info(f"交易汇总: {user_id}")
            return summary

        except Exception as e:
            self.logger.error(f"获取交易汇总失败: {user_id}: {e}")
            return {}
