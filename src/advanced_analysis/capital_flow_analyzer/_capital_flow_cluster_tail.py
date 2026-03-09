"""Tail methods for `capital_flow_cluster.py`."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from src.advanced_analysis.capital_flow_analyzer.capital_flow_models import (
    CapitalFlowCluster,
    MainForceControl,
    SmartMoneyIndicator,
)

logger = logging.getLogger(__name__)


class CapitalFlowClusterTailMixin:
    def _analyze_smart_money(self, stock_code: str, capital_flow_data: pd.DataFrame) -> SmartMoneyIndicator:
        """分析聪明钱指标"""
        try:
            # 计算聪明钱评分
            smart_money_score = self._calculate_smart_money_score(capital_flow_data)
    
            # 计算机构建仓强度
            institutional_accumulation = self._calculate_institutional_accumulation(capital_flow_data)
    
            # 计算内部人活动强度
            insider_activity = self._calculate_insider_activity(capital_flow_data)
    
            # 计算大户交易占比
            whale_transactions = self._calculate_whale_transactions(capital_flow_data)
    
            # 计算资金流背离程度
            flow_divergence = self._calculate_flow_divergence(capital_flow_data)
    
            # 计算择时质量
            timing_quality = self._calculate_timing_quality(capital_flow_data)
    
            # 生成坚定信号
            conviction_signals = self._generate_conviction_signals(
                smart_money_score, institutional_accumulation, flow_divergence, timing_quality
            )
    
            return SmartMoneyIndicator(
                stock_code=stock_code,
                smart_money_score=smart_money_score,
                institutional_accumulation=institutional_accumulation,
                insider_activity=insider_activity,
                whale_transactions=whale_transactions,
                flow_divergence=flow_divergence,
                timing_quality=timing_quality,
                conviction_signals=conviction_signals,
            )
    
        except Exception as e:
            logger.error("Error in smart money analysis: %s", e)
            return SmartMoneyIndicator(
                stock_code=stock_code,
                smart_money_score=0.0,
                institutional_accumulation=0.0,
                insider_activity=0.0,
                whale_transactions=0.0,
                flow_divergence=0.0,
                timing_quality=0.0,
                conviction_signals=[],
            )
    
    
    def _calculate_smart_money_score(self, data: pd.DataFrame) -> float:
        """计算聪明钱评分"""
        if data.empty:
            return 0.0
    
        # 综合多个指标计算聪明钱评分
        institutional_score = self._calculate_institutional_accumulation(data)
        divergence_score = 1 - self._calculate_flow_divergence(data)  # 背离程度取反
        timing_score = self._calculate_timing_quality(data)
        concentration_score = self._calculate_concentration_ratio(data)
    
        # 加权计算
        weights = [0.4, 0.3, 0.2, 0.1]  # 机构、背离、择时、集中度
        scores = [institutional_score, divergence_score, timing_score, concentration_score]
    
        smart_money_score = sum(w * s for w, s in zip(weights, scores))
        return min(smart_money_score, 1.0)
    
    
    def _calculate_institutional_accumulation(self, data: pd.DataFrame) -> float:
        """计算机构建仓强度"""
        if data.empty:
            return 0.0
    
        # 计算机构资金净流入占比
        main_net_flow = data["main_inflow"] - data["main_outflow"]
        total_net_flow = data["net_flow"]
    
        accumulation_ratio = (main_net_flow > 0).sum() / len(main_net_flow)
        accumulation_strength = main_net_flow[main_net_flow > 0].mean() / (abs(total_net_flow).mean() + 1e-8)
    
        return min(accumulation_ratio * accumulation_strength, 1.0)
    
    
    def _calculate_insider_activity(self, data: pd.DataFrame) -> float:
        """计算内部人活动强度"""
        # 简化的内部人活动计算
        # 实际应该基于股东增减持数据
        flow_volatility = data["net_flow"].std() / (abs(data["net_flow"].mean()) + 1e-8)
        return min(flow_volatility, 1.0)
    
    
    def _calculate_whale_transactions(self, data: pd.DataFrame) -> float:
        """计算大户交易占比"""
        # 计算主力资金占比
        main_total = data["main_inflow"] + data["main_outflow"]
        retail_total = data["retail_inflow"] + data["retail_outflow"]
        total_flow = main_total + retail_total
    
        whale_ratio = main_total.sum() / (total_flow.sum() + 1e-8)
        return min(whale_ratio, 1.0)
    
    
    def _calculate_flow_divergence(self, data: pd.DataFrame) -> float:
        """计算资金流背离程度"""
        if len(data) < 10:
            return 0.0
    
        # 计算价格趋势和资金流向的背离
        price_trend = data["close"].pct_change().rolling(window=5).mean()
        flow_trend = data["net_flow"].rolling(window=5).mean()
    
        # 计算相关系数
        correlation = price_trend.corr(flow_trend) if len(price_trend.dropna()) > 1 else 0
    
        # 背离程度 = 1 - |相关系数|
        divergence = 1 - abs(correlation)
        return min(divergence, 1.0)
    
    
    def _calculate_timing_quality(self, data: pd.DataFrame) -> float:
        """计算择时质量"""
        if len(data) < 10:
            return 0.0
    
        # 计算资金流入时机与价格变动的关系
        price_changes = data["close"].pct_change()
        net_flows = data["net_flow"]
    
        # 计算流入时机与后续价格变动的相关性
        inflow_timing = net_flows.shift(-1)  # 次日价格变动
        timing_correlation = price_changes.corr(net_flows) if len(price_changes.dropna()) > 1 else 0
    
        timing_quality = (timing_correlation + 1) / 2  # 转换为0-1范围
        return timing_quality
    
    
    def _generate_conviction_signals(
        self, smart_money_score: float, institutional_accumulation: float, flow_divergence: float, timing_quality: float
    ) -> List[str]:
        """生成坚定信号"""
        signals = []
    
        if smart_money_score > 0.8:
            signals.append("聪明钱高度认可")
        elif smart_money_score > 0.6:
            signals.append("聪明钱较为认可")
    
        if institutional_accumulation > self.smart_money_params["accumulation_threshold"]:
            signals.append("机构持续建仓")
    
        if flow_divergence < 0.3:
            signals.append("资金流与价格趋势一致")
    
        if timing_quality > 0.7:
            signals.append("择时质量优秀")
    
        return signals
    
    
    def _analyze_market_context(self, capital_flow_data: pd.DataFrame) -> Dict[str, Any]:
        """分析市场背景"""
        # 简化的市场背景分析
        return {"market_sentiment": "neutral", "sector_rotation": "balanced", "risk_appetite": "moderate"}
    
    
    def _calculate_capital_flow_scores(
        self,
        data: pd.DataFrame,
        clusters: List[CapitalFlowCluster],
        control: MainForceControl,
        smart_money: SmartMoneyIndicator,
    ) -> Dict[str, float]:
        """计算资金流向分析得分"""
        scores = {}
    
        try:
            # 资金流向强度得分
            if not data.empty:
                avg_net_flow = abs(data["net_flow"].mean())
                flow_volatility = data["net_flow"].std()
                flow_strength_score = min(avg_net_flow / (flow_volatility + 1e-8) / 5, 1.0)
                scores["flow_strength"] = flow_strength_score
    
            # 聚类有效性得分
            if clusters:
                avg_cluster_confidence = np.mean([c.confidence for c in clusters])
                scores["clustering_effectiveness"] = avg_cluster_confidence
    
            # 主力控盘得分
            if control:
                scores["control_degree"] = control.control_degree
                scores["control_stability"] = control.control_stability
    
            # 聪明钱得分
            if smart_money:
                scores["smart_money_score"] = smart_money.smart_money_score
                scores["timing_quality"] = smart_money.timing_quality
    
            # 综合得分
            weights = {
                "flow_strength": 0.3,
                "clustering_effectiveness": 0.2,
                "control_degree": 0.25,
                "smart_money_score": 0.25,
            }
    
            overall_score = sum(scores.get(key, 0) * weight for key, weight in weights.items())
            scores["overall_score"] = overall_score
    
        except Exception as e:
            logger.error("Error calculating capital flow scores: %s", e)
            scores = {"overall_score": 0.0, "error": True}
    
        return scores
