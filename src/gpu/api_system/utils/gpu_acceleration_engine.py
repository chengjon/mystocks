"""
GPU加速引擎
GPU Acceleration Engine
"""

import logging
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Union
from datetime import datetime
import cupy as cp
from cuml.linear_model import LinearRegression, Ridge, Lasso
from cuml.ensemble import RandomForestRegressor
from cuml.preprocessing import StandardScaler as GPUStandardScaler
import cudf
from concurrent.futures import ThreadPoolExecutor

from src.utils.gpu_utils import GPUResourceManager
from src.utils.monitoring import MetricsCollector

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


class FeatureCalculationGPU:
    """GPU加速特征计算引擎"""

    def __init__(self, gpu_manager: GPUResourceManager):
        self.gpu_manager = gpu_manager
        self.feature_cache = {}

    def calculate_features_gpu(self, data: pd.DataFrame, feature_types: List[str] = None) -> Dict[str, Any]:
        """GPU加速特征计算"""
        try:
            logger.info("开始GPU特征计算: %s 数据点", len(data))

            # 转换数据到GPU
            gpu_start = time.time()
            gpu_df = cudf.DataFrame.from_pandas(data)

            features = {}

            # 技术指标
            if not feature_types or "technical" in feature_types:
                features["technical"] = self._calculate_technical_features(gpu_df)

            # 统计特征
            if not feature_types or "statistical" in feature_types:
                features["statistical"] = self._calculate_statistical_features(gpu_df)

            # 波动率特征
            if not feature_types or "volatility" in feature_types:
                features["volatility"] = self._calculate_volatility_features(gpu_df)

            # 量价特征
            if not feature_types or "volume_price" in feature_types:
                features["volume_price"] = self._calculate_volume_price_features(gpu_df)

            # 计算时间
            calculation_time = time.time() - gpu_start

            features["metadata"] = {
                "calculation_time": calculation_time,
                "data_points": len(data),
                "gpu_memory_used_mb": self.gpu_manager.get_gpu_memory_usage(),
                "feature_types": list(features.keys()),
            }

            logger.info("GPU特征计算完成: %s 类特征", len(features))
            return features

        except Exception as e:
            logger.error("GPU特征计算失败: %s", e)
            return {"error": str(e)}

    def _calculate_technical_features(self, gpu_df: cudf.DataFrame) -> Dict[str, Any]:
        """计算技术指标"""
        features = {}

        try:
            # 基础价格指标
            close = gpu_df["close"]

            # 移动平均线
            features["sma_5"] = close.rolling(5).mean().to_pandas().tolist()[-1]
            features["sma_10"] = close.rolling(10).mean().to_pandas().tolist()[-1]
            features["sma_20"] = close.rolling(20).mean().to_pandas().tolist()[-1]
            features["sma_50"] = close.rolling(50).mean().to_pandas().tolist()[-1]

            # 指数移动平均
            features["ema_12"] = self._gpu_ema(close.values, 12)[-1]
            features["ema_26"] = self._gpu_ema(close.values, 26)[-1]

            # MACD
            macd = features["ema_12"] - features["ema_26"]
            features["macd"] = macd
            features["macd_signal"] = self._gpu_ema(cp.array([macd] * len(close)), 9)[-1]
            features["macd_histogram"] = macd - features["macd_signal"]

            # RSI
            features["rsi"] = self._gpu_rsi(close.values, 14)[-1]

            # 布林带
            sma_20 = features["sma_20"]
            bb_std = close.rolling(20).std().to_pandas().tolist()[-1]
            features["bb_upper"] = sma_20 + 2 * bb_std
            features["bb_middle"] = sma_20
            features["bb_lower"] = sma_20 - 2 * bb_std

            return features

        except Exception as e:
            logger.error("技术指标计算失败: %s", e)
            return {}

    def _calculate_statistical_features(self, gpu_df: cudf.DataFrame) -> Dict[str, Any]:
        """计算统计特征"""
        features = {}

        try:
            close = gpu_df["close"].values

            # 基础统计量
            features["mean"] = cp.mean(close)
            features["std"] = cp.std(close)
            features["min"] = cp.min(close)
            features["max"] = cp.max(close)
            features["median"] = cp.median(close)
            features["skew"] = cp.skew(close)
            features["kurtosis"] = cp.kurtosis(close)

            # 百分位数
            features["p25"] = cp.percentile(close, 25)
            features["p75"] = cp.percentile(close, 75)
            features["p90"] = cp.percentile(close, 90)
            features["p95"] = cp.percentile(close, 95)

            return features

        except Exception as e:
            logger.error("统计特征计算失败: %s", e)
            return {}

    def _calculate_volatility_features(self, gpu_df: cudf.DataFrame) -> Dict[str, Any]:
        """计算波动率特征"""
        features = {}

        try:
            close = gpu_df["close"]
            returns = close.pct_change().dropna()

            # 历史波动率
            features["volatility_20d"] = cp.std(returns) * cp.sqrt(252)
            features["volatility_60d"] = cp.std(returns.rolling(60)) * cp.sqrt(252)

            # 波动率聚类
            features["volatility_clustering"] = self._calculate_volatility_clustering(returns)

            return features

        except Exception as e:
            logger.error("波动率特征计算失败: %s", e)
            return {}

    def _calculate_volume_price_features(self, gpu_df: cudf.DataFrame) -> Dict[str, Any]:
        """计算量价特征"""
        features = {}

        try:
            close = gpu_df["close"]
            volume = gpu_df["volume"]

            # 量价相关性
            price_change = close.pct_change()
            volume_change = volume.pct_change()

            # 计算相关性（处理NaN值）
            valid_mask = ~cp.isnan(price_change) & ~cp.isnan(volume_change)
            if cp.any(valid_mask):
                features["volume_price_correlation"] = cp.corrcoef(price_change[valid_mask], volume_change[valid_mask])[
                    0, 1
                ]
            else:
                features["volume_price_correlation"] = 0

            # 成交量加权平均价格
            features["vwap"] = cp.sum(close * volume) / cp.sum(volume)

            # OBV (On Balance Volume)
            features["obv"] = self._calculate_obv(close, volume)

            return features

        except Exception as e:
            logger.error("量价特征计算失败: %s", e)
            return {}

    def _calculate_volatility_clustering(self, returns: cp.ndarray) -> float:
        """计算波动率聚类"""
        try:
            # 计算绝对收益率
            abs_returns = cp.abs(returns)

            # 计算高波动率比例
            threshold = cp.percentile(abs_returns, 75)
            high_vol_periods = cp.sum(abs_returns > threshold)
            total_periods = len(returns)

            return high_vol_periods / total_periods if total_periods > 0 else 0

        except Exception as e:
            logger.error("波动率聚类计算失败: %s", e)
            return 0.0

    def _calculate_obv(self, close: cp.ndarray, volume: cp.ndarray) -> float:
        """计算OBV (On Balance Volume)"""
        try:
            obv = cp.zeros(len(close))

            for i in range(1, len(close)):
                if close[i] > close[i - 1]:
                    obv[i] = obv[i - 1] + volume[i]
                elif close[i] < close[i - 1]:
                    obv[i] = obv[i - 1] - volume[i]
                else:
                    obv[i] = obv[i - 1]

            return obv[-1]

        except Exception as e:
            logger.error("OBV计算失败: %s", e)
            return 0.0

    def _gpu_ema(self, prices: cp.ndarray, period: int) -> cp.ndarray:
        """GPU计算指数移动平均"""
        alpha = 2.0 / (period + 1)
        ema = cp.zeros_like(prices)
        ema[0] = prices[0]

        for i in range(1, len(prices)):
            ema[i] = alpha * prices[i] + (1 - alpha) * ema[i - 1]

        return ema

    def _gpu_rsi(self, prices: cp.ndarray, period: int) -> cp.ndarray:
        """GPU计算相对强弱指数"""
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


