"""
风险管理基础模块

提供风险指标定义、事件记录、基础风险计算功能
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = __import__("logging").getLogger(__name__)


class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskEventType(Enum):
    """风险事件类型"""
    THRESHOLD_BREACH = "threshold_breach"
    POSITION_CHANGE = "position_change"
    MARKET_EVENT = "market_event"
    MODEL_ERROR = "model_error"
    DATA_QUALITY = "data_quality"


@dataclass
class RiskMetrics:
    """风险指标数据类"""
    var_95: float = 0.0
    var_99: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    beta: float = 0.0
    volatility: float = 0.0

    calculated_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'var_95': self.var_95,
            'var_99': self.var_99,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'beta': self.beta,
            'volatility': self.volatility,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }


@dataclass
class RiskEvent:
    """风险事件记录类"""
    event_id: str = ""
    event_type: RiskEventType = RiskEventType.MODEL_ERROR
    risk_level: RiskLevel = RiskLevel.LOW
    message: str = ""
    timestamp: datetime = None
    portfolio_id: Optional[str] = None
    stock_code: Optional[str] = None

    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'risk_level': self.risk_level.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'portfolio_id': self.portfolio_id,
            'stock_code': self.stock_code,
            'metadata': self.metadata
        }


# Compatibility alias for modules that import MonitoringEvent from risk_base.
MonitoringEvent = RiskEvent


@dataclass
class RiskProfile:
    """风险配置文件"""
    profile_id: str = ""
    profile_name: str = ""
    max_position_size: float = 0.0
    max_single_stock_weight: float = 0.0
    stop_loss_threshold: float = 0.0
    var_95_threshold: float = 0.0
    var_99_threshold: float = 0.0
    sharpe_threshold: float = 0.0
    max_drawdown_threshold: float = 0.0

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'profile_id': self.profile_id,
            'profile_name': self.profile_name,
            'max_position_size': self.max_position_size,
            'max_single_stock_weight': self.max_single_stock_weight,
            'stop_loss_threshold': self.stop_loss_threshold,
            'var_95_threshold': self.var_95_threshold,
            'var_99_threshold': self.var_99_threshold,
            'sharpe_threshold': self.sharpe_threshold,
            'max_drawdown_threshold': self.max_drawdown_threshold
        }


class RiskBase:
    """风险管理基类"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history = []
        self.events_history = []

        logger.info("风险管理基础模块初始化")

    def calculate_var(self, returns: List[float]) -> float:
        """计算方差"""
        if not returns or len(returns) < 2:
            return 0.0

        n = len(returns)
        mean_return = sum(returns) / n

        variance = sum((r - mean_return) ** 2 for r in returns) / n

        logger.debug(f"计算方差: {variance:.6f}")
        return variance

    def calculate_var_with_return(self, returns: List[float], risk_free_rate: float = 0.03) -> float:
        """计算带风险调整的方差"""
        if not returns or len(returns) < 2:
            return 0.0

        n = len(returns)
        mean_return = sum(returns) / n
        risk_adjustment = 1 + risk_free_rate

        variance = sum((r - mean_return * risk_adjustment) ** 2 for r in returns) / n

        logger.debug(f"计算调整后方差: {variance:.6f}")
        return variance

    def calculate_cvar(self, returns: List[float], confidence: float = 0.95) -> float:
        """计算条件方差（C-VaR）"""
        if not returns or len(returns) < 2:
            return 0.0

        n = len(returns)
        mean_return = sum(returns) / n

        excess_returns = [max(r - mean_return, 0) for r in returns]
        cvar = sum(e ** 2 for e in excess_returns) / n

        logger.debug(f"计算C-VaR: {cvar:.6f}")
        return cvar

    def calculate_var_at_risk_level(self, returns: List[float], confidence: float = 0.95, level: RiskLevel = RiskLevel.MEDIUM) -> float:
        """根据风险水平计算调整后的方差"""
        base_var = self.calculate_var(returns)

        risk_level_adjustments = {
            RiskLevel.LOW: 0.5,
            RiskLevel.MEDIUM: 1.0,
            RiskLevel.HIGH: 2.0,
            RiskLevel.CRITICAL: 3.0
        }

        adjustment = risk_level_adjustments.get(level, 1.0)
        adjusted_var = base_var * adjustment

        logger.debug(f"风险水平{level.value}调整后方差: {adjusted_var:.6f}")
        return adjusted_var

    def calculate_percentile(self, value: float, distribution: List[float], percentile: float = 95.0) -> float:
        """计算百分位"""
        if not distribution or len(distribution) == 0:
            return 0.0

        sorted_dist = sorted(distribution)
        index = int(len(sorted_dist) * percentile / 100)

        if index >= len(sorted_dist):
            index = len(sorted_dist) - 1

        percentile_value = sorted_dist[index]

        logger.debug(f"计算{percentile}百分位: {percentile_value:.2f}")
        return percentile_value

    def log_risk_event(self, event: RiskEvent):
        """记录风险事件"""
        try:
            event.timestamp = datetime.now()

            self.events_history.append(event)

            if len(self.events_history) > 1000:
                self.events_history = self.events_history[-1000:]

            logger.warning(f"风险事件记录: {event.event_type.value} - {event.message}")

        except Exception as e:
            logger.error(f"记录风险事件失败: {e}")

    def get_risk_level(self, metrics: RiskMetrics, profile: RiskProfile) -> RiskLevel:
        """评估风险水平"""
        if metrics.var_95 > profile.var_95_threshold:
            return RiskLevel.HIGH
        elif metrics.max_drawdown > profile.max_drawdown_threshold:
            return RiskLevel.CRITICAL
        else:
            return RiskLevel.MEDIUM

    def get_metrics_summary(self, count: int = 100) -> Dict:
        """获取风险指标摘要"""
        if len(self.metrics_history) == 0:
            return {
                'count': 0,
                'avg_var_95': 0.0,
                'avg_var_99': 0.0,
                'avg_sharpe': 0.0,
                'avg_max_drawdown': 0.0,
                'avg_beta': 0.0
            }

        recent_metrics = self.metrics_history[-count:]

        if not recent_metrics:
            return {
                'count': len(self.metrics_history),
                'avg_var_95': recent_metrics.var_95,
                'avg_var_99': recent_metrics.var_99,
                'avg_sharpe': recent_metrics.sharpe_ratio,
                'avg_max_drawdown': recent_metrics.max_drawdown,
                'avg_beta': recent_metrics.beta
            }

        return {
            'count': len(recent_metrics),
            'avg_var_95': sum(m.var_95 for m in recent_metrics) / len(recent_metrics),
            'avg_var_99': sum(m.var_99 for m in recent_metrics) / len(recent_metrics),
            'avg_sharpe': sum(m.sharpe_ratio for m in recent_metrics) / len(recent_metrics),
            'avg_max_drawdown': sum(m.max_drawdown for m in recent_metrics) / len(recent_metrics),
            'avg_beta': sum(m.beta for m in recent_metrics) / len(recent_metrics)
        }
