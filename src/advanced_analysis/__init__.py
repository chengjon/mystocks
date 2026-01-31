"""
MyStocks Advanced Quantitative Analysis Framework
A股量化分析平台高级分析功能框架

This module provides a unified framework for implementing 12 advanced quantitative
analysis features on top of the existing MyStocks platform architecture.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import pandas as pd

from src.core import DataClassification, MyStocksUnifiedManager
from src.gpu.core.hardware_abstraction import GPUResourceManager
from src.monitoring import AlertManager


class AnalysisType(Enum):
    """分析类型枚举"""

    FUNDAMENTAL = "fundamental"
    TECHNICAL = "technical"
    TRADING_SIGNALS = "trading_signals"
    TIME_SERIES = "time_series"
    MARKET_PANORAMA = "market_panorama"
    CAPITAL_FLOW = "capital_flow"
    CHIP_DISTRIBUTION = "chip_distribution"
    ANOMALY_TRACKING = "anomaly_tracking"
    FINANCIAL_VALUATION = "financial_valuation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    DECISION_MODELS = "decision_models"
    MULTIDIMENSIONAL_RADAR = "multidimensional_radar"


@dataclass
class AnalysisResult:
    """分析结果数据结构"""

    analysis_type: AnalysisType
    stock_code: str
    timestamp: datetime
    scores: Dict[str, float]
    signals: List[Dict[str, Any]]
    recommendations: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    metadata: Dict[str, Any]
    raw_data: Optional[pd.DataFrame] = None


class BaseAnalyzer(ABC):
    """分析器基类"""

    def __init__(
        self,
        data_manager: MyStocksUnifiedManager,
        gpu_manager: Optional[GPUResourceManager] = None,
    ):
        self.data_manager = data_manager
        self.gpu_manager = gpu_manager
        self.alert_manager = AlertManager()

    @abstractmethod
    def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
        """执行分析的核心方法"""

    def _get_historical_data(self, stock_code: str, days: int = 365, data_type: str = "daily") -> pd.DataFrame:
        """获取历史数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        if data_type == "daily":
            return self.data_manager.load_data_by_classification(
                DataClassification.DAILY_KLINE,
                filters={"symbol": stock_code, "trade_date": f">={start_date.date()}"},
            )
        elif data_type == "minute":
            return self.data_manager.load_data_by_classification(
                DataClassification.MINUTE_KLINE,
                filters={"symbol": stock_code, "ts": f">={start_date}"},
            )
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

    def _calculate_score(self, metrics: Dict[str, float], weights: Dict[str, float]) -> float:
        """计算加权综合得分"""
        total_score = 0.0
        total_weight = 0.0

        for metric, weight in weights.items():
            if metric in metrics:
                total_score += metrics[metric] * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def _generate_recommendation(self, score: float, thresholds: Dict[str, float]) -> str:
        """生成投资建议"""
        if score >= thresholds.get("strong_buy", 0.8):
            return "强烈买入"
        elif score >= thresholds.get("buy", 0.6):
            return "买入"
        elif score >= thresholds.get("hold", 0.4):
            return "持有"
        elif score >= thresholds.get("sell", 0.2):
            return "卖出"
        else:
            return "强烈卖出"


class AdvancedAnalysisEngine:
    """高级分析引擎 - 统一管理所有分析功能"""

    # pylint: disable=abstract-class-instantiated
    def __init__(self, data_manager: MyStocksUnifiedManager):
        self.data_manager = data_manager
        self.gpu_manager = None  # GPU manager will be set if needed
        self.analyzers = {
            AnalysisType.FUNDAMENTAL: FundamentalAnalyzer(data_manager, self.gpu_manager),
            AnalysisType.TECHNICAL: TechnicalAnalyzer(data_manager, self.gpu_manager),
            AnalysisType.TRADING_SIGNALS: TradingSignalAnalyzer(data_manager, self.gpu_manager),
            AnalysisType.TIME_SERIES: TimeSeriesAnalyzer(data_manager, self.gpu_manager),
            AnalysisType.MARKET_PANORAMA: MarketPanoramaAnalyzer(data_manager, self.gpu_manager),
            AnalysisType.CAPITAL_FLOW: CapitalFlowAnalyzer(data_manager, self.gpu_manager),
            AnalysisType.CHIP_DISTRIBUTION: ChipDistributionAnalyzer(data_manager, self.gpu_manager),
            AnalysisType.ANOMALY_TRACKING: AnomalyTrackingAnalyzer(data_manager, self.gpu_manager),
            AnalysisType.FINANCIAL_VALUATION: FinancialValuationAnalyzer(data_manager, self.gpu_manager),
            AnalysisType.SENTIMENT_ANALYSIS: SentimentAnalyzer(data_manager, self.gpu_manager),
            AnalysisType.DECISION_MODELS: DecisionModelsAnalyzer(data_manager, self.gpu_manager),
            AnalysisType.MULTIDIMENSIONAL_RADAR: MultidimensionalRadarAnalyzer(data_manager, self.gpu_manager),
        }


