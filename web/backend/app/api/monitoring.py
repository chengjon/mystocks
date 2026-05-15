"""
监控系统 API 端点
Real-time Monitoring System
"""

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, Path, Query
from pydantic import BaseModel, Field

from app.core.exceptions import BusinessException, NotFoundException
from app.core.responses import UnifiedResponse, create_unified_success_response
from app.core.security import User, get_current_user
from app.models.monitoring import (
    AlertLevel,
    AlertRecordResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    AlertRuleType,
    AlertRuleUpdate,
    DragonTigerListResponse,
    MonitoringSummaryResponse,
    RealtimeMonitoringResponse,
)
from app.api.monitoring_market_routes import (
    fetch_dragon_tiger_data,
    fetch_realtime_data,
    get_dragon_tiger_list,
    get_realtime_monitoring,
    get_realtime_monitoring_list,
    router as market_monitoring_router,
)
from app.api.monitoring_response_specs import (
    ALERT_MARK_ALL_READ_RESPONSES,
    ALERT_MARK_READ_RESPONSES,
    ALERT_RECORDS_LIST_RESPONSES,
    ALERT_RULE_CREATE_RESPONSES,
    ALERT_RULE_DELETE_RESPONSES,
    ALERT_RULE_UPDATE_RESPONSES,
    ALERT_RULES_LIST_RESPONSES,
    MONITORING_STATUS_RESPONSES,
    MONITORING_SUMMARY_RESPONSES,
    START_MONITORING_RESPONSES,
    STOP_MONITORING_RESPONSES,
    TODAY_STATS_RESPONSES,
)
from app.services.monitoring_alert_record_service import MonitoringAlertRecordService
from app.services.monitoring_alert_rule_service import MonitoringAlertRuleService
from app.services.monitoring_control_service import MonitoringControlService
from app.services.monitoring_service import monitoring_service
from app.services.monitoring_summary_service import (
    MonitoringSummaryService,
    is_monitoring_summary_mock_enabled,
    load_mock_monitoring_summary,
)
from app.services.monitoring_runtime_fallbacks import (
    build_runtime_alert_records as _build_runtime_alert_records,
    build_runtime_alert_rules as _build_runtime_alert_rules,
    resolve_query_int as _resolve_query_int,
    runtime_fallback_enabled as _runtime_fallback_enabled,
)
from app.services.monitoring_today_statistics_service import MonitoringTodayStatisticsService


__all__ = [
    "DragonTigerListResponse",
    "fetch_dragon_tiger_data",
    "fetch_realtime_data",
    "get_dragon_tiger_list",
    "get_realtime_monitoring",
    "get_realtime_monitoring_list",
    "RealtimeMonitoringResponse",
    "router",
]

router = APIRouter()
router.include_router(market_monitoring_router)
_monitoring_control_service = MonitoringControlService(monitoring_service)
_monitoring_summary_service = MonitoringSummaryService(monitoring_service)
_monitoring_alert_rule_service = MonitoringAlertRuleService(
    monitoring_service,
    runtime_fallback_enabled=lambda: _runtime_fallback_enabled(),
    runtime_rules_loader=lambda: _build_runtime_alert_rules(),
)
_monitoring_alert_record_service = MonitoringAlertRecordService(
    monitoring_service,
    runtime_fallback_enabled=lambda: _runtime_fallback_enabled(),
    runtime_records_loader=lambda: _build_runtime_alert_records(),
)
_monitoring_today_statistics_service = MonitoringTodayStatisticsService(monitoring_service)


def _is_monitoring_summary_mock_enabled() -> bool:
    return is_monitoring_summary_mock_enabled()


def _get_mock_monitoring_summary() -> Dict[str, Any]:
    return load_mock_monitoring_summary()

def _build_monitoring_control_payload(*, include_interval_key: Optional[str] = None) -> Dict[str, Any]:
    return _monitoring_control_service.build_payload(include_interval_key=include_interval_key)


def _get_monitoring_task() -> Any:
    return _monitoring_control_service.get_task()


# ============================================================================
# 告警规则管理
# ============================================================================


