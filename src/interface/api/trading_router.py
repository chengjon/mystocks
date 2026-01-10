"""
Trading Router
DDD 架构下的交易相关 API
"""
from fastapi import APIRouter, Depends, HTTPException
from src.application.trading.order_mgmt_service import OrderManagementService
from src.application.dto.trading_dto import CreateOrderRequest, OrderResponse

router = APIRouter(prefix="/api/v1/ddd/trading", tags=["DDD Trading"])

@router.post("/orders", response_model=OrderResponse)
async def place_order(request: CreateOrderRequest):
    """下单"""
    # 演示逻辑
    raise HTTPException(status_code=501, detail="Service wire-up in progress")

@router.get("/portfolios/{id}")
async def get_portfolio(id: str):
    """获取投资组合详情"""
    raise HTTPException(status_code=501, detail="Service wire-up in progress")
