#!/usr/bin/env python3
"""FeatureCalculationGPU 尾部价格/成交量计算方法集。"""

from __future__ import annotations

import logging
from typing import List, Union

import numpy as np
import pandas as pd

try:
    import cudf
except ImportError:
    cudf = None

logger = logging.getLogger(__name__)


class FeatureCalculationGPUPostVolumeMixin:
    """价格/成交量尾部计算方法。"""

    def _calculate_obv(
        self,
        close: Union[cudf.Series, pd.Series],
        volume: Union[cudf.Series, pd.Series],
    ) -> float:
        """计算OBV。"""
        try:
            if len(close) < 2 or len(volume) < 2:
                return 0.0

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
        """计算简单移动平均。"""
        try:
            values_array = np.array(values) if is_series else values
            if len(values_array) < window:
                return float(np.mean(values_array))
            return float(np.mean(values_array[-window:]))
        except Exception as e:
            logger.error("SMA计算失败: %s", e)
            return 0.0
