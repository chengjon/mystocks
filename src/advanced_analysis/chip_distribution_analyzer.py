"""
Chip Distribution Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台筹码分布分析功能

This module provides comprehensive chip distribution analysis including:
- Cost distribution analysis based on cost transformation principles
- Chip concentration and peak analysis
- Winning probability calculation based on chip distribution
- Chip flow dynamics and cost area identification
- Long-term vs short-term chip distribution analysis
"""

import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType, BaseAnalyzer

# GPU acceleration support
try:
    pass

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    warnings.warn("GPU libraries not available. Chip distribution analysis will run on CPU.")


@dataclass
class ChipConcentration:
    """筹码集中度分析"""

    concentration_index: float  # 集中度指数 (0-1)
    peak_price: float  # 峰值价格
    peak_density: float  # 峰值密度
    cost_area_width: float  # 成本区宽度
    main_cost_area: Tuple[float, float]  # 主要成本区范围
    secondary_peaks: List[Tuple[float, float]]  # 次要峰值 (价格, 密度)


@dataclass
class ChipFlowDynamics:
    """筹码流动动态"""

    flow_direction: str  # 流动方向 (inflow/outflow/stable)
    flow_intensity: float  # 流动强度 (0-1)
    cost_shift: float  # 成本转移幅度
    distribution_change: float  # 分布变化程度
    new_chip_ratio: float  # 新筹码占比
    old_chip_ratio: float  # 旧筹码占比


@dataclass
class WinningProbability:
    """获胜概率分析"""

    current_win_prob: float  # 当前获胜概率 (0-1)
    break_up_prob: float  # 向上突破概率
    break_down_prob: float  # 向下突破概率
    hold_prob: float  # 震荡概率
    risk_reward_ratio: float  # 风险收益比
    optimal_entry: float  # 最佳入场价格
    optimal_exit: float  # 最佳出场价格


@dataclass
class CostAreaAnalysis:
    """成本区分析"""

    support_areas: List[Tuple[float, float, float]]  # 支撑区 (价格下限, 价格上限, 强度)
    resistance_areas: List[Tuple[float, float, float]]  # 阻力区 (价格下限, 价格上限, 强度)
    equilibrium_price: float  # 均衡价格
    cost_pressure: str  # 成本压力方向 (bullish/bearish/neutral)
    pressure_strength: float  # 压力强度 (0-1)


class ChipDistributionAnalyzer(BaseAnalyzer):
    """
    筹码分布分析器

    基于成本转换原理提供全面的筹码分布分析，包括：
    - 筹码集中度和峰值分析
    - 筹码流动动态分析
    - 基于筹码分布的获胜概率计算
    - 成本区识别和支撑阻力分析
    - 长期vs短期筹码分布对比
    """


def __init__(self, data_manager, gpu_manager=None):
    super().__init__(data_manager, gpu_manager)

    # 筹码分布分析参数
    self.chip_params = {
        "distribution_bins": 50,  # 分布区间数量
        "concentration_threshold": 0.7,  # 集中度阈值
        "peak_threshold": 0.8,  # 峰值阈值
        "cost_area_width": 0.05,  # 成本区宽度比例
        "flow_detection_window": 20,  # 流动检测窗口
    }

    # 概率计算参数
    self.probability_params = {
        "breakout_threshold": 0.6,  # 突破阈值
        "momentum_weight": 0.4,  # 动量权重
        "volume_weight": 0.3,  # 成交量权重
        "chip_weight": 0.3,  # 筹码权重
        "time_decay_factor": 0.95,  # 时间衰减因子
    }

    # 成本区识别参数
    self.cost_area_params = {
        "support_threshold": 0.7,  # 支撑阈值
        "resistance_threshold": 0.6,  # 阻力阈值
        "area_min_width": 0.03,  # 最小区域宽度
        "consolidation_period": 10,  # 整理周期
    }


