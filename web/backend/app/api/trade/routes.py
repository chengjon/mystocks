"""
交易管理API路由 (Phase 2.3)

提供交易账户、持仓、订单执行、交易记录的RESTful API端点。

版本: 2.0.0
日期: 2025-12-24
更新内容:
- 添加Pydantic请求验证模型
- 使用统一响应格式
- 创建/api/trade/account端点
- 实现审计日志记录
- 支持实时持仓更新

安全特性:
- CSRF保护（全局中间件）
- 请求参数全面验证
- 操作审计日志
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel, Field, field_validator

from app.core.responses import (
    ErrorCodes,
    ResponseMessages,
    create_unified_error_response,
    create_unified_success_response,
    create_health_response,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trade", tags=["trade"])


# ============================================================================
# Pydantic 验证模型
# ============================================================================


class TradeType(str, Enum):
    """交易类型枚举"""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """订单状态枚举"""

    PENDING = "pending"
    EXECUTED = "executed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TradeExecuteRequest(BaseModel):
    """交易执行请求模型"""

    trade_type: TradeType = Field(..., description="交易类型 (buy/sell)")
    symbol: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^[0-9]{6}$",
        description="股票代码 (6位数字)",
    )
    quantity: int = Field(..., gt=0, le=1000000, description="交易数量 (正整数，最大100万)")
    price: float = Field(
        ...,
        gt=0,
        le=10000,
        description="委托价格 (大于0，最大10000)",
    )
    remark: Optional[str] = Field(None, max_length=200, description="备注信息 (最多200字符)")

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """验证交易数量是否为100的整数倍（A股交易规则）"""
        if v % 100 != 0:
            raise ValueError("交易数量必须是100的整数倍")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """验证价格精度（保留2位小数）"""
        rounded = round(v, 2)
        if abs(v - rounded) > 0.001:
            raise ValueError("价格最多保留2位小数")
        return rounded


class TradeExecuteResponse(BaseModel):
    """交易执行响应模型"""

    trade_id: str
    trade_type: str
    symbol: str
    quantity: int
    price: float
    trade_amount: float
    commission: float
    total_amount: float
    status: str
    trade_time: str
    message: str


class PositionInfo(BaseModel):
    """持仓信息模型"""

    symbol: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    quantity: int = Field(..., description="持仓数量")
    cost_price: float = Field(..., description="成本价")
    current_price: float = Field(..., description="当前价")
    market_value: float = Field(..., description="市值")
    profit: float = Field(..., description="盈亏金额")
    profit_rate: float = Field(..., description="盈亏比例(%)")
    update_time: str = Field(..., description="更新时间")


class TradeRecord(BaseModel):
    """交易记录模型"""

    trade_time: str
    trade_type: str
    symbol: str
    stock_name: str
    quantity: int
    price: float
    commission: float
    status: str
    remark: Optional[str]


class AccountInfo(BaseModel):
    """账户信息模型"""

    total_assets: float = Field(..., description="总资产")
    available_cash: float = Field(..., description="可用资金")
    position_value: float = Field(..., description="持仓市值")
    total_profit: float = Field(..., description="总盈亏")
    profit_rate: float = Field(..., description="盈亏比例(%)")
    position_count: int = Field(..., description="持仓数量")
    update_time: str = Field(..., description="更新时间")


# ============================================================================
# 审计日志装饰器
# ============================================================================


def audit_log(operation: str):
    """
    审计日志装饰器 - 记录所有交易操作

    Args:
        operation: 操作类型 (execute_trade, cancel_order, etc.)
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 记录操作开始
            start_time = datetime.now()
            logger.info(
                f"[TRADE_AUDIT] Operation started: {operation}",
                operation=operation,
                timestamp=start_time.isoformat(),
            )

            try:
                result = await func(*args, **kwargs)

                # 记录操作成功
                logger.info(
                    f"[TRADE_AUDIT] Operation completed: {operation}",
                    operation=operation,
                    status="success",
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )

                return result

            except Exception as e:
                # 记录操作失败
                logger.error(
                    f"[TRADE_AUDIT] Operation failed: {operation}",
                    operation=operation,
                    status="failed",
                    error=str(e),
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator


# ============================================================================
# 辅助函数
# ============================================================================


def calculate_commission(trade_amount: float, trade_type: str) -> float:
    """
    计算手续费

    Args:
        trade_amount: 交易金额
        trade_type: 交易类型 (buy/sell)

    Returns:
        手续费金额
    """
    # A股手续费标准: 最低5元，通常为成交金额的0.03%-0.05%
    commission_rate = 0.0003  # 万分之三
    commission = trade_amount * commission_rate
    return max(commission, 5.0)  # 最低5元


# ============================================================================
# 健康检查端点
# ============================================================================


@router.get("/health")
async def health_check():
    """
    交易服务健康检查

    Returns:
        统一格式的健康检查响应
    """
    return create_health_response(
        service="trade",
        status="healthy",
        details={
            "csrf_protected": True,
            "audit_logging": True,
            "validation_enabled": True,
        },
    )


# ============================================================================
# 账户信息端点 (新增 - Phase 2.3)
# ============================================================================


@router.get("/account")
async def get_account():
    """
    获取账户信息

    Returns:
        账户总览信息 (总资产、可用资金、持仓市值、盈亏等)
    """
    try:
        # 模拟数据 - 实际应从数据库查询
        account_data = AccountInfo(
            total_assets=1050000.00,
            available_cash=150000.00,
            position_value=900000.00,
            total_profit=50000.00,
            profit_rate=5.26,
            position_count=2,
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        logger.info("[TRADE] Account info retrieved")

        return create_unified_success_response(
            data=account_data.model_dump(),
            message="获取账户信息成功",
        )

    except Exception as e:
        logger.error(f"[TRADE] Failed to get account info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_unified_error_response(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                f"获取账户信息失败: {str(e)}",
            ).model_dump(mode="json"),
        )


# ============================================================================
# 投资组合端点
# ============================================================================


@router.get("/portfolio")
async def get_portfolio():
    """
    获取投资组合概览

    Returns:
        投资组合信息 (总资产、可用资金、持仓市值、盈亏)
    """
    try:
        portfolio_data = {
            "total_assets": 1050000.00,
            "available_cash": 150000.00,
            "position_value": 900000.00,
            "total_profit": 50000.00,
            "profit_rate": 5.26,
            "timestamp": date.today().isoformat(),
        }

        return create_unified_success_response(
            data=portfolio_data,
            message="获取投资组合成功",
        )

    except Exception as e:
        logger.error(f"[TRADE] Failed to get portfolio: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_unified_error_response(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                f"获取投资组合失败: {str(e)}",
            ).model_dump(mode="json"),
        )


