"""Portfolio-related routes for monitoring analysis API."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Path, Query
from app.core.exceptions import BusinessException
from pydantic import BaseModel, Field

from app.core.exception_handlers import handle_exceptions
from app.core.responses import UnifiedResponse
from app.openapi_config import COMMON_RESPONSES

logger = logging.getLogger(__name__)


def _success_response_spec(description: str, message: str, data: Any) -> Dict[int, Dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "code": 200,
                        "message": message,
                        "data": data,
                        "timestamp": "2026-04-04T01:30:00Z",
                        "request_id": "req_monitoring_portfolio_example",
                    }
                }
            },
        }
    }


MONITORING_PORTFOLIO_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

PORTFOLIO_SUMMARY_SUCCESS_RESPONSE = _success_response_spec(
    "投资组合分析摘要",
    "获取组合摘要成功",
    {
        "watchlist_id": 8,
        "watchlist_name": "核心持仓",
        "analysis_date": "2026-04-04",
        "total_score": {"average": 79.2, "min": 68.4, "max": 87.3},
        "radar_averages": {
            "trend": 80.2,
            "technical": 78.4,
            "momentum": 81.7,
            "volatility": 73.1,
            "risk": 82.8,
        },
        "risk_score": 76.4,
        "position_count": 3,
        "sector_allocation": {"白酒": 42.0, "银行": 31.0, "科技": 27.0},
        "alert_summary": {"critical": 1, "warning": 2, "info": 3},
        "rebalance_count": 2,
    },
)

PORTFOLIO_ALERTS_SUCCESS_RESPONSE = _success_response_spec(
    "投资组合预警列表",
    "获取预警列表成功 (共2条)",
    [
        {
            "level": "warning",
            "type": "drawdown",
            "stock_code": "600519",
            "message": "近 5 日回撤接近阈值，建议关注仓位风险。",
            "details": {"current_drawdown": 0.078, "threshold": 0.08},
        }
    ],
)

PORTFOLIO_REBALANCE_SUCCESS_RESPONSE = _success_response_spec(
    "投资组合再平衡建议列表",
    "获取再平衡建议成功 (共1条)",
    [
        {
            "reason": "行业集中度偏高",
            "priority": "high",
            "stock_code": "600519",
            "action": "reduce",
            "current_weight": 0.42,
            "target_weight": 0.3,
            "message": "建议降低白酒板块集中度，释放 12% 仓位到低相关资产。",
            "estimated_cost": 1560.0,
        }
    ],
)


router = APIRouter(responses=MONITORING_PORTFOLIO_ROUTE_RESPONSES)


class PortfolioSummaryResponse(BaseModel):
    """组合摘要响应"""

    watchlist_id: int = Field(..., description="清单ID")
    watchlist_name: str = Field(..., description="清单名称")
    analysis_date: str = Field(..., description="分析时间")
    total_score: Dict[str, float] = Field(..., description="总分统计")
    radar_averages: Dict[str, float] = Field(..., description="五维平均分")
    risk_score: float = Field(..., description="风险评分")
    position_count: int = Field(..., description="持仓数量")
    sector_allocation: Dict[str, float] = Field(..., description="行业配置")
    alert_summary: Dict[str, int] = Field(..., description="预警摘要")
    rebalance_count: int = Field(..., description="再平衡建议数量")


class AlertResponse(BaseModel):
    """预警响应"""

    level: str = Field(..., description="级别: critical/warning/info")
    type: str = Field(..., description="类型")
    stock_code: str = Field(..., description="股票代码")
    message: str = Field(..., description="预警消息")
    details: Dict[str, Any] = Field(..., description="详细信息")


class RebalanceSuggestionResponse(BaseModel):
    """再平衡建议响应"""

    reason: str = Field(..., description="原因")
    priority: str = Field(..., description="优先级")
    stock_code: str = Field(..., description="股票代码")
    action: str = Field(..., description="建议操作")
    current_weight: float = Field(..., description="当前权重")
    target_weight: float = Field(..., description="目标权重")
    message: str = Field(..., description="建议说明")
    estimated_cost: float = Field(..., description="预估成本")


@router.get(
    "/portfolio/{watchlist_id}/summary",
    response_model=UnifiedResponse[PortfolioSummaryResponse],
    summary="获取组合分析摘要",
    description="返回指定自选清单的组合总分、雷达均值、行业分布和预警汇总，供组合总览页展示。",
    responses=PORTFOLIO_SUMMARY_SUCCESS_RESPONSE,
)
@handle_exceptions
async def get_portfolio_summary(
    watchlist_id: int = Path(..., description="清单ID"),
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[PortfolioSummaryResponse]:
    """获取组合分析摘要"""
    try:
        from src.monitoring.domain.calculator_factory import get_calculator_factory
        from src.monitoring.domain.portfolio_optimizer import get_portfolio_optimizer
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        postgres_async = get_postgres_async()
        factory = get_calculator_factory()
        optimizer = get_portfolio_optimizer()

        watchlists = await postgres_async.get_user_watchlists(user_id)
        watchlist = next((watchlist for watchlist in watchlists if watchlist["id"] == watchlist_id), None)

        if not watchlist:
            raise BusinessException(status_code=404, detail="清单不存在")

        stocks = await postgres_async.get_watchlist_stocks(watchlist_id)
        if not stocks:
            raise BusinessException(status_code=400, detail="清单为空")

        inputs = [
            {"stock_code": stock["stock_code"], "close": stock.get("entry_price", 100), "market_regime": "choppy"}
            for stock in stocks
        ]
        health_result = factory.calculate_health_scores(inputs=inputs, engine_type="AUTO", include_risk_metrics=False)

        position_data = [
            {
                "stock_code": stock["stock_code"],
                "weight": float(stock.get("weight", 0)),
                "entry_price": float(stock.get("entry_price", 0)),
                "current_price": float(stock.get("entry_price", 0)),
                "target_weight": float(stock.get("weight", 0)),
                "stop_loss_price": float(stock.get("stop_loss_price", 0)),
                "target_price": float(stock.get("target_price", 0)),
            }
            for stock in stocks
        ]

        analysis = optimizer.analyze_portfolio(
            watchlist_id=watchlist_id,
            watchlist_name=watchlist["name"],
            positions=position_data,
            health_scores=health_result["results"],
        )
        summary = optimizer.get_portfolio_summary(analysis)

        return UnifiedResponse(data=PortfolioSummaryResponse(**summary), message="获取组合摘要成功")

    except BusinessException:
        raise
    except Exception as error:
        logger.error("获取组合摘要失败: %(e)s")
        raise BusinessException(status_code=500, detail=f"获取失败: {str(error)}")


@router.get(
    "/portfolio/{watchlist_id}/alerts",
    response_model=UnifiedResponse[List[AlertResponse]],
    summary="获取组合预警列表",
    description="列出指定自选清单当前触发的组合预警，并支持按预警级别过滤结果。",
    responses=PORTFOLIO_ALERTS_SUCCESS_RESPONSE,
)
@handle_exceptions
async def get_portfolio_alerts(
    watchlist_id: int = Path(..., description="清单ID"),
    user_id: int = Query(1, description="用户ID"),
    level: Optional[str] = Query(None, description="预警级别过滤: critical/warning/info"),
) -> UnifiedResponse[List[AlertResponse]]:
    """获取组合预警列表"""
    try:
        from src.monitoring.domain.calculator_factory import get_calculator_factory
        from src.monitoring.domain.portfolio_optimizer import get_portfolio_optimizer
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        postgres_async = get_postgres_async()
        factory = get_calculator_factory()
        optimizer = get_portfolio_optimizer()

        watchlists = await postgres_async.get_user_watchlists(user_id)
        watchlist = next((watchlist for watchlist in watchlists if watchlist["id"] == watchlist_id), None)

        if not watchlist:
            raise BusinessException(status_code=404, detail="清单不存在")

        stocks = await postgres_async.get_watchlist_stocks(watchlist_id)
        inputs = [
            {"stock_code": stock["stock_code"], "close": stock.get("entry_price", 100), "market_regime": "choppy"}
            for stock in stocks
        ]
        health_result = factory.calculate_health_scores(inputs=inputs, engine_type="AUTO", include_risk_metrics=False)

        position_data = [
            {
                "stock_code": stock["stock_code"],
                "weight": float(stock.get("weight", 0)),
                "entry_price": float(stock.get("entry_price", 0)),
                "current_price": float(stock.get("entry_price", 0)),
                "target_weight": float(stock.get("weight", 0)),
                "stop_loss_price": float(stock.get("stop_loss_price", 0)),
                "target_price": float(stock.get("target_price", 0)),
            }
            for stock in stocks
        ]

        analysis = optimizer.analyze_portfolio(
            watchlist_id=watchlist_id,
            watchlist_name=watchlist["name"],
            positions=position_data,
            health_scores=health_result["results"],
        )

        alerts = analysis.alerts
        if level:
            alerts = [alert for alert in alerts if alert["level"] == level]

        return UnifiedResponse(
            data=[AlertResponse(**alert) for alert in alerts],
            message=f"获取预警列表成功 (共{len(alerts)}条)",
        )

    except BusinessException:
        raise
    except Exception as error:
        logger.error("获取预警列表失败: %(e)s")
        raise BusinessException(status_code=500, detail=f"获取失败: {str(error)}")


@router.get(
    "/portfolio/{watchlist_id}/rebalance",
    response_model=UnifiedResponse[List[RebalanceSuggestionResponse]],
    summary="获取再平衡建议",
    description="根据组合健康度和仓位结构生成再平衡建议，返回优先级、目标权重和预估成本。",
    responses=PORTFOLIO_REBALANCE_SUCCESS_RESPONSE,
)
@handle_exceptions
async def get_rebalance_suggestions(
    watchlist_id: int = Path(..., description="清单ID"),
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[List[RebalanceSuggestionResponse]]:
    """获取再平衡建议"""
    try:
        from src.monitoring.domain.calculator_factory import get_calculator_factory
        from src.monitoring.domain.portfolio_optimizer import get_portfolio_optimizer
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        postgres_async = get_postgres_async()
        factory = get_calculator_factory()
        optimizer = get_portfolio_optimizer()

        watchlists = await postgres_async.get_user_watchlists(user_id)
        watchlist = next((watchlist for watchlist in watchlists if watchlist["id"] == watchlist_id), None)

        if not watchlist:
            raise BusinessException(status_code=404, detail="清单不存在")

        stocks = await postgres_async.get_watchlist_stocks(watchlist_id)
        inputs = [
            {"stock_code": stock["stock_code"], "close": stock.get("entry_price", 100), "market_regime": "choppy"}
            for stock in stocks
        ]
        health_result = factory.calculate_health_scores(inputs=inputs, engine_type="AUTO", include_risk_metrics=False)

        position_data = [
            {
                "stock_code": stock["stock_code"],
                "weight": float(stock.get("weight", 0)),
                "entry_price": float(stock.get("entry_price", 0)),
                "current_price": float(stock.get("entry_price", 0)),
                "target_weight": float(stock.get("weight", 0)),
                "stop_loss_price": float(stock.get("stop_loss_price", 0)),
                "target_price": float(stock.get("target_price", 0)),
            }
            for stock in stocks
        ]

        analysis = optimizer.analyze_portfolio(
            watchlist_id=watchlist_id,
            watchlist_name=watchlist["name"],
            positions=position_data,
            health_scores=health_result["results"],
        )

        suggestions = analysis.rebalance_suggestions
        return UnifiedResponse(
            data=[RebalanceSuggestionResponse(**suggestion) for suggestion in suggestions],
            message=f"获取再平衡建议成功 (共{len(suggestions)}条)",
        )

    except BusinessException:
        raise
    except Exception as error:
        logger.error("获取再平衡建议失败: %(e)s")
        raise BusinessException(status_code=500, detail=f"获取失败: {str(error)}")
