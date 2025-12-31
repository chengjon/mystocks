"""
交易管理API路由

使用统一的Pydantic模型和APIResponse格式
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.responses import (
    APIResponse,
    create_success_response,
    create_error_response,
    ErrorCodes,
)
from app.schemas.trade_schemas import (
    AccountInfo,
    Position,
    PositionsResponse,
    TradeHistoryResponse,
    TradeHistoryItem,
)

router = APIRouter(prefix="/trade", tags=["交易执行"])


# ==================== Health Check ====================


class HealthCheckResponse(BaseModel):
    """健康检查响应"""

    status: str
    service: str


@router.get("/health", response_model=APIResponse)
async def health_check():
    """健康检查"""
    return create_success_response(data={"status": "ok", "service": "trade"}, message="服务正常")


# ==================== Portfolio (Account Info) ====================


@router.get("/portfolio", response_model=APIResponse)
async def get_portfolio():
    """
    获取投资组合概览

    返回账户总资产、可用资金、持仓市值、盈亏等信息
    """
    try:
        # TODO: 实际应从数据库查询
        # 返回模拟数据用于演示
        from decimal import Decimal
        from datetime import datetime

        account_data = AccountInfo(
            account_id="ACC_DEMO_001",
            account_type="stock",
            total_assets=Decimal("1050000.00"),
            cash=Decimal("150000.00"),
            market_value=Decimal("900000.00"),
            frozen_cash=None,
            total_profit_loss=Decimal("50000.00"),
            profit_loss_percent=5.0,
            risk_level="low",
            last_update=datetime.now(),
        )

        return create_success_response(data=account_data.model_dump(), message="获取账户信息成功")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR, message=f"获取账户信息失败: {str(e)}"
            ).model_dump(),
        )


# ==================== Positions ====================


@router.get("/positions", response_model=APIResponse)
async def get_positions():
    """
    获取持仓列表

    返回用户当前所有持仓的详细信息，包括股票代码、数量、成本价、当前价、盈亏等
    """
    try:
        from decimal import Decimal
        from datetime import datetime

        # TODO: 实际应从数据库查询
        # 返回模拟数据用于演示
        positions = [
            Position(
                symbol="600519.SH",
                symbol_name="贵州茅台",
                quantity=500,
                available_quantity=500,
                cost_price=Decimal("1650.00"),
                current_price=Decimal("1750.00"),
                market_value=Decimal("875000.00"),
                profit_loss=Decimal("50000.00"),
                profit_loss_percent=6.06,
                last_update=datetime.now(),
            ),
            Position(
                symbol="000858.SZ",
                symbol_name="五粮液",
                quantity=1000,
                available_quantity=1000,
                cost_price=Decimal("145.00"),
                current_price=Decimal("150.00"),
                market_value=Decimal("150000.00"),
                profit_loss=Decimal("5000.00"),
                profit_loss_percent=3.45,
                last_update=datetime.now(),
            ),
        ]

        # 计算汇总数据
        total_count = len(positions)
        total_market_value = sum(p.market_value for p in positions)
        total_profit_loss = sum(p.profit_loss for p in positions)
        total_profit_loss_percent = (
            (total_profit_loss / (total_market_value - total_profit_loss)) * 100
            if total_market_value != total_profit_loss
            else 0.0
        )

        positions_response = PositionsResponse(
            positions=[p.model_dump() for p in positions],
            total_count=total_count,
            total_market_value=total_market_value,
            total_profit_loss=total_profit_loss,
            total_profit_loss_percent=round(total_profit_loss_percent, 2),
        )

        return create_success_response(
            data=positions_response.model_dump(), message=f"获取持仓列表成功，共{total_count}只股票"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR, message=f"获取持仓列表失败: {str(e)}"
            ).model_dump(),
        )


# ==================== Trade History ====================


@router.get("/trades", response_model=APIResponse)
async def get_trades(
    symbol: Optional[str] = Query(None, description="股票代码 (可选)"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """
    获取交易记录列表

    支持按股票代码、日期范围过滤，返回分页的交易历史记录
    """
    try:
        from decimal import Decimal
        from datetime import datetime

        # TODO: 实际应从数据库按过滤条件查询
        # 返回模拟数据用于演示
        all_trades = [
            TradeHistoryItem(
                trade_id="TRD001",
                order_id="ORDER001",
                symbol="600519.SH",
                direction="buy",
                price=Decimal("1650.00"),
                quantity=500,
                amount=Decimal("825000.00"),
                commission=Decimal("82.50"),
                trade_time=datetime.now(),
                trade_type="normal",
            ),
            TradeHistoryItem(
                trade_id="TRD002",
                order_id="ORDER002",
                symbol="000858.SZ",
                direction="buy",
                price=Decimal("145.00"),
                quantity=1000,
                amount=Decimal("145000.00"),
                commission=Decimal("145.00"),
                trade_time=datetime.now(),
                trade_type="normal",
            ),
        ]

        # 应用过滤条件 (简化实现)
        filtered_trades = all_trades
        if symbol:
            filtered_trades = [t for t in filtered_trades if symbol in t.symbol]
        if start_date or end_date:
            # TODO: 添加日期过滤逻辑
            pass

        # 分页
        total = len(filtered_trades)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_trades = filtered_trades[start_idx:end_idx]

        # 计算汇总
        total_amount = sum(t.amount for t in filtered_trades)
        total_commission = sum(t.commission for t in filtered_trades)

        trade_history_response = TradeHistoryResponse(
            trades=[t.model_dump() for t in paginated_trades],
            total_count=total,
            total_amount=total_amount,
            total_commission=total_commission,
            page=page,
            page_size=page_size,
        )

        return create_success_response(
            data=trade_history_response.model_dump(), message=f"获取交易记录成功，共{total}条记录"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR, message=f"获取交易记录失败: {str(e)}"
            ).model_dump(),
        )


# ==================== Statistics ====================


class TradeStatistics(BaseModel):
    """交易统计数据"""

    total_trades: int
    buy_count: int
    sell_count: int
    position_count: int
    total_buy_amount: float
    total_sell_amount: float
    total_commission: float
    realized_profit: float


@router.get("/statistics", response_model=APIResponse)
async def get_statistics():
    """
    获取交易统计数据

    返回总交易次数、买卖次数、持仓数量、成交金额、手续费、已实现盈亏等统计信息
    """
    try:
        # TODO: 实际应从数据库计算统计数据
        # 返回模拟数据用于演示
        statistics = TradeStatistics(
            total_trades=15,
            buy_count=10,
            sell_count=5,
            position_count=2,
            total_buy_amount=1000000.00,
            total_sell_amount=100000.00,
            total_commission=5500.00,
            realized_profit=15000.00,
        )

        return create_success_response(data=statistics.model_dump(), message="获取交易统计成功")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR, message=f"获取交易统计失败: {str(e)}"
            ).model_dump(),
        )


# ==================== Execute Trade ====================


@router.post("/execute", response_model=APIResponse)
async def execute_trade(order: dict):
    """
    执行买卖交易

    接收交易指令，验证参数，模拟执行交易并返回结果

    Args:
        order: 交易信息字典，包含 type, symbol, quantity, price 等字段

    Returns:
        APIResponse: 包含交易执行结果的响应
    """
    try:
        from datetime import datetime
        import uuid

        # 验证必填字段
        required_fields = ["direction", "symbol", "quantity"]
        if not all(field in order for field in required_fields):
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.VALIDATION_ERROR, message="缺少必填字段: direction, symbol, quantity"
                ).model_dump(),
            )

        direction = order.get("direction")
        if direction not in ["buy", "sell"]:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.INVALID_VALUE, message="交易方向必须是 buy 或 sell"
                ).model_dump(),
            )

        quantity = order.get("quantity")
        if quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.OUT_OF_RANGE, message="委托数量必须大于0"
                ).model_dump(),
            )

        # A股交易数量必须是100的整数倍
        if quantity % 100 != 0:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.INVALID_VALUE, message="委托数量必须是100的整数倍"
                ).model_dump(),
            )

        # 模拟交易执行
        price = order.get("price", 0.0)
        trade_amount = quantity * price
        commission = trade_amount * 0.0005  # 手续费 0.05%

        result = {
            "order_id": f"ORDER_{uuid.uuid4().hex[:12].upper()}",
            "direction": direction,
            "symbol": order.get("symbol"),
            "quantity": quantity,
            "price": price,
            "trade_amount": trade_amount,
            "commission": round(commission, 2),
            "total_amount": round(trade_amount + commission if direction == "buy" else trade_amount - commission, 2),
            "status": "completed",
            "trade_time": datetime.now().isoformat(),
            "message": f"{'买入' if direction == 'buy' else '卖出'}成功",
        }

        return create_success_response(data=result, message=f"{'买入' if direction == 'buy' else '卖出'}委托成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR, message=f"交易执行失败: {str(e)}"
            ).model_dump(),
        )