@router.get(
    "/alert-rules",
    response_model=UnifiedResponse[List[AlertRuleResponse]],
    summary="获取告警规则列表",
    description="查询监控告警规则列表，支持按规则类型和启用状态过滤。",
    responses=ALERT_RULES_LIST_RESPONSES,
)
async def get_alert_rules(
    rule_type: Optional[AlertRuleType] = Query(None, description="规则类型过滤条件，例如 limit_up 或 technical_break。"),
    is_active: Optional[bool] = Query(None, description="按启用状态过滤，true 表示仅返回启用规则。"),
    current_user: User = Depends(get_current_user),
):
    """
    获取告警规则列表

    参数:
    - rule_type: 规则类型 (可选)
    - is_active: 是否启用 (可选)
    """
    try:
        rules = _monitoring_alert_rule_service.list_rules(
            rule_type=rule_type.value if rule_type else None, is_active=is_active
        )
        return create_unified_success_response(
            data=rules,
            message="获取告警规则成功",
        )
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.post(
    "/alert-rules",
    response_model=UnifiedResponse[AlertRuleResponse],
    summary="创建告警规则",
    description="创建新的监控告警规则，定义触发条件、通知方式和优先级。",
    responses=ALERT_RULE_CREATE_RESPONSES,
)
async def create_alert_rule(
    rule: AlertRuleCreate = Body(
        ...,
        example={
            "rule_name": "茅台涨停监控",
            "rule_type": "limit_up",
            "description": "茅台涨停时触发提醒",
            "symbol": "600519",
            "stock_name": "贵州茅台",
            "parameters": {"include_st": False},
            "trigger_conditions": {"field": "change_percent", "operator": ">=", "value": 9.8},
            "notification_config": {"channels": ["ui", "sound"], "level": "warning"},
            "priority": 5,
            "is_active": True,
        },
    ),
    current_user: User = Depends(get_current_user),
):
    """
    创建告警规则
    """
    try:
        return create_unified_success_response(
            data=_monitoring_alert_rule_service.create_rule(rule),
            message="创建告警规则成功",
        )
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=400, error_code="INVALID_MONITORING_REQUEST")


@router.put(
    "/alert-rules/{rule_id}",
    response_model=UnifiedResponse[AlertRuleResponse],
    summary="更新告警规则",
    description="按规则 ID 更新告警规则的部分字段，例如通知配置、优先级或启用状态。",
    responses=ALERT_RULE_UPDATE_RESPONSES,
)
async def update_alert_rule(
    rule_id: int = Path(..., description="告警规则 ID。"),
    updates: AlertRuleUpdate = Body(
        ...,
        example={
            "description": "更新后的涨停提醒规则",
            "notification_config": {"channels": ["ui"], "level": "critical"},
            "priority": 4,
            "is_active": True,
        },
    ),
    current_user: User = Depends(get_current_user),
):
    """
    更新告警规则

    参数:
    - rule_id: 规则ID
    - updates: 要更新的字段
    """
    try:
        return create_unified_success_response(
            data=_monitoring_alert_rule_service.update_rule(rule_id, updates),
            message="更新告警规则成功",
        )
    except ValueError as e:
        raise NotFoundException(resource="监控数据", identifier=str(e))
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=400, error_code="INVALID_MONITORING_REQUEST")


@router.delete(
    "/alert-rules/{rule_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="删除告警规则",
    description="按规则 ID 删除指定告警规则，用于停用不再需要的监控配置。",
    responses=ALERT_RULE_DELETE_RESPONSES,
)
async def delete_alert_rule(
    rule_id: int = Path(..., description="告警规则 ID。"),
    current_user: User = Depends(get_current_user),
):
    """
    删除告警规则

    参数:
    - rule_id: 规则ID
    """
    try:
        return create_unified_success_response(
            data=_monitoring_alert_rule_service.delete_rule(rule_id),
            message="删除告警规则成功",
        )
    except ValueError as e:
        raise NotFoundException(resource="监控数据", identifier=str(e))
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=400, error_code="INVALID_MONITORING_REQUEST")


# ============================================================================
# 告警记录查询
# ============================================================================


class AlertRecordsResponse(BaseModel):
    """告警记录列表响应"""

    success: bool = Field(True, description="查询是否成功。")
    data: List[AlertRecordResponse] = Field(..., description="告警记录列表。")
    total: int = Field(..., description="符合筛选条件的告警总数。")
    limit: int = Field(..., description="当前请求返回上限。")
    offset: int = Field(..., description="当前分页偏移量。")