class OptimizationGPU:
    """GPU加速优化引擎"""

    def __init__(self, gpu_manager: GPUResourceManager):
        self.gpu_manager = gpu_manager
        self.optimization_cache = {}

    def optimize_parameters_gpu(
        self,
        objective_func,
        param_space: Dict,
        method: str = "grid_search",
        n_trials: int = 100,
    ) -> Dict[str, Any]:
        """GPU加速参数优化"""
        try:
            logger.info("开始GPU参数优化: %s", method)

            gpu_start = time.time()

            if method == "grid_search":
                result = self._grid_search_gpu(objective_func, param_space)
            elif method == "random_search":
                result = self._random_search_gpu(objective_func, param_space, n_trials)
            elif method == "bayesian":
                result = self._bayesian_optimization_gpu(objective_func, param_space, n_trials)
            else:
                raise ValueError(f"不支持的优化方法: {method}")

            optimization_time = time.time() - gpu_start

            result["optimization_time"] = optimization_time
            result["gpu_memory_used_mb"] = self.gpu_manager.get_gpu_memory_usage()
            result["method"] = method

            logger.info("GPU参数优化完成: %s", result["best_score"])
            return result

        except Exception as e:
            logger.error("GPU参数优化失败: %s", e)
            return {"error": str(e)}

    def _grid_search_gpu(self, objective_func, param_space: Dict) -> Dict[str, Any]:
        """网格搜索优化（GPU加速）"""
        try:
            # 生成参数网格
            param_grid = self._generate_param_grid(param_space)

            best_params = None
            best_score = float("-inf")

            # 遍历参数组合
            for params in param_grid:
                score = objective_func(params)

                if score > best_score:
                    best_score = score
                    best_params = params

            return {
                "best_params": best_params,
                "best_score": best_score,
                "total_evaluations": len(param_grid),
                "method": "grid_search",
            }

        except Exception as e:
            logger.error("GPU网格搜索失败: %s", e)
            raise

    def _random_search_gpu(self, objective_func, param_space: Dict, n_trials: int) -> Dict[str, Any]:
        """随机搜索优化（GPU加速）"""
        try:
            best_params = None
            best_score = float("-inf")

            for _ in range(n_trials):
                # 随机生成参数
                params = self._sample_random_params(param_space)
                score = objective_func(params)

                if score > best_score:
                    best_score = score
                    best_params = params

            return {
                "best_params": best_params,
                "best_score": best_score,
                "total_evaluations": n_trials,
                "method": "random_search",
            }

        except Exception as e:
            logger.error("GPU随机搜索失败: %s", e)
            raise

    def _bayesian_optimization_gpu(self, objective_func, param_space: Dict, n_trials: int) -> Dict[str, Any]:
        """贝叶斯优化（GPU加速）"""
        try:
            # 简化的贝叶斯优化实现
            best_params = None
            best_score = float("-inf")

            for _ in range(n_trials):
                # 使用高斯过程近似
                params = self._sample_from_gaussian_process(param_space)
                score = objective_func(params)

                if score > best_score:
                    best_score = score
                    best_params = params

            return {
                "best_params": best_params,
                "best_score": best_score,
                "total_evaluations": n_trials,
                "method": "bayesian",
            }

        except Exception as e:
            logger.error("GPU贝叶斯优化失败: %s", e)
            raise

    def _generate_param_grid(self, param_space: Dict) -> List[Dict]:
        """生成参数网格"""
        import itertools

        param_names = list(param_space.keys())
        param_values = list(param_space.values())

        # 生成所有组合
        all_combinations = itertools.product(*param_values)

        # 转换为参数字典列表
        param_grid = []
        for combination in all_combinations:
            param_dict = dict(zip(param_names, combination))
            param_grid.append(param_dict)

        return param_grid

    def _sample_random_params(self, param_space: Dict) -> Dict:
        """随机采样参数"""
        import random

        params = {}
        for param_name, param_range in param_space.items():
            if isinstance(param_range, list):
                # 离散参数
                params[param_name] = random.choice(param_range)
            else:
                # 连续参数
                params[param_name] = random.uniform(param_range[0], param_range[1])

        return params

    def _sample_from_gaussian_process(self, param_space: Dict) -> Dict:
        """从高斯过程采样参数"""
        # 简化的实现：使用正态分布采样
        params = {}
        for param_name, param_range in param_space.items():
            if isinstance(param_range, list):
                # 离散参数：使用正态分布采样然后取整
                mean = (param_range[0] + param_range[-1]) / 2
                std = (param_range[-1] - param_range[0]) / 4
                sampled = np.random.normal(mean, std)
                params[param_name] = max(param_range[0], min(param_range[-1], int(sampled)))
            else:
                # 连续参数：正态分布采样
                mean = (param_range[0] + param_range[1]) / 2
                std = (param_range[1] - param_range[0]) / 4
                sampled = np.random.normal(mean, std)
                params[param_name] = max(param_range[0], min(param_range[1], sampled))

        return params


