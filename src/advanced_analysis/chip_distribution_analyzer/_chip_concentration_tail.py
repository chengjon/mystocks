"""Tail helpers for `chip_concentration.py`."""

import logging
from typing import Any, Dict, List

import numpy as np

from src.advanced_analysis.chip_distribution_analyzer.chip_models import (
    ChipConcentration,
    ChipFlowDynamics,
    CostAreaAnalysis,
    WinningProbability,
)

logger = logging.getLogger(__name__)


class ChipDistributionAnalyzerTailMixin:
    def _find_peaks(self, data: np.ndarray, threshold: float = 0.1) -> np.ndarray:
        """寻找峰值"""
        try:
            from scipy.signal import find_peaks

            peaks, _ = find_peaks(data, height=threshold * data.max())
            return peaks
        except ImportError:
            # 简化的峰值检测
            peaks = []
            for i in range(1, len(data) - 1):
                if data[i] > data[i - 1] and data[i] > data[i + 1] and data[i] > threshold * data.max():
                    peaks.append(i)
            return np.array(peaks)


    def _identify_support_areas(
        self, chip_distribution: pd.Series, current_price: float
    ) -> List[Tuple[float, float, float]]:
        """识别支撑区"""
        support_areas = []

        try:
            # 寻找价格低于当前价的密集筹码区
            lower_prices = chip_distribution.index[chip_distribution.index < current_price]
            lower_densities = chip_distribution.loc[lower_prices]

            if not lower_densities.empty:
                # 计算密度阈值
                density_threshold = lower_densities.quantile(self.cost_area_params["support_threshold"])

                # 找到高密度区域
                high_density_mask = lower_densities >= density_threshold

                if high_density_mask.any():
                    # 合并相邻的支撑区
                    support_prices = lower_prices[high_density_mask]
                    support_groups = self._group_consecutive_prices(support_prices.values)

                    for group in support_groups:
                        if len(group) >= 2:
                            area_min = group.min()
                            area_max = group.max()
                            area_width = (area_max - area_min) / current_price

                            if area_width >= self.cost_area_params["area_min_width"]:
                                # 计算区域强度
                                area_densities = lower_densities.loc[
                                    (lower_prices >= area_min) & (lower_prices <= area_max)
                                ]
                                area_strength = area_densities.mean()

                                support_areas.append((area_min, area_max, area_strength))

        except Exception as e:
            logger.error("Error identifying support areas: %s", e)

        return support_areas


    def _identify_resistance_areas(
        self, chip_distribution: pd.Series, current_price: float
    ) -> List[Tuple[float, float, float]]:
        """识别阻力区"""
        resistance_areas = []

        try:
            # 寻找价格高于当前价的密集筹码区
            higher_prices = chip_distribution.index[chip_distribution.index > current_price]
            higher_densities = chip_distribution.loc[higher_prices]

            if not higher_densities.empty:
                # 计算密度阈值
                density_threshold = higher_densities.quantile(self.cost_area_params["resistance_threshold"])

                # 找到高密度区域
                high_density_mask = higher_densities >= density_threshold

                if high_density_mask.any():
                    # 合并相邻的阻力区
                    resistance_prices = higher_prices[high_density_mask]
                    resistance_groups = self._group_consecutive_prices(resistance_prices.values)

                    for group in resistance_groups:
                        if len(group) >= 2:
                            area_min = group.min()
                            area_max = group.max()
                            area_width = (area_max - area_min) / current_price

                            if area_width >= self.cost_area_params["area_min_width"]:
                                # 计算区域强度
                                area_densities = higher_densities.loc[
                                    (higher_prices >= area_min) & (higher_prices <= area_max)
                                ]
                                area_strength = area_densities.mean()

                                resistance_areas.append((area_min, area_max, area_strength))

        except Exception as e:
            logger.error("Error identifying resistance areas: %s", e)

        return resistance_areas


    def _group_consecutive_prices(self, prices: np.ndarray, gap_threshold: float = 0.02) -> List[np.ndarray]:
        """将连续的价格分组"""
        if len(prices) == 0:
            return []

        # 排序价格
        sorted_prices = np.sort(prices)

        # 识别连续组
        groups = []
        current_group = [sorted_prices[0]]

        for price in sorted_prices[1:]:
            # 检查是否与前一个价格连续
            if price - current_group[-1] <= gap_threshold * price:
                current_group.append(price)
            else:
                if len(current_group) >= 2:
                    groups.append(np.array(current_group))
                current_group = [price]

        # 添加最后一个组
        if len(current_group) >= 2:
            groups.append(np.array(current_group))

        return groups


    def _calculate_chip_scores(
        self,
        chip_distribution: pd.Series,
        concentration: Optional[ChipConcentration],
        flow_dynamics: Optional[ChipFlowDynamics],
        winning_probability: Optional[WinningProbability],
        cost_analysis: Optional[CostAreaAnalysis],
    ) -> Dict[str, float]:
        """计算筹码分析得分"""
        scores = {}

        try:
            # 筹码集中度得分
            if concentration:
                concentration_score = concentration.concentration_index
                scores["concentration_score"] = concentration_score
            else:
                scores["concentration_score"] = 0.0

            # 流动稳定性得分
            if flow_dynamics:
                flow_stability = 1 - flow_dynamics.distribution_change
                scores["flow_stability_score"] = flow_stability
            else:
                scores["flow_stability_score"] = 0.5

            # 获胜概率得分
            if winning_probability:
                probability_score = winning_probability.current_win_prob
                scores["probability_score"] = probability_score
            else:
                scores["probability_score"] = 0.0

            # 成本区清晰度得分
            if cost_analysis:
                support_count = len(cost_analysis.support_areas)
                resistance_count = len(cost_analysis.resistance_areas)
                cost_clarity = min((support_count + resistance_count) / 4, 1.0)  # 最多4个区域得满分
                scores["cost_clarity_score"] = cost_clarity
            else:
                scores["cost_clarity_score"] = 0.0

            # 综合得分
            weights = {
                "concentration_score": 0.25,
                "flow_stability_score": 0.25,
                "probability_score": 0.30,
                "cost_clarity_score": 0.20,
            }

            overall_score = sum(scores.get(key, 0) * weight for key, weight in weights.items())
            scores["overall_score"] = overall_score

        except Exception as e:
            logger.error("Error calculating chip scores: %s", e)
            scores = {"overall_score": 0.0, "error": True}

        return scores


    def _generate_chip_signals(
        self,
        concentration: Optional[ChipConcentration],
        flow_dynamics: Optional[ChipFlowDynamics],
        winning_probability: Optional[WinningProbability],
        cost_analysis: Optional[CostAreaAnalysis],
    ) -> List[Dict[str, Any]]:
        """生成筹码信号"""
        signals = []

        # 筹码集中度信号
        if concentration and concentration.concentration_index > self.chip_params["concentration_threshold"]:
            signals.append(
                {
                    "type": "chip_concentration",
                    "severity": "high",
                    "message": f"筹码高度集中 - 峰值价格: {concentration.peak_price:.2f}, 集中度: {concentration.concentration_index:.2f}",
                    "details": {
                        "peak_price": concentration.peak_price,
                        "concentration_index": concentration.concentration_index,
                        "cost_area_width": concentration.cost_area_width,
                    },
                }
            )

        # 筹码流动信号
        if flow_dynamics and flow_dynamics.flow_intensity > 0.6:
            direction_text = {"inflow": "流入", "outflow": "流出", "stable": "稳定"}.get(
                flow_dynamics.flow_direction, "未知"
            )

            signals.append(
                {
                    "type": "chip_flow",
                    "severity": "medium" if flow_dynamics.flow_intensity > 0.7 else "low",
                    "message": f"筹码{direction_text}活跃 - 强度: {flow_dynamics.flow_intensity:.2f}",
                    "details": {
                        "flow_direction": flow_dynamics.flow_direction,
                        "flow_intensity": flow_dynamics.flow_intensity,
                        "cost_shift": flow_dynamics.cost_shift,
                    },
                }
            )

        # 获胜概率信号
        if winning_probability:
            max_prob = max(
                winning_probability.break_up_prob, winning_probability.break_down_prob, winning_probability.hold_prob
            )

            if winning_probability.break_up_prob == max_prob and winning_probability.break_up_prob > 0.6:
                signals.append(
                    {
                        "type": "winning_probability",
                        "severity": "high",
                        "message": f"向上突破概率高 - {winning_probability.break_up_prob:.1%}",
                        "details": {
                            "break_up_prob": winning_probability.break_up_prob,
                            "risk_reward_ratio": winning_probability.risk_reward_ratio,
                        },
                    }
                )
            elif winning_probability.break_down_prob == max_prob and winning_probability.break_down_prob > 0.6:
                signals.append(
                    {
                        "type": "winning_probability",
                        "severity": "high",
                        "message": f"向下突破概率高 - {winning_probability.break_down_prob:.1%}",
                        "details": {
                            "break_down_prob": winning_probability.break_down_prob,
                            "risk_reward_ratio": winning_probability.risk_reward_ratio,
                        },
                    }
                )

        # 成本区信号
        if cost_analysis:
            # 支撑区信号
            for i, (min_price, max_price, strength) in enumerate(cost_analysis.support_areas):
                signals.append(
                    {
                        "type": "support_area",
                        "severity": "medium",
                        "message": f"支撑区 {i + 1}: {min_price:.2f}-{max_price:.2f}, 强度: {strength:.2f}",
                        "details": {
                            "area_index": i,
                            "min_price": min_price,
                            "max_price": max_price,
                            "strength": strength,
                        },
                    }
                )

            # 阻力区信号
            for i, (min_price, max_price, strength) in enumerate(cost_analysis.resistance_areas):
                signals.append(
                    {
                        "type": "resistance_area",
                        "severity": "medium",
                        "message": f"阻力区 {i + 1}: {min_price:.2f}-{max_price:.2f}, 强度: {strength:.2f}",
                        "details": {
                            "area_index": i,
                            "min_price": min_price,
                            "max_price": max_price,
                            "strength": strength,
                        },
                    }
                )

        return signals
