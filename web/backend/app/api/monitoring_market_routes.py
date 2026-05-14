"""Realtime and dragon-tiger monitoring routes."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, Path, Query

from app.core.exceptions import BusinessException, NotFoundException
from app.core.responses import UnifiedResponse, create_unified_success_response
from app.core.security import User, get_current_user
from app.models.monitoring import DragonTigerListResponse, RealtimeMonitoringResponse
from app.services.monitoring_service import monitoring_service
from app.api.monitoring_response_specs import (
    DRAGON_TIGER_LIST_RESPONSES,
    FETCH_DRAGON_TIGER_DATA_RESPONSES,
    FETCH_REALTIME_DATA_RESPONSES,
    REALTIME_MONITORING_DETAIL_RESPONSES,
    REALTIME_MONITORING_LIST_RESPONSES,
)

router = APIRouter()


# ============================================================================
# 实时监控数据
# ============================================================================


@router.get(
    "/realtime/{symbol}",
    response_model=UnifiedResponse[RealtimeMonitoringResponse],
    summary="获取单只股票实时监控数据",
    description="查询指定股票的最新实时监控快照，返回行情、指标和涨跌停状态等监控字段。",
    responses=REALTIME_MONITORING_DETAIL_RESPONSES,
)
async def get_realtime_monitoring(
    symbol: str = Path(..., description="待查询的股票代码，例如 600519。"),
    current_user: User = Depends(get_current_user),
):
    """
    获取单只股票的最新实时监控数据

    参数:
    - symbol: 股票代码

    示例:
    - GET /api/monitoring/realtime/600519
    """
    try:
        session = monitoring_service.get_session()
        try:
            from app.models.monitoring import RealtimeMonitoring

            record = (
                session.query(RealtimeMonitoring)
                .filter(RealtimeMonitoring.symbol == symbol)
                .order_by(RealtimeMonitoring.timestamp.desc())
                .first()
            )

            if not record:
                raise NotFoundException(resource="股票监控数据", identifier="查询条件")

            return create_unified_success_response(
                data=RealtimeMonitoringResponse.from_orm(record),
                message="获取实时监控数据成功",
            )
        finally:
            session.close()
    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.get(
    "/realtime",
    response_model=UnifiedResponse[List[RealtimeMonitoringResponse]],
    summary="获取实时监控数据列表",
    description="批量查询当日实时监控记录，支持按股票列表、涨停状态和跌停状态筛选。",
    responses=REALTIME_MONITORING_LIST_RESPONSES,
)
async def get_realtime_monitoring_list(
    symbols: Optional[str] = Query(None, description="逗号分隔的股票代码列表，例如 600519,000001。"),
    limit: int = Query(100, ge=1, le=1000, description="返回的最新实时监控记录上限。"),
    is_limit_up: Optional[bool] = Query(None, description="是否仅返回涨停股票，true 表示只保留涨停记录。"),
    is_limit_down: Optional[bool] = Query(None, description="是否仅返回跌停股票，true 表示只保留跌停记录。"),
    current_user: User = Depends(get_current_user),
):
    """
    获取实时监控数据列表

    参数:
    - symbols: 股票代码列表，逗号分隔 (可选，如: "600519,000001")
    - limit: 返回数量限制
    - is_limit_up: 仅返回涨停股票 (可选)
    - is_limit_down: 仅返回跌停股票 (可选)

    示例:
    - GET /api/monitoring/realtime?limit=20
    - GET /api/monitoring/realtime?is_limit_up=true
    - GET /api/monitoring/realtime?symbols=600519,000001,600000
    """
    try:
        session = monitoring_service.get_session()
        try:
            from app.models.monitoring import RealtimeMonitoring

            query = session.query(RealtimeMonitoring).filter(RealtimeMonitoring.trade_date == date.today())

            # 筛选指定股票
            if symbols:
                symbol_list = [s.strip() for s in symbols.split(",")]
                query = query.filter(RealtimeMonitoring.symbol.in_(symbol_list))

            # 筛选涨跌停
            if is_limit_up is not None:
                query = query.filter(RealtimeMonitoring.is_limit_up == is_limit_up)
            if is_limit_down is not None:
                query = query.filter(RealtimeMonitoring.is_limit_down == is_limit_down)

            # 对于每只股票，只取最新的记录
            # 这里简化处理，实际应该用子查询
            records = query.order_by(RealtimeMonitoring.timestamp.desc()).limit(limit).all()

            return create_unified_success_response(
                data=[RealtimeMonitoringResponse.from_orm(r) for r in records],
                message="获取实时监控列表成功",
            )
        finally:
            session.close()
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.post(
    "/realtime/fetch",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="手动触发实时行情抓取",
    description="手动刷新实时监控行情数据，可按股票代码列表定向抓取并同步评估告警规则。",
    responses=FETCH_REALTIME_DATA_RESPONSES,
)
async def fetch_realtime_data(
    symbols: Optional[List[str]] = Body(
        default=None,
        description="需要立即刷新的股票代码数组；为空时抓取当前监控范围内的全量实时数据。",
        example=["600519", "000001", "601318"],
    ),
    current_user: User = Depends(get_current_user),
):
    """
    手动触发获取实时数据

    参数:
    - symbols: 股票代码列表 (可选，不提供则获取全市场)

    请求体示例:
    ```json
    ["600519", "000001", "601318"]
    ```
    """
    try:
        df = monitoring_service.fetch_realtime_data(symbols)
        if df.empty:
            return UnifiedResponse(success=False, code=200, message="未获取到数据", data=None)

        # 保存数据
        count = monitoring_service.save_realtime_data(df)

        # 评估告警规则
        alerts = monitoring_service.evaluate_alert_rules(df)

        return create_unified_success_response(
            data={
                "stocks_count": len(df),
                "saved_count": count,
                "alerts_triggered": len(alerts),
            },
            message="实时数据获取成功",
        )
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


# ============================================================================
# 龙虎榜数据
# ============================================================================


@router.get(
    "/dragon-tiger",
    response_model=UnifiedResponse[List[DragonTigerListResponse]],
    summary="获取龙虎榜列表",
    description="查询监控模块内的龙虎榜记录，支持按交易日、股票代码和净买入额阈值进行过滤。",
    responses=DRAGON_TIGER_LIST_RESPONSES,
)
async def get_dragon_tiger_list(
    trade_date: Optional[date] = Query(None, description="按交易日期筛选龙虎榜数据，默认当天。"),
    symbol: Optional[str] = Query(None, description="按股票代码筛选龙虎榜数据。"),
    min_net_amount: Optional[float] = Query(None, description="按最小净买入额筛选龙虎榜记录。"),
    limit: int = Query(100, ge=1, le=500, description="返回记录数量上限。"),
    current_user: User = Depends(get_current_user),
):
    """
    获取龙虎榜数据

    参数:
    - trade_date: 交易日期 (可选，默认今天)
    - symbol: 股票代码 (可选)
    - min_net_amount: 最小净买入额 (可选)
    - limit: 返回数量限制

    示例:
    - GET /api/monitoring/dragon-tiger
    - GET /api/monitoring/dragon-tiger?trade_date=2025-10-23
    - GET /api/monitoring/dragon-tiger?symbol=600519
    """
    try:
        session = monitoring_service.get_session()
        try:
            from app.models.monitoring import DragonTigerList

            if trade_date is None:
                trade_date = date.today()

            query = session.query(DragonTigerList).filter(DragonTigerList.trade_date == trade_date)

            if symbol:
                query = query.filter(DragonTigerList.symbol == symbol)
            if min_net_amount is not None:
                query = query.filter(DragonTigerList.net_amount >= min_net_amount)

            records = query.order_by(DragonTigerList.net_amount.desc()).limit(limit).all()

            return create_unified_success_response(
                data=[DragonTigerListResponse.from_orm(r) for r in records],
                message="获取龙虎榜列表成功",
            )
        finally:
            session.close()
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.post(
    "/dragon-tiger/fetch",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="手动触发龙虎榜数据抓取",
    description="手动抓取指定交易日的龙虎榜数据，并写入监控侧使用的龙虎榜数据表。",
    responses=FETCH_DRAGON_TIGER_DATA_RESPONSES,
)
async def fetch_dragon_tiger_data(
    trade_date: Optional[date] = Query(None, description="需要抓取的交易日期，默认使用当天交易日。"),
    current_user: User = Depends(get_current_user),
):
    """
    手动触发获取龙虎榜数据

    参数:
    - trade_date: 交易日期 (可选，默认今天)
    """
    try:
        if trade_date is None:
            trade_date = date.today()

        df = monitoring_service.fetch_dragon_tiger_list(trade_date)
        if df.empty:
            return UnifiedResponse(success=False, code=200, message=f"{trade_date} 无龙虎榜数据", data=None)

        count = monitoring_service.save_dragon_tiger_data(df, trade_date)

        return create_unified_success_response(
            data={"trade_date": trade_date.isoformat(), "count": count},
            message="龙虎榜数据获取成功",
        )
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")
