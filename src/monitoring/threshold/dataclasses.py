"""智能阈值管理器 - 数据类定义"""

import logging
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


# 监控组件导入
try:
    from .monitoring_database import get_monitoring_database
    from .performance_monitor import SystemMetrics
except ImportError:
    # 兼容模式
    SystemMetrics = Any
    get_monitoring_database = None

warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger(__name__)


@dataclass
class ThresholdRule:
    """阈值规则定义"""

    name: str
    metric_name: str
    current_threshold: float
    optimal_threshold: Optional[float] = None
    threshold_type: str = "upper"  # 'upper', 'lower', 'range'
    confidence_score: float = 0.5
    learning_rate: float = 0.1
    adaptation_speed: float = 0.05
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    adjustment_count: int = 0
    last_adjustment: Optional[datetime] = None
    history: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.history is None:
            self.history = []


@dataclass
class ThresholdAdjustment:
    """阈值调整记录"""

    timestamp: datetime
    rule_name: str
    old_threshold: float
    new_threshold: float
    reason: str
    confidence: float
    metrics_snapshot: Dict[str, Any]
    predicted_effectiveness: float = 0.0
    actual_effectiveness: Optional[float] = None


@dataclass
class OptimizationResult:
    """优化结果"""

    rule_name: str
    optimization_type: str  # 'anomaly_detection', 'trend_analysis', 'clustering', 'statistical'
    recommended_threshold: float
    confidence_score: float
    expected_improvement: float
    reasoning: str
    supporting_evidence: List[str]
    metadata: Dict[str, Any]


