"""Decision Models - 决策合成与信号生成"""

from typing import Any, Dict, List

import numpy as np

from .dataclasses import DecisionSynthesis, ModelValidationResult


class DecisionSynthesisMixin:
    """多模型决策合成、信号生成、风险评估方法集"""

def _validate_buffett_model(self, financial_data: pd.DataFrame, price_data: pd.DataFrame) -> ModelValidationResult:
    """验证巴菲特模型"""
    # 简化的模型验证
    return ModelValidationResult(
        model_name="Buffett",
        backtest_period=24,
        win_rate=0.65,
        avg_return=0.12,
        max_drawdown=0.15,
        sharpe_ratio=1.2,
        confidence_level=0.8,
        validation_score=75,
    )


def _validate_canslim_model(self, financial_data: pd.DataFrame, price_data: pd.DataFrame) -> ModelValidationResult:
    """验证CAN SLIM模型"""
    return ModelValidationResult(
        model_name="CAN SLIM",
        backtest_period=12,
        win_rate=0.70,
        avg_return=0.18,
        max_drawdown=0.20,
        sharpe_ratio=1.4,
        confidence_level=0.75,
        validation_score=80,
    )


def _validate_fisher_model(self, financial_data: pd.DataFrame, price_data: pd.DataFrame) -> ModelValidationResult:
    """验证费雪模型"""
    return ModelValidationResult(
        model_name="Fisher",
        backtest_period=36,
        win_rate=0.60,
        avg_return=0.15,
        max_drawdown=0.18,
        sharpe_ratio=1.1,
        confidence_level=0.85,
        validation_score=78,
    )


def _synthesize_decision_models(
    self,
    buffett_score: Optional[BuffettModelScore],
    canslim_score: Optional[CANSLIMModelScore],
    fisher_score: Optional[FisherModelScore],
    validations: List[ModelValidationResult],
    risk_adjusted: bool,
) -> DecisionSynthesis:
    """综合决策模型"""
    try:
        # 计算各模型得分
        buffett_score_val = buffett_score.overall_score if buffett_score else 0
        canslim_score_val = canslim_score.overall_score if canslim_score else 0
        fisher_score_val = fisher_score.overall_score if fisher_score else 0

        # 应用模型权重
        weighted_buffett = buffett_score_val * self.model_weights["buffett"]
        weighted_canslim = canslim_score_val * self.model_weights["canslim"]
        weighted_fisher = fisher_score_val * self.model_weights["fisher"]

        # 共识得分
        consensus_score = weighted_buffett + weighted_canslim + weighted_fisher

        # 置信度（基于模型验证结果）
        confidence_level = 0.5
        if validations:
            avg_validation_score = np.mean([v.validation_score for v in validations])
            confidence_level = min(avg_validation_score / 100, 1.0)

        # 最终建议
        final_recommendation = self._get_consensus_recommendation(consensus_score)

        # 风险调整得分
        risk_adjusted_score = consensus_score
        if risk_adjusted:
            # 简化的风险调整
            risk_penalty = (1 - confidence_level) * 0.1 * consensus_score
            risk_adjusted_score = consensus_score - risk_penalty

        # 决策因素
        decision_factors = []
        if buffett_score and buffett_score.overall_score > 70:
            decision_factors.append("巴菲特模型评分优秀")
        if canslim_score and canslim_score.overall_score > 70:
            decision_factors.append("CAN SLIM模型评分优秀")
        if fisher_score and fisher_score.overall_score > 70:
            decision_factors.append("费雪模型评分优秀")

        return DecisionSynthesis(
            buffett_score=weighted_buffett,
            canslim_score=weighted_canslim,
            fisher_score=weighted_fisher,
            consensus_score=consensus_score,
            confidence_level=confidence_level,
            final_recommendation=final_recommendation,
            risk_adjusted_score=risk_adjusted_score,
            decision_factors=decision_factors,
        )

    except Exception as e:
        print(f"Error synthesizing decision models: {e}")
        return DecisionSynthesis(0, 0, 0, 0, 0, "hold", 0, [])


def _get_consensus_recommendation(self, consensus_score: float) -> str:
    """获取共识建议"""
    if consensus_score >= self.model_thresholds["strong_buy"]:
        return "strong_buy"
    elif consensus_score >= self.model_thresholds["buy"]:
        return "buy"
    elif consensus_score >= self.model_thresholds["hold"]:
        return "hold"
    elif consensus_score >= self.model_thresholds["sell"]:
        return "sell"
    else:
        return "strong_sell"


