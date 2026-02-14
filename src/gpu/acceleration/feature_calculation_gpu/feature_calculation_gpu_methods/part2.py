#!/usr/bin/env python3
"""
# 功能：GPU加速特征计算引擎
# 作者：MyStocks AI开发团队
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：GPU加速的金融特征计算和技术指标引擎
"""

import logging
import time
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd

try:
    import cudf
    import cupy as cp

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    from src.gpu.core.hardware_abstraction.resource_manager import GPUResourceManager
except ImportError:
    GPUResourceManager = Any

logger = logging.getLogger(__name__)


class FeatureCalculationGPUCalculatePriceVolumeMixin:
    """FeatureCalculationGPU 方法集 Part 2"""

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

