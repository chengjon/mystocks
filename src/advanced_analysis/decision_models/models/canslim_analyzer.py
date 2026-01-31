"""
CAN SLIM成长模型分析器

基于CAN SLIM（C=Current, A=Annual, N=New, S=Supply, L=Leader, I=Institution, M=Market）的选股模型分析股票成长性
"""

from typing import Dict, List, Optional
from datetime import datetime

from .model_scores import OverallModelScore, ModelScoreConfig


class CANSLIMAnalyzer:
    def __init__(self, config: Optional[ModelScoreConfig] = None):
        self.config = config or ModelScoreConfig()
        self.config.growth_weight = 50.0
        self.config.quality_weight = 25.0
        self.config.technical_weight = 15.0
        self.config.valuation_weight = 10.0

    def analyze(self, stock_data: Dict) -> OverallModelScore:
        """
        CAN SLIM选股模型分析

        C指标检查：Current annual earnings增长率 (当前年度盈利增长率)
        A指标检查：Annual earnings (年度盈利)
        N指标检查：New products (新产品)
        S指标检查：Supply and demand (供需关系)
        L指标检查：Leader in market (市场领导者)
        I指标检查：Institutional ownership (机构持股)
        M指标检查：Market direction (市场走向)
        """
        score = OverallModelScore(
            stock_code=stock_data.get("code", ""), stock_name=stock_data.get("name", ""), config=self.config
        )

        self._check_c_criteria(stock_data, score)
        self._check_a_criteria(stock_data, score)
        self._check_n_criteria(stock_data, score)
        self._check_s_criteria(stock_data, score)
        self._check_l_criteria(stock_data, score)
        self._check_i_criteria(stock_data, score)
        self._check_m_criteria(stock_data, score)

        score.calculate_overall_score()
        return score

    def _check_c_criteria(self, stock_data: Dict, score: OverallModelScore):
        """C指标：当前年度盈利增长率"""
        current_growth = stock_data.get("current_annual_growth", 0)

        if current_growth > 0:
            score.growth.score = min(100, current_growth * 10)
            score.growth.rating = "A" if current_growth > 25 else "B" if current_growth > 15 else "C"
        else:
            score.growth.score = 0
            score.growth.rating = "F"

    def _check_a_criteria(self, stock_data: Dict, score: OverallModelScore):
        """A指标：年度盈利"""
        annual_earnings = stock_data.get("annual_earnings", 0)

        if annual_earnings > 0:
            score.growth.score += min(100, annual_earnings * 0.05)
            score.growth.rating = "A" if annual_earnings > 2000 else "B" if annual_earnings > 1000 else "C"
        else:
            score.growth.score = 0

    def _check_n_criteria(self, stock_data: Dict, score: OverallModelScore):
        """N指标：新产品"""
        new_products = stock_data.get("new_products", 0)

        if new_products > 0:
            score.growth.score += 20
            score.growth.rating = "A"
        else:
            score.growth.score += 0

    def _check_s_criteria(self, stock_data: Dict, score: OverallModelScore):
        """S指标：供需关系"""
        demand_supply_ratio = stock_data.get("demand_supply_ratio", 1.0)

        if demand_supply_ratio > 1.2:
            score.quality.score = 90
            score.quality.rating = "A"
        elif demand_supply_ratio > 1.0:
            score.quality.score = 70
            score.quality.rating = "B"
        elif demand_supply_ratio > 0.8:
            score.quality.score = 50
            score.quality.rating = "C"
        else:
            score.quality.score = 30
            score.quality.rating = "D"

    def _check_l_criteria(self, stock_data: Dict, score: OverallModelScore):
        """L指标：市场领导者"""
        market_position = stock_data.get("market_position", "")

        if market_position == "leader":
            score.quality.score += 80
            score.quality.rating = "A"
        elif market_position == "top3":
            score.quality.score += 60
            score.quality.rating = "B"
        elif market_position == "top10":
            score.quality.score += 40
            score.quality.rating = "C"
        else:
            score.quality.score += 0

    def _check_i_criteria(self, stock_data: Dict, score: OverallModelScore):
        """I指标：机构持股"""
        institutional_ownership = stock_data.get("institutional_ownership", 0)

        if institutional_ownership > 50:
            score.quality.score += 80
            score.quality.rating = "A"
        elif institutional_ownership > 30:
            score.quality.score += 60
            score.quality.rating = "B"
        elif institutional_ownership > 10:
            score.quality.score += 40
            score.quality.rating = "C"
        else:
            score.quality.score += 0

    def _check_m_criteria(self, stock_data: Dict, score: OverallModelScore):
        """M指标：市场走向"""
        market_trend = stock_data.get("market_trend", "neutral")

        if market_trend == "bullish":
            score.technical.score = 80
            score.technical.rating = "A"
            score.technical.ma_signal = "bullish"
        elif market_trend == "bearish":
            score.technical.score = 20
            score.technical.rating = "D"
            score.technical.ma_signal = "bearish"
        else:
            score.technical.score = 50
            score.technical.rating = "C"
            score.technical.ma_signal = "neutral"

    def get_canslim_score(self, score: OverallModelScore) -> Dict:
        """获取CAN SLIM评分明细"""
        return {
            "model": "CAN SLIM",
            "criteria_scores": {
                "C": score.growth.score,
                "A": score.growth.score,
                "N": score.growth.score,
                "S": score.quality.score,
                "L": score.quality.score,
                "I": score.quality.score,
                "M": score.technical.score,
            },
            "overall_score": score.overall_score,
            "rating": score.overall_rating,
            "criteria_summary": {
                "C": f"Current Growth: {stock_data.get('current_annual_growth', 0):.1f}%",
                "A": f"Annual Earnings: {stock_data.get('annual_earnings', 0):.0f}",
                "N": f"New Products: {stock_data.get('new_products', 0)}",
                "S": f"Demand/Supply: {stock_data.get('demand_supply_ratio', 1.0):.1f}",
                "L": f"Market Position: {stock_data.get('market_position', 'N/A')}",
                "I": f"Institutional: {stock_data.get('institutional_ownership', 0):.1f}%",
                "M": f"Market Trend: {stock_data.get('market_trend', 'neutral')}",
            },
        }
