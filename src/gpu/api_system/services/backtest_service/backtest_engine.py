"""
回测服务
Backtest Service
"""

import json
import logging
import queue
import time
from datetime import datetime
from typing import Any, Dict

import numpy as np
import pandas as pd

from src.gpu.api_system.utils.gpu_utils import GPUResourceManager

try:
    from src.gpu.api_system.api_proto.backtest_pb2 import (
        BacktestRequest,
        BatchRequest,
        BatchResponse,
        HistoryResponse,
        OptimizationResult,
        ParameterOptimizationRequest,
        PerformanceMetrics,
        QueryRequest,
        QueryResponse,
        TaskResponse,
    )
    from src.gpu.api_system.api_proto.backtest_pb2_grpc import BacktestServiceServicer
except ImportError:
    import sys

    sys.path.append("/opt/claude/mystocks_spec/src/gpu/api_system/api_proto")
    from backtest_pb2 import (
        BacktestRequest,
        PerformanceMetrics,
    )


logger = logging.getLogger(__name__)

class BacktestEngine:
    """回测引擎"""

    def __init__(self, gpu_manager: GPUResourceManager):
        self.gpu_manager = gpu_manager
        self.strategy_cache = {}
        self.result_cache = {}
        self.processing_queue = queue.Queue()
        self.max_concurrent_backtests = 5

    def run_backtest(self, request: BacktestRequest) -> Dict[str, Any]:
        """执行回测"""
        try:
            logger.info("开始执行回测: %s", request.backtest_id)
            start_time = time.time()

            # 数据预处理
            market_data = self._prepare_market_data(request)

            # 策略加载
            strategy = self._load_strategy(request.strategy_type, request.strategy_config)

            # 回测执行
            if self.gpu_manager.get_available_gpu_count() > 0:
                results = self._run_backtest_gpu(market_data, strategy, request)
            else:
                results = self._run_backtest_cpu(market_data, strategy, request)

            # 计算性能指标
            performance_metrics = self._calculate_performance_metrics(results, request)

            # 生成报告
            backtest_report = self._generate_backtest_report(results, performance_metrics)

            processing_time = time.time() - start_time

            results = {
                "backtest_id": request.backtest_id,
                "status": "completed",
                "processing_time": processing_time,
                "market_data_points": len(market_data),
                "backtest_report": backtest_report,
                "performance_metrics": performance_metrics,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info("回测完成: %s, 耗时: %s秒", request.backtest_id, processing_time)
            return results

        except Exception as e:
            logger.error("回测执行失败: %s, 错误: %s", request.backtest_id, e)
            return {
                "backtest_id": request.backtest_id,
                "status": "failed",
                "error_message": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _prepare_market_data(self, request: BacktestRequest) -> pd.DataFrame:
        """准备市场数据"""
        # 这里应该从数据库获取实际的市场数据
        # 当前模拟数据
        dates = pd.date_range(start=request.start_date, end=request.end_date, freq="D")
        n_points = len(dates)

        # 生成模拟价格数据
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, n_points)
        prices = [100.0]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))

        market_data = pd.DataFrame(
            {
                "date": dates,
                "open": prices,
                "high": [p * 1.01 for p in prices],
                "low": [p * 0.99 for p in prices],
                "close": prices,
                "volume": np.random.randint(10000, 100000, n_points),
            }
        )

        return market_data

    def _load_strategy(self, strategy_type: str, strategy_config: Dict) -> Any:
        """加载策略"""
        strategy_key = f"{strategy_type}_{hash(json.dumps(strategy_config, sort_keys=True))}"

        if strategy_key in self.strategy_cache:
            return self.strategy_cache[strategy_key]

        # 根据策略类型创建策略
        if strategy_type == "trend_following":
            strategy = TrendFollowingStrategy(strategy_config)
        elif strategy_type == "momentum":
            strategy = MomentumStrategy(strategy_config)
        elif strategy_type == "mean_reversion":
            strategy = MeanReversionStrategy(strategy_config)
        elif strategy_type == "arbitrage":
            strategy = ArbitrageStrategy(strategy_config)
        else:
            raise ValueError(f"不支持策略类型: {strategy_type}")

        self.strategy_cache[strategy_key] = strategy
        return strategy

    def _run_backtest_gpu(self, market_data: pd.DataFrame, strategy: Any, request: BacktestRequest) -> Dict[str, Any]:
        """GPU加速回测"""
        try:
            # 分配GPU资源
            gpu_id = self.gpu_manager.allocate_gpu(request.backtest_id, priority="medium", memory_required=1024)

            if gpu_id:
                logger.info("使用GPU %s 执行回测", gpu_id)

                # 这里应该使用cuDF进行GPU加速计算
                # 当前模拟GPU处理
                results = strategy.run_backtest(market_data)

                # 释放GPU资源
                self.gpu_manager.release_gpu(request.backtest_id, gpu_id)

                return {"results": results, "gpu_used": True, "gpu_id": gpu_id}
            else:
                # GPU资源不足，回退到CPU
                logger.warning("GPU资源不足，使用CPU执行回测")
                return self._run_backtest_cpu(market_data, strategy, request)

        except Exception as e:
            logger.error("GPU回测失败: %s", e)
            return self._run_backtest_cpu(market_data, strategy, request)

    def _run_backtest_cpu(self, market_data: pd.DataFrame, strategy: Any, request: BacktestRequest) -> Dict[str, Any]:
        """CPU回测"""
        logger.info("使用CPU执行回测")
        results = strategy.run_backtest(market_data)
        return {"results": results, "gpu_used": False}

    def _calculate_performance_metrics(self, backtest_results: Dict, request: BacktestRequest) -> PerformanceMetrics:
        """计算性能指标"""
        results = backtest_results["results"]

        # 基础指标计算
        total_return = results.get("total_return", 0.0)
        annual_return = total_return * (252 / len(results.get("dates", [])))
        volatility = results.get("volatility", 0.0)
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0.0
        max_drawdown = results.get("max_drawdown", 0.0)

        # 风险指标
        var_95 = results.get("var_95", 0.0)
        var_99 = results.get("var_99", 0.0)
        beta = results.get("beta", 0.0)
        alpha = results.get("alpha", 0.0)

        # 交易统计
        total_trades = results.get("total_trades", 0)
        winning_trades = results.get("winning_trades", 0)
        losing_trades = results.get("losing_trades", 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0

        return PerformanceMetrics(
            total_return=total_return,
            annual_return=annual_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            var_95=var_95,
            var_99=var_99,
            beta=beta,
            alpha=alpha,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            timestamp=datetime.now().isoformat(),
        )

    def _generate_backtest_report(self, results: Dict, performance_metrics: PerformanceMetrics) -> Dict[str, Any]:
        """生成回测报告"""
        return {
            "summary": {
                "total_return": f"{performance_metrics.total_return:.2%}",
                "annual_return": f"{performance_metrics.annual_return:.2%}",
                "sharpe_ratio": f"{performance_metrics.sharpe_ratio:.2f}",
                "max_drawdown": f"{performance_metrics.max_drawdown:.2%}",
                "win_rate": f"{performance_metrics.win_rate:.2%}",
            },
            "risk_metrics": {
                "volatility": f"{performance_metrics.volatility:.2%}",
                "var_95": f"{performance_metrics.var_95:.2%}",
                "var_99": f"{performance_metrics.var_99:.2%}",
                "beta": f"{performance_metrics.beta:.2f}",
                "alpha": f"{performance_metrics.alpha:.2f}",
            },
            "trading_statistics": {
                "total_trades": performance_metrics.total_trades,
                "winning_trades": performance_metrics.winning_trades,
                "losing_trades": performance_metrics.losing_trades,
                "win_rate": f"{performance_metrics.win_rate:.2%}",
            },
            "gpu_acceleration": results.get("gpu_used", False),
            "gpu_id": results.get("gpu_id"),
            "generation_time": datetime.now().isoformat(),
        }


class TrendFollowingStrategy:
    """趋势跟踪策略"""

    def __init__(self, config: Dict):
        self.config = config
        self.ma_window = config.get("ma_window", 20)
        self.rsi_window = config.get("rsi_window", 14)
        self.entry_threshold = config.get("entry_threshold", 0.02)
        self.exit_threshold = config.get("exit_threshold", 0.01)

    def run_backtest(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """执行趋势跟踪策略回测"""
        df = market_data.copy()

        # 计算移动平均
        df["ma"] = df["close"].rolling(window=self.ma_window).mean()

        # 计算RSI
        df["rsi"] = self._calculate_rsi(df["close"])

        # 生成交易信号
        df["signal"] = 0
        df.loc[df["close"] > df["ma"] * (1 + self.entry_threshold), "signal"] = 1
        df.loc[df["close"] < df["ma"] * (1 - self.exit_threshold), "signal"] = -1

        # 计算收益
        df["returns"] = df["close"].pct_change()
        df["strategy_returns"] = df["signal"].shift(1) * df["returns"]

        # 计算累计收益
        df["cumulative_returns"] = (1 + df["strategy_returns"]).cumprod()

        return {
            "total_return": df["cumulative_returns"].iloc[-1] - 1,
            "annual_return": df["strategy_returns"].mean() * 252,
            "volatility": df["strategy_returns"].std() * np.sqrt(252),
            "sharpe_ratio": (df["strategy_returns"].mean() * 252) / (df["strategy_returns"].std() * np.sqrt(252)),
            "max_drawdown": (df["cumulative_returns"].cummax() - df["cumulative_returns"]).max(),
            "total_trades": abs(df["signal"]).sum(),
            "winning_trades": (df["strategy_returns"] > 0).sum(),
            "dates": df["date"].tolist(),
            "returns": df["strategy_returns"].tolist(),
        }

    def _calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=self.rsi_window).mean()
        avg_loss = loss.rolling(window=self.rsi_window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


class MomentumStrategy:
    """动量策略"""

    def __init__(self, config: Dict):
        self.config = config
        self.lookback_period = config.get("lookback_period", 10)
        self.entry_threshold = config.get("entry_threshold", 0.05)
        self.exit_threshold = config.get("exit_threshold", 0.03)

    def run_backtest(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """执行动量策略回测"""
        df = market_data.copy()

        # 计算动量指标
        df["momentum"] = df["close"].pct_change(self.lookback_period)

        # 生成交易信号
        df["signal"] = 0
        df.loc[df["momentum"] > self.entry_threshold, "signal"] = 1
        df.loc[df["momentum"] < -self.exit_threshold, "signal"] = -1

        # 计算收益
        df["returns"] = df["close"].pct_change()
        df["strategy_returns"] = df["signal"].shift(1) * df["returns"]

        # 计算累计收益
        df["cumulative_returns"] = (1 + df["strategy_returns"]).cumprod()

        return {
            "total_return": df["cumulative_returns"].iloc[-1] - 1,
            "annual_return": df["strategy_returns"].mean() * 252,
            "volatility": df["strategy_returns"].std() * np.sqrt(252),
            "sharpe_ratio": (df["strategy_returns"].mean() * 252) / (df["strategy_returns"].std() * np.sqrt(252)),
            "max_drawdown": (df["cumulative_returns"].cummax() - df["cumulative_returns"]).max(),
            "total_trades": abs(df["signal"]).sum(),
            "winning_trades": (df["strategy_returns"] > 0).sum(),
            "dates": df["date"].tolist(),
            "returns": df["strategy_returns"].tolist(),
        }


class MeanReversionStrategy:
    """均值回归策略"""

    def __init__(self, config: Dict):
        self.config = config
        self.bollinger_window = config.get("bollinger_window", 20)
        self.bollinger_std = config.get("bollinger_std", 2)
        self.entry_threshold = config.get("entry_threshold", 1.5)
        self.exit_threshold = config.get("exit_threshold", 0.5)

    def run_backtest(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """执行均值回归策略回测"""
        df = market_data.copy()

        # 计算布林带
        df["ma"] = df["close"].rolling(window=self.bollinger_window).mean()
        df["std"] = df["close"].rolling(window=self.bollinger_window).std()
        df["upper_band"] = df["ma"] + (df["std"] * self.bollinger_std)
        df["lower_band"] = df["ma"] - (df["std"] * self.bollinger_std)

        # 计算z-score
        df["z_score"] = (df["close"] - df["ma"]) / df["std"]

        # 生成交易信号
        df["signal"] = 0
        df.loc[df["z_score"] < -self.entry_threshold, "signal"] = 1
        df.loc[df["z_score"] > self.entry_threshold, "signal"] = -1
        df.loc[abs(df["z_score"]) < self.exit_threshold, "signal"] = 0

        # 计算收益
        df["returns"] = df["close"].pct_change()
        df["strategy_returns"] = df["signal"].shift(1) * df["returns"]

        # 计算累计收益
        df["cumulative_returns"] = (1 + df["strategy_returns"]).cumprod()

        return {
            "total_return": df["cumulative_returns"].iloc[-1] - 1,
            "annual_return": df["strategy_returns"].mean() * 252,
            "volatility": df["strategy_returns"].std() * np.sqrt(252),
            "sharpe_ratio": (df["strategy_returns"].mean() * 252) / (df["strategy_returns"].std() * np.sqrt(252)),
            "max_drawdown": (df["cumulative_returns"].cummax() - df["cumulative_returns"]).max(),
            "total_trades": abs(df["signal"]).sum(),
            "winning_trades": (df["strategy_returns"] > 0).sum(),
            "dates": df["date"].tolist(),
            "returns": df["strategy_returns"].tolist(),
        }


class ArbitrageStrategy:
    """套利策略"""

    def __init__(self, config: Dict):
        self.config = config
        self.spread_threshold = config.get("spread_threshold", 0.02)
        self.mean_reversion_window = config.get("mean_reversion_window", 20)

    def run_backtest(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """执行套利策略回测"""
        df = market_data.copy()

        # 模拟价差数据（实际应该来自不同市场）
        df["spread"] = df["close"] - df["open"]
        df["spread_ma"] = df["spread"].rolling(window=self.mean_reversion_window).mean()
        df["spread_std"] = df["spread"].rolling(window=self.mean_reversion_window).std()

        # 生成交易信号
        df["signal"] = 0
        df.loc[df["spread"] < df["spread_ma"] - df["spread_std"], "signal"] = 1
        df.loc[df["spread"] > df["spread_ma"] + df["spread_std"], "signal"] = -1

        # 计算收益
        df["returns"] = df["close"].pct_change()
        df["strategy_returns"] = df["signal"].shift(1) * df["returns"]

        # 计算累计收益
        df["cumulative_returns"] = (1 + df["strategy_returns"]).cumprod()

        return {
            "total_return": df["cumulative_returns"].iloc[-1] - 1,
            "annual_return": df["strategy_returns"].mean() * 252,
            "volatility": df["strategy_returns"].std() * np.sqrt(252),
            "sharpe_ratio": (df["strategy_returns"].mean() * 252) / (df["strategy_returns"].std() * np.sqrt(252)),
            "max_drawdown": (df["cumulative_returns"].cummax() - df["cumulative_returns"]).max(),
            "total_trades": abs(df["signal"]).sum(),
            "winning_trades": (df["strategy_returns"] > 0).sum(),
            "dates": df["date"].tolist(),
            "returns": df["strategy_returns"].tolist(),
        }