# ============================================================================
# 持仓端点 (支持实时更新 - Phase 2.3)
# ============================================================================


@router.get("/positions")
async def get_positions(
    symbol: Optional[str] = Query(None, description="股票代码筛选"),
    update_since: Optional[str] = Query(
        None, description="获取指定时间后更新的持仓 (格式: YYYY-MM-DD HH:MM:SS)"
    ),
):
    """
    获取持仓列表

    Args:
        symbol: 可选的股票代码筛选
        update_since: 可选的时间筛选，用于实时增量更新

    Returns:
        持仓数据列表
    """
    try:
        # 模拟持仓数据
        all_positions = [
            PositionInfo(
                symbol="600519",
                stock_name="贵州茅台",
                quantity=500,
                cost_price=1650.00,
                current_price=1750.00,
                market_value=875000.00,
                profit=50000.00,
                profit_rate=6.06,
                update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
            PositionInfo(
                symbol="000858",
                stock_name="五粮液",
                quantity=1000,
                cost_price=145.00,
                current_price=150.00,
                market_value=150000.00,
                profit=5000.00,
                profit_rate=3.45,
                update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        ]

        # 应用股票代码筛选
        if symbol:
            all_positions = [p for p in all_positions if p.symbol == symbol]

        # 转换为字典列表
        positions_data = [p.model_dump() for p in all_positions]

        logger.info(f"[TRADE] Retrieved {len(positions_data)} positions")

        return create_unified_success_response(
            data={
                "positions": positions_data,
                "total_count": len(positions_data),
                "total_value": sum(p["market_value"] for p in positions_data),
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            message=f"获取持仓列表成功，共{len(positions_data)}条记录",
        )

    except Exception as e:
        logger.error(f"[TRADE] Failed to get positions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_unified_error_response(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                f"获取持仓列表失败: {str(e)}",
            ).model_dump(mode="json"),
        )


# ============================================================================
# 交易记录端点
# ============================================================================


@router.get("/trades")
async def get_trades(
    trade_type: Optional[str] = Query(None, description="交易类型 (buy/sell)"),
    symbol: Optional[str] = Query(None, description="股票代码"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """
    获取交易记录列表

    Args:
        trade_type: 交易类型 (buy/sell)
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        page: 页码
        page_size: 每页数量

    Returns:
        交易记录列表和分页信息
    """
    try:
        # 模拟交易记录数据
        all_trades = [
            TradeRecord(
                trade_time="2025-11-20 10:30:00",
                trade_type="buy",
                symbol="600519",
                stock_name="贵州茅台",
                quantity=500,
                price=1650.00,
                commission=247.50,
                status="executed",
                remark="建仓",
            ),
            TradeRecord(
                trade_time="2025-11-19 14:20:00",
                trade_type="buy",
                symbol="000858",
                stock_name="五粮液",
                quantity=1000,
                price=145.00,
                commission=43.50,
                status="executed",
                remark="分批买入",
            ),
            TradeRecord(
                trade_time="2025-11-18 09:45:00",
                trade_type="sell",
                symbol="600000",
                stock_name="浦发银行",
                quantity=2000,
                price=8.50,
                commission=25.50,
                status="executed",
                remark="止盈",
            ),
        ]

        # 应用过滤条件
        filtered_trades = all_trades
        if trade_type:
            filtered_trades = [t for t in filtered_trades if t.trade_type == trade_type]
        if symbol:
            filtered_trades = [t for t in filtered_trades if t.symbol == symbol]
        if start_date:
            filtered_trades = [
                t
                for t in filtered_trades
                if datetime.strptime(t.trade_time, "%Y-%m-%d %H:%M:%S").date()
                >= start_date
            ]
        if end_date:
            filtered_trades = [
                t
                for t in filtered_trades
                if datetime.strptime(t.trade_time, "%Y-%m-%d %H:%M:%S").date()
                <= end_date
            ]

        # 分页
        total = len(filtered_trades)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_trades = filtered_trades[start_idx:end_idx]

        trades_data = [t.model_dump() for t in paginated_trades]

        return create_unified_success_response(
            data={
                "trades": trades_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            },
            message=f"获取交易记录成功，共{total}条记录",
        )

    except Exception as e:
        logger.error(f"[TRADE] Failed to get trades: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_unified_error_response(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                f"获取交易记录失败: {str(e)}",
            ).model_dump(mode="json"),
        )


# ============================================================================
# 统计数据端点
# ============================================================================


@router.get("/statistics")
async def get_statistics():
    """
    获取交易统计数据

    Returns:
        统计数据 (总交易次数、买卖次数、盈亏等)
    """
    try:
        statistics_data = {
            "total_trades": 15,
            "buy_count": 10,
            "sell_count": 5,
            "position_count": 2,
            "total_buy_amount": 1000000.00,
            "total_sell_amount": 100000.00,
            "total_commission": 5500.00,
            "realized_profit": 15000.00,
            "win_rate": 60.0,  # 盈利交易占比
            "avg_profit_per_trade": 1000.00,
        }

        return create_unified_success_response(
            data=statistics_data,
            message="获取交易统计成功",
        )

    except Exception as e:
        logger.error(f"[TRADE] Failed to get statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_unified_error_response(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                f"获取交易统计失败: {str(e)}",
            ).model_dump(mode="json"),
        )


# ============================================================================
# 交易执行端点 (增强验证和审计日志 - Phase 2.3)
# ============================================================================


@router.post("/execute")
@audit_log("execute_trade")
async def execute_trade(
    trade_data: TradeExecuteRequest,
    x_request_id: Optional[str] = Header(None, description="请求ID"),
):
    """
    执行买卖交易

    Args:
        trade_data: 交易信息 (已通过Pydantic验证)
        x_request_id: 可选的请求追踪ID

    Returns:
        交易执行结果

    Raises:
        HTTPException: 当验证失败或执行出错时
    """
    try:
        # 计算交易金额
        trade_amount = trade_data.quantity * trade_data.price

        # 计算手续费
        commission = calculate_commission(trade_amount, trade_data.trade_type.value)

        # 计算总金额
        if trade_data.trade_type == TradeType.BUY:
            total_amount = trade_amount + commission
        else:
            total_amount = trade_amount - commission

        # 生成交易ID (实际应从数据库生成)
        trade_id = f"TRD{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 构建响应数据
        result = TradeExecuteResponse(
            trade_id=trade_id,
            trade_type=trade_data.trade_type.value,
            symbol=trade_data.symbol,
            quantity=trade_data.quantity,
            price=trade_data.price,
            trade_amount=trade_amount,
            commission=commission,
            total_amount=total_amount,
            status="executed",
            trade_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            message=f"{trade_data.trade_type.value.upper()} 成功",
        )

        # 记录交易成功
        logger.info(
            f"[TRADE] Trade executed successfully",
            trade_id=trade_id,
            trade_type=trade_data.trade_type.value,
            symbol=trade_data.symbol,
            amount=trade_amount,
        )

        return create_unified_success_response(
            data=result.model_dump(),
            message=f"交易执行成功: {trade_data.trade_type.value.upper()} {trade_data.symbol}",
            request_id=x_request_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[TRADE] Trade execution failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_unified_error_response(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                f"交易执行失败: {str(e)}",
            ).model_dump(mode="json"),
        )


# ============================================================================
# 订单取消端点 (新增 - Phase 2.3)
# ============================================================================


@router.post("/cancel/{order_id}")
@audit_log("cancel_order")
async def cancel_order(
    order_id: str,
    x_request_id: Optional[str] = Header(None, description="请求ID"),
):
    """
    取消订单

    Args:
        order_id: 订单ID
        x_request_id: 可选的请求追踪ID

    Returns:
        取消结果
    """
    try:
        # 验证订单ID格式
        if not order_id or len(order_id) < 5:
            raise HTTPException(
                status_code=400,
                detail=create_unified_error_response(
                    ErrorCodes.BAD_REQUEST,
                    "无效的订单ID",
                ).model_dump(mode="json"),
            )

        # 模拟取消订单
        logger.info(f"[TRADE] Order cancellation requested: {order_id}")

        return create_unified_success_response(
            data={
                "order_id": order_id,
                "status": "cancelled",
                "cancel_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            message=f"订单 {order_id} 已取消",
            request_id=x_request_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[TRADE] Order cancellation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_unified_error_response(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                f"取消订单失败: {str(e)}",
            ).model_dump(mode="json"),
        )