@router.get(
    "/alerts",
    response_model=UnifiedResponse[AlertRecordsResponse],
    summary="获取告警记录列表",
    description="查询监控告警记录，支持按股票、告警类型、等级、已读状态和日期区间进行筛选分页。",
    responses=ALERT_RECORDS_LIST_RESPONSES,
)
async def get_alert_records(
    symbol: Optional[str] = Query(None, description="按股票代码筛选告警记录。"),
    alert_type: Optional[str] = Query(None, description="按告警类型筛选，例如 limit_up 或 volume_spike。"),
    alert_level: Optional[AlertLevel] = Query(None, description="按告警等级筛选，例如 info、warning 或 critical。"),
    is_read: Optional[bool] = Query(None, description="按已读状态筛选告警记录。"),
    start_date: Optional[date] = Query(None, description="限制返回结果的开始日期，包含当天。"),
    end_date: Optional[date] = Query(None, description="限制返回结果的结束日期，包含当天。"),
    limit: int = Query(100, ge=1, le=1000, description="单次请求返回的最大告警记录数。"),
    offset: int = Query(0, ge=0, description="分页偏移量，用于配合 limit 翻页。"),
    current_user: User = Depends(get_current_user),
):
    """
    查询告警记录

    参数:
    - symbol: 股票代码 (可选)
    - alert_type: 告警类型 (可选)
    - alert_level: 告警级别 (可选)
    - is_read: 是否已读 (可选)
    - start_date: 开始日期 (可选)
    - end_date: 结束日期 (可选)
    - limit: 返回数量限制
    - offset: 偏移量

    示例:
    - GET /api/monitoring/alerts?is_read=false&limit=50
    - GET /api/monitoring/alerts?symbol=600519&alert_type=limit_up
    - GET /api/monitoring/alerts?alert_level=critical
    """
    limit_value = _resolve_query_int(limit, 100)
    offset_value = _resolve_query_int(offset, 0)

    try:
        page = _monitoring_alert_record_service.list_records(
            symbol=symbol,
            alert_type=alert_type,
            alert_level=alert_level.value if alert_level else None,
            is_read=is_read,
            start_date=start_date,
            end_date=end_date,
            limit=limit_value,
            offset=offset_value,
        )

        return create_unified_success_response(
            data=AlertRecordsResponse(
                data=page.records,
                total=page.total,
                limit=page.limit,
                offset=page.offset,
            ),
            message="获取告警记录成功",
        )
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.post(
    "/alerts/{alert_id}/mark-read",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="标记告警为已读",
    description="按告警记录 ID 将单条告警标记为已读，便于前端清理未读提醒。",
    responses=ALERT_MARK_READ_RESPONSES,
)
async def mark_alert_read(
    alert_id: int = Path(..., description="告警记录 ID。"),
    current_user: User = Depends(get_current_user),
):
    """
    标记告警为已读

    参数:
    - alert_id: 告警记录ID
    """
    try:
        return create_unified_success_response(
            data=_monitoring_alert_record_service.mark_read(alert_id),
            message="已标记为已读",
        )
    except ValueError as e:
        raise NotFoundException(resource="告警记录", identifier=str(e))
    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.post(
    "/alerts/mark-all-read",
    summary="批量标记全部告警已读",
    description="批量将当前用户可见的未读告警标记为已读，用于监控中心一键清空提醒。",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=ALERT_MARK_ALL_READ_RESPONSES,
)
async def mark_all_alerts_read(current_user: User = Depends(get_current_user)):
    """批量标记所有未读告警为已读。"""
    try:
        return UnifiedResponse(
            success=True,
            code=200,
            message="全部告警已标记为已读",
            data=_monitoring_alert_record_service.mark_all_read(),
        )
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")



# ============================================================================
# 监控摘要和统计
# ============================================================================


@router.get(
    "/analyze",
    response_model=UnifiedResponse[MonitoringSummaryResponse],
    summary="获取监控分析摘要",
    description="兼容旧版调用方的监控分析入口，返回与摘要接口一致的监控汇总结果。",
    responses=MONITORING_SUMMARY_RESPONSES,
)
async def analyze_monitoring(current_user: User = Depends(get_current_user)):
    """
    监控分析 (Alias for summary)

    Compatible with Phase 2.8 requirements
    """
    return await get_monitoring_summary(current_user)


@router.get(
    "/summary",
    response_model=UnifiedResponse[MonitoringSummaryResponse],
    summary="获取监控系统摘要",
    description="返回监控系统的核心汇总指标，包括涨跌停数量、活跃告警数与市场强弱概览。",
    responses=MONITORING_SUMMARY_RESPONSES,
)
async def get_monitoring_summary(current_user: User = Depends(get_current_user)):
    """
    获取监控系统摘要

    返回:
    - 总监控股票数
    - 涨停/跌停数量
    - 大涨/大跌数量
    - 平均涨跌幅
    - 总成交额
    - 活跃告警数
    - 未读告警数
    """
    try:
        return create_unified_success_response(
            data=_monitoring_summary_service.get_summary(),
            message="获取监控系统摘要成功",
        )
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.get(
    "/stats/today",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="获取今日监控统计",
    description="查询当日告警摘要、活跃规则与实时监控总览，供监控中心首页与值班看板展示。",
    responses=TODAY_STATS_RESPONSES,
)
async def get_today_statistics(current_user: User = Depends(get_current_user)):
    """获取今日监控统计聚合结果。"""
    try:
        return create_unified_success_response(
            data=_monitoring_today_statistics_service.get_today_statistics(),
            message="获取今日监控统计成功",
        )
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