def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
    """
    执行筹码分布分析

    Args:
        stock_code: 股票代码
        **kwargs: 分析参数
            - analysis_period: 分析周期 (默认: 90天)
            - include_concentration: 是否包含集中度分析 (默认: True)
            - include_flow_dynamics: 是否包含流动动态分析 (默认: True)
            - include_probability: 是否包含概率分析 (默认: True)
            - include_cost_areas: 是否包含成本区分析 (默认: True)
            - chip_calculation_method: 筹码计算方法 (默认: 'volume_weighted')

    Returns:
        AnalysisResult: 分析结果
    """
    analysis_period = kwargs.get("analysis_period", 90)
    include_concentration = kwargs.get("include_concentration", True)
    include_flow_dynamics = kwargs.get("include_flow_dynamics", True)
    include_probability = kwargs.get("include_probability", True)
    include_cost_areas = kwargs.get("include_cost_areas", True)
    chip_calculation_method = kwargs.get("chip_calculation_method", "volume_weighted")

    try:
        # 获取历史数据
        data = self._get_historical_data(stock_code, days=analysis_period, data_type="1d")
        if data.empty:
            return self._create_error_result(stock_code, "No historical data available for chip distribution analysis")

        # 计算筹码分布
        chip_distribution = self._calculate_chip_distribution(data, method=chip_calculation_method)

        # 筹码集中度分析
        concentration_analysis = None
        if include_concentration:
            concentration_analysis = self._analyze_chip_concentration(chip_distribution)

        # 筹码流动动态分析
        flow_dynamics = None
        if include_flow_dynamics:
            flow_dynamics = self._analyze_chip_flow_dynamics(chip_distribution, data)

        # 获胜概率分析
        winning_probability = None
        if include_probability:
            winning_probability = self._calculate_winning_probability(chip_distribution, concentration_analysis, data)

        # 成本区分析
        cost_area_analysis = None
        if include_cost_areas:
            cost_area_analysis = self._analyze_cost_areas(chip_distribution, data)

        # 计算综合得分
        scores = self._calculate_chip_scores(
            chip_distribution, concentration_analysis, flow_dynamics, winning_probability, cost_area_analysis
        )

        # 生成信号
        signals = self._generate_chip_signals(
            concentration_analysis, flow_dynamics, winning_probability, cost_area_analysis
        )

        # 投资建议
        recommendations = self._generate_chip_recommendations(
            winning_probability, cost_area_analysis, concentration_analysis
        )

        # 风险评估
        risk_assessment = self._assess_chip_risk(chip_distribution, flow_dynamics, winning_probability)

        # 元数据
        metadata = {
            "analysis_period_days": analysis_period,
            "chip_calculation_method": chip_calculation_method,
            "data_points": len(data),
            "chip_distribution_bins": len(chip_distribution) if chip_distribution is not None else 0,
            "concentration_peak_price": concentration_analysis.peak_price if concentration_analysis else None,
            "winning_probability": winning_probability.current_win_prob if winning_probability else 0,
            "support_areas_count": len(cost_area_analysis.support_areas) if cost_area_analysis else 0,
            "resistance_areas_count": len(cost_area_analysis.resistance_areas) if cost_area_analysis else 0,
            "analysis_timestamp": datetime.now(),
        }

        return AnalysisResult(
            analysis_type=AnalysisType.CHIP_DISTRIBUTION,
            stock_code=stock_code,
            timestamp=datetime.now(),
            scores=scores,
            signals=signals,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            metadata=metadata,
            raw_data=chip_distribution if kwargs.get("include_raw_data", False) else None,
        )

    except Exception as e:
        return self._create_error_result(stock_code, str(e))