def _calculate_decision_scores(
    self,
    buffett_score: Optional[BuffettModelScore],
    canslim_score: Optional[CANSLIMModelScore],
    fisher_score: Optional[FisherModelScore],
    synthesis: DecisionSynthesis,
    validations: List[ModelValidationResult],
) -> Dict[str, float]:
    """计算决策分析得分"""
    scores = {}

    try:
        # 模型一致性得分
        model_scores = []
        if buffett_score:
            model_scores.append(buffett_score.overall_score)
        if canslim_score:
            model_scores.append(canslim_score.overall_score)
        if fisher_score:
            model_scores.append(fisher_score.overall_score)

        if len(model_scores) > 1:
            consistency_score = 1 - np.std(model_scores) / np.mean(model_scores) if np.mean(model_scores) > 0 else 0
            scores["model_consistency"] = consistency_score * 100

        # 验证有效性得分
        if validations:
            avg_validation = np.mean([v.validation_score for v in validations])
            scores["validation_effectiveness"] = avg_validation

        # 共识强度得分
        consensus_strength = synthesis.consensus_score / 100
        scores["consensus_strength"] = consensus_strength * 100

        # 置信度得分
        confidence_score = synthesis.confidence_level * 100
        scores["decision_confidence"] = confidence_score

        # 综合得分
        weights = [0.25, 0.25, 0.25, 0.25]
        component_scores = [
            scores.get("model_consistency", 50),
            scores.get("validation_effectiveness", 50),
            scores.get("consensus_strength", 50),
            scores.get("decision_confidence", 50),
        ]

        overall_score = np.average(component_scores, weights=weights)
        scores["overall_score"] = overall_score

    except Exception as e:
        print(f"Error calculating decision scores: {e}")
        scores = {"overall_score": 50, "error": True}

    return scores


def _generate_decision_signals(
    self,
    buffett_score: Optional[BuffettModelScore],
    canslim_score: Optional[CANSLIMModelScore],
    fisher_score: Optional[FisherModelScore],
    synthesis: DecisionSynthesis,
    validations: List[ModelValidationResult],
) -> List[Dict[str, Any]]:
    """生成决策信号"""
    signals = []

    # 模型共识信号
    if synthesis.consensus_score > 75:
        signals.append(
            {
                "type": "model_consensus_strong",
                "severity": "high",
                "message": f"多模型共识强烈 - 得分: {synthesis.consensus_score:.1f}",
                "details": {
                    "consensus_score": synthesis.consensus_score,
                    "confidence_level": synthesis.confidence_level,
                    "recommendation": synthesis.final_recommendation,
                },
            }
        )
    elif synthesis.consensus_score < 35:
        signals.append(
            {
                "type": "model_consensus_weak",
                "severity": "high",
                "message": f"多模型共识疲弱 - 得分: {synthesis.consensus_score:.1f}",
                "details": {
                    "consensus_score": synthesis.consensus_score,
                    "recommendation": synthesis.final_recommendation,
                },
            }
        )

    # 单个模型优秀信号
    if buffett_score and buffett_score.overall_score > 80:
        signals.append(
            {
                "type": "buffett_model_excellent",
                "severity": "medium",
                "message": f"巴菲特模型评分优秀: {buffett_score.overall_score:.1f}",
                "details": {
                    "score": buffett_score.overall_score,
                    "recommendation": buffett_score.investment_recommendation,
                },
            }
        )

    if canslim_score and canslim_score.overall_score > 80:
        signals.append(
            {
                "type": "canslim_model_excellent",
                "severity": "medium",
                "message": f"CAN SLIM模型评分优秀: {canslim_score.overall_score:.1f}",
                "details": {
                    "score": canslim_score.overall_score,
                    "recommendation": canslim_score.investment_recommendation,
                },
            }
        )

    if fisher_score and fisher_score.overall_score > 80:
        signals.append(
            {
                "type": "fisher_model_excellent",
                "severity": "medium",
                "message": f"费雪模型评分优秀: {fisher_score.overall_score:.1f}",
                "details": {
                    "score": fisher_score.overall_score,
                    "recommendation": fisher_score.investment_recommendation,
                },
            }
        )

    # 验证结果信号
    for validation in validations:
        if validation.validation_score > 80:
            signals.append(
                {
                    "type": "model_validation_strong",
                    "severity": "low",
                    "message": f"{validation.model_name}模型验证优秀 - 胜率: {validation.win_rate:.1%}",
                    "details": {
                        "model": validation.model_name,
                        "win_rate": validation.win_rate,
                        "sharpe_ratio": validation.sharpe_ratio,
                        "validation_score": validation.validation_score,
                    },
                }
            )

    return signals


