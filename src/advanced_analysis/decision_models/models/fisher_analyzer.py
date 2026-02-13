"""
费雪成长模型分析器

基于菲利普·费雪的成长投资哲学，分析股票成长性
"""

from typing import Dict, Optional

from .model_scores import OverallModelScore, ModelScoreConfig


class FisherAnalyzer:
    def __init__(self, config: Optional[ModelScoreConfig] = None):
        self.config = config or ModelScoreConfig()
        self.config.growth_weight = 60.0
        self.config.quality_weight = 25.0
        self.config.technical_weight = 10.0
        self.config.valuation_weight = 5.0

    def analyze(self, stock_data: Dict) -> OverallModelScore:
        score = OverallModelScore(
            stock_code=stock_data.get("code", ""), stock_name=stock_data.get("name", ""), config=self.config
        )

        self._check_15_points(stock_data, score)
        score.calculate_overall_score()

        return score

    def _check_15_points(self, stock_data: Dict, score: OverallModelScore):
        growth_factor = stock_data.get("growth_factor", 0)
        profit_margin = stock_data.get("profit_margin", 0)
        earnings_growth = stock_data.get("earnings_growth", 0)

        if growth_factor >= 9:
            score.growth.score = 90
        elif growth_factor >= 7:
            score.growth.score = 70
        elif growth_factor >= 5:
            score.growth.score = 50
        else:
            score.growth.score = 30

        score.growth.score *= self.config.growth_weight / 100

        if profit_margin >= 20:
            score.quality.score = 85
        elif profit_margin >= 15:
            score.quality.score = 65
        elif profit_margin >= 10:
            score.quality.score = 45
        else:
            score.quality.score = 25

        score.quality.score *= self.config.quality_weight / 100

        if earnings_growth >= 15:
            score.growth.score += 10
        elif earnings_growth >= 10:
            score.growth.score += 7
        elif earnings_growth >= 5:
            score.growth.score += 4
