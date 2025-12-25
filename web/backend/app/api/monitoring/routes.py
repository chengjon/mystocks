"""
监控系统API路由 (Phase 2.4.2 - SSE Streaming Support)

提供实时监控告警的SSE流式推送功能。

版本: 2.4.0
日期: 2025-12-24
更新内容:
- 添加 /api/monitoring/alerts/stream SSE端点
- 添加 /api/monitoring/alerts/summary/stream SSE端点
- 集成SSE管理器
- Phase 2.4.4: 更新健康检查为统一响应格式
"""

import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.core.responses import create_health_response, create_success_response

router = APIRouter(prefix="/monitoring")


@router.get("/health")
async def health_check():
    """
    健康检查 (Phase 2.4.4: 更新为统一响应格式)

    Returns:
        统一格式的健康检查响应
    """
    return create_health_response(
        service="monitoring",
        status="healthy",
        details={
            "sse_channels": ["monitoring_alerts", "alert_summary"],
            "version": "2.4.0",
        },
    )


@router.get("/status")
async def get_status():
    """
    获取服务状态 (Phase 2.4.4: 更新为统一响应格式)

    Returns:
        统一格式的状态响应
    """
    from app.core.sse_manager import get_sse_manager

    manager = get_sse_manager()

    return create_unified_success_response(
        data={
            "status": "active",
            "endpoint": "monitoring",
            "sse_connections": {
                "monitoring_alerts": manager.get_connection_count("monitoring_alerts"),
                "alert_summary": manager.get_connection_count("alert_summary"),
                "total": manager.get_connection_count(),
            },
        },
        message="监控服务运行中",
    )


@router.post("/analyze")
async def analyze_data(data: dict):
    """
    监控数据AI智能分析

    使用AI模型对实时监控数据进行智能分析，识别异常行为和市场风险。
    该端点专注于监控告警数据的深度分析，提供风险预警和投资建议。

    **功能说明**:
    - AI驱动的监控数据异常检测
    - 识别价格异常波动和成交量异常
    - 分析龙虎榜数据和资金流向
    - 生成风险评估和预警信号
    - 检测市场操纵行为特征
    - 提供多维度的监控分析结果

    **使用场景**:
    - 实时监控告警的智能筛选
    - 异常交易行为识别
    - 资金流向分析和主力动向追踪
    - 市场风险评估和预警
    - 涨跌停板监控分析
    - 龙虎榜数据智能解读

    **请求参数**:
    - alert_type (可选): 告警类型（limit_up/limit_down/volume_spike）
    - symbols (可选): 股票代码列表
    - time_range (可选): 时间范围（1h/1d/1w）
    - analysis_type (可选): 分析类型（anomaly/risk/flow）
    - sensitivity (可选): 灵敏度（low/medium/high）

    **返回值**:
    - result: 分析结果描述
    - endpoint: 服务端点标识
    - anomalies (可选): 检测到的异常列表
      - symbol: 股票代码
      - anomaly_type: 异常类型
      - severity: 严重程度
      - description: 异常描述
    - risk_level (可选): 风险等级（low/medium/high/critical）
    - recommendations (可选): AI建议列表

    **示例**:
    ```bash
    # 监控数据异常分析
    curl -X POST "http://localhost:8000/api/monitoring/analyze" \\
      -H "Content-Type: application/json" \\
      -d '{
        "alert_type": "volume_spike",
        "symbols": ["600519", "000001"],
        "time_range": "1d",
        "analysis_type": "anomaly",
        "sensitivity": "high"
      }'
    ```

    **响应示例**:
    ```json
    {
      "result": "分析完成",
      "endpoint": "monitoring",
      "anomalies": [
        {
          "symbol": "600519",
          "anomaly_type": "volume_spike",
          "severity": "high",
          "description": "成交量突增300%，疑似重大利好消息"
        }
      ],
      "risk_level": "medium",
      "recommendations": [
        "建议关注该股后续资金流向",
        "注意主力资金是否持续流入"
      ]
    }
    ```

    **注意事项**:
    - 当前版本为开发中状态，返回模拟结果
    - AI分析基于历史模式，不能预测未来
    - 异常检测可能存在误报，需人工复核
    - 建议结合多个数据源综合判断
    - 高频调用可能影响系统性能
    - 分析结果的准确性受数据完整性影响
    """
    # TODO: 实现AI分析逻辑
    return {"result": "分析完成", "endpoint": "monitoring"}


# ============================================================================
# SSE 实时推送端点 (Phase 2.4.2 - 新增)
# ============================================================================