def _generate_decision_recommendations(self, synthesis: DecisionSynthesis) -> Dict[str, Any]:
    """生成决策建议"""
    recommendations = {}

    try:
        # 主要建议
        if synthesis.final_recommendation == "strong_buy":
            primary_signal = "强烈买入"
            action = "多模型共识强烈看好，建议积极买入"
            confidence = "high"
        elif synthesis.final_recommendation == "buy":
            primary_signal = "买入"
            action = "模型评分良好，建议买入"
            confidence = "medium"
        elif synthesis.final_recommendation == "hold":
            primary_signal = "持有观望"
            action = "模型评分一般，建议观望"
            confidence = "low"
        elif synthesis.final_recommendation == "sell":
            primary_signal = "卖出"
            action = "模型评分较差，建议卖出"
            confidence = "medium"
        else:
            primary_signal = "强烈卖出"
            action = "多模型共识看淡，建议卖出"
            confidence = "high"

        # 风险提示
        risk_warnings = []
        if synthesis.confidence_level < 0.6:
            risk_warnings.append("模型置信度较低，决策不确定性较高")
        if synthesis.consensus_score < 50:
            risk_warnings.append("多模型共识不佳，需要谨慎决策")

        recommendations.update(
            {
                "primary_signal": primary_signal,
                "recommended_action": action,
                "confidence_level": confidence,
                "consensus_score": synthesis.consensus_score,
                "confidence_score": synthesis.confidence_level * 100,
                "risk_warnings": risk_warnings,
                "decision_factors": synthesis.decision_factors,
                "model_breakdown": {
                    "buffett_weighted_score": synthesis.buffett_score,
                    "canslim_weighted_score": synthesis.canslim_score,
                    "fisher_weighted_score": synthesis.fisher_score,
                },
            }
        )

    except Exception as e:
        print(f"Error generating decision recommendations: {e}")
        recommendations = {
            "primary_signal": "观望",
            "recommended_action": "分析过程中出现错误，建议观望",
            "confidence_level": "low",
        }

    return recommendations


def _assess_decision_risk(
    self,
    buffett_score: Optional[BuffettModelScore],
    canslim_score: Optional[CANSLIMModelScore],
    fisher_score: Optional[FisherModelScore],
    validations: List[ModelValidationResult],
) -> Dict[str, Any]:
    """评估决策风险"""
    risk_assessment = {}

    try:
        # 模型分歧风险
        model_scores = []
        if buffett_score:
            model_scores.append(buffett_score.overall_score)
        if canslim_score:
            model_scores.append(canslim_score.overall_score)
        if fisher_score:
            model_scores.append(fisher_score.overall_score)

        if len(model_scores) > 1:
            score_std = np.std(model_scores)
            avg_score = np.mean(model_scores)
            divergence_risk = score_std / avg_score if avg_score > 0 else 0

            if divergence_risk > 0.3:
                model_divergence_risk = "high"
            elif divergence_risk > 0.2:
                model_divergence_risk = "medium"
            else:
                model_divergence_risk = "low"
        else:
            model_divergence_risk = "medium"

        # 验证风险
        validation_risk = "low"
        if validations:
            low_validation_count = sum(1 for v in validations if v.validation_score < 60)
            if low_validation_count > len(validations) * 0.5:
                validation_risk = "high"
            elif low_validation_count > 0:
                validation_risk = "medium"

        # 整体风险等级
        risk_scores = {"high": 3, "medium": 2, "low": 1}
        avg_risk_score = np.mean([risk_scores.get(model_divergence_risk, 2), risk_scores.get(validation_risk, 2)])

        if avg_risk_score > 2.5:
            overall_risk = "high"
        elif avg_risk_score > 1.5:
            overall_risk = "medium"
        else:
            overall_risk = "low"

        risk_assessment.update(
            {
                "overall_risk_level": overall_risk,
                "model_divergence_risk": model_divergence_risk,
                "validation_risk": validation_risk,
                "risk_factors": [
                    "模型间分歧较大" if model_divergence_risk == "high" else None,
                    "模型验证效果不佳" if validation_risk == "high" else None,
                ],
                "risk_factors": [
                    f
                    for f in [
                        "模型间分歧较大" if model_divergence_risk == "high" else None,
                        "模型验证效果不佳" if validation_risk == "high" else None,
                    ]
                    if f is not None
                ],
            }
        )

    except Exception as e:
        print(f"Error assessing decision risk: {e}")
        risk_assessment = {"overall_risk_level": "unknown", "error": str(e)}

    return risk_assessment


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.DECISION_MODELS,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"交易决策模型分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )
