"""
信号监控 API 响应模型定义。
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SignalHistoryResponse(BaseModel):
    """信号历史记录响应"""

    id: int = Field(..., description="信号记录主键ID。")
    strategy_id: str = Field(..., description="生成该信号的策略ID。")
    symbol: str = Field(..., description="触发信号的股票或合约代码。")
    signal_type: str = Field(..., description="信号类型，例如 BUY、SELL 或 HOLD。")
    generated_at: datetime = Field(..., description="信号生成时间。")
    status: str = Field(..., description="信号当前处理状态。")
    execution_time_ms: Optional[float] = Field(None, description="信号处理耗时，单位毫秒。")
    gpu_used: bool = Field(False, description="本次信号计算是否使用了GPU。")
    gpu_latency_ms: Optional[float] = Field(None, description="GPU 计算耗时，单位毫秒。")
    executed: bool = Field(False, description="该信号是否已经执行。")
    executed_at: Optional[datetime] = Field(None, description="信号实际执行时间。")
    profit_loss: Optional[float] = Field(None, description="信号对应交易的绝对盈亏。")
    profit_loss_percent: Optional[float] = Field(None, description="信号对应交易的盈亏百分比。")


class SignalQualityReportResponse(BaseModel):
    """信号质量报告响应"""

    strategy_id: str = Field(..., description="统计所对应的策略ID。")
    period_start: date = Field(..., description="统计周期起始日期。")
    period_end: date = Field(..., description="统计周期结束日期。")
    total_signals: int = Field(..., description="统计周期内总信号数。")
    buy_signals: int = Field(..., description="买入信号数量。")
    sell_signals: int = Field(..., description="卖出信号数量。")
    hold_signals: int = Field(..., description="持有信号数量。")
    executed_signals: int = Field(..., description="已执行信号数量。")
    execution_rate: float = Field(..., description="信号执行率，百分比表示。")
    signal_accuracy: float = Field(..., description="已执行信号的准确率。")
    signal_success_rate: float = Field(..., description="信号成功率，衡量有效执行占比。")
    avg_profit_loss: float = Field(..., description="平均单笔盈亏。")
    total_profit_loss: float = Field(..., description="累计总盈亏。")
    avg_execution_time_ms: float = Field(..., description="平均执行耗时，单位毫秒。")
    gpu_usage_rate: float = Field(..., description="GPU 使用率，百分比表示。")
    profitable_signals: int = Field(..., description="盈利信号数量。")
    losing_signals: int = Field(..., description="亏损信号数量。")
    win_rate: float = Field(..., description="胜率，盈利信号占比。")


class StrategyRealtimeMonitoringResponse(BaseModel):
    """策略实时监控响应"""

    strategy_id: str = Field(..., description="实时监控所对应的策略ID。")
    timestamp: datetime = Field(..., description="监控快照生成时间。")
    health_status: int = Field(..., description="策略健康状态编码。")
    active_signals_count: int = Field(..., description="当前活跃信号数量。")
    signal_generation_rate: float = Field(..., description="信号生成速率，单位为每分钟。")
    avg_latency_ms: float = Field(..., description="平均处理延迟，单位毫秒。")
    p95_latency_ms: float = Field(..., description="P95 延迟，单位毫秒。")
    p99_latency_ms: float = Field(..., description="P99 延迟，单位毫秒。")
    gpu_enabled: bool = Field(..., description="当前策略是否启用了GPU。")
    gpu_utilization: Optional[float] = Field(None, description="GPU 利用率，百分比表示。")
    recent_signals: List[Dict[str, Any]] = Field(default_factory=list, description="最近生成的信号摘要列表。")


class UnifiedResponse(BaseModel):
    """统一响应格式"""

    success: bool = Field(..., description="请求是否成功。")
    message: Optional[str] = Field(None, description="响应消息。")
    data: Optional[Dict[str, Any]] = Field(None, description="业务响应数据。")


class SignalStatisticsResponse(BaseModel):
    """信号统计响应（小时级）"""

    strategy_id: str = Field(..., description="统计对应的策略ID。")
    hour_timestamp: datetime = Field(..., description="统计小时的时间戳。")
    signal_count: int = Field(..., description="总信号数量。")
    buy_count: int = Field(..., description="买入信号数量。")
    sell_count: int = Field(..., description="卖出信号数量。")
    hold_count: int = Field(..., description="持有信号数量。")
    executed_count: int = Field(..., description="已执行信号数量。")
    execution_rate: float = Field(..., description="执行率。")
    accuracy_rate: float = Field(..., description="准确率。")
    profit_ratio: float = Field(..., description="盈利占比。")
    total_profit_loss: float = Field(..., description="总盈亏。")
    avg_profit_loss: float = Field(..., description="平均盈亏。")
    max_profit: float = Field(..., description="最大单笔盈利。")
    max_loss: float = Field(..., description="最大单笔亏损。")
    avg_execution_time_ms: float = Field(..., description="平均执行时延，单位毫秒。")
    p50_execution_time_ms: float = Field(..., description="P50 执行时延。")
    p95_execution_time_ms: float = Field(..., description="P95 执行时延。")
    p99_execution_time_ms: float = Field(..., description="P99 执行时延。")
    gpu_used_count: int = Field(..., description="使用 GPU 的信号数量。")
    gpu_rate: float = Field(..., description="GPU 使用比例。")


class ActiveSignalItem(BaseModel):
    """活跃信号项"""

    id: int = Field(..., description="活跃信号记录ID。")
    strategy_id: str = Field(..., description="所属策略ID。")
    symbol: str = Field(..., description="股票或合约代码。")
    signal_type: str = Field(..., description="信号类型。")
    generated_at: datetime = Field(..., description="信号生成时间。")
    status: str = Field(..., description="信号状态。")
    execution_time_ms: Optional[float] = Field(None, description="处理耗时，单位毫秒。")
    gpu_used: bool = Field(False, description="是否使用GPU。")


class ActiveSignalsResponse(BaseModel):
    """活跃信号列表响应"""

    strategy_id: Optional[str] = Field(None, description="筛选后的策略ID；为空表示全量。")
    total_count: int = Field(..., description="活跃信号总数。")
    signals: List[ActiveSignalItem] = Field(..., description="活跃信号明细列表。")


class StrategyDetailedHealthResponse(BaseModel):
    """策略详细健康状态响应"""

    strategy_id: str = Field(..., description="详细健康信息对应的策略ID。")
    timestamp: datetime = Field(..., description="健康快照时间。")
    health_status: int = Field(..., description="健康状态编码。")
    health_status_text: str = Field(..., description="健康状态文本说明。")
    components: Dict[str, str] = Field(
        default_factory=lambda: {
            "signal_generation": "unknown",
            "signal_execution": "unknown",
            "signal_push": "unknown",
            "database": "unknown",
            "gpu": "unknown",
        },
        description="各健康组件的状态映射。",
    )
    metrics: Dict[str, float] = Field(
        default_factory=lambda: {
            "signal_success_rate": 0.0,
            "signal_accuracy": 0.0,
            "avg_execution_time_ms": 0.0,
            "active_signals_count": 0.0,
        },
        description="关键健康指标汇总。",
    )
    last_check_time: datetime = Field(..., description="上一次健康检查时间。")
    alerts: List[str] = Field(default_factory=list, description="当前触发的健康告警列表。")