@router.get("/alerts/stream")
async def sse_alerts_stream(
    request: Request,
    client_id: Optional[str] = None,
):
    """
    SSE endpoint for real-time alert notifications (Phase 2.4.2 - 新增)

    提供实时的告警推送服务，使用Server-Sent Events (SSE)协议。

    **Event Types:**
    - `connected`: 初始连接确认
    - `alert`: 新告警通知
    - `alert_updated`: 告警状态更新
    - `ping`: 心跳保活 (每30秒)

    **Alert Event Data Structure:**
    ```json
    {
        "event": "alert",
        "data": {
            "alert_id": 123,
            "alert_type": "limit_up",
            "severity": "high",
            "symbol": "600519",
            "stock_name": "贵州茅台",
            "message": "贵州茅台涨停",
            "created_at": "2025-12-24T10:30:00",
            "is_read": false
        },
        "timestamp": "2025-12-24T10:30:00"
    }
    ```

    **Example (JavaScript):**
    ```javascript
    const eventSource = new EventSource('/api/monitoring/alerts/stream');

    eventSource.addEventListener('connected', (event) => {
        const data = JSON.parse(event.data);
        console.log('Connected:', data.client_id);
    });

    eventSource.addEventListener('alert', (event) => {
        const alert = JSON.parse(event.data);
        showNotification(alert);
    });

    eventSource.addEventListener('error', () => {
        console.error('SSE connection error');
        eventSource.close();
    });
    ```
    """
    from app.core.sse_manager import get_sse_manager

    async def monitoring_alerts_generator():
        """监控告警SSE生成器"""
        manager = get_sse_manager()
        client, queue = await manager.connect("monitoring_alerts", client_id)

        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {
                        "event": event.event,
                        "data": event.data,
                        "id": event.id,
                    }
                except asyncio.TimeoutError:
                    # 发送心跳保活
                    yield {
                        "event": "ping",
                        "data": {
                            "channel": "monitoring_alerts",
                            "timestamp": datetime.now().isoformat(),
                        },
                    }

        finally:
            await manager.disconnect("monitoring_alerts", client)

    return EventSourceResponse(
        monitoring_alerts_generator,
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # 禁用nginx缓冲
        },
    )


@router.get("/alerts/summary/stream")
async def sse_alerts_summary_stream(
    request: Request,
    client_id: Optional[str] = None,
):
    """
    SSE endpoint for alert summary updates (Phase 2.4.2 - 新增)

    推送告警摘要的实时更新，包括未读告警数量、各级别告警统计等。

    **Event Types:**
    - `connected`: 初始连接确认
    - `summary_updated`: 告警摘要更新
    - `ping`: 心跳保活 (每30秒)

    **Summary Event Data Structure:**
    ```json
    {
        "event": "summary_updated",
        "data": {
            "total_alerts": 150,
            "unread_count": 12,
            "critical_count": 2,
            "high_count": 5,
            "warning_count": 8,
            "info_count": 135,
            "last_update": "2025-12-24T10:30:00"
        },
        "timestamp": "2025-12-24T10:30:00"
    }
    ```
    """
    from app.core.sse_manager import get_sse_manager

    async def alert_summary_generator():
        """告警摘要SSE生成器"""
        manager = get_sse_manager()
        client, queue = await manager.connect("alert_summary", client_id)

        try:
            # 发送初始摘要
            yield {
                "event": "summary_updated",
                "data": {
                    "total_alerts": 0,
                    "unread_count": 0,
                    "critical_count": 0,
                    "high_count": 0,
                    "warning_count": 0,
                    "info_count": 0,
                    "last_update": datetime.now().isoformat(),
                },
            }

            while True:
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {
                        "event": event.event,
                        "data": event.data,
                        "id": event.id,
                    }
                except asyncio.TimeoutError:
                    # 定期发送摘要更新
                    yield {
                        "event": "summary_updated",
                        "data": {
                            "total_alerts": 0,
                            "unread_count": 0,
                            "last_update": datetime.now().isoformat(),
                        },
                    }

        finally:
            await manager.disconnect("alert_summary", client)

    return EventSourceResponse(
        alert_summary_generator,
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# 用于外部调用的告警广播函数
async def broadcast_monitoring_alert(
    alert_type: str,
    severity: str,
    symbol: str,
    message: str,
):
    """
    广播监控告警到所有连接的SSE客户端

    Args:
        alert_type: 告警类型 (limit_up, limit_down, etc.)
        severity: 严重级别 (info, warning, high, critical)
        symbol: 股票代码
        message: 告警消息
    """
    from app.core.sse_manager import SSEEvent, get_sse_manager
    import uuid

    manager = get_sse_manager()

    # 广播到告警频道
    await manager.broadcast(
        "monitoring_alerts",
        SSEEvent(
            event="alert",
            data={
                "alert_type": alert_type,
                "severity": severity,
                "symbol": symbol,
                "message": message,
                "created_at": datetime.now().isoformat(),
            },
            id=str(uuid.uuid4()),
        ),
    )

    # 同时更新摘要
    await manager.broadcast(
        "alert_summary",
        SSEEvent(
            event="summary_updated",
            data={"timestamp": datetime.now().isoformat()},
            id=str(uuid.uuid4()),
        ),
    )


__all__ = ["router", "broadcast_monitoring_alert"]
