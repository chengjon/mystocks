"""
风险计算器模块

提供所有风险指标的计算功能：VaR、CVaR、Sharpe Ratio、最大回撤、Beta系数、波动率等
"""

from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
import numpy as np
import pandas as pd

from .risk_base import RiskMetrics, RiskProfile
from .risk_base import RiskBase

logger = __import__("logging").getLogger(__name__)


@dataclass
class CalculationConfig:
    """计算配置"""

    confidence_level: float = 0.95
    risk_free_rate: float = 0.03
    lookback_window: int = 252
    use_adjusted_var: bool = True
    benchmark_index: str = "000300"  # 沪深300指数


@dataclass
class CalculationResult:
    """计算结果"""

    metrics: RiskMetrics
    config: CalculationConfig
    calculated_at: Optional[datetime] = None
    calculation_time_ms: float = 0.0
    data_points: int = 0
    warnings: List[str] = None

    def to_dict(self) -> Dict:
        return {
            "metrics": self.metrics.to_dict(),
            "config": {
                "confidence_level": self.config.confidence_level,
                "risk_free_rate": self.config.risk_free_rate,
                "lookback_window": self.config.lookback_window,
                "use_adjusted_var": self.config.use_adjusted_var,
                "benchmark_index": self.config.benchmark_index,
            },
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
            "calculation_time_ms": self.calculation_time_ms,
            "data_points": self.data_points,
            "warnings": self.warnings if self.warnings else [],
        }


