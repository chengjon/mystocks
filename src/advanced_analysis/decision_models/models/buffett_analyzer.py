"""
巴菲特价值投资模型分析器

基于沃伦·巴菲特的价值投资哲学，分析股票投资价值
"""

from typing import Dict, List, Optional
from datetime import datetime

from .model_scores import OverallModelScore, ModelScoreConfig, ValuationScore, GrowthScore, QualityScore, TechnicalScore


class BuffettAnalyzer:
    """巴菲特模型分析器"""

    def __init__(self, config: Optional[ModelScoreConfig] = None):
        self.config = config or ModelScoreConfig()

        # 调整权重（巴菲特模型更注重估值和质量）
        self.config.valuation_weight = 40.0  # 估值权重提升
        self.config.quality_weight = 30.0  # 质量权重提升
        self.config.growth_weight = 15.0  # 成长权重降低
        self.config.technical_weight = 15.0  # 技术权重降低

    def analyze(self, stock_data: Dict) -> OverallModelScore:
        """
        分析股票

        Args:
            stock_data: 包含股票数据的字典，需要以下字段：
                - 基础信息: code, name, price
                - 财务数据: pe, pb, roe, roa, profit_growth, revenue_growth
                - 质量数据: gross_margin, operating_margin, net_margin
                - 技术数据: ma_signal, macd_signal, rsi
        """
        score = OverallModelScore(
            stock_code=stock_data.get("code", ""), stock_name=stock_data.get("name", ""), config=self.config
        )

        # 1. 估值分析（权重 40%）
        score.valuation = ValuationScore(
            pe_ratio=stock_data.get("pe", 0),
            pb_ratio=stock_data.get("pb", 0),
            ps_ratio=stock_data.get("ps", 0),
            ev_ebitda=stock_data.get("ev_ebitda", 0),
            peg_ratio=stock_data.get("peg", 0),
        )
        score.valuation.calculate_score(self.config)

        # 2. 成长分析（权重 15%）
        score.growth = GrowthScore(
            revenue_growth=stock_data.get("revenue_growth", 0),
            profit_growth=stock_data.get("profit_growth", 0),
            eps_growth=stock_data.get("eps_growth", 0),
        )
        score.growth.calculate_score(self.config)

        # 3. 质量分析（权重 30%）
        score.quality = QualityScore(
            roe=stock_data.get("roe", 0),
            roa=stock_data.get("roa", 0),
            gross_margin=stock_data.get("gross_margin", 0),
            operating_margin=stock_data.get("operating_margin", 0),
            net_margin=stock_data.get("net_margin", 0),
        )
        score.quality.calculate_score(self.config)

        # 4. 技术分析（权重 15%）
        score.technical = TechnicalScore(
            ma_signal=stock_data.get("ma_signal", "neutral"),
            macd_signal=stock_data.get("macd_signal", "neutral"),
            rsi_score=stock_data.get("rsi", 50),
            bollinger_position=stock_data.get("bollinger_position", "neutral"),
        )
        score.technical.calculate_score(self.config)

        # 5. 计算综合评分
        score.calculate_overall_score()

        return score

    def check_value_investment_criteria(self, score: OverallModelScore) -> Dict:
        """
        检查是否符合巴菲特价值投资标准

        巴菲特价值投资标准：
        1. 估值合理（PE < 20, PB < 3)
        2. 持续增长（营收和利润持续增长）
        3. 高质量（ROE > 15%, 毛利率 > 20%）
        4. 竞争优势（护城河）
        5. 管理优秀（管理层）
        """
        criteria = {"meets_criteria": False, "reasons": [], "warnings": []}

        # 1. 估值检查
        if score.valuation.pe_ratio < 20:
            criteria["reasons"].append("PE比率合理 (< 20)")
        else:
            criteria["warnings"].append(f"PE比率偏高 ({score.valuation.pe_ratio:.1f})")

        if score.valuation.pb_ratio < 3:
            criteria["reasons"].append("PB比率合理 (< 3)")
        else:
            criteria["warnings"].append(f"PB比率偏高 ({score.valuation.pb_ratio:.1f})")

        # 2. 成长检查
        if score.growth.revenue_growth > 10:
            criteria["reasons"].append("营收增长率 > 10%")
        else:
            criteria["warnings"].append(f"营收增长率较低 ({score.growth.revenue_growth:.1f}%)")

        if score.growth.profit_growth > 10:
            criteria["reasons"].append("利润增长率 > 10%")
        else:
            criteria["warnings"].append(f"利润增长率较低 ({score.growth.profit_growth:.1f}%)")

        # 3. 质量检查
        if score.quality.roe > 15:
            criteria["reasons"].append("ROE > 15%")
        else:
            criteria["warnings"].append(f"ROE较低 ({score.quality.roe:.1f}%)")

        if score.quality.gross_margin > 20:
            criteria["reasons"].append("毛利率 > 20%")
        else:
            criteria["warnings"].append(f"毛利率较低 ({score.quality.gross_margin:.1f}%)")

        # 4. 综合判断
        if (
            score.valuation.pe_ratio < 20
            and score.valuation.pb_ratio < 3
            and score.growth.revenue_growth > 10
            and score.growth.profit_growth > 10
            and score.quality.roe > 15
            and score.quality.gross_margin > 20
        ):
            criteria["meets_criteria"] = True

        return criteria

    def get_investment_recommendation(self, score: OverallModelScore) -> str:
        """
        获取投资建议
        """
        criteria = self.check_value_investment_criteria(score)

        if criteria["meets_criteria"] and score.overall_score >= 70:
            return "STRONG_BUY"
        elif criteria["meets_criteria"] and score.overall_score >= 60:
            return "BUY"
        elif score.overall_score >= 60:
            return "HOLD"
        else:
            return "SELL"

    def get_analysis_summary(self, score: OverallModelScore) -> Dict:
        """
        获取分析摘要
        """
        criteria = self.check_value_investment_criteria(score)
        recommendation = self.get_investment_recommendation(score)

        return {
            "model": "Buffett Value Investing",
            "overall_score": score.overall_score,
            "overall_rating": score.overall_rating,
            "recommendation": recommendation,
            "valuation": {
                "score": score.valuation.score,
                "rating": score.valuation.rating,
                "pe_ratio": score.valuation.pe_ratio,
                "pb_ratio": score.valuation.pb_ratio,
            },
            "growth": {
                "score": score.growth.score,
                "rating": score.growth.rating,
                "revenue_growth": score.growth.revenue_growth,
                "profit_growth": score.growth.profit_growth,
            },
            "quality": {
                "score": score.quality.score,
                "rating": score.quality.rating,
                "roe": score.quality.roe,
                "gross_margin": score.quality.gross_margin,
            },
            "technical": {
                "score": score.technical.score,
                "rating": score.technical.rating,
                "ma_signal": score.technical.ma_signal,
                "macd_signal": score.technical.macd_signal,
            },
            "buffett_criteria": criteria,
            "calculated_at": score.calculated_at.isoformat(),
        }
