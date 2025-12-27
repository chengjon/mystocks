"""
监控系统 API 端点
Real-time Monitoring System
"""

import os
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.security import get_current_user, User
from app.mock.unified_mock_data import get_mock_data_manager
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
from app.services.monitoring_service import monitoring_service

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


# ============================================================================
# 告警规则管理
# ============================================================================


@router.get("/alert-rules", response_model=List[AlertRuleResponse])
async def get_alert_rules(
    rule_type: Optional[AlertRuleType] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
):
    """
    获取告警规则列表

    参数:
    - rule_type: 规则类型 (可选)
    - is_active: 是否启用 (可选)
    """
    try:
        rules = monitoring_service.get_alert_rules(
            rule_type=rule_type.value if rule_type else None, is_active=is_active
        )
        return [AlertRuleResponse.from_orm(rule) for rule in rules]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alert-rules", response_model=AlertRuleResponse)
async def create_alert_rule(rule: AlertRuleCreate, current_user: User = Depends(get_current_user)):
    """
    创建告警规则

    示例:
    ```json
    {
      "rule_name": "茅台涨停监控",
      "rule_type": "limit_up",
      "symbol": "600519",
      "stock_name": "贵州茅台",
      "parameters": {"include_st": false},
      "notification_config": {"channels": ["ui", "sound"], "level": "warning"},
      "priority": 5,
      "is_active": true
    }
    ```
    """
    try:
        rule_data = rule.dict()
        created_rule = monitoring_service.create_alert_rule(rule_data)
        return AlertRuleResponse.from_orm(created_rule)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/alert-rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(rule_id: int, updates: AlertRuleUpdate, current_user: User = Depends(get_current_user)):
    """
    更新告警规则

    参数:
    - rule_id: 规则ID
    - updates: 要更新的字段
    """
    try:
        update_data = updates.dict(exclude_unset=True)
        updated_rule = monitoring_service.update_alert_rule(rule_id, update_data)
        return AlertRuleResponse.from_orm(updated_rule)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/alert-rules/{rule_id}")
