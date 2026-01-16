"""
策略结果正确性校验系统
提供策略回测结果与基准结果的对比验证，确保量化策略的准确性
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json

from prometheus_client import Counter, Gauge, Histogram

# ==================== 校验指标 ====================

STRATEGY_VALIDATION_COUNT = Counter(
    "strategy_validation_total", "策略校验总次数", ["strategy_name", "result"]
)

STRATEGY_ACCURACY_SCORE = Gauge(
    "strategy_accuracy_score", "策略准确性评分(0-100)", ["strategy_name"]
)

STRATEGY_VALIDATION_TIME = Histogram(
    "strategy_validation_duration_seconds",
    "策略校验耗时(秒)",
    ["strategy_name"],
    buckets=[1, 5, 10, 30, 60, 300],
)

BENCHMARK_DEVIATION = Gauge(
    "strategy_benchmark_deviation_percent",
    "策略结果与基准偏差(%)",
    ["strategy_name", "metric"],
)

# ==================== 数据结构 ====================


@dataclass
class ValidationResult:
    """校验结果"""

    strategy_name: str
    timestamp: datetime
    is_valid: bool
    accuracy_score: float
    deviations: Dict[str, float]
    benchmark_comparison: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None


@dataclass
class BenchmarkResult:
    """基准结果"""

    strategy_name: str
    total_return: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    total_trades: int
    avg_profit_per_trade: float
    hash: str  # 用于校验完整性


class StrategyValidator:
    """策略校验器"""

    def __init__(self):
        self.benchmarks: Dict[str, BenchmarkResult] = {}
        self.validation_history: List[ValidationResult] = []
        self.max_history_size = 1000

    def register_benchmark(self, strategy_name: str, benchmark_result: BenchmarkResult):
        """注册策略基准结果"""
        self.benchmarks[strategy_name] = benchmark_result
        print(f"✅ 已注册策略 '{strategy_name}' 的基准结果")

    def create_benchmark_from_backtest(
        self, strategy_name: str, backtest_results: Dict[str, Any]
    ) -> BenchmarkResult:
        """从回测结果创建基准"""
        # 计算关键指标
        returns = backtest_results.get("returns", [])
        trades = backtest_results.get("trades", [])

        if not returns:
            raise ValueError("回测结果缺少收益数据")

        # 总收益率
        total_return = (1 + pd.Series(returns)).prod() - 1

        # 年化收益率（假设日频数据）
        days_per_year = 252
        annualized_return = (1 + total_return) ** (days_per_year / len(returns)) - 1

        # 最大回撤
        cumulative = (1 + pd.Series(returns)).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # Sharpe比率（假设无风险利率为3%）
        risk_free_rate = 0.03
        excess_returns = pd.Series(returns) - risk_free_rate / days_per_year
        sharpe_ratio = (
            excess_returns.mean() / excess_returns.std() * np.sqrt(days_per_year)
            if excess_returns.std() > 0
            else 0
        )

        # 胜率和交易统计
        if trades:
            profitable_trades = [t for t in trades if t.get("profit", 0) > 0]
            win_rate = len(profitable_trades) / len(trades)
            total_trades = len(trades)
            avg_profit_per_trade = sum(t.get("profit", 0) for t in trades) / len(trades)
        else:
            win_rate = 0
            total_trades = 0
            avg_profit_per_trade = 0

        # 创建结果哈希
        result_data = {
            "total_return": total_return,
            "annualized_return": annualized_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "win_rate": win_rate,
            "total_trades": total_trades,
            "avg_profit_per_trade": avg_profit_per_trade,
        }
        result_hash = hashlib.sha256(
            json.dumps(result_data, sort_keys=True).encode()
        ).hexdigest()

        benchmark = BenchmarkResult(
            strategy_name=strategy_name,
            total_return=total_return,
            annualized_return=annualized_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate,
            total_trades=total_trades,
            avg_profit_per_trade=avg_profit_per_trade,
            hash=result_hash,
        )

        self.register_benchmark(strategy_name, benchmark)
        return benchmark

    def validate_strategy_result(
        self, strategy_name: str, current_results: Dict[str, Any]
    ) -> ValidationResult:
        """校验策略结果"""
        start_time = datetime.now()

        try:
            # 获取基准结果
            benchmark = self.benchmarks.get(strategy_name)
            if not benchmark:
                raise ValueError(f"未找到策略 '{strategy_name}' 的基准结果")

            # 计算当前结果的关键指标
            current_metrics = self._calculate_metrics(current_results)

            # 比较各项指标的偏差
            deviations = {}
            benchmark_dict = {
                "total_return": benchmark.total_return,
                "annualized_return": benchmark.annualized_return,
                "max_drawdown": benchmark.max_drawdown,
                "sharpe_ratio": benchmark.sharpe_ratio,
                "win_rate": benchmark.win_rate,
                "total_trades": benchmark.total_trades,
                "avg_profit_per_trade": benchmark.avg_profit_per_trade,
            }

            for metric, benchmark_value in benchmark_dict.items():
                current_value = current_metrics.get(metric, 0)
                if benchmark_value != 0:
                    deviation = (
                        abs(current_value - benchmark_value)
                        / abs(benchmark_value)
                        * 100
                    )
                else:
                    deviation = abs(current_value) * 100 if current_value != 0 else 0
                deviations[metric] = deviation

            # 计算准确性评分（偏差越小评分越高）
            max_allowed_deviation = 5.0  # 5%以内认为准确
            accuracy_score = max(0, 100 - sum(deviations.values()) / len(deviations))

            # 判定是否通过校验
            is_valid = all(
                deviation <= max_allowed_deviation for deviation in deviations.values()
            )

            # 创建校验结果
            result = ValidationResult(
                strategy_name=strategy_name,
                timestamp=datetime.now(),
                is_valid=is_valid,
                accuracy_score=accuracy_score,
                deviations=deviations,
                benchmark_comparison={
                    "benchmark": benchmark_dict,
                    "current": current_metrics,
                },
                execution_time=(datetime.now() - start_time).total_seconds(),
            )

            # 记录到历史
            self.validation_history.append(result)
            if len(self.validation_history) > self.max_history_size:
                self.validation_history = self.validation_history[
                    -self.max_history_size :
                ]

            # 更新监控指标
            self._update_monitoring_metrics(result)

            return result

        except Exception as e:
            error_result = ValidationResult(
                strategy_name=strategy_name,
                timestamp=datetime.now(),
                is_valid=False,
                accuracy_score=0,
                deviations={},
                benchmark_comparison={},
                execution_time=(datetime.now() - start_time).total_seconds(),
                error_message=str(e),
            )

            STRATEGY_VALIDATION_COUNT.labels(
                strategy_name=strategy_name, result="error"
            ).inc()
            return error_result

    def _calculate_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """计算策略关键指标"""
        returns = results.get("returns", [])
        trades = results.get("trades", [])

        if not returns:
            return {}

        # 总收益率
        total_return = (1 + pd.Series(returns)).prod() - 1

        # 年化收益率
        days_per_year = 252
        annualized_return = (1 + total_return) ** (days_per_year / len(returns)) - 1

        # 最大回撤
        cumulative = (1 + pd.Series(returns)).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # Sharpe比率
        risk_free_rate = 0.03
        excess_returns = pd.Series(returns) - risk_free_rate / days_per_year
        sharpe_ratio = (
            excess_returns.mean() / excess_returns.std() * np.sqrt(days_per_year)
            if excess_returns.std() > 0
            else 0
        )

        # 交易统计
        if trades:
            profitable_trades = [t for t in trades if t.get("profit", 0) > 0]
            win_rate = len(profitable_trades) / len(trades)
            total_trades = len(trades)
            avg_profit_per_trade = sum(t.get("profit", 0) for t in trades) / len(trades)
        else:
            win_rate = 0
            total_trades = 0
            avg_profit_per_trade = 0

        return {
            "total_return": total_return,
            "annualized_return": annualized_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "win_rate": win_rate,
            "total_trades": total_trades,
            "avg_profit_per_trade": avg_profit_per_trade,
        }

    def _update_monitoring_metrics(self, result: ValidationResult):
        """更新监控指标"""
        # 校验计数
        result_label = "passed" if result.is_valid else "failed"
        STRATEGY_VALIDATION_COUNT.labels(
            strategy_name=result.strategy_name, result=result_label
        ).inc()

        # 准确性评分
        STRATEGY_ACCURACY_SCORE.labels(strategy_name=result.strategy_name).set(
            result.accuracy_score
        )

        # 校验耗时
        STRATEGY_VALIDATION_TIME.labels(strategy_name=result.strategy_name).observe(
            result.execution_time
        )

        # 基准偏差
        for metric, deviation in result.deviations.items():
            BENCHMARK_DEVIATION.labels(
                strategy_name=result.strategy_name, metric=metric
            ).set(deviation)

    def get_validation_history(
        self, strategy_name: Optional[str] = None, limit: int = 50
    ) -> List[ValidationResult]:
        """获取校验历史"""
        history = self.validation_history
        if strategy_name:
            history = [r for r in history if r.strategy_name == strategy_name]

        return history[-limit:]

    def get_validation_summary(
        self, strategy_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取校验汇总统计"""
        history = self.get_validation_history(strategy_name)

        if not history:
            return {}

        total_validations = len(history)
        passed_validations = len([r for r in history if r.is_valid])
        success_rate = passed_validations / total_validations * 100

        avg_accuracy = sum(r.accuracy_score for r in history) / len(history)
        avg_execution_time = sum(r.execution_time for r in history) / len(history)

        return {
            "total_validations": total_validations,
            "passed_validations": passed_validations,
            "success_rate": success_rate,
            "average_accuracy_score": avg_accuracy,
            "average_execution_time": avg_execution_time,
            "latest_validation": history[-1] if history else None,
        }


# ==================== 全局实例 ====================

strategy_validator = StrategyValidator()

# ==================== 便捷函数 ====================


def register_strategy_benchmark(strategy_name: str, backtest_results: Dict[str, Any]):
    """便捷函数：注册策略基准"""
    return strategy_validator.create_benchmark_from_backtest(
        strategy_name, backtest_results
    )


def validate_strategy(
    strategy_name: str, current_results: Dict[str, Any]
) -> ValidationResult:
    """便捷函数：校验策略结果"""
    return strategy_validator.validate_strategy_result(strategy_name, current_results)


def get_strategy_validation_summary(
    strategy_name: Optional[str] = None,
) -> Dict[str, Any]:
    """便捷函数：获取校验汇总"""
    return strategy_validator.get_validation_summary(strategy_name)