def comprehensive_analysis(
    self, stock_code: str, analysis_types: Optional[List[AnalysisType]] = None, **kwargs
) -> Dict[str, AnalysisResult]:
    """
    执行综合分析

    Args:
        stock_code: 股票代码
        analysis_types: 要执行的分析类型列表，默认执行所有
        **kwargs: 各分析器的参数

    Returns:
        包含所有分析结果的字典
    """
    if analysis_types is None:
        analysis_types = list(self.analyzers.keys())

    results = {}

    if self.gpu_manager and len(analysis_types) > 3:
        gpu_results = self._gpu_parallel_analysis(stock_code, analysis_types, **kwargs)
        results.update(gpu_results)
    else:
        for analysis_type in analysis_types:
            analyzer = self.analyzers.get(analysis_type)
            if analyzer:
                try:
                    result = analyzer.analyze(stock_code, **kwargs)
                    results[analysis_type.value] = result
                except Exception as e:
                    print(f"Analysis {analysis_type.value} failed: {e}")
                    continue

    return results


def _gpu_parallel_analysis(
    self, stock_code: str, analysis_types: List[AnalysisType], **kwargs
) -> Dict[str, AnalysisResult]:
    """GPU并行分析"""

    import concurrent.futures

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_analysis = {
            executor.submit(self.analyzers[atype].analyze, stock_code, **kwargs): atype for atype in analysis_types
        }

        for future in concurrent.futures.as_completed(future_to_analysis):
            analysis_type = future_to_analysis[future]
            try:
                result = future.result()
                results[analysis_type.value] = result
            except Exception as e:
                print(f"GPU analysis {analysis_type.value} failed: {e}")

    return results


def get_market_overview(self) -> Dict[str, Any]:
    """获取市场全景分析"""
    panorama_analyzer = self.analyzers[AnalysisType.MARKET_PANORAMA]
    return panorama_analyzer.analyze_market_overview()


def get_realtime_alerts(self, stock_code: str) -> List[Dict[str, Any]]:
    """获取实时预警"""
    signals_analyzer = self.analyzers[AnalysisType.TRADING_SIGNALS]
    anomaly_analyzer = self.analyzers[AnalysisType.ANOMALY_TRACKING]

    signals_result = signals_analyzer.analyze(stock_code)
    anomaly_result = anomaly_analyzer.analyze(stock_code)

    alerts = []
    alerts.extend(signals_result.signals)
    alerts.extend(anomaly_result.signals)

    return sorted(alerts, key=lambda x: x.get("severity", 0), reverse=True)


from .anomaly_tracking_analyzer import AnomalyTrackingAnalyzer
from .capital_flow_analyzer import CapitalFlowAnalyzer
from .chip_distribution_analyzer import ChipDistributionAnalyzer
from .decision_models_analyzer import DecisionModelsAnalyzer
from .financial_valuation_analyzer import FinancialValuationAnalyzer
from .fundamental_analyzer import FundamentalAnalyzer
from .market_panorama_analyzer import MarketPanoramaAnalyzer
from .multidimensional_radar import MultidimensionalRadarAnalyzer
from .sentiment_analyzer import SentimentAnalyzer
from .technical_analyzer import TechnicalAnalyzer
from .timeseries_analyzer import TimeSeriesAnalyzer
from .trading_signals_analyzer import TradingSignalAnalyzer