async def delete_alert_rule(rule_id: int, current_user: User = Depends(get_current_user)):
    """
    删除告警规则

    参数:
    - rule_id: 规则ID
    """
    try:
        success = monitoring_service.delete_alert_rule(rule_id)
        return {"success": success, "message": "告警规则已删除"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# 告警记录查询
# ============================================================================


class AlertRecordsResponse(BaseModel):
    """告警记录列表响应"""

    success: bool = True
    data: List[AlertRecordResponse]
    total: int
    limit: int
    offset: int


@router.get("/alerts", response_model=AlertRecordsResponse)
async def get_alert_records(
    symbol: Optional[str] = None,
    alert_type: Optional[str] = None,
    alert_level: Optional[AlertLevel] = None,
    is_read: Optional[bool] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
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
    try:
        records, total = monitoring_service.get_alert_records(
            symbol=symbol,
            alert_type=alert_type,
            alert_level=alert_level.value if alert_level else None,
            is_read=is_read,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

        return AlertRecordsResponse(
            data=[AlertRecordResponse.from_orm(r) for r in records],
            total=total,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/mark-read")
async def mark_alert_read(alert_id: int, current_user: User = Depends(get_current_user)):
    """
    标记告警为已读

    参数:
    - alert_id: 告警记录ID
    """
    try:
        success = monitoring_service.mark_alert_read(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="告警记录不存在")
        return {"success": True, "message": "已标记为已读"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/mark-all-read")
async def mark_all_alerts_read(current_user: User = Depends(get_current_user)):
    """批量标记所有未读告警为已读"""
    try:
        # TODO: 实现批量标记功能
        return {"success": True, "message": "功能开发中"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 实时监控数据
# ============================================================================


@router.get("/realtime/{symbol}", response_model=RealtimeMonitoringResponse)
async def get_realtime_monitoring(symbol: str, current_user: User = Depends(get_current_user)):
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
                raise HTTPException(status_code=404, detail="未找到该股票的监控数据")

            return RealtimeMonitoringResponse.from_orm(record)
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/realtime", response_model=List[RealtimeMonitoringResponse])
async def get_realtime_monitoring_list(
    symbols: Optional[str] = Query(None, description="逗号分隔的股票代码列表"),
    limit: int = Query(100, ge=1, le=1000),
    is_limit_up: Optional[bool] = None,
    is_limit_down: Optional[bool] = None,
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

            return [RealtimeMonitoringResponse.from_orm(r) for r in records]
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/realtime/fetch")
async def fetch_realtime_data(symbols: Optional[List[str]] = None, current_user: User = Depends(get_current_user)):
    """
    手动触发获取实时数据

    参数:
    - symbols: 股票代码列表 (可选，不提供则获取全市场)

    示例:
    ```json
    {
      "symbols": ["600519", "000001", "600000"]
    }
    ```
    """
    try:
        df = monitoring_service.fetch_realtime_data(symbols)
        if df.empty:
            return {"success": False, "message": "未获取到数据"}

        # 保存数据
        count = monitoring_service.save_realtime_data(df)

        # 评估告警规则
        alerts = monitoring_service.evaluate_alert_rules(df)

        return {
            "success": True,
            "message": "实时数据获取成功",
            "data": {
                "stocks_count": len(df),
                "saved_count": count,
                "alerts_triggered": len(alerts),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 龙虎榜数据
# ============================================================================


@router.get("/dragon-tiger", response_model=List[DragonTigerListResponse])
async def get_dragon_tiger_list(
    trade_date: Optional[date] = None,
    symbol: Optional[str] = None,
    min_net_amount: Optional[float] = None,
    limit: int = Query(100, ge=1, le=500),
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

            return [DragonTigerListResponse.from_orm(r) for r in records]
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dragon-tiger/fetch")
async def fetch_dragon_tiger_data(trade_date: Optional[date] = None, current_user: User = Depends(get_current_user)):
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
            return {"success": False, "message": f"{trade_date} 无龙虎榜数据"}

        count = monitoring_service.save_dragon_tiger_data(df, trade_date)

        return {
            "success": True,
            "message": "龙虎榜数据获取成功",
            "data": {"trade_date": trade_date.isoformat(), "count": count},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 监控摘要和统计
# ============================================================================


@router.get("/summary", response_model=MonitoringSummaryResponse)
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
        # 检查是否使用Mock数据
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        if use_mock:
            # 使用Mock数据
            mock_manager = get_mock_data_manager()
            monitoring_data = mock_manager.get_data("monitoring", alert_type="all")

            # 构建返回的监控摘要数据
            summary = {
                "total_stocks": 1568,
                "limit_up_count": 23,
                "limit_down_count": 5,
                "strong_up_count": 127,
                "strong_down_count": 89,
                "avg_change_percent": 0.85,
                "total_amount": 2456789000.0,
                "active_alerts": 12,
                "unread_alerts": 5,
            }
            return MonitoringSummaryResponse(**summary)
        else:
            # 使用真实数据库
            summary = monitoring_service.get_monitoring_summary()
            return MonitoringSummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/today")
async def get_today_statistics(current_user: User = Depends(get_current_user)):
    """获取今日统计数据"""
    try:
        session = monitoring_service.get_session()
        try:
            # 使用视图查询
            from sqlalchemy import text

            # 今日告警摘要
            alerts_summary = session.execute(text("SELECT * FROM v_today_alerts_summary")).fetchall()

            # 活跃规则
            active_rules = session.execute(text("SELECT * FROM v_active_alert_rules LIMIT 10")).fetchall()

            # 实时监控摘要
            realtime_summary = session.execute(text("SELECT * FROM v_realtime_summary")).fetchone()

            return {
                "success": True,
                "data": {
                    "alerts_summary": [dict(row._mapping) for row in alerts_summary],
                    "active_rules": [dict(row._mapping) for row in active_rules],
                    "realtime_summary": (dict(realtime_summary._mapping) if realtime_summary else {}),
                },
            }
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 监控控制
# ============================================================================


class MonitoringControlRequest(BaseModel):
    """监控控制请求"""

    symbols: Optional[List[str]] = None
    interval: int = 60  # 更新间隔(秒)


@router.post("/control/start")
async def start_monitoring(request: MonitoringControlRequest, current_user: User = Depends(get_current_user)):
    """
    启动监控

    参数:
    - symbols: 要监控的股票代码列表 (可选，不提供则监控全市场)
    - interval: 更新间隔(秒)，默认60秒
    """
    try:
        # 这里应该在后台启动监控任务
        # 实际应该使用 Celery 或 BackgroundTasks
        return {
            "success": True,
            "message": "监控启动功能开发中",
            "data": {"symbols": request.symbols, "interval": request.interval},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/control/stop")
async def stop_monitoring(current_user: User = Depends(get_current_user)):
    """停止监控"""
    try:
        monitoring_service.stop_monitoring()
        return {"success": True, "message": "监控已停止"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/control/status")
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
    curl -X GET "http://localhost:8000/api/monitoring/control/status"
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
        return {
            "success": True,
            "data": {
                "is_monitoring": monitoring_service.is_monitoring,
                "monitored_symbols": monitoring_service.monitored_symbols,
                "monitored_count": len(monitoring_service.monitored_symbols),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
