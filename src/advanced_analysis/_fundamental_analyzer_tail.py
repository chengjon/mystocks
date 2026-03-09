"""Tail helpers for `fundamental_analyzer.py`."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType
from src.advanced_analysis.fundamental_models import FinancialRatios, FundamentalScore, ValuationMetrics

logger = logging.getLogger(__name__)


class FundamentalAnalyzerTailMixin:
    def _analyze_valuation(self, stock_code: str, financial_data: pd.DataFrame) -> ValuationMetrics:
        """估值分析"""
        try:
            # 获取当前股价
            current_price = self._get_current_price(stock_code)

            pe_ratio = None
            pb_ratio = None
            pe_percentile = None
            pb_percentile = None

            if not financial_data.empty and "eps" in financial_data.columns:
                latest_eps = financial_data["eps"].iloc[-1]
                if latest_eps > 0:
                    pe_ratio = current_price / latest_eps

            if not financial_data.empty and "bvps" in financial_data.columns:
                latest_bvps = financial_data["bvps"].iloc[-1]
                if latest_bvps > 0:
                    pb_ratio = current_price / latest_bvps

            pe_vs_industry = self._compare_with_industry_valuation(stock_code, "pe", pe_ratio)
            pb_vs_industry = self._compare_with_industry_valuation(stock_code, "pb", pb_ratio)

            # 计算行业百分位
            if pe_ratio is not None:
                pe_percentile = self._calculate_valuation_percentile(stock_code, "pe", pe_ratio)
            if pb_ratio is not None:
                pb_percentile = self._calculate_valuation_percentile(stock_code, "pb", pb_ratio)

            return ValuationMetrics(
                pe_ratio=pe_ratio,
                pb_ratio=pb_ratio,
                pe_percentile=pe_percentile,
                pb_percentile=pb_percentile,
                pe_vs_industry=pe_vs_industry,
                pb_vs_industry=pb_vs_industry,
            )

        except Exception as e:
            logger.error("Error in valuation analysis for %s: %s", stock_code, e)
            return ValuationMetrics()

    def _compare_with_industry(self, stock_code: str, ratios: FinancialRatios) -> Dict[str, Any]:
        """与行业比较"""
        try:
            industry = self._get_stock_industry(stock_code)
            if not industry or industry not in self.industry_benchmarks:
                return {}

            return {
                "industry": industry,
                "comparison_available": False,  # 暂时不支持
                "note": "Industry comparison feature under development",
            }

        except Exception as e:
            logger.error("Error in industry comparison for %s: %s", stock_code, e)
            return {}

    def _load_industry_benchmarks(self) -> Dict[str, List[float]]:
        """加载行业基准数据"""

        return {}

    def _get_stock_industry(self, stock_code: str) -> Optional[str]:
        """获取股票所属行业"""
        try:
            industry_info = self.relational_source.get_stock_industry(stock_code)
            return industry_info
        except Exception:
            return None

    def _get_current_price(self, stock_code: str) -> Optional[float]:
        """获取当前股价"""
        try:
            from src.data_sources.factory import get_timeseries_source

            timeseries_source = get_timeseries_source(source_type="mock")
            realtime_data = timeseries_source.get_realtime_quotes([stock_code])
            if realtime_data and stock_code in realtime_data:
                return realtime_data[stock_code].get("price")
        except Exception as e:
            logger.error("Error getting current price for %s: %s", stock_code, e)

        return None

    def _calculate_historical_percentile(self, metric: str, value: Optional[float]) -> Optional[float]:
        """计算历史百分位"""
        if value is None:
            return None

        try:
            return 50.0
        except Exception:
            return None

    def _compare_with_industry_valuation(self, stock_code: str, metric: str, value: Optional[float]) -> Optional[float]:
        """与行业估值比较"""
        if value is None:
            return None

        try:
            return 0.0  # 行业均值差值
        except Exception:
            return None

    def _assess_data_quality(self, data: pd.DataFrame) -> float:
        """评估数据质量"""
        if data.empty:
            return 0.0

        quality_score = 100.0

        # 检查数据合理性
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            # 检查是否有异常值
            if data[col].std() > 0:
                z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
                outlier_ratio = (z_scores > 3).sum() / len(data)
                quality_score -= outlier_ratio * 20

        return max(0.0, min(100.0, quality_score))

    def _generate_investment_suggestion(self, score: FundamentalScore) -> str:
        """生成投资建议"""
        if score.rating in ["A", "B+"]:
            if len(score.red_flags) == 0:
                return "强烈推荐买入"
            else:
                return "谨慎推荐买入"
        elif score.rating in ["B", "C+"]:
            return "观望"
        elif score.rating == "C":
            return "谨慎卖出"
        else:
            return "建议卖出"

    def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
        """创建错误结果"""
        return AnalysisResult(
            analysis_type=AnalysisType.FUNDAMENTAL,
            stock_code=stock_code,
            timestamp=datetime.now(),
            scores={"error": True},
            signals=[{"type": "analysis_error", "severity": "high", "message": f"基本面分析失败: {error_msg}"}],
            recommendations={"error": error_msg},
            risk_assessment={"error": True},
            metadata={"error": True, "error_message": error_msg},
        )