class GPUAccelerationEngine:
    """GPU加速引擎主类"""

    def __init__(self, gpu_manager: GPUResourceManager, metrics_collector: MetricsCollector):
        self.gpu_manager = gpu_manager
        self.metrics_collector = metrics_collector

        # 初始化各个组件
        self.backtest_engine = BacktestEngineGPU(gpu_manager)
        self.ml_engine = MLTrainingGPU(gpu_manager)
        self.feature_engine = FeatureCalculationGPU(gpu_manager)
        self.optimization_engine = OptimizationGPU(gpu_manager)

        # 并发执行池
        self.executor = ThreadPoolExecutor(max_workers=4)

        logger.info("GPU加速引擎初始化完成")

    def process_batch_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """批量处理任务（并发执行）"""
        try:
            logger.info("开始批量处理 %s 个任务", len(tasks))

            # 提交任务到线程池
            futures = []
            for task in tasks:
                future = self.executor.submit(self._process_single_task, task)
                futures.append(future)

            # 收集结果
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=300)  # 5分钟超时
                    results.append(result)
                except Exception as e:
                    logger.error("任务处理失败: %s", e)
                    results.append({"status": "failed", "error": str(e)})

            logger.info("批量处理完成: %s 个结果", len(results))
            return results

        except Exception as e:
            logger.error("批量处理失败: %s", e)
            return [{"status": "failed", "error": str(e)} for _ in tasks]

    def _process_single_task(self, task: Dict) -> Dict:
        """处理单个任务"""
        try:
            task_type = task.get("type")
            task_id = task.get("task_id")

            logger.info("处理任务: %s (%s)", task_id, task_type)

            # 记录开始时间
            start_time = time.time()

            # 根据任务类型处理
            if task_type == "backtest":
                result = self.backtest_engine.run_gpu_backtest(
                    task["data"],
                    task["strategy_config"],
                    task.get("initial_capital", 1000000),
                )
            elif task_type == "ml_training":
                result = self.ml_engine.train_model_gpu(
                    task["X_train"],
                    task["y_train"],
                    task["model_type"],
                    task.get("params", {}),
                )
            elif task_type == "feature_calculation":
                result = self.feature_engine.calculate_features_gpu(task["data"], task.get("feature_types", None))
            elif task_type == "optimization":
                result = self.optimization_engine.optimize_parameters_gpu(
                    task["objective_func"],
                    task["param_space"],
                    task["method"],
                    task.get("n_trials", 100),
                )
            else:
                raise ValueError(f"不支持的任务类型: {task_type}")

            # 记录处理时间
            processing_time = time.time() - start_time

            # 更新结果
            result["task_id"] = task_id
            result["processing_time"] = processing_time
            result["gpu_memory_used_mb"] = self.gpu_manager.get_gpu_memory_usage()

            # 记录指标
            self.metrics_collector.record_task_metrics("gpu_acceleration", "success", processing_time)

            logger.info("任务完成: %s (耗时: %ss)", task_id, processing_time)
            return result

        except Exception as e:
            logger.error("任务处理失败: %s, 错误: %s", task.get("task_id", "unknown"), e)
            return {
                "task_id": task.get("task_id", "unknown"),
                "status": "failed",
                "error": str(e),
                "processing_time": (time.time() - start_time if "start_time" in locals() else 0),
            }

    def get_engine_statistics(self) -> Dict[str, Any]:
        """获取引擎统计信息"""
        try:
            stats = {
                "timestamp": datetime.now().isoformat(),
                "backtest_stats": {
                    "total_tasks": len(self.backtest_engine.cache),
                    "average_processing_time": 0,  # 可以添加统计逻辑
                    "gpu_memory_usage_mb": self.gpu_manager.get_gpu_memory_usage(),
                },
                "ml_stats": {
                    "total_models": len(self.ml_engine.models),
                    "total_scalers": len(self.ml_engine.scalers),
                    "gpu_memory_usage_mb": self.gpu_manager.get_gpu_memory_usage(),
                },
                "feature_stats": {
                    "total_calculations": len(self.feature_engine.feature_cache),
                    "gpu_memory_usage_mb": self.gpu_manager.get_gpu_memory_usage(),
                },
                "optimization_stats": {
                    "total_optimizations": len(self.optimization_engine.optimization_cache),
                    "gpu_memory_usage_mb": self.gpu_manager.get_gpu_memory_usage(),
                },
                "overall_stats": {
                    "total_tasks_processed": sum(
                        [
                            len(self.backtest_engine.cache),
                            len(self.ml_engine.models),
                            len(self.feature_engine.feature_cache),
                            len(self.optimization_engine.optimization_cache),
                        ]
                    ),
                    "gpu_memory_usage_mb": self.gpu_manager.get_gpu_memory_usage(),
                    "gpu_utilization": self.gpu_manager.get_gpu_stats().get("utilization", 0),
                },
            }

            return stats

        except Exception as e:
            logger.error("获取引擎统计信息失败: %s", e)
            return {"error": str(e)}

    def cleanup(self):
        """清理资源"""
        try:
            # 关闭线程池
            self.executor.shutdown(wait=True)

            # 清理缓存
            self.backtest_engine.cache.clear()
            self.ml_engine.models.clear()
            self.ml_engine.scalers.clear()
            self.feature_engine.feature_cache.clear()
            self.optimization_engine.optimization_cache.clear()

            logger.info("GPU加速引擎资源清理完成")

        except Exception as e:
            logger.error("资源清理失败: %s", e)
