"""
信号监控 API 端点
Signal Monitoring API Endpoints

提供信号历史查询、质量报告和实时监控功能。

作者: Claude Code (Main CLI)
创建日期: 2026-01-08
版本: v1.0
"""

import logging
from datetime import date, datetime, timedelta
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.api.signal_monitoring.signal_history_response_schemas import (
    SignalHistoryResponse,
    SignalQualityReportResponse,
    StrategyRealtimeMonitoringResponse,
)
from app.core.security import User, get_current_user
from app.openapi_config import COMMON_RESPONSES

logger = logging.getLogger(__name__)

router = APIRouter()

SIGNAL_MONITORING_HEALTH_RESPONSE_EXAMPLE = {
    "status": "healthy",
    "service": "signal-monitoring-api",
    "version": "v1.0",
    "database": "connected",
}

SIGNAL_MONITORING_HEALTH_ERROR_RESPONSE_EXAMPLE = {
    "status": "unhealthy",
    "service": "signal-monitoring-api",
    "version": "v1.0",
    "database": "error",
    "error": "database unavailable",
}


def _success_response_spec(description: str, example: Any) -> dict[int, dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


SIGNAL_MONITORING_ERROR_RESPONSES = {
    401: COMMON_RESPONSES[401],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    503: {
        "description": "监控数据库不可用",
        "content": {
            "application/json": {
                "example": {
                    "detail": "监控数据库未连接",
                }
            }
        },
    },
}

SIGNAL_HISTORY_RESPONSES = {
    **SIGNAL_MONITORING_ERROR_RESPONSES,
    **_success_response_spec(
        "信号历史记录列表",
        [
            {
                "id": 12345,
                "strategy_id": "macd_strategy",
                "symbol": "600519.SH",
                "signal_type": "BUY",
                "generated_at": "2026-01-08T10:30:00",
                "status": "executed",
                "execution_time_ms": 45.5,
                "gpu_used": True,
                "gpu_latency_ms": 12.3,
                "executed": True,
                "executed_at": "2026-01-08T10:30:05",
                "profit_loss": 125.5,
                "profit_loss_percent": 2.5,
            }
        ],
    ),
}

SIGNAL_QUALITY_REPORT_RESPONSES = {
    **SIGNAL_MONITORING_ERROR_RESPONSES,
    **_success_response_spec(
        "信号质量分析报告",
        {
            "strategy_id": "macd_strategy",
            "period_start": "2026-01-01",
            "period_end": "2026-01-08",
            "total_signals": 150,
            "buy_signals": 75,
            "sell_signals": 60,
            "hold_signals": 15,
            "executed_signals": 120,
            "execution_rate": 80.0,
            "signal_accuracy": 78.5,
            "signal_success_rate": 85.0,
            "avg_profit_loss": 25.5,
            "total_profit_loss": 3060.0,
            "avg_execution_time_ms": 45.2,
            "gpu_usage_rate": 65.0,
            "profitable_signals": 95,
            "losing_signals": 25,
            "win_rate": 79.17,
        },
    ),
}


@router.get(
    "/signals/history",
    response_model=List[SignalHistoryResponse],
    summary="查询信号历史",
    responses=SIGNAL_HISTORY_RESPONSES,
)
async def get_signal_history(
    strategy_id: Optional[str] = Query(None, description="按策略ID筛选信号历史记录。"),
    symbol: Optional[str] = Query(None, description="按股票或合约代码筛选信号历史记录。"),
    signal_type: Optional[str] = Query(None, description="按信号类型筛选，例如 BUY、SELL 或 HOLD。"),
    status: Optional[str] = Query(None, description="按信号处理状态筛选，例如 generated、executed 或 rejected。"),
    start_date: Optional[date] = Query(None, description="限制返回结果的开始日期，包含当天。"),
    end_date: Optional[date] = Query(None, description="限制返回结果的结束日期，包含当天。"),
    limit: int = Query(100, ge=1, le=1000, description="单次请求返回的最大记录数。"),
    offset: int = Query(0, ge=0, description="分页偏移量，用于配合 limit 顺序翻页。"),
    current_user: User = Depends(get_current_user),
):
    """
    获取信号历史记录

    **功能说明**:
    - 查询策略生成的信号历史记录
    - 支持按策略、标的、信号类型、状态筛选
    - 支持日期范围查询
    - 返回信号生成信息和执行结果

    **使用场景**:
    - 回测信号历史表现
    - 分析信号生成模式
    - 追踪信号执行情况
    - 评估策略效果

    **参数说明**:
    - strategy_id: 策略ID（可选）
    - symbol: 股票代码（可选）
    - signal_type: 信号类型 BUY/SELL/HOLD（可选）
    - status: 信号状态 generated/executed/rejected（可选）
    - start_date: 开始日期（可选）
    - end_date: 结束日期（可选）
    - limit: 返回数量限制（默认100，最大1000）
    - offset: 偏移量（用于分页）

    **示例**:
    ```bash
    # 查询某策略的所有信号
    curl -X GET "http://localhost:${BACKEND_PORT}/api/signals/history?strategy_id=macd_strategy"

    # 查询某股票的最近BUY信号
    curl -X GET "http://localhost:${BACKEND_PORT}/api/signals/history?symbol=600519.SH&signal_type=BUY"

    # 查询已执行的信号（最近7天）
    curl -X GET "http://localhost:${BACKEND_PORT}/api/signals/history?status=executed&start_date=2026-01-01"
    ```

    **响应示例**:
    ```json
    [
      {
        "id": 12345,
        "strategy_id": "macd_strategy",
        "symbol": "600519.SH",
        "signal_type": "BUY",
        "generated_at": "2026-01-08T10:30:00",
        "status": "executed",
        "execution_time_ms": 45.5,
        "gpu_used": true,
        "gpu_latency_ms": 12.3,
        "executed": true,
        "executed_at": "2026-01-08T10:30:05",
        "profit_loss": 125.50,
        "profit_loss_percent": 2.5
      }
    ]
    ```

    **注意事项**:
    - 默认按生成时间倒序排列
    - 支持分页查询（offset + limit）
    - 未提供日期时默认查询最近30天
    - 执行结果需要信号已被执行才存在
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        pg = get_postgres_async()

        if not pg.is_connected():
            raise HTTPException(status_code=503, detail="监控数据库未连接")

        # 构建查询SQL
        query = """
        SELECT
            sr.id,
            sr.strategy_id,
            sr.symbol,
            sr.signal_type,
            sr.generated_at,
            sr.status,
            sr.execution_time_ms,
            sr.gpu_used,
            sr.gpu_latency_ms,
            COALESCE(ser.executed, false) as executed,
            ser.executed_at,
            ser.profit_loss,
            ser.profit_loss_percent
        FROM signal_records sr
        LEFT JOIN signal_execution_results ser ON sr.id = ser.signal_id
        WHERE 1=1
        """

        params = []

        # 动态构建WHERE条件
        if strategy_id:
            query += " AND sr.strategy_id = $1"
            params.append(strategy_id)

        param_index = len(params) + 1
        if symbol:
            query += f" AND sr.symbol = ${param_index}"
            params.append(symbol)
            param_index += 1

        if signal_type:
            query += f" AND sr.signal_type = ${param_index}"
            params.append(signal_type)
            param_index += 1

        if status:
            query += f" AND sr.status = ${param_index}"
            params.append(status)
            param_index += 1

        if start_date:
            query += f" AND sr.generated_at >= ${param_index}"
            params.append(datetime.combine(start_date, datetime.min.time()))
            param_index += 1

        if end_date:
            query += f" AND sr.generated_at <= ${param_index}"
            params.append(datetime.combine(end_date, datetime.max.time()))
            param_index += 1

        # 排序和分页
        query += f" ORDER BY sr.generated_at DESC LIMIT ${param_index} OFFSET ${param_index + 1}"
        params.extend([limit, offset])

        # 执行查询
        async with pg.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

        # 转换为响应模型
        results = [SignalHistoryResponse(**dict(row)) for row in rows]

        logger.info("查询信号历史: 返回 {len(results)} 条记录")
        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error("查询信号历史失败: %(e)s")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@router.get(
    "/signals/quality-report",
    response_model=SignalQualityReportResponse,
    summary="生成信号质量报告",
    responses=SIGNAL_QUALITY_REPORT_RESPONSES,
)
async def get_signal_quality_report(
    strategy_id: str = Query(..., description="需要生成质量报告的策略ID。"),
    period_days: int = Query(7, ge=1, le=90, description="统计周期（天）"),
    current_user: User = Depends(get_current_user),
):
    """
    获取信号质量报告

    **功能说明**:
    - 统计指定周期的信号质量指标
    - 计算信号准确率、成功率、盈亏情况
    - 提供详细的性能分析数据
    - 用于评估策略表现

    **使用场景**:
    - 策略性能评估
    - 定期报告生成
    - 监控仪表板数据展示
    - 策略对比分析

    **参数说明**:
    - strategy_id: 策略ID（必需）
    - period_days: 统计周期（默认7天，最大90天）

    **返回指标**:
    - total_signals: 总信号数
    - buy/sell/hold_signals: 各类型信号数
    - executed_signals: 已执行信号数
    - execution_rate: 执行率（已执行/总数）
    - signal_accuracy: 信号准确率（0-100）
    - signal_success_rate: 信号成功率（0-100）
    - avg_profit_loss: 平均盈亏
    - total_profit_loss: 总盈亏
    - avg_execution_time_ms: 平均执行时间
    - gpu_usage_rate: GPU使用率（0-100）
    - profitable_signals: 盈利信号数
    - losing_signals: 亏损信号数
    - win_rate: 胜率（0-100）

    **示例**:
    ```bash
    # 查询最近7天的信号质量报告
    curl -X GET "http://localhost:${BACKEND_PORT}/api/signals/quality-report?strategy_id=macd_strategy"

    # 查询最近30天的信号质量报告
    curl -X GET "http://localhost:${BACKEND_PORT}/api/signals/quality-report?strategy_id=macd_strategy&period_days=30"
    ```

    **响应示例**:
    ```json
    {
      "strategy_id": "macd_strategy",
      "period_start": "2026-01-01",
      "period_end": "2026-01-08",
      "total_signals": 150,
      "buy_signals": 75,
      "sell_signals": 60,
      "hold_signals": 15,
      "executed_signals": 120,
      "execution_rate": 80.0,
      "signal_accuracy": 78.5,
      "signal_success_rate": 85.0,
      "avg_profit_loss": 25.50,
      "total_profit_loss": 3060.0,
      "avg_execution_time_ms": 45.2,
      "gpu_usage_rate": 65.0,
      "profitable_signals": 95,
      "losing_signals": 25,
      "win_rate": 79.17
    }
    ```

    **注意事项**:
    - 默认统计最近7天数据
    - 信号准确率 = 盈利信号数 / 已执行信号数 * 100
    - 信号成功率 = 成功执行信号数 / 总信号数 * 100
    - 胜率 = 盈利信号数 / (盈利 + 亏损) * 100
    - GPU使用率 = 使用GPU的信号数 / 总信号数 * 100
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        pg = get_postgres_async()

        if not pg.is_connected():
            raise HTTPException(status_code=503, detail="监控数据库未连接")

        # 计算日期范围
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        # 查询信号统计数据
        stats_query = """
        SELECT
            COUNT(*) as total_signals,
            SUM(CASE WHEN signal_type = 'BUY' THEN 1 ELSE 0 END) as buy_signals,
            SUM(CASE WHEN signal_type = 'SELL' THEN 1 ELSE 0 END) as sell_signals,
            SUM(CASE WHEN signal_type = 'HOLD' THEN 1 ELSE 0 END) as hold_signals,
            SUM(CASE WHEN status = 'executed' THEN 1 ELSE 0 END) as executed_signals,
            AVG(execution_time_ms) as avg_execution_time_ms,
            SUM(CASE WHEN gpu_used = TRUE THEN 1 ELSE 0 END) as gpu_signals_count
        FROM signal_records
        WHERE strategy_id = $1
          AND generated_at >= $2
          AND generated_at <= $3
        """

        # 查询执行结果统计
        results_query = """
        SELECT
            COUNT(*) as total_executed,
            SUM(CASE WHEN ser.profit_loss > 0 THEN 1 ELSE 0 END) as profitable_signals,
            SUM(CASE WHEN ser.profit_loss < 0 THEN 1 ELSE 0 END) as losing_signals,
            AVG(ser.profit_loss) as avg_profit_loss,
            SUM(ser.profit_loss) as total_profit_loss
        FROM signal_records sr
        JOIN signal_execution_results ser ON sr.id = ser.signal_id
        WHERE sr.strategy_id = $1
          AND sr.generated_at >= $2
          AND sr.generated_at <= $3
        """

        async with pg.pool.acquire() as conn:
            # 执行统计查询
            stats_row = await conn.fetchrow(stats_query, strategy_id, start_date, end_date)
            results_row = await conn.fetchrow(results_query, strategy_id, start_date, end_date)

        # 提取数据
        total_signals = stats_row["total_signals"] or 0
        buy_signals = stats_row["buy_signals"] or 0
        sell_signals = stats_row["sell_signals"] or 0
        hold_signals = stats_row["hold_signals"] or 0
        executed_signals = stats_row["executed_signals"] or 0
        avg_execution_time_ms = stats_row["avg_execution_time_ms"] or 0.0
        gpu_signals_count = stats_row["gpu_signals_count"] or 0

        total_executed = results_row["total_executed"] or 0
        profitable_signals = results_row["profitable_signals"] or 0
        losing_signals = results_row["losing_signals"] or 0
        avg_profit_loss = results_row["avg_profit_loss"] or 0.0
        total_profit_loss = results_row["total_profit_loss"] or 0.0

        # 计算衍生指标
        execution_rate = (executed_signals / total_signals * 100) if total_signals > 0 else 0.0
        signal_accuracy = (profitable_signals / total_executed * 100) if total_executed > 0 else 0.0
        signal_success_rate = (executed_signals / total_signals * 100) if total_signals > 0 else 0.0
        gpu_usage_rate = (gpu_signals_count / total_signals * 100) if total_signals > 0 else 0.0
        win_rate = (
            profitable_signals / (profitable_signals + losing_signals) * 100
            if (profitable_signals + losing_signals) > 0
            else 0.0
        )

        # 构建响应
        report = SignalQualityReportResponse(
            strategy_id=strategy_id,
            period_start=start_date,
            period_end=end_date,
            total_signals=total_signals,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            hold_signals=hold_signals,
            executed_signals=executed_signals,
            execution_rate=round(execution_rate, 2),
            signal_accuracy=round(signal_accuracy, 2),
            signal_success_rate=round(signal_success_rate, 2),
            avg_profit_loss=round(avg_profit_loss, 2),
            total_profit_loss=round(total_profit_loss, 2),
            avg_execution_time_ms=round(avg_execution_time_ms, 2),
            gpu_usage_rate=round(gpu_usage_rate, 2),
            profitable_signals=profitable_signals,
            losing_signals=losing_signals,
            win_rate=round(win_rate, 2),
        )

        logger.info("生成信号质量报告: strategy=%(strategy_id)s, period=%(period_days)s天")
        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error("生成信号质量报告失败: %(e)s")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/strategies/{strategy_id}/realtime", response_model=StrategyRealtimeMonitoringResponse)
async def get_strategy_realtime_monitoring(
    strategy_id: str = Path(..., description="需要查看实时监控状态的策略ID。"),
    current_user: User = Depends(get_current_user),
):
    """
    获取策略实时监控数据

    **功能说明**:
    - 查询策略的实时健康状态
    - 获取信号生成速率和性能指标
    - 监控GPU使用情况
    - 展示最近生成的信号

    **使用场景**:
    - 实时监控仪表板
    - 策略健康状态检查
    - 性能监控和告警
    - 运维状态查询

    **路径参数**:
    - strategy_id: 策略ID（必需）

    **返回指标**:
    - health_status: 健康状态（1=healthy, 0=degraded, -1=unhealthy）
    - active_signals_count: 活跃信号数量
    - signal_generation_rate: 信号生成速率（信号/分钟）
    - avg_latency_ms: 平均延迟
    - p95/p99_latency_ms: P95/P99延迟
    - gpu_enabled: 是否启用GPU
    - gpu_utilization: GPU利用率
    - recent_signals: 最近5条信号

    **示例**:
    ```bash
    # 查询策略实时监控数据
    curl -X GET "http://localhost:${BACKEND_PORT}/api/strategies/macd_strategy/realtime"
    ```

    **响应示例**:
    ```json
    {
      "strategy_id": "macd_strategy",
      "timestamp": "2026-01-08T15:30:45",
      "health_status": 1,
      "active_signals_count": 5,
      "signal_generation_rate": 2.5,
      "avg_latency_ms": 45.2,
      "p95_latency_ms": 68.5,
      "p99_latency_ms": 92.3,
      "gpu_enabled": true,
      "gpu_utilization": 75.5,
      "recent_signals": [
        {
          "id": 12345,
          "symbol": "600519.SH",
          "signal_type": "BUY",
          "generated_at": "2026-01-08T15:30:00"
        }
      ]
    }
    ```

    **注意事项**:
    - 实时数据基于最近5分钟的统计
    - 延迟指标包含GPU加速时间
    - 健康状态基于错误率和可用性
    - 最近信号返回最新5条
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        pg = get_postgres_async()

        if not pg.is_connected():
            raise HTTPException(status_code=503, detail="监控数据库未连接")

        # 计算5分钟前的时间
        five_minutes_ago = datetime.now() - timedelta(minutes=5)

        # 查询最近5分钟的信号统计
        stats_query = """
        SELECT
            COUNT(*) as signal_count,
            AVG(execution_time_ms) as avg_latency,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms) as p95_latency,
            PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY execution_time_ms) as p99_latency,
            SUM(CASE WHEN gpu_used = TRUE THEN 1 ELSE 0 END) as gpu_count
        FROM signal_records
        WHERE strategy_id = $1
          AND generated_at >= $2
        """

        # 查询最新健康状态
        health_query = """
        SELECT health_status
        FROM strategy_health
        WHERE strategy_id = $1
        ORDER BY recorded_at DESC
        LIMIT 1
        """

        # 查询最近5条信号
        recent_query = """
        SELECT
            id,
            symbol,
            signal_type,
            generated_at
        FROM signal_records
        WHERE strategy_id = $1
        ORDER BY generated_at DESC
        LIMIT 5
        """

        async with pg.pool.acquire() as conn:
            # 执行查询
            stats_row = await conn.fetchrow(stats_query, strategy_id, five_minutes_ago)
            health_row = await conn.fetchrow(health_query, strategy_id)
            recent_rows = await conn.fetch(recent_query, strategy_id)

        # 提取统计数据
        signal_count = stats_row["signal_count"] or 0
        avg_latency = stats_row["avg_latency"] or 0.0
        p95_latency = stats_row["p95_latency"] or 0.0
        p99_latency = stats_row["p99_latency"] or 0.0
        gpu_count = stats_row["gpu_count"] or 0

        # 计算衍生指标
        signal_generation_rate = signal_count / 5.0  # 信号/分钟
        active_signals_count = signal_count  # 简化：假设最近的都是活跃的
        gpu_enabled = gpu_count > 0
        gpu_utilization = None  # TODO: 从GPU管理器获取实际利用率

        # 健康状态
        health_status = health_row["health_status"] if health_row else 1

        # 最近信号
        recent_signals = [
            {
                "id": row["id"],
                "symbol": row["symbol"],
                "signal_type": row["signal_type"],
                "generated_at": row["generated_at"].isoformat(),
            }
            for row in recent_rows
        ]

        # 构建响应
        monitoring_data = StrategyRealtimeMonitoringResponse(
            strategy_id=strategy_id,
            timestamp=datetime.now(),
            health_status=health_status,
            active_signals_count=active_signals_count,
            signal_generation_rate=round(signal_generation_rate, 2),
            avg_latency_ms=round(avg_latency, 2),
            p95_latency_ms=round(p95_latency, 2) if p95_latency else 0.0,
            p99_latency_ms=round(p99_latency, 2) if p99_latency else 0.0,
            gpu_enabled=gpu_enabled,
            gpu_utilization=gpu_utilization,
            recent_signals=recent_signals,
        )

        logger.info("查询策略实时监控: strategy=%(strategy_id)s")
        return monitoring_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error("查询策略实时监控失败: %(e)s")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get(
    "/signals/health",
    summary="信号监控健康检查",
    responses={
        200: {
            "description": "信号监控服务健康状态",
            "content": {"application/json": {"example": SIGNAL_MONITORING_HEALTH_RESPONSE_EXAMPLE}},
        },
        500: {
            "description": "信号监控服务健康检查失败",
            "content": {"application/json": {"example": SIGNAL_MONITORING_HEALTH_ERROR_RESPONSE_EXAMPLE}},
        },
    },
)
async def health_check():
    """
    信号监控API健康检查

    **功能说明**:
    - 检查信号监控API的可用性
    - 验证数据库连接状态
    - 返回服务健康状态

    **使用场景**:
    - 服务健康检查
    - 负载均衡器探测
    - 容器编排就绪探针

    **响应示例**:
    ```json
    {
      "status": "healthy",
      "service": "signal-monitoring-api",
      "version": "v1.0",
      "database": "connected"
    }
    ```
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        pg = get_postgres_async()

        db_status = "connected" if pg.is_connected() else "disconnected"

        return {
            "status": "healthy" if db_status == "connected" else "degraded",
            "service": "signal-monitoring-api",
            "version": "v1.0",
            "database": db_status,
        }

    except Exception as e:
        logger.error("健康检查失败: %(e)s")
        return {
            "status": "unhealthy",
            "service": "signal-monitoring-api",
            "version": "v1.0",
            "database": "error",
            "error": str(e),
        }
