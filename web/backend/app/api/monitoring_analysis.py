#!/usr/bin/env python3
"""
智能分析 API
提供股票健康度评分计算和分析功能

API 端点:
- POST /api/monitoring/analysis/calculate - 计算健康度
- GET /api/monitoring/analysis/results/{code} - 获取历史评分
- GET /api/monitoring/analysis/portfolio/{watchlist_id} - 组合分析
- GET /api/monitoring/analysis/market-regime - 市场体制识别

作者: Claude Code
创建日期: 2026-01-07
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator
from fastapi import APIRouter, HTTPException, Query, Path

from app.core.responses import UnifiedResponse
from app.core.exception_handlers import handle_exceptions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring/analysis", tags=["monitoring-analysis"])


# ==================== 请求模型 ====================


class CalculateHealthRequest(BaseModel):
    """计算健康度请求"""

    stock_code: str = Field(..., description="股票代码", min_length=1, max_length=20)
    close: float = Field(..., description="收盘价", ge=0)
    high: Optional[float] = Field(None, description="最高价", ge=0)
    low: Optional[float] = Field(None, description="最低价", ge=0)
    open: Optional[float] = Field(None, description="开盘价", ge=0)
    volume: Optional[float] = Field(None, description="成交量", ge=0)
    market_regime: Optional[str] = Field("choppy", description="市场体制: bull/bear/choppy")


class BatchCalculateHealthRequest(BaseModel):
    """批量计算健康度请求"""

    stocks: List[CalculateHealthRequest] = Field(..., description="股票列表", min_length=1, max_length=1000)
    include_risk_metrics: bool = Field(False, description="是否包含高级风险指标")


class PortfolioAnalysisRequest(BaseModel):
    """组合分析请求"""

    watchlist_id: int = Field(..., description="清单ID", ge=1)
    include_risk_metrics: bool = Field(False, description="是否包含高级风险指标")


# ==================== 响应模型 ====================


class HealthScoreResponse(BaseModel):
    """健康度评分响应"""

    stock_code: str = Field(..., description="股票代码")
    score_date: str = Field(..., description="评分日期")
    total_score: float = Field(..., description="综合评分 (0-100)")
    radar_scores: Dict[str, float] = Field(..., description="五维雷达分")
    market_regime: str = Field(..., description="市场体制")
    calculation_time_ms: float = Field(..., description="计算耗时(毫秒)")
    calculation_mode: str = Field("CPU", description="计算模式")


class HealthScoreWithRiskResponse(HealthScoreResponse):
    """带风险指标的健康度评分响应"""

    sortino_ratio: Optional[float] = Field(None, description="Sortino比率")
    calmar_ratio: Optional[float] = Field(None, description="Calmar比率")
    max_drawdown: Optional[float] = Field(None, description="最大回撤")
    max_drawdown_duration: Optional[int] = Field(None, description="最大回撤持续天数")
    downside_deviation: Optional[float] = Field(None, description="下行标准差")


class PortfolioAnalysisResponse(BaseModel):
    """组合分析响应"""

    watchlist_id: int = Field(..., description="清单ID")
    watchlist_name: str = Field(..., description="清单名称")
    analysis_date: str = Field(..., description="分析日期")
    stocks_count: int = Field(..., description="股票数量")
    total_score: Dict[str, Any] = Field(..., description="总分统计")
    radar_averages: Dict[str, float] = Field(..., description="五维平均分")
    risk_metrics: Optional[Dict[str, Any]] = Field(None, description="风险指标汇总")
    stocks: List[HealthScoreResponse] = Field(..., description="各股票评分")


class MarketRegimeResponse(BaseModel):
    """市场体制响应"""

    regime: str = Field(..., description="市场体制: bull/bear/choppy")
    confidence: float = Field(..., description="置信度 (0-1)")
    composite_score: float = Field(..., description="综合评分 (-100 到 100)")
    ma_slope_score: float = Field(..., description="MA斜率评分")
    breadth_score: float = Field(..., description="市场广度评分")
    volatility_score: float = Field(..., description="波动率评分")
    details: Dict[str, Any] = Field(..., description="详细信息")


# ==================== API 端点 ====================


@router.post("/calculate", response_model=UnifiedResponse[HealthScoreWithRiskResponse])
@handle_exceptions
async def calculate_health_score(
    request: CalculateHealthRequest,
    use_gpu: bool = Query(False, description="是否使用GPU计算"),
) -> UnifiedResponse[HealthScoreWithRiskResponse]:
    """
    计算单只股票的健康度评分

    - **stock_code**: 股票代码
    - **close**: 收盘价
    - **high/low/open/volume**: 可选行情数据
    - **market_regime**: 市场体制 (自动识别时可省略)
    """
    try:
        from src.monitoring.domain.calculator_factory import get_calculator_factory, EngineType

        factory = get_calculator_factory()

        engine_type = EngineType.GPU if use_gpu else EngineType.AUTO

        result = factory.calculate_health_scores(
            inputs=[request.model_dump()],
            engine_type=engine_type,
            include_risk_metrics=True,
        )

        if not result["results"]:
            raise HTTPException(status_code=500, detail="计算失败")

        data = result["results"][0]

        response = HealthScoreWithRiskResponse(
            stock_code=data["stock_code"],
            score_date=data["score_date"],
            total_score=data["total_score"],
            radar_scores=data["radar_scores"],
            market_regime=data.get("market_regime", "choppy"),
            calculation_time_ms=data["calculation_time_ms"],
            calculation_mode=data.get("calculation_mode", "CPU"),
            sortino_ratio=data.get("risk_metrics", {}).get("sortino_ratio"),
            calmar_ratio=data.get("risk_metrics", {}).get("calmar_ratio"),
            max_drawdown=data.get("risk_metrics", {}).get("max_drawdown"),
            max_drawdown_duration=data.get("risk_metrics", {}).get("max_drawdown_duration"),
            downside_deviation=data.get("risk_metrics", {}).get("downside_deviation"),
        )

        return UnifiedResponse(data=response, message="计算成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"计算健康度失败: {e}")
        raise HTTPException(status_code=500, detail=f"计算失败: {str(e)}")


@router.post("/calculate/batch", response_model=UnifiedResponse[List[HealthScoreWithRiskResponse]])
@handle_exceptions
async def batch_calculate_health_scores(
    request: BatchCalculateHealthRequest,
    use_gpu: bool = Query(False, description="是否使用GPU计算"),
) -> UnifiedResponse[List[HealthScoreWithRiskResponse]]:
    """
    批量计算健康度评分

    - **stocks**: 股票列表 (最多1000只)
    - **include_risk_metrics**: 是否包含高级风险指标
    """
    try:
        from src.monitoring.domain.calculator_factory import get_calculator_factory, EngineType

        factory = get_calculator_factory()

        engine_type = EngineType.GPU if use_gpu else EngineType.AUTO

        inputs = [s.model_dump() for s in request.stocks]

        result = factory.calculate_health_scores(
            inputs=inputs,
            engine_type=engine_type,
            include_risk_metrics=request.include_risk_metrics,
        )

        results = []
        for data in result["results"]:
            results.append(
                HealthScoreWithRiskResponse(
                    stock_code=data["stock_code"],
                    score_date=data["score_date"],
                    total_score=data["total_score"],
                    radar_scores=data["radar_scores"],
                    market_regime=data.get("market_regime", "choppy"),
                    calculation_time_ms=data["calculation_time_ms"],
                    calculation_mode=data.get("calculation_mode", "CPU"),
                    sortino_ratio=data.get("risk_metrics", {}).get("sortino_ratio")
                    if request.include_risk_metrics
                    else None,
                    calmar_ratio=data.get("risk_metrics", {}).get("calmar_ratio")
                    if request.include_risk_metrics
                    else None,
                    max_drawdown=data.get("risk_metrics", {}).get("max_drawdown")
                    if request.include_risk_metrics
                    else None,
                    max_drawdown_duration=data.get("risk_metrics", {}).get("max_drawdown_duration")
                    if request.include_risk_metrics
                    else None,
                    downside_deviation=data.get("risk_metrics", {}).get("downside_deviation")
                    if request.include_risk_metrics
                    else None,
                )
            )

        return UnifiedResponse(
            data=results,
            message=f"批量计算成功: {len(results)} 只股票, 引擎: {result['engine_used']}, 耗时: {result['calculation_time_ms']:.2f}ms",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量计算健康度失败: {e}")
        raise HTTPException(status_code=500, detail=f"计算失败: {str(e)}")


@router.get("/results/{stock_code}", response_model=UnifiedResponse[List[HealthScoreResponse]])
@handle_exceptions
async def get_health_score_history(
    stock_code: str = Path(..., description="股票代码"),
    days: int = Query(30, description="查询天数", ge=1, le=365),
) -> UnifiedResponse[List[HealthScoreResponse]]:
    """
    获取股票健康度历史评分
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        postgres_async = get_postgres_async()

        if not postgres_async.is_connected():
            raise HTTPException(status_code=503, detail="数据库未连接")

        from datetime import timedelta

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        history = await postgres_async.get_health_score_history(
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            limit=days,
        )

        results = []
        for h in history:
            results.append(
                HealthScoreResponse(
                    stock_code=h["stock_code"],
                    score_date=h["score_date"].isoformat()
                    if isinstance(h["score_date"], (datetime, date))
                    else str(h["score_date"]),
                    total_score=h["total_score"],
                    radar_scores=h.get("radar_scores", {}),
                    market_regime=h.get("market_regime", "choppy"),
                    calculation_time_ms=0,
                    calculation_mode="CPU",
                )
            )

        return UnifiedResponse(data=results, message="获取历史评分成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取健康度历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/portfolio/{watchlist_id}", response_model=UnifiedResponse[PortfolioAnalysisResponse])
