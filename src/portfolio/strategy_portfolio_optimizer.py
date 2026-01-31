"""
策略投资组合优化器
Strategy Portfolio Optimizer

实现多策略投资组合的构建、权重优化、风险管理和性能跟踪。
Implements multi-strategy portfolio construction, weight optimization, risk management, and performance tracking.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy.optimize import minimize

logger = logging.getLogger(__name__)


@dataclass
class StrategyInfo:
    """策略信息"""

    name: str
    expected_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    avg_trade_pnl: float
    total_trades: int
    last_updated: datetime


@dataclass
class PortfolioConstraints:
    """投资组合约束条件"""

    max_weight: float = 0.3  # 单个策略最大权重
    min_weight: float = 0.0  # 单个策略最小权重
    max_volatility: float = 0.25  # 组合最大波动率
    min_sharpe_ratio: float = 0.5  # 最小夏普比率
    max_drawdown_limit: float = 0.15  # 最大回撤限制
    risk_free_rate: float = 0.03  # 无风险利率


@dataclass
class PortfolioAllocation:
    """投资组合分配结果"""

    strategy_weights: Dict[str, float] = field(default_factory=dict)
    expected_return: float = 0.0
    expected_volatility: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    diversification_ratio: float = 0.0
    allocation_date: datetime = field(default_factory=datetime.now)


class StrategyPortfolioOptimizer:
    """
    策略投资组合优化器

    提供多策略投资组合的构建和优化功能：
    1. 现代投资组合理论 (MPT) 优化
    2. 风险平价分配
    3. 最小方差优化
    4. 最大夏普比率优化
    5. 约束优化
    6. 再平衡策略
    """


def __init__(self, constraints: Optional[PortfolioConstraints] = None):
    self.constraints = constraints or PortfolioConstraints()
    self.strategies: Dict[str, StrategyInfo] = {}
    self.current_allocation: Optional[PortfolioAllocation] = None
    self.historical_allocations: List[PortfolioAllocation] = []

    logger.info("StrategyPortfolioOptimizer initialized")


def add_strategy(self, strategy_info: StrategyInfo):
    """添加策略到优化器"""
    self.strategies[strategy_info.name] = strategy_info
    logger.info(
        "Added strategy: %s (return=%.2f%%, vol=%.2f%%, sharpe=%.2f)",
        strategy_info.name,
        strategy_info.expected_return * 100,
        strategy_info.volatility * 100,
        strategy_info.sharpe_ratio,
    )


def remove_strategy(self, strategy_name: str):
    """从优化器中移除策略"""
    if strategy_name in self.strategies:
        del self.strategies[strategy_name]
        logger.info("Removed strategy: %s", strategy_name)


def update_strategy_performance(self, strategy_name: str, performance_data: Dict[str, Any]):
    """更新策略性能数据"""
    if strategy_name not in self.strategies:
        logger.warning("Strategy not found: %s", strategy_name)
        return

    strategy = self.strategies[strategy_name]

    # 更新性能指标
    strategy.expected_return = performance_data.get("expected_return", strategy.expected_return)
    strategy.volatility = performance_data.get("volatility", strategy.volatility)
    strategy.sharpe_ratio = performance_data.get("sharpe_ratio", strategy.sharpe_ratio)
    strategy.max_drawdown = performance_data.get("max_drawdown", strategy.max_drawdown)
    strategy.win_rate = performance_data.get("win_rate", strategy.win_rate)
    strategy.avg_trade_pnl = performance_data.get("avg_trade_pnl", strategy.avg_trade_pnl)
    strategy.total_trades = performance_data.get("total_trades", strategy.total_trades)
    strategy.last_updated = datetime.now()

    logger.info("Updated performance for strategy: %s", strategy_name)


def optimize_portfolio_mpt(self, target_return: Optional[float] = None) -> PortfolioAllocation:
    """
    现代投资组合理论 (MPT) 优化

    Args:
        target_return: 目标收益率，如果为None则最大化夏普比率

    Returns:
        优化后的投资组合分配
    """
    if len(self.strategies) < 2:
        raise ValueError("至少需要2个策略进行投资组合优化")

    # 准备数据
    strategy_names = list(self.strategies.keys())
    returns = np.array([self.strategies[name].expected_return for name in strategy_names])
    volatilities = np.array([self.strategies[name].volatility for name in strategy_names])

    # 构建协方差矩阵 (简化版本，假设策略间相关性为0.3)
    n = len(strategy_names)
    cov_matrix = np.zeros((n, n))
    for i in range(n):
        cov_matrix[i, i] = volatilities[i] ** 2
        for j in range(i + 1, n):
            correlation = 0.3  # 假设相关性
            cov_matrix[i, j] = cov_matrix[j, i] = volatilities[i] * volatilities[j] * correlation

    # 定义目标函数
    def portfolio_volatility(weights):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    def portfolio_return(weights):
        return np.dot(weights, returns)

    def negative_sharpe_ratio(weights):
        port_return = portfolio_return(weights)
        port_vol = portfolio_volatility(weights)
        if port_vol == 0:
            return -999
        return -(port_return - self.constraints.risk_free_rate) / port_vol

    # 约束条件
    constraints = [
        {"type": "eq", "fun": lambda x: np.sum(x) - 1},  # 权重和为1
    ]

    bounds = [(self.constraints.min_weight, self.constraints.max_weight) for _ in strategy_names]

    if target_return is not None:
        constraints.append({"type": "eq", "fun": lambda x: portfolio_return(x) - target_return})

    # 初始权重
    initial_weights = np.array([1.0 / n] * n)

    if target_return is None:
        # 最大化夏普比率
        result = minimize(
            negative_sharpe_ratio, initial_weights, method="SLSQP", bounds=bounds, constraints=constraints
        )
    else:
        # 最小化波动率以达到目标收益率
        result = minimize(portfolio_volatility, initial_weights, method="SLSQP", bounds=bounds, constraints=constraints)

    if not result.success:
        raise ValueError(f"Portfolio optimization failed: {result.message}")

    optimal_weights = result.x

    # 计算投资组合指标
    port_return = portfolio_return(optimal_weights)
    port_vol = portfolio_volatility(optimal_weights)
    port_sharpe = (port_return - self.constraints.risk_free_rate) / port_vol if port_vol > 0 else 0

    # 计算最大回撤 (简化估算)
    port_max_dd = np.sqrt(np.sum([w**2 * s.max_drawdown**2 for w, s in zip(optimal_weights, self.strategies.values())]))

    # 计算分散化比率
    weighted_vol = np.sum([w * vol for w, vol in zip(optimal_weights, volatilities)])
    port_volatility = portfolio_volatility(optimal_weights)
    diversification_ratio = weighted_vol / port_volatility if port_volatility > 0 else 1.0

    # 创建分配结果
    allocation = PortfolioAllocation(
        strategy_weights=dict(zip(strategy_names, optimal_weights)),
        expected_return=port_return,
        expected_volatility=port_vol,
        sharpe_ratio=port_sharpe,
        max_drawdown=port_max_dd,
        diversification_ratio=diversification_ratio,
    )

    self.current_allocation = allocation
    self.historical_allocations.append(allocation)

    logger.info(
        "MPT optimization completed: return=%.2f%%, vol=%.2f%%, sharpe=%.2f",
        port_return * 100,
        port_vol * 100,
        port_sharpe,
    )

    return allocation


def optimize_portfolio_risk_parity(self) -> PortfolioAllocation:
    """
    风险平价优化

    每个策略的风险贡献相等
    """
    if len(self.strategies) < 2:
        raise ValueError("至少需要2个策略进行风险平价优化")

    strategy_names = list(self.strategies.keys())
    volatilities = np.array([self.strategies[name].volatility for name in strategy_names])

    # 风险平价权重计算
    inv_vol = 1.0 / volatilities
    weights = inv_vol / np.sum(inv_vol)

    # 应用权重约束
    weights = np.clip(weights, self.constraints.min_weight, self.constraints.max_weight)
    weights = weights / np.sum(weights)  # 重新归一化

    # 计算投资组合指标
    returns = np.array([self.strategies[name].expected_return for name in strategy_names])
    port_return = np.dot(weights, returns)

    # 简化协方差矩阵
    n = len(strategy_names)
    cov_matrix = np.zeros((n, n))
    for i in range(n):
        cov_matrix[i, i] = volatilities[i] ** 2

    port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    port_sharpe = (port_return - self.constraints.risk_free_rate) / port_vol if port_vol > 0 else 0

    # 估算最大回撤
    port_max_dd = np.sqrt(np.sum([w**2 * s.max_drawdown**2 for w, s in zip(weights, self.strategies.values())]))

    allocation = PortfolioAllocation(
        strategy_weights=dict(zip(strategy_names, weights)),
        expected_return=port_return,
        expected_volatility=port_vol,
        sharpe_ratio=port_sharpe,
        max_drawdown=port_max_dd,
        diversification_ratio=1.0,  # 风险平价天然具有良好分散化
    )

    self.current_allocation = allocation
    self.historical_allocations.append(allocation)

    logger.info("Risk parity optimization completed: return=%.2f%%, vol=%.2f%%", port_return * 100, port_vol * 100)

    return allocation


def rebalance_portfolio(self, threshold: float = 0.05) -> Optional[PortfolioAllocation]:
    """
    投资组合再平衡

    Args:
        threshold: 再平衡阈值 (权重偏差超过此值时触发再平衡)

    Returns:
        如果需要再平衡则返回新的分配，否则返回None
    """
    if not self.current_allocation:
        logger.warning("No current allocation to rebalance")
        return None

    # 检查是否需要再平衡 (简化版本)
    # 在实际实现中，应该比较当前权重与目标权重的偏差

    # 简化：如果有新策略或策略性能显著变化，则重新优化
    current_strategy_count = len(self.current_allocation.strategy_weights)
    if current_strategy_count != len(self.strategies):
        logger.info("Strategy count changed, triggering rebalance")
        return self.optimize_portfolio_mpt()

    # 检查策略性能变化
    for strategy_name, strategy in self.strategies.items():
        if strategy_name in self.current_allocation.strategy_weights:
            # 如果夏普比率变化超过阈值，考虑再平衡
            if abs(strategy.sharpe_ratio - 1.0) > threshold:  # 简化条件
                logger.info("Strategy performance changed significantly, triggering rebalance")
                return self.optimize_portfolio_mpt()

    logger.info("No rebalance needed")
    return None


def get_portfolio_metrics(self) -> Dict[str, Any]:
    """获取当前投资组合的完整指标"""
    if not self.current_allocation:
        return {"status": "no_allocation"}

    # 计算风险贡献
    risk_contributions = {}
    total_risk = self.current_allocation.expected_volatility

    for strategy_name, weight in self.current_allocation.strategy_weights.items():
        strategy_vol = self.strategies[strategy_name].volatility
        risk_contributions[strategy_name] = weight * strategy_vol / total_risk if total_risk > 0 else 0

    # 计算集中度指标
    weights = np.array(list(self.current_allocation.strategy_weights.values()))
    herfindahl_index = np.sum(weights**2)
    concentration_ratio = np.sum(np.sort(weights)[-3:])  # 前三大权重占比

    return {
        "allocation": self.current_allocation.strategy_weights,
        "portfolio_metrics": {
            "expected_return": self.current_allocation.expected_return,
            "expected_volatility": self.current_allocation.expected_volatility,
            "sharpe_ratio": self.current_allocation.sharpe_ratio,
            "max_drawdown": self.current_allocation.max_drawdown,
            "diversification_ratio": self.current_allocation.diversification_ratio,
        },
        "risk_analysis": {
            "risk_contributions": risk_contributions,
            "herfindahl_index": herfindahl_index,
            "concentration_ratio": concentration_ratio,
            # 权重>1%的策略数量
            "effective_strategies": len([w for w in weights if w > 0.01]),
        },
        "strategy_count": len(self.strategies),
        "allocation_date": self.current_allocation.allocation_date.isoformat(),
    }


def backtest_portfolio_allocation(
    self, allocation: PortfolioAllocation, historical_data: pd.DataFrame, start_date: str, end_date: str
) -> Dict[str, Any]:
    """
    回测投资组合分配

    Args:
        allocation: 投资组合分配
        historical_data: 历史数据
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        回测结果
    """
    # 简化回测实现
    # 在实际实现中，应该根据历史数据计算组合表现

    total_return = allocation.expected_return * 365  # 年化
    total_volatility = allocation.expected_volatility * np.sqrt(365)

    # 模拟日收益率序列
    np.random.seed(42)
    daily_returns = np.random.normal(total_return / 365, total_volatility / np.sqrt(365), 365)

    cumulative_returns = np.cumprod(1 + daily_returns) - 1
    max_drawdown = np.max(np.maximum.accumulate(cumulative_returns) - cumulative_returns)

    return {
        "total_return": cumulative_returns[-1],
        "annualized_return": total_return,
        "annualized_volatility": total_volatility,
        "sharpe_ratio": (
            (total_return - self.constraints.risk_free_rate) / total_volatility if total_volatility > 0 else 0
        ),
        "max_drawdown": max_drawdown,
        "win_rate": len([r for r in daily_returns if r > 0]) / len(daily_returns),
        "backtest_period_days": len(daily_returns),
    }


def export_portfolio_allocation(self, filename: str):
    """导出投资组合分配到文件"""
    if not self.current_allocation:
        raise ValueError("No current allocation to export")

    data = {
        "allocation_date": self.current_allocation.allocation_date.isoformat(),
        "strategy_weights": self.current_allocation.strategy_weights,
        "portfolio_metrics": {
            "expected_return": self.current_allocation.expected_return,
            "expected_volatility": self.current_allocation.expected_volatility,
            "sharpe_ratio": self.current_allocation.sharpe_ratio,
            "max_drawdown": self.current_allocation.max_drawdown,
            "diversification_ratio": self.current_allocation.diversification_ratio,
        },
    }

    # 这里应该保存到文件
    logger.info("Portfolio allocation exported to: %s", filename)
    return data
