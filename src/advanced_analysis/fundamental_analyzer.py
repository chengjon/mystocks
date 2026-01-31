"""
Fundamental Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台基本面分析功能

This module provides comprehensive fundamental analysis capabilities including:
- Multi-dimensional financial analysis (profitability, solvency, operation, growth)
- Financial anomaly detection and red flag identification
- Industry comparison and benchmarking
- Valuation metrics and scoring
"""

import warnings
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType, BaseAnalyzer

try:
    pass

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    warnings.warn("GPU libraries not available. Fundamental analysis will run on CPU.")


@dataclass
class FinancialRatios:
    """财务比率数据结构"""

    # 盈利能力
    profitability: Dict[str, float] = None
    # 偿债能力
    solvency: Dict[str, float] = None
    # 运营能力
    operation: Dict[str, float] = None
    # 成长能力
    growth: Dict[str, float] = None
    # 现金流质量
    cashflow: Dict[str, float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FundamentalScore:
    """基本面评分结果"""

    overall_score: float
    dimension_scores: Dict[str, float]
    rating: str
    industry_percentile: float
    red_flags: List[str]
    strengths: List[str]
    weaknesses: List[str]


@dataclass
class ValuationMetrics:
    """估值指标"""

    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    dividend_yield: Optional[float] = None

    # 历史分位数
    pe_percentile: Optional[float] = None
    pb_percentile: Optional[float] = None
    pe_vs_industry: Optional[float] = None
    pb_vs_industry: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FundamentalAnalyzer(BaseAnalyzer):
    """
    基本面分析器

    提供全面的基本面分析功能，包括：
    - 多维度财务分析
    - 财务异常检测
    - 估值分析
    - 行业比较
    """


def __init__(self, data_manager, gpu_manager=None):
    super().__init__(data_manager, gpu_manager)

    self.dimension_weights = {
        "profitability": 0.30,
        "solvency": 0.20,
        "operation": 0.20,
        "growth": 0.20,
        "cashflow": 0.10,
    }
    self.industry_benchmarks = self._load_industry_benchmarks()


def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
    """
    执行基本面分析

    Args:
        stock_code: 股票代码
        **kwargs: 分析参数
            - periods: 分析周期数 (默认: 4个季度)
            - include_valuation: 是否包含估值分析 (默认: True)
            - include_comparison: 是否包含行业比较 (默认: True)

    Returns:
        AnalysisResult: 分析结果
    """
    periods = kwargs.get("periods", 4)
    include_valuation = kwargs.get("include_valuation", True)
    include_comparison = kwargs.get("include_comparison", True)

    try:
        # 获取财务数据
        financial_data = self._get_financial_data(stock_code, periods)

        # 计算财务比率
        ratios = self._calculate_financial_ratios(financial_data)

        # 计算基本面分数
        fundamental_score = self._calculate_fundamental_score(ratios, stock_code)

        scores = {
            "fundamental_score": fundamental_score.overall_score,
            "dimension_scores": fundamental_score.dimension_scores,
            "industry_percentile": fundamental_score.industry_percentile,
        }

        signals = []
        if fundamental_score.red_flags:
            signals.extend(
                [
                    {
                        "type": "fundamental_risk",
                        "severity": "high" if len(fundamental_score.red_flags) > 2 else "medium",
                        "message": f"发现{len(fundamental_score.red_flags)}个财务风险信号",
                        "details": fundamental_score.red_flags[:3],  # 最多显示3个
                    }
                ]
            )

        recommendations = {
            "rating": fundamental_score.rating,
            "investment_suggestion": self._generate_investment_suggestion(fundamental_score),
            "risk_assessment": (
                "high" if len(fundamental_score.red_flags) > 2 else "medium" if fundamental_score.red_flags else "low"
            ),
        }

        risk_assessment = {
            "red_flags": fundamental_score.red_flags,
            "strengths": fundamental_score.strengths,
            "weaknesses": fundamental_score.weaknesses,
            "overall_risk_level": recommendations["risk_assessment"],
        }

        metadata = {
            "analysis_periods": periods,
            "data_quality_score": self._assess_data_quality(financial_data),
            "last_updated": financial_data.index.max() if not financial_data.empty else None,
            "industry": self._get_stock_industry(stock_code),
        }

        return AnalysisResult(
            analysis_type=AnalysisType.FUNDAMENTAL,
            stock_code=stock_code,
            timestamp=datetime.now(),
            scores=scores,
            signals=signals,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            metadata=metadata,
            raw_data=financial_data if kwargs.get("include_raw_data", False) else None,
        )

    except Exception as e:
        return self._create_error_result(stock_code, str(e))


def _get_financial_data(self, stock_code: str, periods: int) -> pd.DataFrame:
    """
    获取财务数据

    从多个数据源获取财务数据，包括：
    - 资产负债表
    - 利润表
    - 现金流量表
    """
    try:
        from src.data_sources.factory import get_timeseries_source

        timeseries_source = get_timeseries_source(source_type="mock")
        # TODO: 实现从timeseries_source获取财务数据的逻辑
        return pd.DataFrame()

    except Exception as e:
        print(f"Error fetching financial data for {stock_code}: {e}")
        return pd.DataFrame()


def _calculate_financial_ratios(self, financial_data: pd.DataFrame) -> FinancialRatios:
    """计算财务比率"""
    if financial_data.empty:
        return FinancialRatios()

    profitability = self._calculate_profitability_ratios(financial_data)
    solvency = self._calculate_solvency_ratios(financial_data)
    operation = self._calculate_operation_ratios(financial_data)
    growth = self._calculate_growth_ratios(financial_data)
    cashflow = self._calculate_cashflow_ratios(financial_data)

    return FinancialRatios(
        profitability=profitability, solvency=solvency, operation=operation, growth=growth, cashflow=cashflow
    )


def _calculate_profitability_ratios(self, data: pd.DataFrame) -> Dict[str, float]:
    """计算盈利能力比率"""
    ratios = {}

    try:
        if "ebitda" in data.columns and "revenue" in data.columns:
            ratios["ebitda_margin"] = (data["ebitda"] / data["revenue"]).mean()

    except Exception as e:
        print(f"Error calculating profitability ratios: {e}")

    return ratios


def _calculate_solvency_ratios(self, data: pd.DataFrame) -> Dict[str, float]:
    """计算偿债能力比率"""
    ratios = {}

    try:
        if "ebit" in data.columns and "interest_expense" in data.columns:
            ratios["interest_coverage"] = (data["ebit"] / data["interest_expense"]).mean()

    except Exception as e:
        print(f"Error calculating solvency ratios: {e}")

    return ratios


def _calculate_operation_ratios(self, data: pd.DataFrame) -> Dict[str, float]:
    """计算运营能力比率"""
    ratios = {}

    try:
        if "revenue" in data.columns and "current_assets" in data.columns:
            ratios["current_asset_turnover"] = (data["revenue"] / data["current_assets"]).mean()

    except Exception as e:
        print(f"Error calculating operation ratios: {e}")

    return ratios


def _calculate_growth_ratios(self, data: pd.DataFrame) -> Dict[str, float]:
    """计算成长能力比率"""
    ratios = {}

    try:
        numeric_columns = data.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            if len(data) >= 2:
                growth_rate = (data[col].iloc[-1] - data[col].iloc[0]) / abs(data[col].iloc[0])
                ratios[f"{col}_growth"] = growth_rate

    except Exception as e:
        print(f"Error calculating growth ratios: {e}")

    return ratios


def _calculate_cashflow_ratios(self, data: pd.DataFrame) -> Dict[str, float]:
    """计算现金流质量比率"""
    ratios = {}

    try:
        if "operating_cashflow" in data.columns and "current_liabilities" in data.columns:
            ratios["cashflow_ratio"] = (data["operating_cashflow"] / data["current_liabilities"]).mean()

    except Exception as e:
        print(f"Error calculating cashflow ratios: {e}")

    return ratios


def _calculate_fundamental_score(self, ratios: FinancialRatios, stock_code: str) -> FundamentalScore:
    """计算基本面综合评分"""
    dimension_scores = {}

    # 计算各维度评分
    if ratios.profitability:
        dimension_scores["profitability"] = self._score_profitability(ratios.profitability)
    if ratios.solvency:
        dimension_scores["solvency"] = self._score_solvency(ratios.solvency)
    if ratios.operation:
        dimension_scores["operation"] = self._score_operation(ratios.operation)
    if ratios.growth:
        dimension_scores["growth"] = self._score_growth(ratios.growth)
    if ratios.cashflow:
        dimension_scores["cashflow"] = self._score_cashflow(ratios.cashflow)

    # 计算总分
    overall_score = self._calculate_overall_score(dimension_scores)

    # 确定评级
    rating = self._determine_rating(overall_score)

    # 计算行业百分位
    industry_percentile = self._calculate_industry_percentile(overall_score, stock_code)

    red_flags, strengths, weaknesses = self._identify_flags_and_strengths(ratios, dimension_scores)

    return FundamentalScore(
        overall_score=overall_score,
        dimension_scores=dimension_scores,
        rating=rating,
        industry_percentile=industry_percentile,
        red_flags=red_flags,
        strengths=strengths,
        weaknesses=weaknesses,
    )


def _score_profitability(self, ratios: Dict[str, float]) -> float:
    """盈利能力评分"""
    score = 0

    # ROE评分
    if "roe" in ratios:
        roe = ratios["roe"]
        if roe > 0.20:
            score += 25  # 优秀
        elif roe > 0.15:
            score += 20  # 良好
        elif roe > 0.10:
            score += 15  # 一般
        elif roe > 0.05:
            score += 10  # 较低
        elif roe > 0:
            score += 5  # 微利
        else:
            score += 0  # 亏损

    # 净利率评分
    if "net_margin" in ratios:
        margin = ratios["net_margin"]
        if margin > 0.15:
            score += 15
        elif margin > 0.10:
            score += 12
        elif margin > 0.05:
            score += 8
        elif margin > 0:
            score += 4
        else:
            score += 0

    if "gross_margin" in ratios:
        gross_margin = ratios["gross_margin"]
        if gross_margin > 0.40:
            score += 10
        elif gross_margin > 0.30:
            score += 8
        elif gross_margin > 0.20:
            score += 5
        elif gross_margin > 0:
            score += 2
        else:
            score += 0

    return min(100, score)


def _score_solvency(self, ratios: Dict[str, float]) -> float:
    """偿债能力评分"""
    score = 0

    # 资产负债率评分
    if "debt_ratio" in ratios:
        debt_ratio = ratios["debt_ratio"]
        if debt_ratio < 0.30:
            score += 30  # 优秀
        elif debt_ratio < 0.40:
            score += 25  # 良好
        elif debt_ratio < 0.50:
            score += 20  # 一般
        elif debt_ratio < 0.60:
            score += 15  # 较高
        else:
            score += 5  # 很高

    # 流动比率评分
    if "current_ratio" in ratios:
        current_ratio = ratios["current_ratio"]
        if current_ratio > 2.0:
            score += 15
        elif current_ratio > 1.5:
            score += 12
        elif current_ratio > 1.0:
            score += 8
        else:
            score += 3

    if "quick_ratio" in ratios:
        quick_ratio = ratios["quick_ratio"]
        if quick_ratio > 1.5:
            score += 10
        elif quick_ratio > 1.0:
            score += 8
        elif quick_ratio > 0.8:
            score += 5
        else:
            score += 2

    return min(100, score)


def _score_operation(self, ratios: Dict[str, float]) -> float:
    """运营能力评分"""
    score = 0

    if "asset_turnover" in ratios:
        turnover = ratios["asset_turnover"]
        if turnover > 1.5:
            score += 25
        elif turnover > 1.0:
            score += 20
        elif turnover > 0.8:
            score += 15
        elif turnover > 0.5:
            score += 10
        else:
            score += 5

    if "receivables_turnover" in ratios:
        rec_turnover = ratios["receivables_turnover"]
        if rec_turnover > 8:
            score += 20
        elif rec_turnover > 6:
            score += 15
        elif rec_turnover > 4:
            score += 10
        else:
            score += 5

    if "inventory_turnover" in ratios:
        inv_turnover = ratios["inventory_turnover"]
        if inv_turnover > 6:
            score += 15
        elif inv_turnover > 4:
            score += 12
        elif inv_turnover > 2:
            score += 8
        else:
            score += 4

    return min(100, score)


def _score_growth(self, ratios: Dict[str, float]) -> float:
    """成长能力评分"""
    score = 0

    revenue_growth_keys = [k for k in ratios.keys() if "revenue" in k and "growth" in k]
    if revenue_growth_keys:
        avg_revenue_growth = np.mean([ratios[k] for k in revenue_growth_keys])
        if avg_revenue_growth > 0.30:
            score += 25
        elif avg_revenue_growth > 0.20:
            score += 20
        elif avg_revenue_growth > 0.10:
            score += 15
        elif avg_revenue_growth > 0.05:
            score += 10
        elif avg_revenue_growth > 0:
            score += 5
        else:
            score += 0

    profit_growth_keys = [k for k in ratios.keys() if "profit" in k and "growth" in k]
    if profit_growth_keys:
        avg_profit_growth = np.mean([ratios[k] for k in profit_growth_keys])
        if avg_profit_growth > 0.30:
            score += 25
        elif avg_profit_growth > 0.20:
            score += 20
        elif avg_profit_growth > 0.10:
            score += 15
        elif avg_profit_growth > 0.05:
            score += 10
        elif avg_profit_growth > 0:
            score += 5
        else:
            score += 0

    return min(100, score)


def _score_cashflow(self, ratios: Dict[str, float]) -> float:
    """现金流质量评分"""
    score = 0

    if "cashflow_to_profit" in ratios:
        cf_to_profit = ratios["cashflow_to_profit"]
        if cf_to_profit > 1.2:
            score += 40  # 现金流显著好于利润
        elif cf_to_profit > 1.0:
            score += 30  # 现金流与利润匹配
        elif cf_to_profit > 0.8:
            score += 20  # 现金流略低于利润
        elif cf_to_profit > 0.5:
            score += 10  # 现金流明显低于利润
        else:
            score += 0  # 现金流质量较差

    # 自由现金流评分
    if "free_cashflow" in ratios:
        fcf = ratios["free_cashflow"]
        if fcf > 0:
            score += 30  # 正的自由现金流
        else:
            score += 0  # 负的自由现金流

    # 现金流比率评分
    if "cashflow_ratio" in ratios:
        cf_ratio = ratios["cashflow_ratio"]
        if cf_ratio > 0.5:
            score += 30
        elif cf_ratio > 0.3:
            score += 20
        elif cf_ratio > 0.1:
            score += 10
        else:
            score += 0

    return min(100, score)


def _determine_rating(self, score: float) -> str:
    """根据得分确定评级"""
    if score >= 85:
        return "A"  # 优秀
    elif score >= 75:
        return "B+"  # 良好+
    elif score >= 65:
        return "B"  # 良好
    elif score >= 55:
        return "C+"  # 一般+
    elif score >= 45:
        return "C"  # 一般
    elif score >= 35:
        return "D"  # 较差
    else:
        return "E"  # 很差


def _calculate_industry_percentile(self, score: float, stock_code: str) -> float:
    """计算行业百分位"""
    try:
        industry = self._get_stock_industry(stock_code)
        if industry and industry in self.industry_benchmarks:
            industry_scores = self.industry_benchmarks[industry]
            if industry_scores:
                return np.percentile(industry_scores, score)
    except Exception as e:
        print(f"Error calculating industry percentile: {e}")

        return 50.0


def _identify_flags_and_strengths(
    self, ratios: FinancialRatios, dimension_scores: Dict[str, float]
) -> Tuple[List[str], List[str], List[str]]:
    """识别红旗、优势和劣势"""
    red_flags = []
    strengths = []
    weaknesses = []

    if ratios.profitability:
        if ratios.profitability.get("roe", 0) < 0:
            red_flags.append("净资产收益率为负")
        elif ratios.profitability.get("roe", 0) > 0.20:
            strengths.append("净资产收益率优秀")

        if ratios.profitability.get("net_margin", 0) < 0:
            red_flags.append("净利润率为负")
        elif ratios.profitability.get("net_margin", 0) > 0.15:
            strengths.append("净利润率较高")

    if ratios.solvency:
        if ratios.solvency.get("debt_ratio", 1) > 0.70:
            red_flags.append("资产负债率过高")
        elif ratios.solvency.get("debt_ratio", 1) < 0.40:
            strengths.append("资产负债率较低")

        if ratios.solvency.get("current_ratio", 0) < 1.0:
            red_flags.append("流动比率小于1")
        elif ratios.solvency.get("current_ratio", 0) > 2.0:
            strengths.append("流动比率充足")

    if ratios.growth:
        revenue_growth = None
        for k, v in ratios.growth.items():
            if "revenue" in k and "growth" in k:
                revenue_growth = v
                break

        if revenue_growth is not None:
            if revenue_growth < -0.1:
                red_flags.append("营收增长率大幅下降")
            elif revenue_growth > 0.2:
                strengths.append("营收增长强劲")

    if ratios.cashflow:
        if ratios.cashflow.get("cashflow_to_profit", 0) < 0.5:
            red_flags.append("经营现金流远低于净利润")
        elif ratios.cashflow.get("cashflow_to_profit", 0) > 1.2:
            strengths.append("经营现金流显著高于净利润")

    for dim, score in dimension_scores.items():
        if score < 40:
            weaknesses.append(f"{dim}能力较弱")
        elif score > 80:
            strengths.append(f"{dim}能力优秀")

    return red_flags, strengths, weaknesses


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
        print(f"Error in valuation analysis: {e}")
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
        print(f"Error in industry comparison: {e}")
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
        print(f"Error getting current price for {stock_code}: {e}")

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
