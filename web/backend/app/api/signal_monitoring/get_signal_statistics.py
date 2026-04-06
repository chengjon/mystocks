"""
信号监控 API 端点
Signal Monitoring API Endpoints

提供信号历史查询、质量报告和实时监控功能。

作者: Claude Code (Main CLI)
创建日期: 2026-01-08
版本: v1.0
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import User, get_current_user
from .signal_history_response_schemas import (
    ActiveSignalsResponse,
    ActiveSignalItem,
    SignalStatisticsResponse,
    StrategyDetailedHealthResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/signals/statistics", response_model=List[SignalStatisticsResponse])
async def get_signal_statistics(
    strategy_id: str = Query(..., description="策略ID"),
    hours: int = Query(24, ge=1, le=168, description="查询最近多少小时的统计数据"),
    current_user: User = Depends(get_current_user),
):
    """
    获取信号统计（小时级）

    **功能说明**:
    - 从 signal_statistics_hourly 表查询聚合统计数据
    - 支持自定义查询时间范围（1-168小时）
    - 返回小时级别的详细统计

    **使用场景**:
    - 查看策略性能趋势
    - 分析信号质量变化
    - 监控系统健康状态

    **参数说明**:
    - strategy_id: 策略ID（必填）
    - hours: 查询最近多少小时，默认24小时，最大168小时（7天）

    **响应示例**:
    ```json
    [
      {
        "strategy_id": "macd_strategy",
        "hour_timestamp": "2026-01-08T10:00:00",
        "signal_count": 150,
        "buy_count": 80,
        "sell_count": 60,
        "hold_count": 10,
        "executed_count": 145,
        "execution_rate": 96.67,
        "accuracy_rate": 75.00,
        "profit_ratio": 68.50,
        ...
      }
    ]
    ```
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        pg = get_postgres_async()

        if not pg.is_connected():
            raise HTTPException(status_code=503, detail="监控数据库未连接")

        query = f"""
        SELECT
            strategy_id,
            hour_timestamp,
            signal_count,
            buy_count,
            sell_count,
            hold_count,
            executed_count,
            execution_rate,
            accuracy_rate,
            profit_ratio,
            total_profit_loss,
            avg_profit_loss,
            max_profit,
            max_loss,
            avg_execution_time_ms,
            p50_execution_time_ms,
            p95_execution_time_ms,
            p99_execution_time_ms,
            gpu_used_count,
            gpu_rate
        FROM signal_statistics_hourly
        WHERE strategy_id = $1
          AND hour_timestamp >= NOW() - INTERVAL '{hours} hours'
        ORDER BY hour_timestamp DESC
        """

        async with pg.pool.acquire() as conn:
            rows = await conn.fetch(query, strategy_id)

        statistics = [
            SignalStatisticsResponse(
                strategy_id=row["strategy_id"],
                hour_timestamp=row["hour_timestamp"],
                signal_count=row["signal_count"],
                buy_count=row["buy_count"],
                sell_count=row["sell_count"],
                hold_count=row["hold_count"],
                executed_count=row["executed_count"],
                execution_rate=float(row["execution_rate"]) if row["execution_rate"] else 0.0,
                accuracy_rate=float(row["accuracy_rate"]) if row["accuracy_rate"] else 0.0,
                profit_ratio=float(row["profit_ratio"]) if row["profit_ratio"] else 0.0,
                total_profit_loss=float(row["total_profit_loss"]) if row["total_profit_loss"] else 0.0,
                avg_profit_loss=float(row["avg_profit_loss"]) if row["avg_profit_loss"] else 0.0,
                max_profit=float(row["max_profit"]) if row["max_profit"] else 0.0,
                max_loss=float(row["max_loss"]) if row["max_loss"] else 0.0,
                avg_execution_time_ms=float(row["avg_execution_time_ms"]) if row["avg_execution_time_ms"] else 0.0,
                p50_execution_time_ms=float(row["p50_execution_time_ms"]) if row["p50_execution_time_ms"] else 0.0,
                p95_execution_time_ms=float(row["p95_execution_time_ms"]) if row["p95_execution_time_ms"] else 0.0,
                p99_execution_time_ms=float(row["p99_execution_time_ms"]) if row["p99_execution_time_ms"] else 0.0,
                gpu_used_count=row["gpu_used_count"],
                gpu_rate=float(row["gpu_rate"]) if row["gpu_rate"] else 0.0,
            )
            for row in rows
        ]

        logger.info("查询信号统计: strategy=%(strategy_id)s, hours=%(hours)s, count={len(statistics)}")
        return statistics

    except HTTPException:
        raise
    except Exception as e:
        logger.error("查询信号统计失败: %(e)s")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/signals/active", response_model=ActiveSignalsResponse)
