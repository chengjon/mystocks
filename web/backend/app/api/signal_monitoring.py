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
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.security import get_current_user, User

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Pydantic Models (请求/响应模型)
# ============================================================================


class SignalHistoryResponse(BaseModel):
    """信号历史记录响应"""

    id: int
    strategy_id: str
    symbol: str
    signal_type: str
    generated_at: datetime
    status: str
    execution_time_ms: Optional[float] = None
    gpu_used: bool = False
    gpu_latency_ms: Optional[float] = None

    # 执行结果（如果存在）
    executed: bool = False
    executed_at: Optional[datetime] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None


class SignalQualityReportResponse(BaseModel):
    """信号质量报告响应"""

    strategy_id: str
    period_start: date
    period_end: date

    # 信号统计
    total_signals: int
    buy_signals: int
    sell_signals: int
    hold_signals: int

    # 执行统计
    executed_signals: int
    execution_rate: float

    # 性能指标
    signal_accuracy: float  # 信号准确率（0-100）
    signal_success_rate: float  # 信号成功率（0-100）
    avg_profit_loss: float  # 平均盈亏
    total_profit_loss: float  # 总盈亏

    # 性能指标
    avg_execution_time_ms: float
    gpu_usage_rate: float  # GPU使用率（0-100）

    # 盈利信号统计
    profitable_signals: int
    losing_signals: int
    win_rate: float  # 胜率（0-100）


class StrategyRealtimeMonitoringResponse(BaseModel):
    """策略实时监控响应"""

    strategy_id: str
    timestamp: datetime

    # 健康状态
    health_status: int  # 1=healthy, 0=degraded, -1=unhealthy

    # 实时指标
    active_signals_count: int  # 活跃信号数量
    signal_generation_rate: float  # 信号生成速率（信号/分钟）

    # 性能指标
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float

    # GPU使用情况
    gpu_enabled: bool
    gpu_utilization: Optional[float] = None

    # 最近信号（最新5条）
    recent_signals: List[dict] = []


class UnifiedResponse(BaseModel):
    """统一响应格式"""

    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


# ============================================================================
# 1. 信号历史查询 API
# ============================================================================


@router.get("/signals/history", response_model=List[SignalHistoryResponse])
async def get_signal_history(
    strategy_id: Optional[str] = None,
    symbol: Optional[str] = None,
    signal_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
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
    curl -X GET "http://localhost:8000/api/signals/history?strategy_id=macd_strategy"

    # 查询某股票的最近BUY信号
    curl -X GET "http://localhost:8000/api/signals/history?symbol=600519.SH&signal_type=BUY"

    # 查询已执行的信号（最近7天）
    curl -X GET "http://localhost:8000/api/signals/history?status=executed&start_date=2026-01-01"
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

        logger.info(f"查询信号历史: 返回 {len(results)} 条记录")
        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询信号历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# ============================================================================
# 2. 信号质量报告 API
# ============================================================================


@router.get("/signals/quality-report", response_model=SignalQualityReportResponse)
async def get_signal_quality_report(
    strategy_id: str,
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
    curl -X GET "http://localhost:8000/api/signals/quality-report?strategy_id=macd_strategy"

    # 查询最近30天的信号质量报告
    curl -X GET "http://localhost:8000/api/signals/quality-report?strategy_id=macd_strategy&period_days=30"
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

        logger.info(f"生成信号质量报告: strategy={strategy_id}, period={period_days}天")
        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成信号质量报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# ============================================================================
# 3. 策略实时监控 API
# ============================================================================


@router.get("/strategies/{strategy_id}/realtime", response_model=StrategyRealtimeMonitoringResponse)
async def get_strategy_realtime_monitoring(
    strategy_id: str,
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
    curl -X GET "http://localhost:8000/api/strategies/macd_strategy/realtime"
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

        logger.info(f"查询策略实时监控: strategy={strategy_id}")
        return monitoring_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询策略实时监控失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# ============================================================================
# 健康检查端点
# ============================================================================


@router.get("/health")
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

        return {"status": "healthy" if db_status == "connected" else "degraded", "service": "signal-monitoring-api", "version": "v1.0", "database": db_status}

    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {"status": "unhealthy", "service": "signal-monitoring-api", "version": "v1.0", "database": "error", "error": str(e)}


# ============================================================================
# 额外 API 端点（Phase 2 扩展）
# ============================================================================


class SignalStatisticsResponse(BaseModel):
    """信号统计响应（小时级）"""

    strategy_id: str
    hour_timestamp: datetime

    # 信号统计
    signal_count: int
    buy_count: int
    sell_count: int
    hold_count: int

    # 执行统计
    executed_count: int
    execution_rate: float

    # 性能指标
    accuracy_rate: float
    profit_ratio: float

    # 盈亏统计
    total_profit_loss: float
    avg_profit_loss: float
    max_profit: float
    max_loss: float

    # 延迟统计
    avg_execution_time_ms: float
    p50_execution_time_ms: float
    p95_execution_time_ms: float
    p99_execution_time_ms: float

    # GPU统计
    gpu_used_count: int
    gpu_rate: float


class ActiveSignalItem(BaseModel):
    """活跃信号项"""

    id: int
    strategy_id: str
    symbol: str
    signal_type: str
    generated_at: datetime
    status: str
    execution_time_ms: Optional[float] = None
    gpu_used: bool = False


class ActiveSignalsResponse(BaseModel):
    """活跃信号列表响应"""

    strategy_id: Optional[str] = None
    total_count: int
    signals: List[ActiveSignalItem]


class StrategyDetailedHealthResponse(BaseModel):
    """策略详细健康状态响应"""

    strategy_id: str
    timestamp: datetime

    # 整体健康状态
    health_status: int  # 1=healthy, 0=degraded, -1=unhealthy
    health_status_text: str  # healthy/degraded/unhealthy

    # 组件状态
    components: dict = {
        "signal_generation": str,  # healthy/degraded/unhealthy
        "signal_execution": str,
        "signal_push": str,
        "database": str,
        "gpu": str,
    }

    # 性能指标
    metrics: dict = {
        "signal_success_rate": float,  # 0-100
        "signal_accuracy": float,  # 0-100
        "avg_execution_time_ms": float,
        "active_signals_count": int,
    }

    # 最近检查时间
    last_check_time: datetime

    # 告警信息
    alerts: List[str] = []


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

        logger.info(f"查询信号统计: strategy={strategy_id}, hours={hours}, count={len(statistics)}")
        return statistics

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询信号统计失败: {e}")
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

        logger.info(f"查询活跃信号: strategy={strategy_id}, count={len(signals)}/{total_count}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询活跃信号失败: {e}")
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

        logger.info(f"查询策略详细健康状态: strategy={strategy_id}, status={health_data['status_text']}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询策略详细健康状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
