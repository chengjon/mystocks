"""
决策模型分析核心逻辑

整合数据管理、模型分析和结果输出的核心逻辑
"""

from typing import Dict, List

from .data_manager import DataManager
from .buffett_analyzer import BuffettAnalyzer
from .canslim_analyzer import CANSLIMAnalyzer
from .fisher_analyzer import FisherAnalyzer
from .model_synthesis import ModelSynthesis

from .analysis_result import ModelAnalysisResult, BatchAnalysisResult


class DecisionAnalyzerCore:
    """决策模型分析核心"""

    def __init__(self, data_path: str = "data/"):
        self.data_manager = DataManager(data_path)
        self.model_synthesis = ModelSynthesis()

        self.buffett_analyzer = BuffettAnalyzer()
        self.canslim_analyzer = CANSLIMAnalyzer()
        self.fisher_analyzer = FisherAnalyzer()

        self.analysis_history = []

    def analyze_single_stock(self, stock_code: str, stock_name: str) -> ModelAnalysisResult:
        """
        分析单个股票

        返回巴菲特、CAN SLIM、费雪模型的综合分析结果
        """
        result = ModelAnalysisResult()
        result.model_name = f"Decision Analysis: {stock_code}"
        result.model_type = "synthesis"
        result.stock_code = stock_code
        result.stock_name = stock_name

        stock_data = self.data_manager.load_stock_data(stock_code)

        if not stock_data:
            result.add_error(f"Stock data not found: {stock_code}")
            return result

        try:
            buffett_score = self.buffett_analyzer.analyze(stock_data)
            canslim_score = self.canslim_analyzer.analyze(stock_data)
            fisher_score = self.fisher_analyzer.analyze(stock_data)

            synthesis = self.model_synthesis.synthesize(stock_data)

            result.analysis_data = {
                "buffett": {
                    "score": buffett_score.overall_score,
                    "rating": buffett_score.overall_rating,
                    "summary": self.buffett_analyzer.get_analysis_summary(buffett_score),
                },
                "canslim": {
                    "score": canslim_score.overall_score,
                    "rating": canslim_score.overall_rating,
                    "summary": self.canslim_analyzer.get_canslim_score(canslim_score),
                },
                "fisher": {
                    "score": fisher_score.overall_score,
                    "rating": fisher_score.overall_rating,
                    "summary": self.fisher_analyzer.get_analysis_summary(fisher_score),
                },
                "synthesis": {
                    "overall_score": synthesis.score,
                    "overall_rating": synthesis.rating,
                    "recommendation": self.model_synthesis.get_consensus(stock_code, stock_name, synthesis.score),
                },
            }

            result.score = synthesis.score
            result.rating = synthesis.rating
            result.success = True

            result.data_manager.save_analysis_result(stock_code, "decision_models", result.to_dict())

        except Exception as e:
            result.add_error(f"Analysis failed: {e}")

        self.analysis_history.append(result)
        return result

    def analyze_multiple_stocks(self, stock_codes: List[str]) -> BatchAnalysisResult:
        """
        批量分析多个股票

        返回所有股票的分析结果
        """
        batch_result = BatchAnalysisResult()

        import time

        start_time = time.time()

        for i, stock_code in enumerate(stock_codes, 1):
            print(f"Analyzing stock {i}/{len(stock_codes)}: {stock_code}")
            result = self.analyze_single_stock(stock_code, f"Stock_{i}")
            batch_result.add_result(result)

        end_time = time.time()
        batch_result.analysis_time = end_time - start_time
        batch_result.avg_time_per_stock = batch_result.analysis_time / len(stock_codes) if stock_codes else 0

        return batch_result

    def get_model_comparison(self, stock_code: str, stock_name: str) -> Dict:
        """
        获取三个模型的对比
        """
        stock_data = self.data_manager.load_stock_data(stock_code)

        if not stock_data:
            return {"error": "Stock data not found"}

        buffett_score = self.buffett_analyzer.analyze(stock_data)
        canslim_score = self.canslim_analyzer.analyze(stock_data)
        fisher_score = self.fisher_analyzer.analyze(stock_data)

        comparison = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "models": {
                "buffett": {
                    "score": buffett_score.overall_score,
                    "rating": buffett_score.overall_rating,
                    "valuation_score": buffett_score.valuation.score,
                    "growth_score": buffett_score.growth.score,
                    "quality_score": buffett_score.quality.score,
                },
                "canslim": {
                    "score": canslim_score.overall_score,
                    "rating": canslim_score.overall_rating,
                    "c_score": canslim_score.growth.score,
                    "a_score": canslim_score.growth.score,
                    "n_score": canslim_score.growth.score,
                },
                "fisher": {
                    "score": fisher_score.overall_score,
                    "rating": fisher_score.overall_rating,
                    "growth_factor_score": fisher_score.growth.score,
                },
            },
            "summary": {
                "best_model": "buffett" if buffett_score.overall_score >= canslim_score.overall_score else "canslim",
                "overall_score": max(
                    buffett_score.overall_score, canslim_score.overall_score, fisher_score.overall_score
                ),
                "agreement": self._calculate_model_agreement(buffett_score, canslim_score, fisher_score),
            },
        }

        return comparison

    def _calculate_model_agreement(self, buffett_score, canslim_score, fisher_score) -> float:
        """
        计算模型一致性（基于评级）
        """
        ratings = [buffett_score.overall_rating, canslim_score.overall_rating, fisher_score.overall_rating]

        if len(set(ratings)) == 1:
            return 1.0
        elif "A" in ratings and "D" not in ratings:
            return 0.8
        else:
            return 0.5

    def export_results(self, filepath: str):
        """
        导出所有分析结果
        """
        results = {
            "analysis_history": [r.to_dict() for r in self.analysis_history],
            "cache_stats": self.data_manager.get_cache_stats(),
            "timestamp": str(self.data_manager.last_update) if self.data_manager.last_update else None,
        }

        import json

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