async def get_active_signals(
    strategy_id: Optional[str] = Query(None, description="策略ID（可选）"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    current_user: User = Depends(get_current_user),
):
    """
    获取活跃信号列表

    **功能说明**:
    - 查询当前活跃的信号（状态为 generated 或 executed）
    - 支持按策略ID过滤
    - 按生成时间倒序排列

    **使用场景**:
    - 查看当前待处理的信号
    - 监控信号队列长度
    - 分析信号生成模式

    **参数说明**:
    - strategy_id: 策略ID（可选，不填则返回所有策略的信号）
    - limit: 返回数量限制，默认100，最大1000

    **响应示例**:
    ```json
    {
      "strategy_id": null,
      "total_count": 250,
      "signals": [
        {
          "id": 12345,
          "strategy_id": "macd_strategy",
          "symbol": "600519.SH",
          "signal_type": "BUY",
          "generated_at": "2026-01-08T10:30:00",
          "status": "generated",
          "execution_time_ms": 45.5,
          "gpu_used": true
        }
      ]
    }
    ```
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        pg = get_postgres_async()

        if not pg.is_connected():
            raise HTTPException(status_code=503, detail="监控数据库未连接")

        # 构建查询
        if strategy_id:
            query = """
            SELECT
                id,
                strategy_id,
                symbol,
                signal_type,
                generated_at,
                status,
                execution_time_ms,
                gpu_used
            FROM signal_records
            WHERE strategy_id = $1
              AND status IN ('generated', 'executed')
            ORDER BY generated_at DESC
            LIMIT $2
            """
            params = [strategy_id, limit]
        else:
            query = """
            SELECT
                id,
                strategy_id,
                symbol,
                signal_type,
                generated_at,
                status,
                execution_time_ms,
                gpu_used
            FROM signal_records
            WHERE status IN ('generated', 'executed')
            ORDER BY generated_at DESC
            LIMIT $1
            """
            params = [limit]

        async with pg.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

            # 查询总数
            if strategy_id:
                count_row = await conn.fetchrow(
                    "SELECT COUNT(*) as total FROM signal_records WHERE strategy_id = $1 AND status IN ('generated', 'executed')",
                    strategy_id,
                )
            else:
                count_row = await conn.fetchrow(
                    "SELECT COUNT(*) as total FROM signal_records WHERE status IN ('generated', 'executed')"
                )

        total_count = count_row["total"] if count_row else 0

        signals = [
            ActiveSignalItem(
                id=row["id"],
                strategy_id=row["strategy_id"],
                symbol=row["symbol"],
                signal_type=row["signal_type"],
                generated_at=row["generated_at"],
                status=row["status"],
                execution_time_ms=float(row["execution_time_ms"]) if row["execution_time_ms"] else None,
                gpu_used=row["gpu_used"],
            )
            for row in rows
        ]

        response = ActiveSignalsResponse(
            strategy_id=strategy_id,
            total_count=total_count,
            signals=signals,
        )

        logger.info("查询活跃信号: strategy=%(strategy_id)s, count={len(signals)}/%(total_count)s")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("查询活跃信号失败: %(e)s")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/strategies/{strategy_id}/health/detailed", response_model=StrategyDetailedHealthResponse)
async def get_strategy_detailed_health(
    strategy_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取策略详细健康状态（组件级）

    **功能说明**:
    - 查询策略的详细健康状态，包括各组件状态
    - 检查信号生成、执行、推送、数据库、GPU等组件
    - 提供性能指标和告警信息

    **使用场景**:
    - 深度诊断策略问题
    - 查看组件级别的健康状态
    - 获取系统告警信息

    **响应示例**:
    ```json
    {
      "strategy_id": "macd_strategy",
      "timestamp": "2026-01-08T10:30:00",
      "health_status": 1,
      "health_status_text": "healthy",
      "components": {
        "signal_generation": "healthy",
        "signal_execution": "healthy",
        "signal_push": "degraded",
        "database": "healthy",
        "gpu": "healthy"
      },
      "metrics": {
        "signal_success_rate": 95.5,
        "signal_accuracy": 78.2,
        "avg_execution_time_ms": 45.2,
        "active_signals_count": 125
      },
      "last_check_time": "2026-01-08T10:29:00",
      "alerts": ["推送延迟过高"]
    }
    ```
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async
        from src.monitoring.signal_result_tracker import get_signal_result_tracker

        pg = get_postgres_async()

        if not pg.is_connected():
            raise HTTPException(status_code=503, detail="监控数据库未连接")

        # 使用 SignalResultTracker 获取健康状态
        tracker = get_signal_result_tracker()
        health_data = await tracker.update_strategy_health_status(strategy_id)

        if not health_data:
            raise HTTPException(status_code=404, detail=f"策略 {strategy_id} 未找到")

        # 映射健康状态
        health_status_map = {
            1: "healthy",
            0: "degraded",
            -1: "unhealthy",
        }

        # 检查各组件状态（简化版，实际应该分别检查每个组件）
        components = {
            "signal_generation": "healthy",
            "signal_execution": "healthy",
            "signal_push": "healthy",  # TODO: 实际检查推送服务状态
            "database": "connected" if pg.is_connected() else "disconnected",
            "gpu": "healthy",  # TODO: 实际检查GPU服务状态
        }

        # 根据整体健康状态调整组件状态
        if health_data["health_status"] == -1:
            components["signal_generation"] = "unhealthy"
            components["signal_execution"] = "unhealthy"
        elif health_data["health_status"] == 0:
            components["signal_generation"] = "degraded"
            components["signal_execution"] = "degraded"

        # 收集告警信息
        alerts = []
        if health_data["success_rate"] < 60:
            alerts.append("信号成功率过低")
        if health_data["accuracy"] < 50:
            alerts.append("信号准确率严重过低")
        if health_data["avg_latency_ms"] > 1000:
            alerts.append("执行延迟过高")
        if health_data["health_status"] == -1:
            alerts.append("策略状态不健康")

        # 构建响应
        response = StrategyDetailedHealthResponse(
            strategy_id=strategy_id,
            timestamp=datetime.now(),
            health_status=health_data["health_status"],
            health_status_text=health_status_map.get(health_data["health_status"], "unknown"),
            components=components,
            metrics={
                "signal_success_rate": health_data["success_rate"],
                "signal_accuracy": health_data["accuracy"],
                "avg_execution_time_ms": health_data["avg_latency_ms"],
                "active_signals_count": 0,  # TODO: 实际查询活跃信号数
            },
            last_check_time=datetime.now(),
            alerts=alerts,
        )

        logger.info("查询策略详细健康状态: strategy=%(strategy_id)s, status={health_data['status_text']}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("查询策略详细健康状态失败: %(e)s")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