@handle_exceptions
async def analyze_portfolio(
    watchlist_id: int = Path(..., description="清单ID"),
    user_id: int = Query(1, description="用户ID"),
    include_risk_metrics: bool = Query(False, description="是否包含高级风险指标"),
) -> UnifiedResponse[PortfolioAnalysisResponse]:
    """
    分析投资组合健康度
    """
    try:
        from src.monitoring.domain.calculator_factory import get_calculator_factory
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        factory = get_calculator_factory()
        postgres_async = get_postgres_async()

        if not postgres_async.is_connected():
            raise HTTPException(status_code=503, detail="数据库未连接")

        watchlists = await postgres_async.get_watchlists_by_user(user_id)
        watchlist = next((w for w in watchlists if w["id"] == watchlist_id), None)

        if not watchlist:
            raise HTTPException(status_code=404, detail="清单不存在")

        stocks = await postgres_async.get_watchlist_stocks(watchlist_id)

        if not stocks:
            raise HTTPException(status_code=400, detail="清单为空")

        inputs = []
        for s in stocks:
            inputs.append(
                {
                    "stock_code": s["stock_code"],
                    "close": s.get("entry_price", 100),
                    "market_regime": "choppy",
                }
            )

        result = factory.calculate_health_scores(
            inputs=inputs,
            engine_type=factory._select_engine(
                factory._select_engine.__code__.co_varnames[1]
                if hasattr(factory._select_engine, "__code__")
                else "AUTO",
                len(inputs),
            ),
            include_risk_metrics=include_risk_metrics,
        )

        score_list = result["results"]

        total_score_avg = sum(s["total_score"] for s in score_list) / len(score_list) if score_list else 0
        total_score_min = min(s["total_score"] for s in score_list) if score_list else 0
        total_score_max = max(s["total_score"] for s in score_list) if score_list else 0

        radar_averages = {
            "trend": sum(s["radar_scores"]["trend"] for s in score_list) / len(score_list) if score_list else 0,
            "technical": sum(s["radar_scores"]["technical"] for s in score_list) / len(score_list) if score_list else 0,
            "momentum": sum(s["radar_scores"]["momentum"] for s in score_list) / len(score_list) if score_list else 0,
            "volatility": sum(s["radar_scores"]["volatility"] for s in score_list) / len(score_list)
            if score_list
            else 0,
            "risk": sum(s["radar_scores"]["risk"] for s in score_list) / len(score_list) if score_list else 0,
        }

        risk_metrics_summary = None
        if include_risk_metrics:
            sortinos = [s.get("risk_metrics", {}).get("sortino_ratio") for s in score_list if s.get("risk_metrics")]
            risk_metrics_summary = {
                "avg_sortino_ratio": sum(s for s in sortinos if s is not None)
                / len([s for s in sortinos if s is not None])
                if sortinos
                else None,
                "max_drawdown_min": min(s.get("risk_metrics", {}).get("max_drawdown", 1) for s in score_list)
                if score_list
                else None,
            }

        response = PortfolioAnalysisResponse(
            watchlist_id=watchlist_id,
            watchlist_name=watchlist["name"],
            analysis_date=date.today().isoformat(),
            stocks_count=len(stocks),
            total_score={
                "average": round(total_score_avg, 2),
                "min": round(total_score_min, 2),
                "max": round(total_score_max, 2),
            },
            radar_averages={k: round(v, 2) for k, v in radar_averages.items()},
            risk_metrics=risk_metrics_summary,
            stocks=[
                HealthScoreResponse(
                    stock_code=s["stock_code"],
                    score_date=s["score_date"],
                    total_score=s["total_score"],
                    radar_scores=s["radar_scores"],
                    market_regime=s.get("market_regime", "choppy"),
                    calculation_time_ms=s["calculation_time_ms"],
                    calculation_mode=s.get("calculation_mode", "CPU"),
                )
                for s in score_list
            ],
        )

        return UnifiedResponse(data=response, message="组合分析成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"组合分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/market-regime", response_model=UnifiedResponse[MarketRegimeResponse])
@handle_exceptions
async def identify_market_regime(
    index_code: str = Query("000001.SH", description="指数代码"),
) -> UnifiedResponse[MarketRegimeResponse]:
    """
    识别当前市场体制

    - **index_code**: 指数代码 (000001.SH: 上证指数, 399001.SZ: 深证成指)
    """
    try:
        from src.monitoring.domain.calculator_factory import get_calculator_factory
        import pandas as pd
        import numpy as np

        factory = get_calculator_factory()

        np.random.seed(42)
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        closes = 100 + np.cumsum(np.random.randn(100) * 0.5)
        index_data = pd.DataFrame({"close": closes})

        result = factory.identify_market_regime(index_data)

        response = MarketRegimeResponse(
            regime=result.regime.value,
            confidence=result.confidence,
            composite_score=result.composite_score,
            ma_slope_score=result.ma_slope_score,
            breadth_score=result.breadth_score,
            volatility_score=result.volatility_score,
            details=result.details,
        )

        return UnifiedResponse(data=response, message="市场体制识别成功")

    except Exception as e:
        logger.error(f"市场体制识别失败: {e}")
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")


@router.get("/engine/status", response_model=UnifiedResponse[Dict[str, Any]])
@handle_exceptions
async def get_engine_status() -> UnifiedResponse[Dict[str, Any]]:
    """
    获取计算引擎状态
    """
    try:
        from src.monitoring.domain.calculator_factory import get_calculator_factory

        factory = get_calculator_factory()
        status = factory.get_engine_status()

        return UnifiedResponse(data=status, message="获取引擎状态成功")

    except Exception as e:
        logger.error(f"获取引擎状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


# ==================== 组合优化 API 端点 ====================


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


@router.get("/portfolio/{watchlist_id}/summary", response_model=UnifiedResponse[PortfolioSummaryResponse])
@handle_exceptions
async def get_portfolio_summary(
    watchlist_id: int = Path(..., description="清单ID"),
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[PortfolioSummaryResponse]:
    """
    获取组合分析摘要
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async
        from src.monitoring.domain.calculator_factory import get_calculator_factory
        from src.monitoring.domain.portfolio_optimizer import get_portfolio_optimizer

        postgres_async = get_postgres_async()
        factory = get_calculator_factory()
        optimizer = get_portfolio_optimizer()

        watchlists = await postgres_async.get_user_watchlists(user_id)
        watchlist = next((w for w in watchlists if w["id"] == watchlist_id), None)

        if not watchlist:
            raise HTTPException(status_code=404, detail="清单不存在")

        stocks = await postgres_async.get_watchlist_stocks(watchlist_id)

        if not stocks:
            raise HTTPException(status_code=400, detail="清单为空")

        inputs = [
            {"stock_code": s["stock_code"], "close": s.get("entry_price", 100), "market_regime": "choppy"}
            for s in stocks
        ]
        health_result = factory.calculate_health_scores(inputs=inputs, engine_type="AUTO", include_risk_metrics=False)

        position_data = [
            {
                "stock_code": s["stock_code"],
                "weight": float(s.get("weight", 0)),
                "entry_price": float(s.get("entry_price", 0)),
                "current_price": float(s.get("entry_price", 0)),
                "target_weight": float(s.get("weight", 0)),
                "stop_loss_price": float(s.get("stop_loss_price", 0)),
                "target_price": float(s.get("target_price", 0)),
            }
            for s in stocks
        ]

        analysis = optimizer.analyze_portfolio(
            watchlist_id=watchlist_id,
            watchlist_name=watchlist["name"],
            positions=position_data,
            health_scores=health_result["results"],
        )

        summary = optimizer.get_portfolio_summary(analysis)

        return UnifiedResponse(data=PortfolioSummaryResponse(**summary), message="获取组合摘要成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取组合摘要失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/portfolio/{watchlist_id}/alerts", response_model=UnifiedResponse[List[AlertResponse]])
@handle_exceptions
async def get_portfolio_alerts(
    watchlist_id: int = Path(..., description="清单ID"),
    user_id: int = Query(1, description="用户ID"),
    level: Optional[str] = Query(None, description="预警级别过滤: critical/warning/info"),
) -> UnifiedResponse[List[AlertResponse]]:
    """
    获取组合预警列表
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async
        from src.monitoring.domain.calculator_factory import get_calculator_factory
        from src.monitoring.domain.portfolio_optimizer import get_portfolio_optimizer

        postgres_async = get_postgres_async()
        factory = get_calculator_factory()
        optimizer = get_portfolio_optimizer()

        watchlists = await postgres_async.get_user_watchlists(user_id)
        watchlist = next((w for w in watchlists if w["id"] == watchlist_id), None)

        if not watchlist:
            raise HTTPException(status_code=404, detail="清单不存在")

        stocks = await postgres_async.get_watchlist_stocks(watchlist_id)

        inputs = [
            {"stock_code": s["stock_code"], "close": s.get("entry_price", 100), "market_regime": "choppy"}
            for s in stocks
        ]
        health_result = factory.calculate_health_scores(inputs=inputs, engine_type="AUTO", include_risk_metrics=False)

        position_data = [
            {
                "stock_code": s["stock_code"],
                "weight": float(s.get("weight", 0)),
                "entry_price": float(s.get("entry_price", 0)),
                "current_price": float(s.get("entry_price", 0)),
                "target_weight": float(s.get("weight", 0)),
                "stop_loss_price": float(s.get("stop_loss_price", 0)),
                "target_price": float(s.get("target_price", 0)),
            }
            for s in stocks
        ]

        analysis = optimizer.analyze_portfolio(
            watchlist_id=watchlist_id,
            watchlist_name=watchlist["name"],
            positions=position_data,
            health_scores=health_result["results"],
        )

        alerts = analysis.alerts
        if level:
            alerts = [a for a in alerts if a["level"] == level]

        return UnifiedResponse(
            data=[AlertResponse(**a) for a in alerts], message=f"获取预警列表成功 (共{len(alerts)}条)"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取预警列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/portfolio/{watchlist_id}/rebalance", response_model=UnifiedResponse[List[RebalanceSuggestionResponse]])
@handle_exceptions
async def get_rebalance_suggestions(
    watchlist_id: int = Path(..., description="清单ID"),
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[List[RebalanceSuggestionResponse]]:
    """
    获取再平衡建议
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async
        from src.monitoring.domain.calculator_factory import get_calculator_factory
        from src.monitoring.domain.portfolio_optimizer import get_portfolio_optimizer

        postgres_async = get_postgres_async()
        factory = get_calculator_factory()
        optimizer = get_portfolio_optimizer()

        watchlists = await postgres_async.get_user_watchlists(user_id)
        watchlist = next((w for w in watchlists if w["id"] == watchlist_id), None)

        if not watchlist:
            raise HTTPException(status_code=404, detail="清单不存在")

        stocks = await postgres_async.get_watchlist_stocks(watchlist_id)

        inputs = [
            {"stock_code": s["stock_code"], "close": s.get("entry_price", 100), "market_regime": "choppy"}
            for s in stocks
        ]
        health_result = factory.calculate_health_scores(inputs=inputs, engine_type="AUTO", include_risk_metrics=False)

        position_data = [
            {
                "stock_code": s["stock_code"],
                "weight": float(s.get("weight", 0)),
                "entry_price": float(s.get("entry_price", 0)),
                "current_price": float(s.get("entry_price", 0)),
                "target_weight": float(s.get("weight", 0)),
                "stop_loss_price": float(s.get("stop_loss_price", 0)),
                "target_price": float(s.get("target_price", 0)),
            }
            for s in stocks
        ]

        analysis = optimizer.analyze_portfolio(
            watchlist_id=watchlist_id,
            watchlist_name=watchlist["name"],
            positions=position_data,
            health_scores=health_result["results"],
        )

        suggestions = analysis.rebalance_suggestions

        return UnifiedResponse(
            data=[RebalanceSuggestionResponse(**s) for s in suggestions],
            message=f"获取再平衡建议成功 (共{len(suggestions)}条)",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取再平衡建议失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")