class RiskCalculator(RiskBase):
    """风险计算器"""

    def __init__(self, config: Optional[CalculationConfig] = None):
        super().__init__()
        self.config = config or CalculationConfig()
        self.benchmark_returns = None
        self.cache = {}

        logger.info("风险计算器初始化")

    def calculate_all_metrics(self, returns: List[float], risk_profile: RiskProfile) -> CalculationResult:
        """计算所有风险指标"""
        try:
            self._log_request_start("calculate_all_metrics", {"data_points": len(returns)})

            if not returns or len(returns) < 2:
                return CalculationResult(metrics=RiskMetrics(), config=self.config, warnings=["数据点不足"])

            config = self.config
            n = len(returns)

            start_time = datetime.now()

            result_metrics = RiskMetrics()
            warnings = []

            result_metrics.var_95 = self._calculate_percentile(returns, config.confidence_level)
            result_metrics.var_99 = self._calculate_percentile(returns, 0.99)

            if config.use_adjusted_var:
                risk_free_returns = [r * (1 + config.risk_free_rate) for r in returns]
                result_metrics.var_95 = self.calculate_var(risk_free_returns)
                result_metrics.var_99 = self.calculate_var(risk_free_returns)
            else:
                result_metrics.var_95 = self.calculate_var(returns)
                result_metrics.var_99 = self.calculate_var(returns)

            daily_returns = pd.Series(returns).pct_change()
            result_metrics.volatility = self._calculate_volatility(daily_returns)

            result_metrics.sharpe_ratio = self._calculate_sharpe_ratio(returns, config.risk_free_rate)

            result_metrics.max_drawdown = self._calculate_max_drawdown(returns)

            if config.use_adjusted_var:
                risk_free_returns = [r * (1 + config.risk_free_rate) for r in returns]
                result_metrics.beta = self._calculate_beta(risk_free_returns)
            else:
                result_metrics.beta = self._calculate_beta(returns)

            result_metrics.calculated_at = datetime.now()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000

            if warnings:
                logger.warning(f"计算警告: {'; '.join(warnings)}")

            self._log_request_success(
                "calculate_all_metrics",
                {
                    "var_95": result_metrics.var_95,
                    "var_99": result_metrics.var_99,
                    "sharpe_ratio": result_metrics.sharpe_ratio,
                    "max_drawdown": result_metrics.max_drawdown,
                },
            )

            return CalculationResult(
                metrics=result_metrics,
                config=config,
                calculated_at=end_time,
                calculation_time_ms=duration,
                data_points=n,
                warnings=warnings,
            )

        except Exception as e:
            self._log_request_error("calculate_all_metrics", e)
            return CalculationResult(
                metrics=RiskMetrics(),
                config=config,
                calculated_at=datetime.now(),
                calculation_time_ms=0,
                data_points=len(returns),
                warnings=[str(e)],
            )

    def _calculate_var(self, returns: List[float]) -> float:
        """计算方差"""
        n = len(returns)
        if n == 0:
            return 0.0

        mean_return = sum(returns) / n
        variance = sum((r - mean_return) ** 2 for r in returns) / n

        return variance

    def _calculate_cvar(self, returns: List[float], alpha: float = 0.95) -> float:
        """计算条件VaR"""
        if not returns or len(returns) < 2:
            return 0.0

        n = len(returns)
        mean_return = sum(returns) / n

        tail_losses = [min(r - mean_return, 0) for r in returns]

        if not tail_losses:
            return 0.0

        cvar = alpha * sum(tl**2 for tl in tail_losses) / n

        return cvar

    def _calculate_percentile(self, returns: List[float], percentile: float = 95.0) -> float:
        """计算百分位"""
        if not returns:
            return 0.0

        sorted_returns = sorted(returns)
        index = int(len(sorted_returns) * percentile / 100)

        if index >= len(sorted_returns):
            index = len(sorted_returns) - 1

        percentile_value = sorted_returns[index]

        return percentile_value

    def _calculate_volatility(self, returns: List[float]) -> float:
        """计算波动率（使用标准差）"""
        if not returns or len(returns) < 2:
            return 0.0

        return np.std(returns) ** 2

    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float) -> float:
        """计算夏普比率"""
        if not returns or len(returns) < 2:
            return 0.0

        n = len(returns)
        mean_return = sum(returns) / n

        if mean_return <= 0:
            return 0.0

        return (mean_return - risk_free_rate) / np.std(returns)

    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """计算最大回撤"""
        if not returns:
            return 0.0

        cumulative_returns = []
        cumulative = 0.0
        max_drawdown = 0.0
        peak = 0.0

        for r in returns:
            cumulative += r
            cumulative_returns.append(cumulative)

            if cumulative > peak:
                peak = cumulative

            drawdown = (peak - cumulative) / peak if peak > 0 else 0.0

            if drawdown < max_drawdown:
                max_drawdown = drawdown

        return abs(max_drawdown)

    def _calculate_beta(self, returns: List[float]) -> float:
        """计算Beta系数"""
        if not returns or len(returns) < 2:
            return 0.0

        try:
            returns_array = np.array(returns)

            if not self.benchmark_returns:
                logger.warning("基准指数数据未加载，使用假设的基准收益率")
                self.benchmark_returns = [0.0005] * len(returns)

            benchmark_array = np.array(self.benchmark_returns[: len(returns)])

            if len(benchmark_array) != len(returns_array):
                logger.warning(f"基准指数数据与收益率数据长度不匹配: {len(benchmark_array)} vs {len(returns_array)}")
                benchmark_array = np.resize(benchmark_array, len(returns_array))

            covariance_matrix = np.cov(returns_array, benchmark_array)
            benchmark_variance = np.var(benchmark_array)

            if benchmark_variance == 0:
                return 0.0

            beta = covariance_matrix[0, 1] / benchmark_variance

            return beta

        except Exception as e:
            self.logger.error(f"计算Beta系数失败: {e}")
            return 0.0

    def _calculate_information_ratio(self, returns: List[float]) -> float:
        """计算信息比率"""
        if not returns or len(returns) < 2:
            return 0.0

        positive_returns = [r for r in returns if r > 0]
        negative_returns = [abs(r) for r in returns if r < 0]

        if not positive_returns or not negative_returns:
            return 0.0

        avg_positive = sum(positive_returns) / len(positive_returns)
        avg_negative = sum(negative_returns) / len(negative_returns)

        if avg_negative == 0:
            return float("inf")

        return avg_positive / avg_negative

    def _calculate_omega_ratio(self, returns: List[float]) -> float:
        """计算Omega比率"""
        if not returns or len(returns) < 3:
            return 0.0

        n = len(returns)
        mean_return = sum(returns) / n

        downside_returns = [r for r in returns if r < mean_return]

        if not downside_returns:
            return 0.0

        downside_variance = sum((r - mean_return) ** 2 for r in downside_returns) / n
        total_variance = sum((r - mean_return) ** 2 for r in returns) / n

        if total_variance == 0:
            return 0.0

        return downside_variance / total_variance

    def _calculate_sortino_ratio(self, returns: List[float], target_return: float = 0.0) -> float:
        """计算索提诺比率"""
        if not returns or len(returns) < 2:
            return 0.0

        downside_returns = [r - target_return for r in returns if r - target_return < 0]
        total_returns = returns

        if not downside_returns:
            return 0.0

        downside_variance = sum((r - target_return) ** 2 for r in downside_returns) / len(downside_returns)
        total_variance = sum((r - np.mean(returns)) ** 2 for r in total_returns) / len(total_returns)

        if total_variance == 0:
            return 0.0

        return downside_variance / total_variance

    def _calculate_calmar_ratio(self, returns: List[float]) -> float:
        """计算卡玛比率"""
        if not returns or len(returns) < 2:
            return 0.0

        n = len(returns)
        returns_array = np.array(returns)

        rolling_returns = []
        window_size = min(n, 20)

        for i in range(n):
            start_idx = max(0, i - window_size)
            end_idx = i

            window_returns = returns_array[start_idx:end_idx]

            if len(window_returns) > 0:
                rolling_returns.append(np.std(window_returns))
            else:
                rolling_returns.append(0.0)

        if not rolling_returns:
            return 0.0

        rolling_variance = np.var(rolling_returns)
        return_variance = np.var(returns_array)

        if return_variance == 0:
            return 0.0

        return rolling_variance / return_variance

    def _calculate_modigliani_ratio(self, returns: List[float]) -> float:
        """计算莫迪利亚尼比率"""
        if not returns or len(returns) < 2:
            return 0.0

        returns_array = np.array(returns)
        n = len(returns_array)

        tail_losses = np.maximum.accumulate(-returns_array)
        tail = tail_losses[n - 1]
        max_tail = tail[-1] if len(tail) > 0 else 0

        if max_tail == 0:
            return 0.0

        expected_shortfall = np.mean(tail)

        if expected_shortfall == 0:
            return 0.0

        return expected_shortfall / max_tail

    def calculate_value_at_risk(self, returns: List[float], confidence: float = 0.95) -> float:
        """计算VaR（在险价值）"""
        try:
            self._log_request_start("calculate_value_at_risk", {"confidence": confidence, "data_points": len(returns)})

            if not returns or len(returns) < 2:
                return 0.0

            confidence_levels = [0.90, 0.95, 0.99]
            var_levels = []

            for conf in confidence_levels:
                var_at_risk = self._calculate_percentile(returns, conf * 100)
                var_levels.append(var_at_risk)

            return var_levels[1]

        except Exception as e:
            self._log_request_error("calculate_value_at_risk", e)
            return 0.0

    def calculate_conditional_value_at_risk(self, returns: List[float], alpha: float = 0.95) -> float:
        """计算CVaR（条件在险价值）"""
        try:
            self._log_request_start(
                "calculate_conditional_value_at_risk", {"alpha": alpha, "data_points": len(returns)}
            )

            cvar = self._calculate_cvar(returns, alpha)

            return cvar

        except Exception as e:
            self._log_request_error("calculate_conditional_value_at_risk", e)
            return 0.0

    def clear_cache(self) -> None:
        """清空计算缓存"""
        self.cache.clear()
        self.benchmark_returns = None
        self.logger.info("计算缓存已清空")

    def get_cache_size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)
