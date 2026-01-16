#!/usr/bin/env python3
"""
高级风险指标计算器
计算风险调整后的收益指标和回撤分析

功能：
- Sortino 比率（下行风险调整收益）
- Calmar 比率（最大回撤调整收益）
- 最大回撤持续期
- 下行标准差

作者: Claude Code
创建日期: 2026-01-07
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import date, timedelta

logger = logging.getLogger(__name__)


@dataclass
class RiskMetricsInput:
    """风险指标输入数据"""

    stock_code: str
    close_prices: List[float]
    dates: Optional[List[str]] = None
    risk_free_rate: float = 0.03  # 年化无风险利率


def to_dataframe(self) -> pd.DataFrame:
    """转换为DataFrame"""
    if self.dates:
        df = pd.DataFrame({"date": self.dates, "close": self.close_prices})
    else:
        df = pd.DataFrame({"close": self.close_prices})
    return df


@dataclass
class RiskMetricsOutput:
    """风险指标输出数据"""

    stock_code: str
    sortino_ratio: Optional[float]
    calmar_ratio: Optional[float]
    max_drawdown: Optional[float]
    max_drawdown_duration: Optional[int]
    downside_deviation: Optional[float]

    annual_return: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None


def to_dict(self) -> Dict[str, Any]:
    return {
        "stock_code": self.stock_code,
        "sortino_ratio": self.sortino_ratio,
        "calmar_ratio": self.calmar_ratio,
        "max_drawdown": self.max_drawdown,
        "max_drawdown_duration": self.max_drawdown_duration,
        "downside_deviation": self.downside_deviation,
        "annual_return": self.annual_return,
        "volatility": self.volatility,
        "sharpe_ratio": self.sharpe_ratio,
    }


@dataclass
class RiskMetricsConfig:
    """风险指标计算配置"""

    trading_days_per_year: int = 252
    min_data_points: int = 30
    return_window: int = 252


class AdvancedRiskCalculator:
    """
    高级风险指标计算器

    计算以下指标：
    1. Sortino Ratio - 仅惩罚下行波动
    2. Calmar Ratio - 年化收益 / 最大回撤
    3. Max Drawdown Duration - 最大回撤持续天数
    4. Downside Deviation - 下行标准差
    """


def __init__(self, config: Optional[RiskMetricsConfig] = None):
    self.config = config or RiskMetricsConfig()


def calculate(
    self,
    inputs: List[RiskMetricsInput],
) -> List[RiskMetricsOutput]:
    """
    批量计算风险指标

    Args:
        inputs: 输入数据列表

    Returns:
        List[RiskMetricsOutput]: 风险指标列表
    """
    results = []

    for input_data in inputs:
        try:
            output = self._calculate_single(input_data)
            results.append(output)
        except Exception as e:
            logger.error(f"计算 {input_data.stock_code} 风险指标失败: {e}")
            results.append(
                RiskMetricsOutput(
                    stock_code=input_data.stock_code,
                    sortino_ratio=None,
                    calmar_ratio=None,
                    max_drawdown=None,
                    max_drawdown_duration=None,
                    downside_deviation=None,
                )
            )

    return results


def _calculate_single(self, input_data: RiskMetricsInput) -> RiskMetricsOutput:
    """计算单个股票的风险指标"""
    df = input_data.to_dataframe()
    closes = np.array(input_data.close_prices)

    if len(closes) < self.config.min_data_points:
        logger.warning(
            f"数据点不足: {
                len(closes)}, 需要至少 {
                self.config.min_data_points}"
        )
        return RiskMetricsOutput(
            stock_code=input_data.stock_code,
            sortino_ratio=None,
            calmar_ratio=None,
            max_drawdown=None,
            max_drawdown_duration=None,
            downside_deviation=None,
        )

    returns = self._calculate_returns(closes)

    max_drawdown, max_dd_duration = self._calculate_max_drawdown(closes)
    downside_deviation = self._calculate_downside_deviation(returns)
    sortino_ratio = self._calculate_sortino_ratio(returns, downside_deviation, input_data.risk_free_rate)
    calmar_ratio = self._calculate_calmar_ratio(closes, max_drawdown)
    annual_return = self._calculate_annual_return(closes)
    volatility = self._calculate_volatility(returns)
    sharpe_ratio = self._calculate_sharpe_ratio(returns, volatility, input_data.risk_free_rate)

    return RiskMetricsOutput(
        stock_code=input_data.stock_code,
        sortino_ratio=sortino_ratio,
        calmar_ratio=calmar_ratio,
        max_drawdown=max_drawdown,
        max_drawdown_duration=max_dd_duration,
        downside_deviation=downside_deviation,
        annual_return=annual_return,
        volatility=volatility,
        sharpe_ratio=sharpe_ratio,
    )


def _calculate_returns(self, prices: np.ndarray) -> np.ndarray:
    """计算日收益率"""
    if len(prices) < 2:
        return np.array([])

    returns = np.diff(prices) / prices[:-1]
    returns = returns[~np.isnan(returns)]
    returns = returns[~np.isinf(returns)]

    return np.asarray(returns)


def _calculate_max_drawdown(self, prices: np.ndarray) -> Tuple[float, int]:
    """
    计算最大回撤和持续期

    Returns:
        Tuple[float, int]: (最大回撤比例, 持续天数)
    """
    if len(prices) < 2:
        return 0.0, 0

    cumulative = np.cumprod(1 + np.diff(prices) / prices[:-1])
    running_max = np.maximum.accumulate(cumulative)
    drawdowns = (cumulative - running_max) / running_max

    max_dd_idx = np.argmin(drawdowns)
    max_drawdown = abs(drawdowns[max_dd_idx])

    if max_drawdown == 0:
        return 0.0, 0

    drawdown_start = np.argmax(running_max[: max_dd_idx + 1])
    duration = max_dd_idx - drawdown_start

    return float(max_drawdown), int(duration)


def _calculate_downside_deviation(self, returns: np.ndarray) -> float:
    """
    计算下行标准差

    只考虑负收益
    """
    if len(returns) == 0:
        return 0.0

    negative_returns = returns[returns < 0]

    if len(negative_returns) == 0:
        return 0.0

    downside_std = np.std(negative_returns, ddof=1)

    return float(downside_std * np.sqrt(self.config.trading_days_per_year))


def _calculate_sortino_ratio(
    self,
    returns: np.ndarray,
    downside_deviation: float,
    risk_free_rate: float,
) -> float:
    """
    计算Sortino比率

    Sortino = (年化收益 - 无风险利率) / 下行标准差
    """
    if len(returns) == 0 or downside_deviation == 0:
        return 0.0

    annual_return = np.mean(returns) * self.config.trading_days_per_year
    excess_return = annual_return - risk_free_rate

    sortino_ratio = excess_return / downside_deviation

    return round(float(sortino_ratio), 4)


def _calculate_calmar_ratio(self, prices: np.ndarray, max_drawdown: float) -> float:
    """
    计算Calmar比率

    Calmar = 年化收益 / 最大回撤
    """
    if len(prices) < 2 or max_drawdown == 0:
        return 0.0

    annual_return = self._calculate_annual_return(prices)

    calmar_ratio = annual_return / max_drawdown

    return round(float(calmar_ratio), 4)


def _calculate_annual_return(self, prices: np.ndarray) -> float:
    """计算年化收益率"""
    if len(prices) < 2:
        return 0.0

    total_return = (prices[-1] - prices[0]) / prices[0]
    years = len(prices) / self.config.trading_days_per_year

    if years <= 0:
        return 0.0

    annual_return = ((1 + total_return) ** (1 / years)) - 1

    return round(float(annual_return), 4)


def _calculate_volatility(self, returns: np.ndarray) -> float:
    """计算年化波动率"""
    if len(returns) == 0:
        return 0.0

    daily_vol = np.std(returns, ddof=1)
    annual_vol = daily_vol * np.sqrt(self.config.trading_days_per_year)

    return round(float(annual_vol), 4)


def _calculate_sharpe_ratio(
    self,
    returns: np.ndarray,
    volatility: float,
    risk_free_rate: float,
) -> float:
    """计算夏普比率"""
    if len(returns) == 0 or volatility == 0:
        return 0.0

    annual_return = np.mean(returns) * self.config.trading_days_per_year
    excess_return = annual_return - risk_free_rate

    sharpe_ratio = excess_return / volatility

    return round(float(sharpe_ratio), 4)


def get_advanced_risk_calculator(
    config: Optional[RiskMetricsConfig] = None,
) -> AdvancedRiskCalculator:
    """获取高级风险计算器实例"""
    return AdvancedRiskCalculator(config)
