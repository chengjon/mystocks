"""Tail helpers for `market_panorama_analyzer.py`."""

from typing import Dict, List, Tuple

import numpy as np


class MarketPanoramaAnalyzerTailMixin:
    def _get_valuation_distribution(self, index_code: str) -> Tuple[Dict[str, float], Dict[str, float]]:
        """获取模拟估值分布数据"""
        np.random.seed(int(index_code) if index_code.isdigit() else 42)

        pe_distribution = {
            "p10": np.random.uniform(10, 15),
            "p25": np.random.uniform(15, 20),
            "p50": np.random.uniform(20, 25),
            "p75": np.random.uniform(25, 35),
            "p90": np.random.uniform(35, 50),
        }

        pb_distribution = {
            "p10": np.random.uniform(0.8, 1.2),
            "p25": np.random.uniform(1.2, 1.5),
            "p50": np.random.uniform(1.5, 2.0),
            "p75": np.random.uniform(2.0, 2.5),
            "p90": np.random.uniform(2.5, 3.5),
        }

        return pe_distribution, pb_distribution

    def _calculate_market_valuation_percentile(self, pe_dist: Dict, pb_dist: Dict) -> float:
        """计算市场估值分位数"""
        pe_median = pe_dist.get("p50", 25)
        pb_median = pb_dist.get("p50", 2.0)

        pe_percentile = min(pe_median / 30, 1.0)
        pb_percentile = min(pb_median / 3.0, 1.0)

        return (pe_percentile + pb_percentile) / 2

    def _analyze_sector_valuations(self) -> Dict[str, float]:
        """分析板块估值"""
        sector_valuations = {}
        for sector_name in self.sectors.keys():
            valuation = np.random.uniform(0.3, 0.9)
            sector_valuations[sector_name] = valuation

        return sector_valuations

    def _identify_valuation_extremes(self) -> Dict[str, List[str]]:
        """识别估值极值"""
        return {
            "overvalued": ["股票A", "股票B"],
            "undervalued": ["股票C", "股票D"],
        }

    def _calculate_sentiment_index(self) -> float:
        """计算情绪指数"""
        return np.random.uniform(0.2, 0.8)

    def _calculate_fear_greed_index(self) -> float:
        """计算恐惧贪婪指数"""
        return np.random.uniform(0.1, 0.9)

    def _get_put_call_ratio(self) -> float:
        """获取认沽认购比"""
        return np.random.uniform(0.8, 1.3)

    def _get_vix_level(self) -> float:
        """获取波动率指数水平"""
        return np.random.uniform(10, 40)

    def _analyze_sentiment_trend(self, sentiment_index: float, fear_greed_index: float) -> str:
        """分析情绪趋势"""
        if sentiment_index > 0.6 and fear_greed_index > 0.6:
            return "乐观情绪上升"
        if sentiment_index < 0.4 and fear_greed_index < 0.4:
            return "悲观情绪加深"
        return "情绪相对稳定"
