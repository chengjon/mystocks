"""信号监控 API 响应模型定义。"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


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
    executed: bool = False
    executed_at: Optional[datetime] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None


class SignalQualityReportResponse(BaseModel):
    """信号质量报告响应"""

    strategy_id: str
    period_start: date
    period_end: date
    total_signals: int
    buy_signals: int
    sell_signals: int
    hold_signals: int
    executed_signals: int
    execution_rate: float
    signal_accuracy: float
    signal_success_rate: float
    avg_profit_loss: float
    total_profit_loss: float
    avg_execution_time_ms: float
    gpu_usage_rate: float
    profitable_signals: int
    losing_signals: int
    win_rate: float


class StrategyRealtimeMonitoringResponse(BaseModel):
    """策略实时监控响应"""

    strategy_id: str
    timestamp: datetime
    health_status: int
    active_signals_count: int
    signal_generation_rate: float
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    gpu_enabled: bool
    gpu_utilization: Optional[float] = None
    recent_signals: List[dict] = []


class UnifiedResponse(BaseModel):
    """统一响应格式"""

    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


class SignalStatisticsResponse(BaseModel):
    """信号统计响应（小时级）"""

    strategy_id: str
    hour_timestamp: datetime
    signal_count: int
    buy_count: int
    sell_count: int
    hold_count: int
    executed_count: int
    execution_rate: float
    accuracy_rate: float
    profit_ratio: float
    total_profit_loss: float
    avg_profit_loss: float
    max_profit: float
    max_loss: float
    avg_execution_time_ms: float
    p50_execution_time_ms: float
    p95_execution_time_ms: float
    p99_execution_time_ms: float
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
    health_status: int
    health_status_text: str
    components: dict = {
        "signal_generation": str,
        "signal_execution": str,
        "signal_push": str,
        "database": str,
        "gpu": str,
    }
    metrics: dict = {
        "signal_success_rate": float,
        "signal_accuracy": float,
        "avg_execution_time_ms": float,
        "active_signals_count": int,
    }
    last_check_time: datetime
    alerts: List[str] = []
