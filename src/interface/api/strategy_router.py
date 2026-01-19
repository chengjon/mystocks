"""
Strategy Router
DDD 架构下的策略相关 API
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.application.strategy.backtest_service import BacktestApplicationService
from src.application.dto.strategy_dto import BacktestRequest, BacktestResultDTO

router = APIRouter(prefix="/api/v1/ddd/strategies", tags=["DDD Strategy"])


# 这里应该有依赖注入逻辑来获取 Service
# 简化演示：
def get_backtest_service():
    # 实际应从容器中获取
    return None


@router.post("/backtest/run", response_model=BacktestResultDTO)
async def run_backtest(
    request: BacktestRequest,
    # service: BacktestApplicationService = Depends(get_backtest_service)
):
    """执行回测"""
    # 演示逻辑：由于依赖注入尚未完全配置，这里抛出未实现或返回 mock
    # result = service.run_backtest(request)
    # return result
    raise HTTPException(status_code=501, detail="Service wire-up in progress")
