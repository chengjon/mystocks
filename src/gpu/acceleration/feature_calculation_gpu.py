#!/usr/bin/env python3
"""
# 功能：GPU加速特征计算引擎
# 作者：MyStocks AI开发团队
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：GPU加速的金融特征计算和技术指标引擎
"""

import time
import logging
from typing import Dict, Any, List, Union
import numpy as np
import pandas as pd

try:
    import cupy as cp
    import cudf

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    from src.gpu.core.hardware_abstraction.resource_manager import GPUResourceManager
except ImportError:
    GPUResourceManager = Any

logger = logging.getLogger(__name__)


class FeatureCalculationGPU:
    """GPU加速特征计算引擎

    功能特性:
    ✅ GPU加速技术指标计算
    ✅ 统计特征和波动率分析
    ✅ 量价特征和相关性分析
    ✅ 智能缓存机制提升性能
    ✅ CPU回退确保兼容性
    """

    def __init__(self, gpu_manager: GPUResourceManager = None):
        """初始化特征计算引擎

        Args:
            gpu_manager: GPU资源管理器实例
        """
        self.gpu_manager = gpu_manager
        self.feature_cache = {}
        self.gpu_available = GPU_AVAILABLE and gpu_manager is not None

        if not self.gpu_available:
            logger.warning("GPU不可用，将使用CPU模式")
        else:
            logger.info("GPU特征计算引擎初始化完成")

    def calculate_features_gpu(self, data: pd.DataFrame, feature_types: List[str] = None) -> Dict[str, Any]:
        """GPU加速特征计算

        Args:
            data: 包含OHLCV数据的DataFrame
            feature_types: 要计算的特征类型列表

        Returns:
            特征计算结果字典
        """
        try:
            logger.info("开始GPU特征计算: %s 数据点", len(data))

            # 数据验证
            self._validate_data(data)

            # 生成缓存键
            cache_key = self._generate_cache_key(data, feature_types)
            if cache_key in self.feature_cache:
                logger.info("使用缓存的特征结果")
                return self.feature_cache[cache_key]

            calculation_start = time.time()

            # 转换数据到GPU
            if self.gpu_available:
                gpu_df = cudf.DataFrame.from_pandas(data)
            else:
                gpu_df = data.copy()

            features = {}

            # 计算各类特征
            if not feature_types or "technical" in feature_types:
                features["technical"] = self._calculate_technical_features(gpu_df)

            if not feature_types or "statistical" in feature_types:
                features["statistical"] = self._calculate_statistical_features(gpu_df)

            if not feature_types or "volatility" in feature_types:
                features["volatility"] = self._calculate_volatility_features(gpu_df)

            if not feature_types or "volume_price" in feature_types:
                features["volume_price"] = self._calculate_volume_price_features(gpu_df)

            if not feature_types or "momentum" in feature_types:
                features["momentum"] = self._calculate_momentum_features(gpu_df)

            if not feature_types or "pattern" in feature_types:
                features["pattern"] = self._calculate_pattern_features(gpu_df)

            # 计算元数据
            calculation_time = time.time() - calculation_start
            gpu_memory_used = 0
            if self.gpu_manager:
                gpu_memory_used = self.gpu_manager.get_gpu_memory_usage()

            features["metadata"] = {
                "calculation_time": calculation_time,
                "data_points": len(data),
                "gpu_memory_used_mb": gpu_memory_used,
                "feature_types": list(features.keys()),
                "gpu_mode": self.gpu_available,
                "cache_key": cache_key,
            }

            # 缓存结果
            self.feature_cache[cache_key] = features

            logger.info("GPU特征计算完成: %s 类特征 (%ss)", len(features), calculation_time)
            return features

        except Exception as e:
            logger.error("GPU特征计算失败: %s", e)
            return {"error": str(e), "gpu_mode": self.gpu_available}

    def _calculate_technical_features(self, df: Union[cudf.DataFrame, pd.DataFrame]) -> Dict[str, Any]:
        """计算技术指标"""
        features = {}

        try:
            # 确保必需列存在
            required_columns = ["close", "high", "low", "volume"]
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"缺少必需列: {col}")

            close = df["close"]
            high = df["high"]
            low = df["low"]
            df["volume"]

            # 移动平均线
            windows = [5, 10, 20, 50]
            for window in windows:
                if self.gpu_available:
                    sma = close.rolling(window).mean()
                    features[f"sma_{window}"] = float(sma.iloc[-1].to_pandas())
                else:
                    sma = close.rolling(window).mean()
                    features[f"sma_{window}"] = float(sma.iloc[-1])

            # 指数移动平均
            features["ema_12"] = self._calculate_ema(close, 12)
            features["ema_26"] = self._calculate_ema(close, 26)

            # MACD
            macd = features["ema_12"] - features["ema_26"]
            features["macd"] = macd
            features["macd_signal"] = self._calculate_ema(close, 9, base_values=[macd] * len(close))
            features["macd_histogram"] = macd - features["macd_signal"]

            # RSI
            features["rsi"] = self._calculate_rsi(close, 14)

            # 布林带
            bb_period = 20
            if self.gpu_available:
                sma_20 = close.rolling(bb_period).mean()
                bb_std = close.rolling(bb_period).std()
                features["bb_upper"] = float((sma_20 + 2 * bb_std).iloc[-1].to_pandas())
                features["bb_middle"] = float(sma_20.iloc[-1].to_pandas())
                features["bb_lower"] = float((sma_20 - 2 * bb_std).iloc[-1].to_pandas())
            else:
                sma_20 = close.rolling(bb_period).mean()
                bb_std = close.rolling(bb_period).std()
                features["bb_upper"] = float((sma_20 + 2 * bb_std).iloc[-1])
                features["bb_middle"] = float(sma_20.iloc[-1])
                features["bb_lower"] = float((sma_20 - 2 * bb_std).iloc[-1])

            # 布林带位置
            bb_width = features["bb_upper"] - features["bb_lower"]
            bb_position = (close.iloc[-1] - features["bb_lower"]) / bb_width if bb_width > 0 else 0.5
            features["bb_position"] = float(bb_position)

            # KDJ指标
            features["kdj_k"], features["kdj_d"], features["kdj_j"] = self._calculate_kdj(high, low, close)

            # Williams %R
            features["williams_r"] = self._calculate_williams_r(high, low, close, 14)

            return features

        except Exception as e:
            logger.error("技术指标计算失败: %s", e)
            return {}

    def _calculate_statistical_features(self, df: Union[cudf.DataFrame, pd.DataFrame]) -> Dict[str, Any]:
        """计算统计特征"""
        features = {}

        try:
            if "close" not in df.columns:
                raise ValueError("缺少close列")

            close_values = df["close"].values

            # 基础统计量
            if self.gpu_available:
                features["mean"] = float(cp.mean(close_values))
                features["std"] = float(cp.std(close_values))
                features["min"] = float(cp.min(close_values))
                features["max"] = float(cp.max(close_values))
                features["median"] = float(cp.median(close_values))
                features["skew"] = float(cp.skew(close_values))
                features["kurtosis"] = float(cp.kurtosis(close_values))
            else:
                features["mean"] = float(np.mean(close_values))
                features["std"] = float(np.std(close_values))
                features["min"] = float(np.min(close_values))
                features["max"] = float(np.max(close_values))
                features["median"] = float(np.median(close_values))
                features["skew"] = float(float(pd.Series(close_values).skew()))
                features["kurtosis"] = float(float(pd.Series(close_values).kurtosis()))

            # 百分位数
            percentiles = [25, 75, 90, 95]
            for p in percentiles:
                if self.gpu_available:
                    features[f"p{p}"] = float(cp.percentile(close_values, p))
                else:
                    features[f"p{p}"] = float(np.percentile(close_values, p))

            # 价格范围
            features["price_range"] = features["max"] - features["min"]
            features["price_range_ratio"] = features["price_range"] / features["mean"] if features["mean"] > 0 else 0

            # 变异系数
            features["cv"] = features["std"] / features["mean"] if features["mean"] > 0 else 0

            # Z-score (最新价格)
            latest_price = float(close_values[-1]) if len(close_values) > 0 else 0
            features["z_score"] = (latest_price - features["mean"]) / features["std"] if features["std"] > 0 else 0

            return features

        except Exception as e:
            logger.error("统计特征计算失败: %s", e)
            return {}

    def _calculate_volatility_features(self, df: Union[cudf.DataFrame, pd.DataFrame]) -> Dict[str, Any]:
        """计算波动率特征"""
        features = {}

        try:
            if "close" not in df.columns:
                raise ValueError("缺少close列")

            close = df["close"]
            returns = close.pct_change().dropna()

            if len(returns) < 2:
                return {}

            # 历史波动率
            volatility_periods = [20, 60, 120]
            for period in volatility_periods:
                if len(returns) >= period:
                    if self.gpu_available:
                        period_returns = returns.tail(period)
                        vol = float(cp.std(period_returns.values) * cp.sqrt(252))
                    else:
                        period_returns = returns.tail(period)
                        vol = float(np.std(period_returns) * np.sqrt(252))
                    features[f"volatility_{period}d"] = vol

            # 现期波动率
            if self.gpu_available:
                short_vol = float(cp.std(returns.tail(10).values) * cp.sqrt(252))
                features["volatility_short"] = short_vol
            else:
                short_vol = float(np.std(returns.tail(10)) * np.sqrt(252))
                features["volatility_short"] = short_vol

            # 波动率聚类
            features["volatility_clustering"] = self._calculate_volatility_clustering(returns)

            # GARCH特征（简化版）
            features["garch_effect"] = self._calculate_garch_effect(returns)

            # 波动率偏度和峰度
            if self.gpu_available:
                returns_gpu = cp.array(returns)
                features["vol_skewness"] = float(cp.skew(returns_gpu))
                features["vol_kurtosis"] = float(cp.kurtosis(returns_gpu))
            else:
                features["vol_skewness"] = float(returns.skew())
                features["vol_kurtosis"] = float(returns.kurtosis())

            return features

        except Exception as e:
            logger.error("波动率特征计算失败: %s", e)
            return {}

    def _calculate_volume_price_features(self, df: Union[cudf.DataFrame, pd.DataFrame]) -> Dict[str, Any]:
        """计算量价特征"""
        features = {}

        try:
            required_columns = ["close", "volume"]
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"缺少必需列: {col}")

            close = df["close"]
            volume = df["volume"]

            # 量价相关性
            price_change = close.pct_change()
            volume_change = volume.pct_change()

            # 处理NaN值
            valid_mask = ~(price_change.isna() | volume_change.isna())
            if valid_mask.sum() > 1:
                if self.gpu_available:
                    price_change_valid = price_change[valid_mask]
                    volume_change_valid = volume_change[valid_mask]
                    if len(price_change_valid) > 1:
                        corr_matrix = cp.corrcoef(price_change_valid, volume_change_valid)
                        features["volume_price_correlation"] = float(corr_matrix[0, 1])
                    else:
                        features["volume_price_correlation"] = 0
                else:
                    features["volume_price_correlation"] = float(
                        price_change[valid_mask].corr(volume_change[valid_mask])
                    )
            else:
                features["volume_price_correlation"] = 0

            # 成交量加权平均价格 (VWAP)
            if self.gpu_available:
                vwap = cp.sum(close.values * volume.values) / cp.sum(volume.values)
                features["vwap"] = float(vwap)
            else:
                features["vwap"] = float((close * volume).sum() / volume.sum())

            # VWAP偏离度
            latest_price = float(close.iloc[-1])
            features["vwap_deviation"] = (latest_price - features["vwap"]) / features["vwap"]

            # OBV (On Balance Volume)
            features["obv"] = self._calculate_obv(close, volume)
            features["obv_sma"] = self._calculate_sma(features["obv"], window=20, is_series=False)

            # 价量背离指标
            features["price_volume_divergence"] = self._calculate_price_volume_divergence(close, volume)

            # 成交量分布特征
            if self.gpu_available:
                volume_gpu = volume.values
                features["volume_mean"] = float(cp.mean(volume_gpu))
                features["volume_std"] = float(cp.std(volume_gpu))
                features["volume_cv"] = (
                    features["volume_std"] / features["volume_mean"] if features["volume_mean"] > 0 else 0
                )
            else:
                features["volume_mean"] = float(volume.mean())
                features["volume_std"] = float(volume.std())
                features["volume_cv"] = (
                    features["volume_std"] / features["volume_mean"] if features["volume_mean"] > 0 else 0
                )

            return features

        except Exception as e:
            logger.error("量价特征计算失败: %s", e)
            return {}

    def _calculate_momentum_features(self, df: Union[cudf.DataFrame, pd.DataFrame]) -> Dict[str, Any]:
        """计算动量特征"""
        features = {}

        try:
            if "close" not in df.columns:
                raise ValueError("缺少close列")

            close = df["close"]

            # 价格动量
            periods = [5, 10, 20, 60]
            for period in periods:
                if len(close) > period:
                    momentum = (close.iloc[-1] - close.iloc[-period - 1]) / close.iloc[-period - 1]
                    features[f"momentum_{period}d"] = float(momentum)

            # 动量排名 (在N日内的表现)
            momentum_rank_period = 20
            if len(close) > momentum_rank_period:
                recent_returns = close.pct_change().tail(momentum_rank_period)
                latest_return = recent_returns.iloc[-1]
                features["momentum_rank"] = float((recent_returns <= latest_return).sum() / len(recent_returns))

            # 加速度 (价格变化的变化率)
            if len(close) > 10:
                price_changes = close.pct_change().tail(10)
                if self.gpu_available:
                    acceleration = float(cp.diff(price_changes.values).mean())
                else:
                    acceleration = float(price_changes.diff().mean())
                features["price_acceleration"] = acceleration

            # 相对强弱
            if "high" in df.columns and "low" in df.columns:
                high = df["high"]
                low = df["low"]
                latest_high = float(high.iloc[-1])
                latest_low = float(low.iloc[-1])
                latest_close = float(close.iloc[-1])

                # Stochastic oscillator
                features["stochastic_k"] = (
                    ((latest_close - latest_low) / (latest_high - latest_low)) * 100
                    if latest_high != latest_low
                    else 50
                )

            return features

        except Exception as e:
            logger.error("动量特征计算失败: %s", e)
            return {}

    def _calculate_pattern_features(self, df: Union[cudf.DataFrame, pd.DataFrame]) -> Dict[str, Any]:
        """计算图表模式特征"""
        features = {}

        try:
            required_columns = ["high", "low", "close"]
            for col in required_columns:
                if col not in df.columns:
                    logger.warning("缺少列 %s，跳过部分模式识别", col)
                    continue

            if len(df) < 20:
                return features

            high = df["high"] if "high" in df.columns else None
            low = df["low"] if "low" in df.columns else None
            close = df["close"]

            # 支撑和阻力位
            features["support_level"], features["resistance_level"] = self._calculate_support_resistance(
                high, low, close
            )

            # 趋势强度
            features["trend_strength"] = self._calculate_trend_strength(close)

            # 价格波动模式
            features["price_pattern"] = self._identify_price_pattern(close)

            return features

        except Exception as e:
            logger.error("模式特征计算失败: %s", e)
            return {}

    # 辅助方法
    def _calculate_ema(
        self,
        prices: Union[cudf.Series, pd.Series],
        period: int,
        base_values: List[float] = None,
    ) -> float:
        """计算指数移动平均"""
        try:
            if base_values:
                # 使用基础值计算EMA（用于MACD信号线）
                if self.gpu_available:
                    series_gpu = cp.array(base_values)
                else:
                    series_gpu = np.array(base_values)
            else:
                series_gpu = prices.values

            alpha = 2.0 / (period + 1)
            ema = np.zeros_like(series_gpu)
            ema[0] = series_gpu[0]

            for i in range(1, len(series_gpu)):
                ema[i] = alpha * series_gpu[i] + (1 - alpha) * ema[i - 1]

            return float(ema[-1])

        except Exception as e:
            logger.error("EMA计算失败: %s", e)
            return 0.0

    def _calculate_rsi(self, prices: Union[cudf.Series, pd.Series], period: int) -> float:
        """计算相对强弱指数"""
        try:
            if len(prices) < period + 1:
                return 50.0

            if self.gpu_available:
                price_values = prices.values
                deltas = cp.diff(price_values)
                gains = cp.where(deltas > 0, deltas, 0)
                losses = cp.where(deltas < 0, -deltas, 0)
            else:
                price_values = prices.values
                deltas = np.diff(price_values)
                gains = np.where(deltas > 0, deltas, 0)
                losses = np.where(deltas < 0, -deltas, 0)

            # 计算平均收益和损失
            avg_gains = (
                np.convolve(
                    gains.get() if self.gpu_available else gains,
                    np.ones(period),
                    "valid",
                )
                / period
            )
            avg_losses = (
                np.convolve(
                    losses.get() if self.gpu_available else losses,
                    np.ones(period),
                    "valid",
                )
                / period
            )

            # RSI计算
            if len(avg_losses) > 0:
                rs = avg_gains[-1] / (avg_losses[-1] + 1e-8)
                rsi = 100 - (100 / (1 + rs))
                return float(np.clip(rsi, 0, 100))
            else:
                return 50.0

        except Exception as e:
            logger.error("RSI计算失败: %s", e)
            return 50.0

    def _calculate_kdj(
        self,
        high: Union[cudf.Series, pd.Series],
        low: Union[cudf.Series, pd.Series],
        close: Union[cudf.Series, pd.Series],
        period: int = 9,
    ):
        """计算KDJ指标"""
        try:
            if len(high) < period:
                return 50.0, 50.0, 50.0

            # 计算RSV
            if self.gpu_available:
                high_values = high.values
                low_values = low.values
                close_values = close.values

                highest = cp.array(
                    [cp.max(high_values[max(0, i - period + 1) : i + 1]) for i in range(len(high_values))]
                )
                lowest = cp.array([cp.min(low_values[max(0, i - period + 1) : i + 1]) for i in range(len(low_values))])
            else:
                highest = high.rolling(period).max()
                lowest = low.rolling(period).min()
                close_values = close.values

            rsv = ((close_values - lowest) / (highest - lowest + 1e-8)) * 100

            # K值和D值 (简化计算)
            if self.gpu_available:
                rsv_cpu = rsv.get()
            else:
                rsv_cpu = rsv

            k_values = np.zeros_like(rsv_cpu)
            d_values = np.zeros_like(rsv_cpu)

            k_values[0] = 50
            d_values[0] = 50

            for i in range(1, len(rsv_cpu)):
                k_values[i] = (2 / 3) * k_values[i - 1] + (1 / 3) * rsv_cpu[i]
                d_values[i] = (2 / 3) * d_values[i - 1] + (1 / 3) * k_values[i]

            j_values = 3 * k_values - 2 * d_values

            return float(k_values[-1]), float(d_values[-1]), float(j_values[-1])

        except Exception as e:
            logger.error("KDJ计算失败: %s", e)
            return 50.0, 50.0, 50.0

    def _calculate_williams_r(
        self,
        high: Union[cudf.Series, pd.Series],
        low: Union[cudf.Series, pd.Series],
        close: Union[cudf.Series, pd.Series],
        period: int,
    ) -> float:
        """计算Williams %R"""
        try:
            if len(high) < period:
                return -50.0

            if self.gpu_available:
                highest = high.rolling(period).max().iloc[-1].to_pandas()
                lowest = low.rolling(period).min().iloc[-1].to_pandas()
                latest_close = close.iloc[-1].to_pandas()
            else:
                highest = high.rolling(period).max().iloc[-1]
                lowest = low.rolling(period).min().iloc[-1]
                latest_close = close.iloc[-1]

            wr = ((highest - latest_close) / (highest - lowest + 1e-8)) * -100
            return float(np.clip(wr, -100, 0))

        except Exception as e:
            logger.error("Williams %R计算失败: %s", e)
            return -50.0

    def _calculate_volatility_clustering(self, returns: Union[cudf.Series, pd.Series]) -> float:
        """计算波动率聚类"""
        try:
            if len(returns) < 10:
                return 0.0

            # 计算绝对收益率
            if self.gpu_available:
                abs_returns = cp.abs(returns.values)
            else:
                abs_returns = np.abs(returns.values)

            # 计算高波动率比例
            threshold = np.percentile(abs_returns, 75)
            high_vol_periods = np.sum(abs_returns > threshold)
            total_periods = len(abs_returns)

            return float(high_vol_periods / total_periods if total_periods > 0 else 0)

        except Exception as e:
            logger.error("波动率聚类计算失败: %s", e)
            return 0.0

    def _calculate_garch_effect(self, returns: Union[cudf.Series, pd.Series]) -> float:
        """计算GARCH效应（简化版）"""
        try:
            if len(returns) < 20:
                return 0.0

            # 计算收益率的自相关性
            returns_squared = returns**2
            if self.gpu_available:
                returns_squared_gpu = returns_squared.values
                lag1_corr = cp.corrcoef(returns_squared_gpu[:-1], returns_squared_gpu[1:])[0, 1]
            else:
                lag1_corr = returns_squared.autocorr(lag=1)

            return float(np.abs(lag1_corr) if not np.isnan(lag1_corr) else 0)

        except Exception as e:
            logger.error("GARCH效应计算失败: %s", e)
            return 0.0

    def _calculate_obv(
        self,
        close: Union[cudf.Series, pd.Series],
        volume: Union[cudf.Series, pd.Series],
    ) -> float:
        """计算OBV (On Balance Volume)"""
        try:
            if len(close) < 2 or len(volume) < 2:
                return 0.0

            if self.gpu_available:
                close_values = close.values
                volume_values = volume.values
            else:
                close_values = close.values
                volume_values = volume.values

            obv = np.zeros(len(close_values))

            for i in range(1, len(close_values)):
                if close_values[i] > close_values[i - 1]:
                    obv[i] = obv[i - 1] + volume_values[i]
                elif close_values[i] < close_values[i - 1]:
                    obv[i] = obv[i - 1] - volume_values[i]
                else:
                    obv[i] = obv[i - 1]

            return float(obv[-1])

        except Exception as e:
            logger.error("OBV计算失败: %s", e)
            return 0.0

    def _calculate_sma(
        self,
        values: Union[List[float], np.ndarray],
        window: int,
        is_series: bool = True,
    ) -> float:
        """计算简单移动平均"""
        try:
            if is_series:
                values_array = np.array(values)
            else:
                values_array = values

            if len(values_array) < window:
                return float(np.mean(values_array))
            else:
                return float(np.mean(values_array[-window:]))

        except Exception as e:
            logger.error("SMA计算失败: %s", e)
            return 0.0

    def _calculate_price_volume_divergence(
        self,
        close: Union[cudf.Series, pd.Series],
        volume: Union[cudf.Series, pd.Series],
    ) -> float:
        """计算价量背离指标"""
        try:
            if len(close) < 10 or len(volume) < 10:
                return 0.0

            # 计算价格和成交量的趋势
            close_trend = np.polyfit(
                range(len(close)),
                close.values.get() if self.gpu_available else close.values,
                1,
            )[0]
            volume_trend = np.polyfit(
                range(len(volume)),
                volume.values.get() if self.gpu_available else volume.values,
                1,
            )[0]

            # 背离程度（趋势方向相反的程度）
            divergence = -close_trend * volume_trend
            return float(divergence)

        except Exception as e:
            logger.error("价量背离计算失败: %s", e)
            return 0.0

    def _calculate_support_resistance(
        self,
        high: Union[cudf.Series, pd.Series],
        low: Union[cudf.Series, pd.Series],
        close: Union[cudf.Series, pd.Series],
    ) -> tuple:
        """计算支撑和阻力位"""
        try:
            if len(close) < 20:
                return float(close.iloc[-1]), float(close.iloc[-1])

            # 简化的支撑阻力计算
            recent_high = float(high.tail(20).max())
            recent_low = float(low.tail(20).min())
            float(close.iloc[-1])

            # 支撑位：近期低点
            support = recent_low
            # 阻力位：近期高点
            resistance = recent_high

            return support, resistance

        except Exception as e:
            logger.error("支撑阻力计算失败: %s", e)
            return float(close.iloc[-1]), float(close.iloc[-1])

    def _calculate_trend_strength(self, close: Union[cudf.Series, pd.Series]) -> float:
        """计算趋势强度"""
        try:
            if len(close) < 10:
                return 0.0

            # 使用线性回归的R平方值作为趋势强度
            x = np.arange(len(close))
            y = close.values.get() if self.gpu_available else close.values

            # 计算线性回归
            slope, intercept = np.polyfit(x, y, 1)
            y_pred = slope * x + intercept

            # 计算R平方
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            ss_res = np.sum((y - y_pred) ** 2)

            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            return float(abs(r_squared))

        except Exception as e:
            logger.error("趋势强度计算失败: %s", e)
            return 0.0

    def _identify_price_pattern(self, close: Union[cudf.Series, pd.Series]) -> str:
        """识别价格模式"""
        try:
            if len(close) < 20:
                return "insufficient_data"

            # 简化的模式识别
            recent_prices = close.tail(20).values.get() if self.gpu_available else close.tail(20).values

            # 计算趋势
            x = np.arange(len(recent_prices))
            slope, _ = np.polyfit(x, recent_prices, 1)

            # 计算波动性
            volatility = np.std(np.diff(recent_prices))

            # 模式分类
            if abs(slope) < 0.1 * np.mean(recent_prices):
                if volatility < 0.05 * np.mean(recent_prices):
                    return "sideways_low_volatility"
                else:
                    return "sideways_high_volatility"
            elif slope > 0:
                if volatility < 0.05 * np.mean(recent_prices):
                    return "uptrend_smooth"
                else:
                    return "uptrend_volatile"
            else:
                if volatility < 0.05 * np.mean(recent_prices):
                    return "downtrend_smooth"
                else:
                    return "downtrend_volatile"

        except Exception as e:
            logger.error("价格模式识别失败: %s", e)
            return "unknown"

    def _validate_data(self, data: pd.DataFrame) -> None:
        """验证输入数据"""
        if data is None or data.empty:
            raise ValueError("输入数据不能为空")

        required_columns = ["close"]
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"缺少必需列: {col}")

        if len(data) < 5:
            raise ValueError("数据长度不足，至少需要5个数据点")

    def _generate_cache_key(self, data: pd.DataFrame, feature_types: List[str]) -> str:
        """生成缓存键"""
        import hashlib

        # 使用数据形状、列名、最后一行数据等生成唯一键
        key_data = f"{data.shape}_{list(data.columns)}_{feature_types}_{data.iloc[-1].to_dict()}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def clear_cache(self) -> None:
        """清除特征缓存"""
        self.feature_cache.clear()
        logger.info("特征缓存已清除")

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            "cache_size": len(self.feature_cache),
            "cached_keys": list(self.feature_cache.keys()),
            "memory_usage_estimate": len(str(self.feature_cache)),  # 简单的内存使用估计
        }