def _calculate_chip_distribution(self, data: pd.DataFrame, method: str = "volume_weighted") -> Optional[pd.Series]:
    """计算筹码分布"""
    if data.empty or "close" not in data.columns or "volume" not in data.columns:
        return None

    try:
        prices = data["close"].values
        volumes = data["volume"].values

        # 创建价格区间
        price_min, price_max = prices.min(), prices.max()
        price_bins = np.linspace(price_min, price_max, self.chip_params["distribution_bins"] + 1)

        # 计算各价格区间的筹码量
        chip_distribution = np.zeros(self.chip_params["distribution_bins"])

        for i in range(len(prices)):
            # 找到价格对应的区间
            bin_idx = np.digitize(prices[i], price_bins) - 1
            if 0 <= bin_idx < len(chip_distribution):
                if method == "volume_weighted":
                    # 按成交量加权
                    weight = volumes[i] / volumes.max() if volumes.max() > 0 else 1.0
                    chip_distribution[bin_idx] += weight
                elif method == "time_weighted":
                    # 按时间衰减加权（近期更重要）
                    time_weight = np.exp((i - len(prices)) / len(prices) * 2)  # 时间衰减
                    chip_distribution[bin_idx] += time_weight
                else:
                    # 简单计数
                    chip_distribution[bin_idx] += 1

        # 归一化
        if chip_distribution.sum() > 0:
            chip_distribution = chip_distribution / chip_distribution.sum()

        # 创建价格区间标签
        bin_centers = (price_bins[:-1] + price_bins[1:]) / 2

        return pd.Series(chip_distribution, index=bin_centers)

    except Exception as e:
        print(f"Error calculating chip distribution: {e}")
        return None