# ============================================================================
# 监控控制
# ============================================================================


class MonitoringControlRequest(BaseModel):
    """监控控制请求"""

    symbols: Optional[List[str]] = Field(None, description="需要纳入监控的股票代码列表；为空表示使用默认监控池。")
    interval: int = Field(60, description="监控轮询间隔，单位秒。")


@router.post(
    "/control/start",
    summary="启动实时监控任务",
    description="提交监控启动请求，指定监控股票范围和刷新间隔，用于监控面板手动拉起任务。",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=START_MONITORING_RESPONSES,
)
async def start_monitoring(
    request: MonitoringControlRequest = Body(
        ...,
        example={"symbols": ["600519", "000001", "601318"], "interval": 30},
    ),
    current_user: User = Depends(get_current_user),
):
    """
    启动监控

    参数:
    - symbols: 要监控的股票代码列表 (可选，不提供则监控全市场)
    - interval: 更新间隔(秒)，默认60秒
    """
    try:
        data = await _monitoring_control_service.start(symbols=request.symbols, interval=request.interval)
        return create_unified_success_response(
            data=data,
            message="监控已启动",
        )
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.post(
    "/control/stop",
    summary="停止实时监控任务",
    description="停止当前运行中的监控任务，并返回停止结果给监控控制面板。",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=STOP_MONITORING_RESPONSES,
)
async def stop_monitoring(current_user: User = Depends(get_current_user)):
    """停止当前监控任务并返回结果。"""
    try:
        data = await _monitoring_control_service.stop()
        return create_unified_success_response(
            data=data,
            message="监控已停止",
        ).model_dump()
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.get(
    "/control/status",
    summary="获取监控运行状态",
    description="查询实时监控系统的运行状态、监控范围和当前监控股票数量，用于面板状态展示。",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=MONITORING_STATUS_RESPONSES,
)
async def get_monitoring_status():
    """
    获取实时监控系统运行状态

    查询当前监控系统的运行状态、监控范围和统计信息。该端点用于检查监控服务是否
    正常运行，以及正在监控的股票列表。

    **功能说明**:
    - 返回监控服务运行状态（运行中/已停止）
    - 提供当前监控的股票代码列表
    - 统计监控股票数量
    - 显示监控配置信息（更新间隔、告警规则数量等）
    - 支持监控面板状态展示

    **使用场景**:
    - 监控面板实时状态展示
    - 健康检查和服务可用性监测
    - 调试监控服务启停状态
    - 确认特定股票是否在监控范围内
    - 运维监控系统状态查询

    **返回值**:
    - success: 请求是否成功（布尔值）
    - data: 监控状态数据对象
      - is_monitoring: 是否正在监控（布尔值）
      - monitored_symbols: 监控的股票代码列表（数组）
      - monitored_count: 监控股票数量（整数）
      - update_interval (可选): 更新间隔秒数
      - active_rules_count (可选): 活跃告警规则数量
      - last_update_time (可选): 最后更新时间

    **示例**:
    ```bash
    # 查询监控状态
    curl -X GET "http://localhost:${BACKEND_PORT}/api/monitoring/control/status"
    ```

    **响应示例**:
    ```json
    {
      "success": true,
      "data": {
        "is_monitoring": true,
        "monitored_symbols": ["600519", "000001", "600036", "601318"],
        "monitored_count": 4,
        "update_interval": 60,
        "active_rules_count": 12,
        "last_update_time": "2025-11-30T10:30:45"
      }
    }
    ```

    **监控停止状态响应**:
    ```json
    {
      "success": true,
      "data": {
        "is_monitoring": false,
        "monitored_symbols": [],
        "monitored_count": 0
      }
    }
    ```

    **注意事项**:
    - 该端点不需要认证即可访问（用于健康检查）
    - 频繁调用不会影响监控性能
    - 返回的股票列表可能很长，建议配合分页展示
    - 监控状态变更后立即生效
    - 配合 /control/start 和 /control/stop 端点使用
    """
    try:
        return create_unified_success_response(
            data=_monitoring_control_service.get_status(),
            message="获取监控状态成功",
        ).model_dump()
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")
