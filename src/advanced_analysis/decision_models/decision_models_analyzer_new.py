"""
决策模型分析器 - 向后兼容的主文件

此文件提供向后兼容的接口，导出原始decision_models_analyzer.py的所有功能
"""

from typing import Dict, List, Optional
from datetime import datetime

from .base.model_scores import (
    ModelScoreConfig,
    OverallModelScore,
    ValuationScore,
    GrowthScore,
    QualityScore,
    TechnicalScore,
)
from .base.analysis_result import AnalysisResult, ModelAnalysisResult, BatchAnalysisResult
from .models.buffett_analyzer import BuffettAnalyzer
from .models.canslim_analyzer import CANSLIMAnalyzer
from .models.fisher_analyzer import FisherAnalyzer
from .models.model_synthesis import ModelSynthesis
from .main.data_manager import DataManager
from .main.analyzer_core import DecisionAnalyzerCore


class DecisionModelsAnalyzer:
    """
    决策模型分析器主类（向后兼容）

    整合了三个投资模型的分析功能：
    1. 巴菲特价值投资模型
    2. CAN SLIM成长模型
    3. 费雪成长模型
    """

    def __init__(self, data_path: str = "data/"):
        self.analyzer = DecisionAnalyzerCore(data_path)
        self.model_synthesis = ModelSynthesis()

    def analyze(self, stock_code: str, stock_data: Optional[Dict] = None) -> ModelAnalysisResult:
        """
        分析股票（向后兼容接口）

        Args:
            stock_code: 股票代码
            stock_data: 股票数据（可选，如果不提供则从data_manager加载）

        Returns:
            ModelAnalysisResult: 分析结果
        """
        if stock_data is None:
            stock_data = self.analyzer.data_manager.load_stock_data(stock_code)

        return self.analyzer.analyze_single_stock(stock_code, stock_data.get("name", f"Stock {stock_code}"))

    def analyze_multiple(self, stock_codes: List[str]) -> BatchAnalysisResult:
        """
        分析多个股票（向后兼容接口）

        Args:
            stock_codes: 股票代码列表

        Returns:
            BatchAnalysisResult: 批量分析结果
        """
        return self.analyzer.analyze_multiple_stocks(stock_codes)

    def get_buffett_analysis(self, stock_code: str) -> Dict:
        """
        获取巴菲特分析结果（向后兼容接口）
        """
        stock_data = self.analyzer.data_manager.load_stock_data(stock_code)
        buffett_score = self.analyzer.buffett_analyzer.analyze(stock_data)
        return self.analyzer.buffett_analyzer.get_analysis_summary(buffett_score)

    def get_canslim_analysis(self, stock_code: str) -> Dict:
        """
        获取CAN SLIM分析结果（向后兼容接口）
        """
        stock_data = self.analyzer.data_manager.load_stock_data(stock_code)
        canslim_score = self.analyzer.canslim_analyzer.analyze(stock_data)
        return self.analyzer.canslim_analyzer.get_canslim_score(canslim_score)

    def get_fisher_analysis(self, stock_code: str) -> Dict:
        """
        获取费雪分析结果（向后兼容接口）
        """
        stock_data = self.analyzer.data_manager.load_stock_data(stock_code)
        fisher_score = self.analyzer.fisher_analyzer.analyze(stock_data)
        return self.analyzer.fisher_analyzer.get_analysis_summary(fisher_score)

    def get_model_synthesis(self, stock_code: str) -> Dict:
        """
        获取模型综合分析结果（向后兼容接口）
        """
        stock_data = self.analyzer.data_manager.load_stock_data(stock_code)
        return self.model_synthesis.get_consensus(stock_code, stock_data.get("name", f"Stock {stock_code}"))


def analyze_stock(stock_code: str, stock_data: Optional[Dict] = None) -> Dict:
    """
    分析股票（向后兼容函数）

    Args:
        stock_code: 股票代码
        stock_data: 股票数据（可选）

    Returns:
        Dict: 分析结果
    """
    analyzer = DecisionModelsAnalyzer()
    result = analyzer.analyze(stock_code, stock_data)
    return result.to_dict()


def analyze_multiple_stocks(stock_codes: List[str]) -> Dict:
    """
    分析多个股票（向后兼容函数）

    Args:
        stock_codes: 股票代码列表

    Returns:
        Dict: 批量分析结果
    """
    analyzer = DecisionModelsAnalyzer()
    result = analyzer.analyze_multiple(stock_codes)
    return result.get_statistics()


def get_model_comparison(stock_code: str) -> Dict:
    """
    获取模型对比（向后兼容函数）

    Args:
        stock_code: 股票代码

    Returns:
        Dict: 模型对比结果
    """
    analyzer = DecisionModelsAnalyzer()
    return analyzer.analyzer.get_model_comparison(stock_code, f"Stock {stock_code}")


if __name__ == "__main__":
    import sys

    print("Decision Models Analyzer - Backward Compatible Version")
    print("=" * 60)
    print(f"Created: {datetime.now().isoformat()}")
    print("=" * 60)

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("\nUsage:")
        print("  python decision_models_analyzer.py")
        print("  python decision_models_analyzer.py <stock_code>")
        print("  python decision_models_analyzer.py <stock_code_1> <stock_code_2> ...")
        print("\nExamples:")
        print("  python decision_models_analyzer.py 600519")
        print("  python decision_models_analyzer.py 600519 300750")
        print("\nAPI:")
        print("  analyze_stock(stock_code, stock_data)")
        print("  analyze_multiple_stocks(stock_codes)")
        print("  get_model_comparison(stock_code)")
        sys.exit(0)