def _analyze_chip_concentration(self, chip_distribution: pd.Series) -> Optional[ChipConcentration]:
    """分析筹码集中度"""
    if chip_distribution is None or chip_distribution.empty:
        return None

    try:
        # 找到峰值
        peaks_indices = self._find_peaks(chip_distribution.values)

        if not peaks_indices:
            return ChipConcentration(
                concentration_index=0.0,
                peak_price=chip_distribution.index[len(chip_distribution) // 2],
                peak_density=chip_distribution.max(),
                cost_area_width=chip_distribution.index.max() - chip_distribution.index.min(),
                main_cost_area=(chip_distribution.index.min(), chip_distribution.index.max()),
                secondary_peaks=[],
            )

        # 主要峰值
        main_peak_idx = peaks_indices[np.argmax(chip_distribution.values[peaks_indices])]
        main_peak_price = chip_distribution.index[main_peak_idx]
        main_peak_density = chip_distribution.values[main_peak_idx]

        # 计算集中度指数
        concentration_index = main_peak_density / chip_distribution.sum()

        # 识别主要成本区
        cost_area_threshold = main_peak_density * 0.5
        cost_area_mask = chip_distribution.values >= cost_area_threshold

        if np.any(cost_area_mask):
            cost_area_indices = np.where(cost_area_mask)[0]
            cost_area_prices = chip_distribution.index[cost_area_indices]
            main_cost_area = (cost_area_prices.min(), cost_area_prices.max())
            cost_area_width = main_cost_area[1] - main_cost_area[0]
        else:
            main_cost_area = (chip_distribution.index.min(), chip_distribution.index.max())
            cost_area_width = main_cost_area[1] - main_cost_area[0]

        # 次要峰值
        secondary_peaks = []
        for peak_idx in peaks_indices:
            if peak_idx != main_peak_idx:
                density = chip_distribution.values[peak_idx]
                if density >= main_peak_density * 0.3:  # 至少30%的主要峰值密度
                    secondary_peaks.append((chip_distribution.index[peak_idx], density))

        return ChipConcentration(
            concentration_index=concentration_index,
            peak_price=main_peak_price,
            peak_density=main_peak_density,
            cost_area_width=cost_area_width,
            main_cost_area=main_cost_area,
            secondary_peaks=secondary_peaks,
        )

    except Exception as e:
        print(f"Error analyzing chip concentration: {e}")
        return None


def _analyze_chip_flow_dynamics(self, chip_distribution: pd.Series, data: pd.DataFrame) -> Optional[ChipFlowDynamics]:
    """分析筹码流动动态"""
    if chip_distribution is None or data.empty:
        return None

    try:
        # 计算筹码重心变化
        price_centers = chip_distribution.index.values
        weights = chip_distribution.values

        # 当前筹码重心
        current_centroid = np.average(price_centers, weights=weights)

        # 历史筹码重心（过去一段时间）
        historical_data = data.tail(self.chip_params["flow_detection_window"])
        if len(historical_data) >= 10:
            historical_distribution = self._calculate_chip_distribution(historical_data)
            if historical_distribution is not None:
                historical_centroid = np.average(
                    historical_distribution.index.values, weights=historical_distribution.values
                )
                cost_shift = current_centroid - historical_centroid
            else:
                cost_shift = 0.0
        else:
            cost_shift = 0.0

        # 判断流动方向和强度
        shift_threshold = data["close"].std() * 0.1  # 10%波动率作为阈值

        if abs(cost_shift) < shift_threshold:
            flow_direction = "stable"
            flow_intensity = 0.0
        elif cost_shift > 0:
            flow_direction = "inflow"
            flow_intensity = min(abs(cost_shift) / (data["close"].mean() * 0.2), 1.0)
        else:
            flow_direction = "outflow"
            flow_intensity = min(abs(cost_shift) / (data["close"].mean() * 0.2), 1.0)

        # 计算分布变化程度
        if historical_distribution is not None:
            distribution_change = np.mean(np.abs(chip_distribution.values - historical_distribution.values))
        else:
            distribution_change = 0.0

        # 估算新旧筹码比例（简化的计算）
        current_price = data["close"].iloc[-1]
        new_chip_ratio = len(data[data["close"] > current_price * 1.05]) / len(data)  # 高于当前价格5%的新筹码
        old_chip_ratio = 1 - new_chip_ratio

        return ChipFlowDynamics(
            flow_direction=flow_direction,
            flow_intensity=flow_intensity,
            cost_shift=cost_shift,
            distribution_change=distribution_change,
            new_chip_ratio=new_chip_ratio,
            old_chip_ratio=old_chip_ratio,
        )

    except Exception as e:
        print(f"Error analyzing chip flow dynamics: {e}")
        return None


def _calculate_winning_probability(
    self, chip_distribution: pd.Series, concentration: Optional[ChipConcentration], data: pd.DataFrame
) -> Optional[WinningProbability]:
    """计算获胜概率"""
    if chip_distribution is None or data.empty or concentration is None:
        return None

    try:
        current_price = data["close"].iloc[-1]

        # 基于筹码分布计算各项概率
        prices = chip_distribution.index.values
        densities = chip_distribution.values

        # 上方筹码阻力
        upper_prices = prices[prices > current_price]
        upper_densities = densities[prices > current_price]
        upper_resistance = np.sum(upper_densities) if len(upper_densities) > 0 else 0

        # 下方筹码支撑
        lower_prices = prices[prices < current_price]
        lower_densities = densities[prices < current_price]
        lower_support = np.sum(lower_densities) if len(lower_densities) > 0 else 0

        # 计算突破概率
        total_density = np.sum(densities)
        break_up_prob = 1 - upper_resistance / total_density if total_density > 0 else 0.5
        break_down_prob = 1 - lower_support / total_density if total_density > 0 else 0.5

        # 当前获胜概率（价格在成本区间的概率）
        current_win_prob = densities[np.abs(prices - current_price).argmin()] / densities.max()

        # 震荡概率
        hold_prob = (upper_resistance + lower_support) / (2 * total_density) if total_density > 0 else 0.5

        # 标准化概率
        total_prob = break_up_prob + break_down_prob + hold_prob
        if total_prob > 0:
            break_up_prob /= total_prob
            break_down_prob /= total_prob
            hold_prob /= total_prob

        # 计算风险收益比
        avg_upper_price = (
            np.average(upper_prices, weights=upper_densities) if len(upper_prices) > 0 else current_price * 1.1
        )
        avg_lower_price = (
            np.average(lower_prices, weights=lower_densities) if len(lower_prices) > 0 else current_price * 0.9
        )

        reward = abs(avg_upper_price - current_price)
        risk = abs(current_price - avg_lower_price)
        risk_reward_ratio = reward / risk if risk > 0 else float("inf")

        # 确定最优入场和出场价格
        optimal_entry = concentration.peak_price if concentration else current_price
        optimal_exit = concentration.main_cost_area[1] if concentration else current_price * 1.1

        return WinningProbability(
            current_win_prob=current_win_prob,
            break_up_prob=break_up_prob,
            break_down_prob=break_down_prob,
            hold_prob=hold_prob,
            risk_reward_ratio=risk_reward_ratio,
            optimal_entry=optimal_entry,
            optimal_exit=optimal_exit,
        )

    except Exception as e:
        print(f"Error calculating winning probability: {e}")
        return None


def _analyze_cost_areas(self, chip_distribution: pd.Series, data: pd.DataFrame) -> Optional[CostAreaAnalysis]:
    """分析成本区"""
    if chip_distribution is None or data.empty:
        return None

    try:
        current_price = data["close"].iloc[-1]

        # 识别支撑区
        support_areas = self._identify_support_areas(chip_distribution, current_price)

        # 识别阻力区
        resistance_areas = self._identify_resistance_areas(chip_distribution, current_price)

        # 计算均衡价格（筹码重心）
        prices = chip_distribution.index.values
        densities = chip_distribution.values
        equilibrium_price = np.average(prices, weights=densities)

        # 判断成本压力方向
        if current_price > equilibrium_price * 1.05:
            cost_pressure = "bearish"  # 成本压力向下
            pressure_strength = min((current_price - equilibrium_price) / equilibrium_price, 1.0)
        elif current_price < equilibrium_price * 0.95:
            cost_pressure = "bullish"  # 成本压力向上
            pressure_strength = min((equilibrium_price - current_price) / equilibrium_price, 1.0)
        else:
            cost_pressure = "neutral"
            pressure_strength = 0.0

        return CostAreaAnalysis(
            support_areas=support_areas,
            resistance_areas=resistance_areas,
            equilibrium_price=equilibrium_price,
            cost_pressure=cost_pressure,
            pressure_strength=pressure_strength,
        )

    except Exception as e:
        print(f"Error analyzing cost areas: {e}")
        return None


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
        print(f"Error identifying support areas: {e}")

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
        print(f"Error identifying resistance areas: {e}")

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
        print(f"Error calculating chip scores: {e}")
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


def _generate_chip_recommendations(
    self,
    winning_probability: Optional[WinningProbability],
    cost_analysis: Optional[CostAreaAnalysis],
    concentration: Optional[ChipConcentration],
) -> Dict[str, Any]:
    """生成筹码分析建议"""
    recommendations = {}

    try:
        # 基于获胜概率的建议
        if winning_probability:
            max_prob = max(
                winning_probability.break_up_prob,
                winning_probability.break_down_prob,
                winning_probability.hold_prob,
            )

            if winning_probability.break_up_prob == max_prob and winning_probability.break_up_prob > 0.6:
                primary_signal = "bullish"
                action = f"建议买入，向上突破概率较高 ({winning_probability.break_up_prob:.1%})"
                confidence = "high" if winning_probability.break_up_prob > 0.7 else "medium"
            elif winning_probability.break_down_prob == max_prob and winning_probability.break_down_prob > 0.6:
                primary_signal = "bearish"
                action = f"建议卖出，向下突破概率较高 ({winning_probability.break_down_prob:.1%})"
                confidence = "high" if winning_probability.break_down_prob > 0.7 else "medium"
            else:
                primary_signal = "neutral"
                action = "建议观望，市场震荡概率较高"
                confidence = "low"
        else:
            primary_signal = "unknown"
            action = "筹码分布分析不足，建议结合其他指标判断"
            confidence = "low"

        # 考虑成本区压力
        if cost_analysis:
            if cost_analysis.cost_pressure == "bearish" and cost_analysis.pressure_strength > 0.5:
                action += " (成本压力向下，需谨慎)"
            elif cost_analysis.cost_pressure == "bullish" and cost_analysis.pressure_strength > 0.5:
                action += " (成本压力向上，可积极)"

        # 考虑筹码集中度
        if concentration and concentration.concentration_index > 0.8:
            action += " (筹码高度集中，突破可能性大)"

        recommendations.update(
            {
                "primary_signal": primary_signal,
                "recommended_action": action,
                "confidence_level": confidence,
                "optimal_entry_exit": (
                    {
                        "entry_price": winning_probability.optimal_entry if winning_probability else None,
                        "exit_price": winning_probability.optimal_exit if winning_probability else None,
                        "risk_reward_ratio": winning_probability.risk_reward_ratio if winning_probability else None,
                    }
                    if winning_probability
                    else None
                ),
                "key_levels": {
                    "equilibrium_price": cost_analysis.equilibrium_price if cost_analysis else None,
                    "peak_price": concentration.peak_price if concentration else None,
                    "main_cost_area": concentration.main_cost_area if concentration else None,
                },
            }
        )

    except Exception as e:
        print(f"Error generating chip recommendations: {e}")
        recommendations = {
            "primary_signal": "unknown",
            "recommended_action": "分析过程中出现错误，建议观望",
            "confidence_level": "low",
        }

    return recommendations


def _assess_chip_risk(
    self,
    chip_distribution: pd.Series,
    flow_dynamics: Optional[ChipFlowDynamics],
    winning_probability: Optional[WinningProbability],
) -> Dict[str, Any]:
    """评估筹码风险"""
    risk_assessment = {}

    try:
        # 筹码分布风险
        if chip_distribution is not None:
            # 计算分布偏度风险
            skewness = chip_distribution.skew()
            if abs(skewness) > 1:
                distribution_risk = "high"  # 分布严重偏斜
            elif abs(skewness) > 0.5:
                distribution_risk = "medium"
            else:
                distribution_risk = "low"
        else:
            distribution_risk = "unknown"

        # 流动风险
        if flow_dynamics and flow_dynamics.distribution_change > 0.7:
            flow_risk = "high"  # 筹码分布变化剧烈
        elif flow_dynamics and flow_dynamics.distribution_change > 0.4:
            flow_risk = "medium"
        else:
            flow_risk = "low"

        # 概率风险
        if winning_probability:
            prob_uncertainty = 1 - max(
                winning_probability.break_up_prob,
                winning_probability.break_down_prob,
                winning_probability.hold_prob,
            )
            if prob_uncertainty > 0.6:
                probability_risk = "high"  # 概率不确定性高
            elif prob_uncertainty > 0.4:
                probability_risk = "medium"
            else:
                probability_risk = "low"
        else:
            probability_risk = "medium"

        # 综合风险等级
        risk_scores = {"high": 3, "medium": 2, "low": 1, "unknown": 2}
        avg_risk_score = np.mean(
            [
                risk_scores.get(distribution_risk, 2),
                risk_scores.get(flow_risk, 2),
                risk_scores.get(probability_risk, 2),
            ]
        )

        if avg_risk_score > 2.5:
            overall_risk = "high"
        elif avg_risk_score > 1.5:
            overall_risk = "medium"
        else:
            overall_risk = "low"

        risk_assessment.update(
            {
                "overall_risk_level": overall_risk,
                "distribution_risk": distribution_risk,
                "flow_risk": flow_risk,
                "probability_risk": probability_risk,
                "risk_factors": [
                    "筹码分布偏斜严重" if distribution_risk == "high" else None,
                    "筹码流动过于剧烈" if flow_risk == "high" else None,
                    "概率判断不确定性高" if probability_risk == "high" else None,
                ],
                "risk_factors": [
                    f
                    for f in [
                        "筹码分布偏斜严重" if distribution_risk == "high" else None,
                        "筹码流动过于剧烈" if flow_risk == "high" else None,
                        "概率判断不确定性高" if probability_risk == "high" else None,
                    ]
                    if f is not None
                ],
            }
        )

    except Exception as e:
        print(f"Error assessing chip risk: {e}")
        risk_assessment = {"overall_risk_level": "unknown", "error": str(e)}

    return risk_assessment


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.CHIP_DISTRIBUTION,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"筹码分布分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )
