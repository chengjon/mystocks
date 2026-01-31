#!/usr/bin/env python3
"""
市场体制识别器
识别当前市场体制：牛市(bull)、熊市(bear)、震荡市(choppy)

功能：
- MA斜率计算（趋势判断）
- 涨跌家数比计算（市场广度）
- ATR波动率计算（波动水平）
- 综合评分（权重：MA斜率0.4，市场广度0.3，波动率0.3）

作者: Claude Code
创建日期: 2026-01-07
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """市场体制枚举"""

    BULL = "bull"  # 牛市
    BEAR = "bear"  # 熊市
    CHOPPY = "choppy"  # 震荡市
    UNKNOWN = "unknown"  # 未知


@dataclass
class MarketRegimeConfig:
    """市场体制识别配置"""

    ma_short_window: int = 20  # 短期MA窗口
    ma_long_window: int = 60  # 长期MA窗口
    ma_slope_threshold: float = 0.001  # MA斜率阈值
    breadthlookback_days: int = 5  # 广度回溯天数
    atr_window: int = 14  # ATR计算窗口
    atr_volatility_threshold: float = 0.03  # 波动率阈值

    # 综合评分权重
    weight_ma_slope: float = 0.4
    weight_breadth: float = 0.3
    weight_volatility: float = 0.3


@dataclass
class MarketRegimeResult:
    """市场体制识别结果"""

    regime: MarketRegime
    confidence: float  # 置信度 0-1
    ma_slope_score: float  # MA斜率评分 0-100
    breadth_score: float  # 广度评分 0-100
    volatility_score: float  # 波动率评分 0-100
    composite_score: float  # 综合评分 -100 到 100
    details: Dict[str, Any]


class MarketRegimeIdentifier:
    """
    市场体制识别器

    识别当前市场体制，综合考虑：
    1. 趋势（MA斜率）
    2. 市场广度（涨跌家数比）
    3. 波动水平（ATR波动率）
    """

    def __init__(self, config: Optional[MarketRegimeConfig] = None):
        self.config = config or MarketRegimeConfig()
        self._validate_config()

    def _validate_config(self):
        """验证配置参数"""
        if not 0 < self.config.weight_ma_slope <= 1:
            logger.warning("无效的MA斜率权重: {self.config.weight_ma_slope}，使用默认值0.4")
            self.config.weight_ma_slope = 0.4
        if not 0 < self.config.weight_breadth <= 1:
            logger.warning("无效的市场广度权重: {self.config.weight_breadth}，使用默认值0.3")
            self.config.weight_breadth = 0.3
        if not 0 < self.config.weight_volatility <= 1:
            logger.warning("无效的波动率权重: {self.config.weight_volatility}，使用默认值0.3")
            self.config.weight_volatility = 0.3

        total_weight = self.config.weight_ma_slope + self.config.weight_breadth + self.config.weight_volatility
        if abs(total_weight - 1.0) > 0.001:
            logger.warning("权重之和不为1: %(total_weight)s，将进行归一化")
            self.config.weight_ma_slope /= total_weight
            self.config.weight_breadth /= total_weight
            self.config.weight_volatility /= total_weight

    def identify(
        self,
        index_data: pd.DataFrame,
        market_breadth_data: Optional[pd.DataFrame] = None,
    ) -> MarketRegimeResult:
        """
        识别市场体制

        Args:
            index_data: 指数数据，需包含 'close' 列
            market_breadth_data: 市场广度数据，需包含 'up_count', 'down_count' 列

        Returns:
            MarketRegimeResult: 识别结果
        """
        try:
            if index_data is None or index_data.empty:
                logger.warning("指数数据为空")
                return self._create_unknown_result("空数据")

            required_cols = ["close"]
            if not all(col in index_data.columns for col in required_cols):
                logger.warning("指数数据缺少必要列: %(required_cols)s")
                return self._create_unknown_result("缺少数据列")

            ma_slope_score = self._calculate_ma_slope(index_data)
            breadth_score = self._calculate_market_breadth(index_data, market_breadth_data)
            volatility_score = self._calculate_regime_volatility(index_data)

            composite_score = self._calculate_composite_score(ma_slope_score, breadth_score, volatility_score)

            regime, confidence = self._determine_regime(composite_score)

            details = {
                "ma_slope_score": ma_slope_score,
                "breadth_score": breadth_score,
                "volatility_score": volatility_score,
                "composite_score": composite_score,
                "ma_config": {
                    "short_window": self.config.ma_short_window,
                    "long_window": self.config.ma_long_window,
                },
                "breadth_config": {"lookback_days": self.config.breadthlookback_days},
                "volatility_config": {"atr_window": self.config.atr_window},
            }

            logger.info("市场体制识别: {regime.value}, 置信度: {confidence:.2f}, 综合评分: %(composite_score)s")

            return MarketRegimeResult(
                regime=regime,
                confidence=confidence,
                ma_slope_score=ma_slope_score,
                breadth_score=breadth_score,
                volatility_score=volatility_score,
                composite_score=composite_score,
                details=details,
            )

        except Exception as e:
            logger.error("市场体制识别失败: %(e)s")
            return self._create_unknown_result(f"识别错误: {str(e)}")

    def _calculate_ma_slope(self, data: pd.DataFrame) -> float:
        """
        计算MA斜率评分

        Args:
            data: 包含 'close' 列的DataFrame

        Returns:
            float: MA斜率评分 (-100 到 100)
        """
        try:
            closes = data["close"].dropna()

            if len(closes) < self.config.ma_long_window:
                logger.warning("数据点不足: {len(closes)}, 需要至少 {self.config.ma_long_window")
                return 0.0

            short_ma = closes.rolling(window=self.config.ma_short_window).mean()
            long_ma = closes.rolling(window=self.config.ma_long_window).mean()

            if len(short_ma) < 2 or len(long_ma) < 2:
                return 0.0

            short_slope = (short_ma.iloc[-1] - short_ma.iloc[-2]) / short_ma.iloc[-2]
            long_slope = (long_ma.iloc[-1] - long_ma.iloc[-2]) / long_ma.iloc[-2]

            avg_slope = (short_slope + long_slope) / 2

            score = np.clip(avg_slope / self.config.ma_slope_threshold * 50, -100, 100)

            logger.debug("MA斜率计算: short={short_slope:.6f}, long={long_slope:.6f}, score=%(score)s")

            return float(score)

        except Exception as e:
            logger.error("MA斜率计算失败: %(e)s")
            return 0.0

    def _calculate_market_breadth(
        self,
        index_data: pd.DataFrame,
        breadth_data: Optional[pd.DataFrame] = None,
    ) -> float:
        """
        计算市场广度评分

        Args:
            index_data: 指数数据（用于计算涨跌）
            breadth_data: 预计算的市场广度数据

        Returns:
            float: 市场广度评分 (-100 到 100)
        """
        try:
            if breadth_data is not None and "up_ratio" in breadth_data.columns:
                up_ratio = breadth_data["up_ratio"].dropna()
                if len(up_ratio) > 0:
                    avg_up_ratio = up_ratio.iloc[-min(self.config.breadthlookback_days, len(up_ratio)) :].mean()
                    score = (avg_up_ratio - 0.5) * 200
                    return float(np.clip(score, -100, 100))

            closes = index_data["close"].dropna()

            if len(closes) < self.config.breadthlookback_days + 1:
                logger.warning("市场广度计算数据不足: %s")
                return 0.0

            daily_returns = closes.pct_change().dropna()

            if len(daily_returns) == 0:
                return 0.0

            up_count = (daily_returns > 0).sum()
            down_count = (daily_returns < 0).sum()
            total = up_count + down_count

            if total == 0:
                return 0.0

            up_ratio = up_count / total

            score = (up_ratio - 0.5) * 200

            logger.debug("市场广度计算: up=%(up_count)s, down=%(down_count)s, ratio={up_ratio:.2f}, score=%(score)s")

            return float(np.clip(score, -100, 100))

        except Exception as e:
            logger.error("市场广度计算失败: %(e)s")
            return 0.0

    def _calculate_regime_volatility(self, data: pd.DataFrame) -> float:
        """
        计算波动率评分

        Args:
            data: 包含 'close' 列的DataFrame

        Returns:
            float: 波动率评分 (0 到 100)
        """
        try:
            closes = data["close"].dropna()

            if len(closes) < self.config.atr_window + 1:
                logger.warning("波动率计算数据不足: %s")
                return 50.0

            high = data.get("high", closes)
            low = data.get("low", closes)
            close_col = data.get("close", closes)

            high = high.dropna()
            low = low.dropna()
            close_col = close_col.dropna()

            if len(high) < self.config.atr_window + 1 or len(low) < self.config.atr_window + 1:
                returns = closes.pct_change().dropna()
                if len(returns) < self.config.atr_window:
                    return 50.0
                volatility = returns.std() * np.sqrt(252)
                score = min(volatility / self.config.atr_volatility_threshold * 50, 100)
                return float(np.clip(score, 0, 100))

            true_range = pd.concat(
                [
                    high - low,
                    (high - close_col.shift(1)).abs(),
                    (low - close_col.shift(1)).abs(),
                ],
                axis=1,
            ).max(axis=1)

            atr = true_range.rolling(window=self.config.atr_window).mean()
            atr_value = atr.iloc[-1]

            if np.isnan(atr_value) or atr_value == 0:
                return 50.0

            atr_percent = atr_value / close_col.iloc[-1]

            volatility = atr_percent * (252**0.5)

            score = min(volatility / self.config.atr_volatility_threshold * 50, 100)

            logger.debug(
                f"波动率计算: ATR={atr_value:.2f}, 百分比={atr_percent:.4f},  annualized={volatility:.4f}, score={score:.2f}"
            )

            return float(np.clip(score, 0, 100))

        except Exception as e:
            logger.error("波动率计算失败: %(e)s")
            return 50.0

    def _calculate_composite_score(self, ma_score: float, breadth_score: float, volatility_score: float) -> float:
        """
        计算综合评分

        Args:
            ma_score: MA斜率评分 (-100 到 100)
            breadth_score: 市场广度评分 (-100 到 100)
            volatility_score: 波动率评分 (0 到 100)

        Returns:
            float: 综合评分 (-100 到 100)
        """
        composite = (
            self.config.weight_ma_slope * ma_score
            + self.config.weight_breadth * breadth_score
            + self.config.weight_volatility * (volatility_score - 50)
        )

        return float(np.clip(composite, -100, 100))

    def _determine_regime(self, composite_score: float) -> Tuple[MarketRegime, float]:
        """
        根据综合评分确定市场体制

        Args:
            composite_score: 综合评分

        Returns:
            Tuple[MarketRegime, float]: 市场体制和置信度
        """
        if composite_score >= 30:
            regime = MarketRegime.BULL
            confidence = min((composite_score - 30) / 70 + 0.5, 1.0)
        elif composite_score <= -30:
            regime = MarketRegime.BEAR
            confidence = min((abs(composite_score) - 30) / 70 + 0.5, 1.0)
        else:
            regime = MarketRegime.CHOPPY
            confidence = 0.5 + (1 - abs(composite_score) / 30) * 0.3

        return regime, confidence

    def _create_unknown_result(self, reason: str) -> MarketRegimeResult:
        """创建未知状态的结果"""
        return MarketRegimeResult(
            regime=MarketRegime.UNKNOWN,
            confidence=0.0,
            ma_slope_score=0.0,
            breadth_score=0.0,
            volatility_score=50.0,
            composite_score=0.0,
            details={"error": reason},
        )


def get_market_regime_identifier(
    config: Optional[MarketRegimeConfig] = None,
) -> MarketRegimeIdentifier:
    """
    获取市场体制识别器实例

    Args:
        config: 可选配置

    Returns:
        MarketRegimeIdentifier: 识别器实例
    """
    return MarketRegimeIdentifier(config)
