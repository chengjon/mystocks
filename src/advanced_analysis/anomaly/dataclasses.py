"""异常追踪分析器子模块"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)

"""
Anomaly Tracking Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台异动跟踪分析功能

This module provides comprehensive anomaly detection and tracking including:
- Multi-dimensional anomaly detection (price, volume, technical indicators)
- Statistical outlier identification and pattern recognition
- Real-time anomaly monitoring and alerting
- Anomaly clustering and trend analysis
- Risk assessment based on anomaly patterns
"""

import warnings



# GPU acceleration support
try:
    from cuml import IsolationForest

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    try:
        from sklearn.ensemble import IsolationForest
    except ImportError:
        IsolationForest = None
        warnings.warn("Neither GPU nor CPU ML libraries available. Some anomaly detection features will be limited.")


@dataclass
class AnomalyEvent:
    """异常事件数据结构"""

    event_id: str
    timestamp: datetime
    anomaly_type: str  # price_anomaly, volume_anomaly, technical_anomaly, pattern_anomaly
    severity: str  # critical, major, minor, warning
    confidence: float  # 检测置信度 (0-1)
    value: float  # 异常值
    expected_value: float  # 期望值
    deviation: float  # 偏差程度
    description: str  # 异常描述
    impact_assessment: str  # 影响评估
    recommended_action: str  # 建议行动


@dataclass
class AnomalyCluster:
    """异常聚类结果"""

    cluster_id: int
    anomaly_count: int
    cluster_type: str  # price_cluster, volume_cluster, mixed_cluster
    time_span: Tuple[datetime, datetime]  # 异常时间跨度
    severity_distribution: Dict[str, int]  # 严重程度分布
    common_characteristics: List[str]  # 共同特征
    cluster_risk_level: str  # 聚类风险等级


@dataclass
class AnomalyPattern:
    """异常模式分析"""

    pattern_type: str  # sudden_spike, gradual_drift, cyclical_anomaly, clustered_events
    pattern_strength: float  # 模式强度 (0-1)
    pattern_duration: int  # 模式持续时间（天）
    recurrence_probability: float  # 复发概率 (0-1)
    trend_direction: str  # 模式发展趋势
    predictive_value: float  # 预测价值 (0-1)


@dataclass
class AnomalyAlert:
    """异常告警配置"""

    alert_id: str
    alert_type: str
    threshold: float
    time_window: int  # 时间窗口（分钟）
    cooldown_period: int  # 冷却期（分钟）
    enabled: bool
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

