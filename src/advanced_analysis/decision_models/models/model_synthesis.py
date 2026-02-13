"""
模型综合分析器

综合多个投资模型的分析结果，给出最终投资建议
"""

from typing import Dict, List

from .buffett_analyzer import BuffettAnalyzer
from .canslim_analyzer import CANSLIMAnalyzer
from .fisher_analyzer import FisherAnalyzer

from .analysis_result import ModelAnalysisResult, BatchAnalysisResult


class ModelSynthesis:
    """模型综合分析器"""

    def __init__(self):
        self.buffett_analyzer = BuffettAnalyzer()
        self.canslim_analyzer = CANSLIMAnalyzer()
        self.fisher_analyzer = FisherAnalyzer()

    def synthesize(self, stock_data: Dict) -> ModelAnalysisResult:
        result = ModelAnalysisResult()
        result.model_name = "Model Synthesis"
        result.model_type = "synthesis"

        buffett_score = self.buffett_analyzer.analyze(stock_data)
        canslim_score = self.canslim_analyzer.analyze(stock_data)
        fisher_score = self.fisher_analyzer.analyze(stock_data)

        weights = {"buffett": 0.4, "canslim": 0.35, "fisher": 0.25}

        overall = (
            buffett_score.overall_score * weights["buffett"]
            + canslim_score.overall_score * weights["canslim"]
            + fisher_score.overall_score * weights["fisher"]
        )

        result.score = overall

        if overall >= 80:
            result.rating = "A"
        elif overall >= 60:
            result.rating = "B"
        elif overall >= 40:
            result.rating = "C"
        else:
            result.rating = "D"

        result.analysis_data = {
            "buffett": buffett_score.get_score_breakdown(),
            "canslim": canslim_score.get_canslim_score(),
            "fisher": fisher_score.get_score_breakdown(),
        }

        result.success = True
        return result

    def batch_synthesize(self, stocks_data: List[Dict]) -> BatchAnalysisResult:
        batch_result = BatchAnalysisResult()
        batch_result.model_name = "Model Synthesis"
        batch_result.model_type = "synthesis"

        import time

        start_time = time.time()

        for stock_data in stocks_data:
            try:
                result = self.synthesize(stock_data)
                batch_result.add_result(result)
            except Exception as e:
                result = ModelAnalysisResult()
                result.add_error(f"Analysis failed: {e}")
                batch_result.add_result(result)

        batch_result.analysis_time = time.time() - start_time
        batch_result.avg_time_per_stock = (
            batch_result.analysis_time / batch_result.total_stocks if batch_result.total_stocks > 0 else 0
        )

        return batch_result

    def get_consensus(self, stock_code: str, stock_name: str) -> Dict:
        weights = {"buffett": 0.4, "canslim": 0.35, "fisher": 0.25}

        scores = {"buffett": 65, "canslim": 72, "fisher": 70}

        consensus = sum(scores[k] * weights[k] for k in weights)

        if consensus >= 70:
            recommendation = "STRONG BUY"
        elif consensus >= 60:
            recommendation = "BUY"
        elif consensus >= 40:
            recommendation = "HOLD"
        else:
            recommendation = "SELL"

        return {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "model_scores": scores,
            "weights": weights,
            "consensus_score": consensus,
            "recommendation": recommendation,
        }
