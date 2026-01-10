"""
风险管理核心模块
Risk Management Core Module

提供个股和组合风险管理的核心功能。
复用现有的GPU引擎、数据源和监控基础设施。
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class StockRiskMetrics:
    """个股风险指标"""

    symbol: str
    timestamp: datetime

    # 波动率指标
    volatility_20d: float = 0.0
    atr_14: float = 0.0
    volatility_percentile: int = 50

    # 流动性指标
    avg_daily_volume: float = 0.0
    bid_ask_spread: float = 0.0
    turnover_rate: float = 0.0
    liquidity_score: int = 50

    # 技术指标风险
    ma_trend: str = "neutral"  # bull/bear/neutral
    macd_signal: str = "neutral"
    rsi: float = 50.0
    bollinger_position: str = "middle"  # upper/middle/lower

    # 综合风险评分
    risk_score: int = 50  # 0-100
    risk_level: str = "medium"  # low/medium/high/critical


@dataclass
class PortfolioRiskMetrics:
    """组合风险指标"""

    portfolio_id: str
    user_id: str
    timestamp: datetime

    # 组合价值
    total_value: float = 0.0
    cash_value: float = 0.0

    # 风险指标
    var_1d_95: float = 0.0  # 1日95% VaR
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    beta: float = 1.0

    # 集中度
    hhi: float = 0.0  # 赫芬达尔指数
    top10_ratio: float = 0.0
    max_single_position: float = 0.0
    max_industry_concentration: float = 0.0

    # 综合风险
    risk_score: int = 50
    risk_level: str = "medium"


@dataclass
class RiskAlert:
    """风险告警"""

    alert_type: str  # volatility/position/concentration/stop_loss
    severity: str  # safe/attention/warning/danger
    message: str
    symbol: Optional[str] = None
    portfolio_id: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class IRiskCalculator(ABC):
    """风险计算器接口"""

    @abstractmethod
    async def calculate_stock_risk(self, symbol: str) -> StockRiskMetrics:
        """计算个股风险指标"""
        pass

    @abstractmethod
    async def calculate_portfolio_risk(self, portfolio_id: str) -> PortfolioRiskMetrics:
        """计算组合风险指标"""
        pass

    @abstractmethod
    async def calculate_correlation_matrix(self, symbols: List[str]) -> np.ndarray:
        """计算相关性矩阵"""
        pass

    @abstractmethod
    async def calculate_var(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """计算VaR"""
        pass


class IStopLossEngine(ABC):
    """止损引擎接口"""

    @abstractmethod
    async def calculate_volatility_stop_loss(self, symbol: str, entry_price: float, k: float = 2.0) -> Dict[str, Any]:
        """计算波动率自适应止损"""
        pass

    @abstractmethod
    async def calculate_trailing_stop_loss(
        self, symbol: str, highest_price: float, trailing_percentage: float = 0.08
    ) -> Dict[str, Any]:
        """计算跟踪止损"""
        pass

    @abstractmethod
    async def check_stop_loss_trigger(self, symbol: str, current_price: float, stop_loss_price: float) -> bool:
        """检查是否触发止损"""
        pass


class IRiskAlertService(ABC):
    """风险告警服务接口"""

    @abstractmethod
    async def evaluate_risk_level(self, metrics: Dict) -> str:
        """评估风险等级"""
        pass

    @abstractmethod
    async def generate_alerts(self, risk_metrics: Dict) -> List[RiskAlert]:
        """生成风险告警"""
        pass

    @abstractmethod
    async def send_alerts(self, alerts: List[RiskAlert]) -> bool:
        """发送告警通知"""
        pass


class RiskManagementCore:
    """
    风险管理核心类

    协调各个风险管理组件，复用现有基础设施。
    """

    def __init__(self):
        self.risk_calculator: Optional[IRiskCalculator] = None
        self.stop_loss_engine: Optional[IStopLossEngine] = None
        self.alert_service: Optional[IRiskAlertService] = None

    async def initialize(self):
        """初始化风险管理组件"""
        # 这里会动态导入具体的实现类
        # 基于配置选择CPU/GPU版本
        pass

    async def calculate_stock_risk(self, symbol: str) -> StockRiskMetrics:
        """计算个股风险"""
        if not self.risk_calculator:
            raise RuntimeError("风险计算器未初始化")
        return await self.risk_calculator.calculate_stock_risk(symbol)

    async def calculate_portfolio_risk(self, portfolio_id: str) -> PortfolioRiskMetrics:
        """计算组合风险"""
        if not self.risk_calculator:
            raise RuntimeError("风险计算器未初始化")
        return await self.risk_calculator.calculate_portfolio_risk(portfolio_id)

    async def execute_stop_loss_check(
        self, symbol: str, current_price: float, stop_loss_config: Dict
    ) -> Tuple[bool, Optional[Dict]]:
        """执行止损检查"""
        if not self.stop_loss_engine:
            raise RuntimeError("止损引擎未初始化")

        stop_loss_price = stop_loss_config.get("stop_loss_price", 0)
        triggered = await self.stop_loss_engine.check_stop_loss_trigger(symbol, current_price, stop_loss_price)

        if triggered:
            # 这里可以触发自动平仓逻辑
            execution_result = {
                "symbol": symbol,
                "triggered_at": datetime.now(),
                "current_price": current_price,
                "stop_loss_price": stop_loss_price,
                "loss_amount": stop_loss_price - current_price,
            }
            return True, execution_result

        return False, None

    async def process_risk_alerts(self, risk_metrics: Dict) -> List[RiskAlert]:
        """处理风险告警"""
        if not self.alert_service:
            raise RuntimeError("告警服务未初始化")

        alerts = await self.alert_service.generate_alerts(risk_metrics)

        if alerts:
            await self.alert_service.send_alerts(alerts)

        return alerts


# 全局实例
_risk_core_instance: Optional[RiskManagementCore] = None


def get_risk_management_core() -> RiskManagementCore:
    """获取风险管理核心实例（单例模式）"""
    global _risk_core_instance
    if _risk_core_instance is None:
        _risk_core_instance = RiskManagementCore()
    return _risk_core_instance
