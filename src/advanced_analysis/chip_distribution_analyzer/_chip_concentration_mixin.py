"""Shared methods for `chip_concentration.py`."""

import logging
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType
from src.advanced_analysis.chip_distribution_analyzer._chip_concentration_tail import ChipDistributionAnalyzerTailMixin
from src.advanced_analysis.chip_distribution_analyzer.chip_models import (
    ChipConcentration,
    ChipFlowDynamics,
    CostAreaAnalysis,
    WinningProbability,
)

logger = logging.getLogger(__name__)


class ChipDistributionAnalyzerMixin(ChipDistributionAnalyzerTailMixin):
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
            logger.error("Error calculating chip distribution: %s", e)
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
            logger.error("Error analyzing chip concentration: %s", e)
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
            logger.error("Error analyzing chip flow dynamics: %s", e)
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
            logger.error("Error calculating winning probability: %s", e)
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
            logger.error("Error analyzing cost areas: %s", e)
            return None
