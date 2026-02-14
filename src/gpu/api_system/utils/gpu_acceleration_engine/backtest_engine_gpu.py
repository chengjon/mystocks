"""
GPU加速引擎
GPU Acceleration Engine
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Union

import cudf
import cupy as cp
import numpy as np
import pandas as pd
from cuml.ensemble import RandomForestRegressor
from cuml.linear_model import Lasso, LinearRegression, Ridge
from cuml.preprocessing import StandardScaler as GPUStandardScaler

from src.gpu.api_system.utils.gpu_utils import GPUResourceManager
from src.gpu.api_system.utils.monitoring import MetricsCollector

logger = logging.getLogger(__name__)

class BacktestEngineGPU:
    """GPU加速回测引擎"""

    def __init__(self, gpu_manager: GPUResourceManager):
        self.gpu_manager = gpu_manager
        self.cache = {}
        self.gpu_memory_limit = 0.9  # GPU内存使用限制90%

    def run_gpu_backtest(
        self,
        stock_data: pd.DataFrame,
        strategy_config: Dict,
        initial_capital: float = 1000000,
    ) -> Dict[str, Any]:
        """运行GPU加速回测"""
        try:
            logger.info("开始GPU回测: 策略=%s, 资金=%s", strategy_config["name"], initial_capital)

            # 转换数据到GPU
            gpu_start = time.time()
            gpu_df = self._convert_to_gpu(stock_data)
            gpu_conversion_time = time.time() - gpu_start

            # 计算技术指标（GPU加速）
            indicators = self._calculate_gpu_indicators(gpu_df)

            # 应用策略信号
            signals = self._apply_strategy_gpu(gpu_df, indicators, strategy_config)

            # 模拟交易执行
            portfolio = self._simulate_trading_gpu(signals, initial_capital)

            # 计算性能指标
            performance = self._calculate_performance_gpu(portfolio, gpu_df)

            # 记录指标
            metrics = {
                "gpu_conversion_time": gpu_conversion_time,
                "processing_time": time.time() - gpu_start - gpu_conversion_time,
                "total_processing_time": time.time() - gpu_start,
                "gpu_memory_used_mb": self.gpu_manager.get_gpu_memory_usage(),
                "data_points_processed": len(stock_data),
            }

            result = {
                "status": "success",
                "strategy": strategy_config["name"],
                "performance": performance,
                "portfolio": portfolio,
                "indicators": indicators.to_dict(),
                "signals": signals.to_dict(),
                "metrics": metrics,
            }

            logger.info("GPU回测完成: %s 收益率", performance["total_return"])
            return result

        except Exception as e:
            logger.error("GPU回测失败: %s", e)
            return {"status": "failed", "error": str(e)}

    def _convert_to_gpu(self, data: pd.DataFrame) -> cudf.DataFrame:
        """将数据转换为GPU DataFrame"""
        try:
            # 检查GPU内存
            available_mem = self.gpu_manager.get_available_memory()
            required_mem = data.memory_usage(deep=True).sum() * 2  # 预估

            if required_mem > available_mem * self.gpu_memory_limit:
                raise MemoryError(f"GPU内存不足: 需要 {required_mem / 1e6:.1f}MB, 可用 {available_mem / 1e6:.1f}MB")

            # 转换到GPU
            gpu_df = cudf.DataFrame.from_pandas(data)
            logger.debug("数据已转换到GPU: %s 行", len(gpu_df))
            return gpu_df

        except Exception as e:
            logger.error("GPU数据转换失败: %s", e)
            raise

    def _calculate_gpu_indicators(self, gpu_df: cudf.DataFrame) -> cudf.DataFrame:
        """计算技术指标（GPU加速）"""
        try:
            indicators = cudf.DataFrame()

            # 价格数据
            close = gpu_df["close"].values

            # 移动平均线
            indicators["sma_5"] = gpu_df["close"].rolling(5).mean()
            indicators["sma_10"] = gpu_df["close"].rolling(10).mean()
            indicators["sma_20"] = gpu_df["close"].rolling(20).mean()
            indicators["sma_50"] = gpu_df["close"].rolling(50).mean()

            # 指数移动平均
            indicators["ema_12"] = self._gpu_ema(close, 12)
            indicators["ema_26"] = self._gpu_ema(close, 26)

            # MACD
            ema_12 = indicators["ema_12"]
            ema_26 = indicators["ema_26"]
            indicators["macd"] = ema_12 - ema_26
            indicators["macd_signal"] = indicators["macd"].rolling(9).mean()
            indicators["macd_histogram"] = indicators["macd"] - indicators["macd_signal"]

            # RSI
            indicators["rsi"] = self._gpu_rsi(close, 14)

            # 布林带
            sma_20 = indicators["sma_20"]
            indicators["bb_upper"] = sma_20 + 2 * gpu_df["close"].rolling(20).std()
            indicators["bb_middle"] = sma_20
            indicators["bb_lower"] = sma_20 - 2 * gpu_df["close"].rolling(20).std()

            # 成交量指标
            volume = gpu_df["volume"]
            indicators["volume_sma"] = volume.rolling(20).mean()
            indicators["volume_ratio"] = volume / indicators["volume_sma"]

            # 价格变动
            indicators["price_change"] = gpu_df["close"].pct_change()
            indicators["price_change_abs"] = indicators["price_change"].abs()

            return indicators.fillna(0)

        except Exception as e:
            logger.error("GPU技术指标计算失败: %s", e)
            raise

    def _gpu_ema(self, prices: cp.ndarray, period: int) -> cp.ndarray:
        """GPU计算指数移动平均"""
        try:
            alpha = 2.0 / (period + 1)
            ema = cp.zeros_like(prices)
            ema[0] = prices[0]

            for i in range(1, len(prices)):
                ema[i] = alpha * prices[i] + (1 - alpha) * ema[i - 1]

            return ema

        except Exception as e:
            logger.error("GPU EMA计算失败: %s", e)
            raise

    def _gpu_rsi(self, prices: cp.ndarray, period: int) -> cp.ndarray:
        """GPU计算相对强弱指数"""
        try:
            deltas = cp.diff(prices)
            gains = cp.where(deltas > 0, deltas, 0)
            losses = cp.where(deltas < 0, -deltas, 0)

            # 计算平均收益和损失
            avg_gains = cp.convolve(gains, cp.ones(period), "valid") / period
            avg_losses = cp.convolve(losses, cp.ones(period), "valid") / period

            # RSI计算
            rs = avg_gains / (avg_losses + 1e-8)
            rsi = 100 - (100 / (1 + rs))

            # 填充前面的NaN值
            result = cp.concatenate([cp.full(period, 50), rsi])
            return result

        except Exception as e:
            logger.error("GPU RSI计算失败: %s", e)
            raise

    def _apply_strategy_gpu(
        self, gpu_df: cudf.DataFrame, indicators: cudf.DataFrame, strategy_config: Dict
    ) -> cudf.DataFrame:
        """应用交易策略（GPU加速）"""
        try:
            strategy_type = strategy_config["type"]

            if strategy_type == "trend_following":
                signals = self._trend_following_gpu(gpu_df, indicators, strategy_config)
            elif strategy_type == "momentum":
                signals = self._momentum_strategy_gpu(gpu_df, indicators, strategy_config)
            elif strategy_type == "mean_reversion":
                signals = self._mean_reversion_gpu(gpu_df, indicators, strategy_config)
            elif strategy_type == "arbitrage":
                signals = self._arbitrage_strategy_gpu(gpu_df, indicators, strategy_config)
            else:
                raise ValueError(f"未知策略类型: {strategy_type}")

            return signals

        except Exception as e:
            logger.error("GPU策略应用失败: %s", e)
            raise

    def _trend_following_gpu(self, gpu_df: cudf.DataFrame, indicators: cudf.DataFrame, config: Dict) -> cudf.DataFrame:
        """趋势跟踪策略（GPU加速）"""
        signals = cudf.DataFrame()

        # 获取参数
        fast_ma = config.get("fast_ma", 5)
        slow_ma = config.get("slow_ma", 20)
        config.get("rsi_period", 14)
        rsi_overbought = config.get("rsi_overbought", 70)
        rsi_oversold = config.get("rsi_oversold", 30)

        # 计算信号
        fast_ma_line = gpu_df["close"].rolling(fast_ma).mean()
        slow_ma_line = gpu_df["close"].rolling(slow_ma).mean()
        rsi = indicators["rsi"]

        # 买入信号：快线上穿慢线且RSI未超买
        signals["buy"] = (
            (fast_ma_line > slow_ma_line) & (fast_ma_line.shift(1) <= slow_ma_line.shift(1)) & (rsi < rsi_overbought)
        ).astype(int)

        # 卖出信号：快线下穿慢线且RSI未超卖
        signals["sell"] = (
            (fast_ma_line < slow_ma_line) & (fast_ma_line.shift(1) >= slow_ma_line.shift(1)) & (rsi > rsi_oversold)
        ).astype(int)

        return signals.fillna(0)

    def _momentum_strategy_gpu(
        self, gpu_df: cudf.DataFrame, indicators: cudf.DataFrame, config: Dict
    ) -> cudf.DataFrame:
        """动量策略（GPU加速）"""
        signals = cudf.DataFrame()

        # 获取参数
        lookback_period = config.get("lookback_period", 10)
        momentum_threshold = config.get("momentum_threshold", 0.02)
        volume_threshold = config.get("volume_threshold", 1.5)

        # 计算动量
        momentum = gpu_df["close"].pct_change(lookback_period)
        volume_ratio = indicators["volume_ratio"]

        # 买入信号：正动量且成交量放大
        signals["buy"] = ((momentum > momentum_threshold) & (volume_ratio > volume_threshold)).astype(int)

        # 卖出信号：负动量
        signals["sell"] = (momentum < -momentum_threshold).astype(int)

        return signals.fillna(0)

    def _mean_reversion_gpu(self, gpu_df: cudf.DataFrame, indicators: cudf.DataFrame, config: Dict) -> cudf.DataFrame:
        """均值回归策略（GPU加速）"""
        signals = cudf.DataFrame()

        # 获取参数
        config.get("bb_period", 20)
        config.get("bb_std", 2)
        config.get("rsi_period", 14)
        rsi_threshold = config.get("rsi_threshold", 50)

        # 布林带信号
        bb_upper = indicators["bb_upper"]
        bb_lower = indicators["bb_lower"]
        bb_middle = indicators["bb_middle"]
        current_price = gpu_df["close"]
        rsi = indicators["rsi"]

        # 买入信号：价格接近下轨且RSI显示超卖
        signals["buy"] = (
            (current_price <= bb_lower)
            | ((current_price <= bb_middle - 0.5 * (bb_upper - bb_lower)) & (rsi < rsi_threshold))
        ).astype(int)

        # 卖出信号：价格接近上轨且RSI显示超买
        signals["sell"] = (
            (current_price >= bb_upper)
            | ((current_price >= bb_middle + 0.5 * (bb_upper - bb_lower)) & (rsi > rsi_threshold))
        ).astype(int)

        return signals.fillna(0)

    def _arbitrage_strategy_gpu(
        self, gpu_df: cudf.DataFrame, indicators: cudf.DataFrame, config: Dict
    ) -> cudf.DataFrame:
        """套利策略（GPU加速）"""
        signals = cudf.DataFrame()

        # 获取参数
        spread_threshold = config.get("spread_threshold", 0.01)
        config.get("reversion_speed", 0.1)

        # 简化的套利信号（基于价格偏离）
        price_deviation = indicators["price_change_abs"].rolling(20).mean()

        # 买入信号：价格偏离正向且预期回归
        signals["buy"] = ((price_deviation > spread_threshold) & (price_deviation.shift(1) > price_deviation)).astype(
            int
        )

        # 卖出信号：价格偏离负向且预期回归
        signals["sell"] = ((price_deviation > spread_threshold) & (price_deviation.shift(1) < price_deviation)).astype(
            int
        )

        return signals.fillna(0)

    def _simulate_trading_gpu(self, signals: cudf.DataFrame, initial_capital: float) -> Dict[str, Any]:
        """模拟交易执行（GPU加速）"""
        try:
            portfolio = {
                "cash": initial_capital,
                "position": 0,
                "portfolio_value": [],
                "trades": [],
            }

            current_cash = initial_capital
            current_position = 0
            position_size = initial_capital * 0.1  # 每次交易10%资金

            # 获取信号
            buy_signals = signals["buy"].values
            sell_signals = signals["sell"].values

            for i in range(len(buy_signals)):
                if buy_signals[i] == 1 and current_position == 0:
                    # 买入
                    shares = position_size / current_cash
                    current_position = shares
                    current_cash -= position_size

                    trade = {
                        "date": i,
                        "action": "BUY",
                        "shares": shares,
                        "price": 1.0,  # 简化价格
                        "value": position_size,
                    }
                    portfolio["trades"].append(trade)

                elif sell_signals[i] == 1 and current_position > 0:
                    # 卖出
                    current_cash += current_position
                    trade = {
                        "date": i,
                        "action": "SELL",
                        "shares": current_position,
                        "price": 1.0,  # 简化价格
                        "value": current_position,
                    }
                    portfolio["trades"].append(trade)
                    current_position = 0

                # 更新投资组合价值
                portfolio_value = current_cash + current_position
                portfolio["portfolio_value"].append(portfolio_value)

            return portfolio

        except Exception as e:
            logger.error("GPU交易模拟失败: %s", e)
            raise

    def _calculate_performance_gpu(self, portfolio: Dict, gpu_df: cudf.DataFrame) -> Dict[str, float]:
        """计算性能指标（GPU加速）"""
        try:
            portfolio_values = portfolio["portfolio_value"]
            if len(portfolio_values) == 0:
                return self._empty_performance()

            # 转换为CuPy数组进行GPU计算
            portfolio_values_gpu = cp.array(portfolio_values)
            returns = cp.diff(portfolio_values_gpu) / portfolio_values_gpu[:-1]

            # 基础指标
            total_return = (portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0]
            annual_return = total_return * 252 / len(portfolio_values) * 252

            # 风险指标（GPU计算）
            volatility = cp.std(returns) * cp.sqrt(252)
            max_drawdown = self._gpu_max_drawdown(portfolio_values_gpu)
            sharpe_ratio = annual_return / volatility if volatility > 0 else 0

            # 回撤相关指标
            drawdown_periods = self._gpu_drawdown_periods(portfolio_values_gpu)
            calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0

            # 交易统计
            total_trades = len(portfolio["trades"])
            winning_trades = sum(1 for trade in portfolio["trades"] if trade["action"] == "SELL")
            win_rate = winning_trades / total_trades if total_trades > 0 else 0

            return {
                "total_return": float(total_return),
                "annual_return": float(annual_return),
                "volatility": float(volatility),
                "sharpe_ratio": float(sharpe_ratio),
                "max_drawdown": float(max_drawdown),
                "calmar_ratio": float(calmar_ratio),
                "win_rate": float(win_rate),
                "total_trades": total_trades,
                "max_drawdown_periods": float(drawdown_periods),
            }

        except Exception as e:
            logger.error("GPU性能计算失败: %s", e)
            return self._empty_performance()

    def _gpu_max_drawdown(self, portfolio_values: cp.ndarray) -> float:
        """GPU计算最大回撤"""
        try:
            peak = cp.maximum.accumulate(portfolio_values)
            drawdown = (peak - portfolio_values) / peak
            return cp.max(drawdown)
        except Exception as e:
            logger.error("GPU最大回撤计算失败: %s", e)
            return 0.0

    def _gpu_drawdown_periods(self, portfolio_values: cp.ndarray) -> float:
        """GPU计算回撤期间"""
        try:
            peak = cp.maximum.accumulate(portfolio_values)
            drawdown = (peak - portfolio_values) / peak
            drawdown_periods = cp.sum(drawdown > 0)
            return float(drawdown_periods)
        except Exception as e:
            logger.error("GPU回撤期间计算失败: %s", e)
            return 0.0

    def _empty_performance(self) -> Dict[str, float]:
        """空性能指标"""
        return {
            "total_return": 0.0,
            "annual_return": 0.0,
            "volatility": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "calmar_ratio": 0.0,
            "win_rate": 0.0,
            "total_trades": 0,
            "max_drawdown_periods": 0.0,
        }


class MLTrainingGPU:
    """GPU加速机器学习训练引擎"""

    def __init__(self, gpu_manager: GPUResourceManager):
        self.gpu_manager = gpu_manager
        self.models = {}
        self.scalers = {}

    def train_model_gpu(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        model_type: str = "random_forest",
        params: Dict = None,
    ) -> Dict[str, Any]:
        """GPU加速模型训练"""
        try:
            logger.info("开始GPU模型训练: %s", model_type)

            # 转换数据到GPU
            gpu_start = time.time()
            X_train_gpu = self._convert_to_gpu(X_train)
            y_train_gpu = self._convert_to_gpu(y_train)

            # 数据标准化
            scaler = GPUStandardScaler()
            X_train_scaled = scaler.fit_transform(X_train_gpu)

            # 根据模型类型训练
            if model_type == "linear_regression":
                model = LinearRegression(**(params or {}))
            elif model_type == "ridge":
                model = Ridge(**(params or {}))
            elif model_type == "lasso":
                model = Lasso(**(params or {}))
            elif model_type == "random_forest":
                model = RandomForestRegressor(**(params or {}))
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")

            # 模型训练
            model.fit(X_train_scaled, y_train_gpu)

            # 保存模型和scaler
            model_id = f"{model_type}_{int(time.time())}"
            self.models[model_id] = model
            self.scalers[model_id] = scaler

            training_time = time.time() - gpu_start

            # 获取特征重要性
            feature_importance = None
            if hasattr(model, "feature_importances_"):
                feature_importance = model.feature_importances_.to_pandas().tolist()

            result = {
                "model_id": model_id,
                "model_type": model_type,
                "training_time": training_time,
                "feature_count": len(X_train.columns),
                "sample_count": len(X_train),
                "feature_importance": feature_importance,
                "gpu_memory_used_mb": self.gpu_manager.get_gpu_memory_usage(),
                "status": "success",
            }

            logger.info("GPU模型训练完成: %s", model_id)
            return result

        except Exception as e:
            logger.error("GPU模型训练失败: %s", e)
            return {"status": "failed", "error": str(e)}

    def predict_gpu(self, model_id: str, X_test: pd.DataFrame) -> np.ndarray:
        """GPU加速预测"""
        try:
            if model_id not in self.models:
                raise ValueError(f"模型 {model_id} 不存在")

            # 获取模型和scaler
            model = self.models[model_id]
            scaler = self.scalers[model_id]

            # 转换数据到GPU
            X_test_gpu = self._convert_to_gpu(X_test)

            # 数据标准化
            X_test_scaled = scaler.transform(X_test_gpu)

            # 预测
            predictions = model.predict(X_test_scaled)

            # 转换回CPU
            return predictions.to_pandas().values

        except Exception as e:
            logger.error("GPU预测失败: %s", e)
            raise

    def _convert_to_gpu(self, data: Union[pd.DataFrame, pd.Series]) -> Union[cudf.DataFrame, cudf.Series]:
        """将数据转换为GPU格式"""
        if isinstance(data, pd.DataFrame):
            return cudf.DataFrame.from_pandas(data)
        elif isinstance(data, pd.Series):
            return cudf.Series.from_pandas(data)
        else:
            raise TypeError("不支持的数据类型")


