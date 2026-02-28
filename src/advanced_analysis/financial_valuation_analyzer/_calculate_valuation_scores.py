"""
Financial Valuation Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台财务估值分析功能

This module provides comprehensive financial valuation analysis including:
- DCF (Discounted Cash Flow) valuation models
- Multi-model valuation comparison (PE, PB, EV/EBITDA)
- DuPont analysis for financial health decomposition
- Modern financial engineering pricing methods
- Industry-relative valuation benchmarking
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from src.advanced_analysis import AnalysisResult, AnalysisType

def _calculate_valuation_scores(
    self,
    dcf: Optional[DCFValuation],
    relative: Optional[RelativeValuation],
    dupont: Optional[DuPontAnalysis],
    consensus: Optional[ValuationConsensus],
) -> Dict[str, float]:
    """计算估值分析得分"""
    scores = {}

    try:
        # DCF估值得分
        if dcf:
            upside_score = max(0, min(dcf.upside_potential / 50, 1))  # 上涨潜力标准化
            confidence_score = dcf.confidence_level
            scores["dcf_score"] = (upside_score + confidence_score) / 2
        else:
            scores["dcf_score"] = 0.5

        # 相对估值得分
        if relative:
            # 估值越低得分越高
            pe_score = 1 - relative.industry_pe_percentile
            pb_score = 1 - relative.industry_pb_percentile
            scores["relative_score"] = (pe_score + pb_score) / 2
        else:
            scores["relative_score"] = 0.5

        # 杜邦分析得分
        if dupont:
            roe_score = min(dupont.roe / 0.20, 1)  # ROE标准化
            profit_score = min(dupont.profit_margin / 0.10, 1)  # 利润率标准化
            efficiency_score = min(dupont.asset_turnover / 2.0, 1)  # 周转率标准化
            scores["dupont_score"] = (roe_score + profit_score + efficiency_score) / 3
        else:
            scores["dupont_score"] = 0.5

        # 共识估值得分
        if consensus:
            gap_score = 1 - abs(consensus.valuation_gap) / 50  # 估值差距标准化
            confidence_score = consensus.confidence_score
            scores["consensus_score"] = (gap_score + confidence_score) / 2
        else:
            scores["consensus_score"] = 0.5

        # 综合得分
        weights = {"dcf_score": 0.3, "relative_score": 0.3, "dupont_score": 0.2, "consensus_score": 0.2}

        overall_score = sum(scores.get(key, 0) * weight for key, weight in weights.items())
        scores["overall_score"] = overall_score

    except Exception as e:
        print(f"Error calculating valuation scores: {e}")
        scores = {"overall_score": 0.5, "error": True}

    return scores


def _generate_valuation_signals(
    self,
    dcf: Optional[DCFValuation],
    relative: Optional[RelativeValuation],
    consensus: Optional[ValuationConsensus],
) -> List[Dict[str, Any]]:
    """生成估值信号"""
    signals = []

    # DCF信号
    if dcf and dcf.confidence_level > 0.6:
        if dcf.upside_potential > 30:
            signals.append(
                {
                    "type": "dcf_strong_buy",
                    "severity": "high",
                    "message": f"DCF显示显著低估 - 上涨潜力: {dcf.upside_potential:.1f}%",
                    "details": {
                        "intrinsic_value": dcf.intrinsic_value,
                        "current_price": dcf.current_price,
                        "upside_potential": dcf.upside_potential,
                        "confidence": dcf.confidence_level,
                    },
                }
            )
        elif dcf.upside_potential < -20:
            signals.append(
                {
                    "type": "dcf_overvalued",
                    "severity": "medium",
                    "message": f"DCF显示显著高估 - 下跌风险: {abs(dcf.upside_potential):.1f}%",
                    "details": {
                        "intrinsic_value": dcf.intrinsic_value,
                        "current_price": dcf.current_price,
                        "upside_potential": dcf.upside_potential,
                    },
                }
            )

    # 相对估值信号
    if relative:
        if relative.valuation_fairness == "undervalued":
            signals.append(
                {
                    "type": "relative_undervalued",
                    "severity": "medium",
                    "message": f"相对估值显示低估 - PE百分位: {relative.industry_pe_percentile:.2f}",
                    "details": {
                        "pe_percentile": relative.industry_pe_percentile,
                        "pb_percentile": relative.industry_pb_percentile,
                        "valuation_fairness": relative.valuation_fairness,
                    },
                }
            )
        elif relative.valuation_fairness == "overvalued":
            signals.append(
                {
                    "type": "relative_overvalued",
                    "severity": "medium",
                    "message": f"相对估值显示高估 - PE百分位: {relative.industry_pe_percentile:.2f}",
                    "details": {
                        "pe_percentile": relative.industry_pe_percentile,
                        "pb_percentile": relative.industry_pb_percentile,
                        "valuation_fairness": relative.valuation_fairness,
                    },
                }
            )

    # 共识信号
    if consensus and consensus.confidence_score > 0.7:
        if consensus.recommendation in ["strong_buy", "buy"]:
            signals.append(
                {
                    "type": "valuation_consensus_buy",
                    "severity": "high" if consensus.recommendation == "strong_buy" else "medium",
                    "message": f"估值共识: {consensus.recommendation} - 估值差距: {consensus.valuation_gap:.1f}%",
                    "details": {
                        "consensus_value": consensus.consensus_value,
                        "market_price": consensus.market_price,
                        "valuation_gap": consensus.valuation_gap,
                        "confidence": consensus.confidence_score,
                    },
                }
            )
        elif consensus.recommendation in ["strong_sell", "sell"]:
            signals.append(
                {
                    "type": "valuation_consensus_sell",
                    "severity": "high" if consensus.recommendation == "strong_sell" else "medium",
                    "message": f"估值共识: {consensus.recommendation} - 估值差距: {consensus.valuation_gap:.1f}%",
                    "details": {
                        "consensus_value": consensus.consensus_value,
                        "market_price": consensus.market_price,
                        "valuation_gap": consensus.valuation_gap,
                    },
                }
            )

    return signals


def _generate_valuation_recommendations(
    self, consensus: Optional[ValuationConsensus], dupont: Optional[DuPontAnalysis]
) -> Dict[str, Any]:
    """生成估值建议"""
    recommendations = {}

    try:
        # 基于估值共识的建议
        if consensus:
            if consensus.recommendation == "strong_buy":
                primary_signal = "strong_buy"
                action = f"强烈推荐买入 - 估值共识显示上涨潜力{consensus.valuation_gap:.1f}%"
                confidence = "high"
            elif consensus.recommendation == "buy":
                primary_signal = "buy"
                action = f"建议买入 - 估值显示{consensus.valuation_gap:.1f}%上涨空间"
                confidence = "medium"
            elif consensus.recommendation == "hold":
                primary_signal = "hold"
                action = "建议观望 - 估值相对合理"
                confidence = "medium"
            elif consensus.recommendation == "sell":
                primary_signal = "sell"
                action = f"建议卖出 - 估值显示{abs(consensus.valuation_gap):.1f}%下跌风险"
                confidence = "medium"
            else:
                primary_signal = "strong_sell"
                action = f"强烈建议卖出 - 估值严重高估{abs(consensus.valuation_gap):.1f}%"
                confidence = "high"
        else:
            primary_signal = "hold"
            action = "估值分析不足，建议结合其他指标判断"
            confidence = "low"

        # 考虑杜邦分析
        if dupont:
            if dupont.roe > 0.15:
                action += " (ROE优秀，基本面支撑较好)"
            elif dupont.roe < 0.08:
                action += " (ROE偏低，需关注盈利能力)"

            if dupont.equity_multiplier > 2.5:
                action += " (财务杠杆较高，风险较大)"
            elif dupont.equity_multiplier < 1.5:
                action += " (财务杠杆保守，稳定性较好)"

        recommendations.update(
            {
                "primary_signal": primary_signal,
                "recommended_action": action,
                "confidence_level": confidence,
                "valuation_metrics": {
                    "consensus_value": consensus.consensus_value if consensus else None,
                    "valuation_gap": consensus.valuation_gap if consensus else None,
                    "confidence_score": consensus.confidence_score if consensus else None,
                },
                "fundamental_health": (
                    {
                        "roe": dupont.roe if dupont else None,
                        "profit_margin": dupont.profit_margin if dupont else None,
                        "asset_turnover": dupont.asset_turnover if dupont else None,
                    }
                    if dupont
                    else None
                ),
            }
        )

    except Exception as e:
        print(f"Error generating valuation recommendations: {e}")
        recommendations = {
            "primary_signal": "hold",
            "recommended_action": "分析过程中出现错误，建议观望",
            "confidence_level": "low",
        }

    return recommendations


def _assess_valuation_risk(
    self,
    dcf: Optional[DCFValuation],
    relative: Optional[RelativeValuation],
    consensus: Optional[ValuationConsensus],
) -> Dict[str, Any]:
    """评估估值风险"""
    risk_assessment = {}

    try:
        # DCF风险
        dcf_risk = "low"
        if dcf:
            if dcf.confidence_level < 0.5:
                dcf_risk = "high"  # DCF置信度低
            elif abs(dcf.upside_potential) > 50:
                dcf_risk = "medium"  # 估值偏差较大
        else:
            dcf_risk = "medium"

        # 相对估值风险
        relative_risk = "low"
        if relative:
            pe_extreme = relative.industry_pe_percentile > 0.9 or relative.industry_pe_percentile < 0.1
            pb_extreme = relative.industry_pb_percentile > 0.9 or relative.industry_pb_percentile < 0.1

            if pe_extreme and pb_extreme:
                relative_risk = "high"
            elif pe_extreme or pb_extreme:
                relative_risk = "medium"

        # 共识风险
        consensus_risk = "low"
        if consensus:
            if consensus.confidence_score < 0.6:
                consensus_risk = "high"
            elif abs(consensus.valuation_gap) > 30:
                consensus_risk = "medium"

        # 综合风险等级
        risk_scores = {"high": 3, "medium": 2, "low": 1}
        avg_risk_score = np.mean(
            [risk_scores.get(dcf_risk, 1), risk_scores.get(relative_risk, 1), risk_scores.get(consensus_risk, 1)]
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
                "dcf_risk": dcf_risk,
                "relative_risk": relative_risk,
                "consensus_risk": consensus_risk,
                "risk_factors": [
                    "DCF估值置信度低" if dcf_risk == "high" else None,
                    "相对估值极端偏离" if relative_risk == "high" else None,
                    "估值共识分歧较大" if consensus_risk == "high" else None,
                ],
                "risk_factors": [
                    f
                    for f in [
                        "DCF估值置信度低" if dcf_risk == "high" else None,
                        "相对估值极端偏离" if relative_risk == "high" else None,
                        "估值共识分歧较大" if consensus_risk == "high" else None,
                    ]
                    if f is not None
                ],
            }
        )

    except Exception as e:
        print(f"Error assessing valuation risk: {e}")
        risk_assessment = {"overall_risk_level": "unknown", "error": str(e)}

    return risk_assessment


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.FINANCIAL_VALUATION,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"财务估值分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )


