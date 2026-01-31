"""
Financial Valuation Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台财务估值分析功能

This module provides comprehensive financial valuation analysis including:
- DCF (Discounted Cash Flow) valuation models
- Multi-model valuation comparison (PE, PB, EV/EBITDA)
- DuPont analysis for financial health decomposition
- Modern financial engineering pricing methods
- Industry-relative valuation benchmarking
"""

import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType, BaseAnalyzer

# GPU acceleration support
try:
    pass

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    warnings.warn("GPU libraries not available. Financial valuation analysis will run on CPU.")


@dataclass
class DCFValuation:
    """DCF估值结果"""

    intrinsic_value: float  # 内在价值
    current_price: float  # 当前价格
    upside_potential: float  # 上涨潜力 (%)
    wacc: float  # 加权平均资本成本
    terminal_growth: float  # 永续增长率
    projected_cashflows: List[float]  # 预测现金流
    confidence_level: float  # 估值置信度 (0-1)


@dataclass
class RelativeValuation:
    """相对估值结果"""

    pe_ratio: float  # PE比率
    pb_ratio: float  # PB比率
    ps_ratio: float  # PS比率
    ev_ebitda: float  # EV/EBITDA比率
    industry_pe_percentile: float  # 行业PE百分位
    industry_pb_percentile: float  # 行业PB百分位
    valuation_fairness: str  # 估值公平性 (undervalued/fair/overvalued)
    comparable_companies: List[str]  # 可比公司列表


@dataclass
class DuPontAnalysis:
    """杜邦分析结果"""

    roe: float  # 净资产收益率
    profit_margin: float  # 净利润率
    asset_turnover: float  # 总资产周转率
    equity_multiplier: float  # 权益乘数
    roa: float  # 总资产收益率
    interest_burden: float  # 利息负担
    tax_burden: float  # 税负
    operating_margin: float  # 经营利润率
    decomposition_factors: Dict[str, float]  # 分解因子


@dataclass
class ModernValuation:
    """现代估值方法"""

    black_scholes_value: Optional[float] = None  # 布莱克-舒尔斯模型
    binomial_value: Optional[float] = None  # 二叉树模型
    monte_carlo_value: Optional[float] = None  # 蒙特卡洛模拟
    real_options_value: Optional[float] = None  # 实物期权
    risk_neutral_probability: float = 0.5  # 风险中性概率
    implied_volatility: float = 0.0  # 隐含波动率


@dataclass
class ValuationConsensus:
    """估值共识"""

    dcf_valuation: float  # DCF估值
    relative_valuation: float  # 相对估值
    market_price: float  # 市场价格
    consensus_value: float  # 共识价值
    valuation_gap: float  # 估值差距 (%)
    confidence_score: float  # 置信度得分 (0-1)
    recommendation: str  # 投资建议


class FinancialValuationAnalyzer(BaseAnalyzer):
    """
    财务估值分析器

    提供全面的财务估值分析，包括：
    - DCF估值模型和现金流折现
    - 多模型相对估值比较
    - 杜邦分析财务健康分解
    - 现代金融工程定价方法
    - 行业相对估值基准
    """


def __init__(self, data_manager, gpu_manager=None):
    super().__init__(data_manager, gpu_manager)

    # DCF参数
    self.dcf_params = {
        "default_wacc": 0.08,  # 默认WACC
        "terminal_growth": 0.025,  # 永续增长率
        "projection_years": 5,  # 预测年数
        "risk_premium": 0.04,  # 风险溢价
    }

    # 相对估值参数
    self.relative_params = {
        "industry_pe_avg": 20.0,  # 行业平均PE
        "industry_pb_avg": 2.0,  # 行业平均PB
        "industry_ps_avg": 1.5,  # 行业平均PS
        "growth_adjustment": 0.02,  # 增长调整因子
    }

    # 杜邦分析参数
    self.dupont_params = {
        "leverage_threshold": 2.0,  # 杠杆阈值
        "margin_threshold": 0.05,  # 利润率阈值
        "turnover_threshold": 1.0,  # 周转率阈值
    }

    # 现代估值参数
    self.modern_params = {
        "time_to_maturity": 1.0,  # 到期时间
        "risk_free_rate": 0.03,  # 无风险利率
        "dividend_yield": 0.02,  # 股息收益率
        "steps": 100,  # 二叉树步数
        "simulations": 10000,  # 蒙特卡洛模拟次数
    }


def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
    """
    执行财务估值分析

    Args:
        stock_code: 股票代码
        **kwargs: 分析参数
            - include_dcf: 是否包含DCF估值 (默认: True)
            - include_relative: 是否包含相对估值 (默认: True)
            - include_dupont: 是否包含杜邦分析 (默认: True)
            - include_modern: 是否包含现代估值方法 (默认: False)
            - projection_years: DCF预测年数 (默认: 5)

    Returns:
        AnalysisResult: 分析结果
    """
    include_dcf = kwargs.get("include_dcf", True)
    include_relative = kwargs.get("include_relative", True)
    include_dupont = kwargs.get("include_dupont", True)
    include_modern = kwargs.get("include_modern", False)
    projection_years = kwargs.get("projection_years", self.dcf_params["projection_years"])

    try:
        # 获取财务数据
        financial_data = self._get_financial_data(stock_code, periods=8)  # 8个季度数据
        current_price = self._get_current_price(stock_code)

        if financial_data.empty or current_price is None:
            return self._create_error_result(stock_code, "Insufficient financial data for valuation analysis")

        # DCF估值
        dcf_valuation = None
        if include_dcf:
            dcf_valuation = self._calculate_dcf_valuation(financial_data, current_price, projection_years)

        # 相对估值
        relative_valuation = None
        if include_relative:
            relative_valuation = self._calculate_relative_valuation(financial_data, current_price, stock_code)

        # 杜邦分析
        dupont_analysis = None
        if include_dupont:
            dupont_analysis = self._perform_dupont_analysis(financial_data)

        # 现代估值方法
        modern_valuation = None
        if include_modern:
            modern_valuation = self._calculate_modern_valuation(financial_data, current_price)

        # 估值共识
        valuation_consensus = self._calculate_valuation_consensus(dcf_valuation, relative_valuation, current_price)

        # 计算综合得分
        scores = self._calculate_valuation_scores(
            dcf_valuation, relative_valuation, dupont_analysis, valuation_consensus
        )

        # 生成信号
        signals = self._generate_valuation_signals(dcf_valuation, relative_valuation, valuation_consensus)

        # 投资建议
        recommendations = self._generate_valuation_recommendations(valuation_consensus, dupont_analysis)

        # 风险评估
        risk_assessment = self._assess_valuation_risk(dcf_valuation, relative_valuation, valuation_consensus)

        # 元数据
        metadata = {
            "stock_code": stock_code,
            "current_price": current_price,
            "analysis_timestamp": datetime.now(),
            "dcf_included": include_dcf,
            "relative_included": include_relative,
            "dupont_included": include_dupont,
            "modern_included": include_modern,
            "projection_years": projection_years,
            "data_periods": len(financial_data) if not financial_data.empty else 0,
            "valuation_consensus_value": valuation_consensus.consensus_value if valuation_consensus else None,
            "valuation_gap_pct": valuation_consensus.valuation_gap if valuation_consensus else None,
        }

        return AnalysisResult(
            analysis_type=AnalysisType.FINANCIAL_VALUATION,
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
    """获取财务数据"""
    try:
        from src.data_sources.factory import get_relational_source

        relational_source = get_relational_source(source_type="mock")

        # 获取财务数据
        financial_data = relational_source.get_financial_data(stock_code=stock_code, periods=periods)

        if financial_data.empty:
            # 生成模拟财务数据
            financial_data = self._generate_mock_financial_data(stock_code, periods)

        return financial_data

    except Exception as e:
        print(f"Error getting financial data for {stock_code}: {e}")
        return self._generate_mock_financial_data(stock_code, periods)


def _generate_mock_financial_data(self, stock_code: str, periods: int) -> pd.DataFrame:
    """生成模拟财务数据"""
    np.random.seed(hash(stock_code) % 2**32)

    data = []
    base_revenue = np.random.uniform(10000000, 100000000)  # 基础营收
    base_net_profit = base_revenue * np.random.uniform(0.05, 0.15)  # 净利润率
    base_assets = base_revenue * np.random.uniform(2, 5)  # 资产规模
    base_equity = base_assets * np.random.uniform(0.3, 0.6)  # 净资产

    for i in range(periods):
        # 添加趋势和波动
        trend_factor = 1 + 0.02 * i  # 增长趋势
        random_factor = np.random.normal(1, 0.1)  # 随机波动

        revenue = base_revenue * trend_factor * random_factor
        net_profit = base_net_profit * trend_factor * random_factor
        total_assets = base_assets * trend_factor * random_factor
        equity = base_equity * trend_factor * random_factor

        # 计算其他财务指标
        eps = net_profit / 100000  # 每股收益（简化）
        bvps = equity / 100000  # 每股净资产（简化）
        ebitda = net_profit * np.random.uniform(1.2, 1.8)  # EBITDA
        operating_cashflow = net_profit * np.random.uniform(1.1, 1.5)  # 经营现金流

        data.append(
            {
                "period": f"Q{i % 4 + 1} {2023 + i // 4}",
                "revenue": revenue,
                "net_profit": net_profit,
                "total_assets": total_assets,
                "equity": equity,
                "eps": eps,
                "bvps": bvps,
                "ebitda": ebitda,
                "operating_cashflow": operating_cashflow,
                "capex": operating_cashflow * np.random.uniform(0.1, 0.3),  # 资本支出
                "interest_expense": net_profit * np.random.uniform(0.1, 0.3),  # 利息支出
                "tax_expense": net_profit * np.random.uniform(0.2, 0.3),  # 税费
                "depreciation": ebitda * np.random.uniform(0.1, 0.2),  # 折旧
            }
        )

    return pd.DataFrame(data)


def _get_current_price(self, stock_code: str) -> Optional[float]:
    """获取当前股价"""
    try:
        from src.data_sources.factory import get_timeseries_source

        timeseries_source = get_timeseries_source(source_type="mock")

        realtime_data = timeseries_source.get_realtime_quotes([stock_code])
        if realtime_data and stock_code in realtime_data:
            return realtime_data[stock_code].get("price")

        # 如果没有实时数据，从历史数据获取最新价格
        historical_data = self._get_historical_data(stock_code, days=1, data_type="1d")
        if not historical_data.empty:
            return historical_data["close"].iloc[-1]

    except Exception as e:
        print(f"Error getting current price for {stock_code}: {e}")

    return None


def _calculate_dcf_valuation(
    self, financial_data: pd.DataFrame, current_price: float, projection_years: int
) -> DCFValuation:
    """计算DCF估值"""
    try:
        # 获取最新财务数据
        latest_data = financial_data.iloc[-1] if not financial_data.empty else {}

        # 估算自由现金流
        operating_cashflow = latest_data.get("operating_cashflow", 0)
        capex = latest_data.get("capex", 0)
        free_cashflow = operating_cashflow - capex

        if free_cashflow <= 0:
            # 如果自由现金流为负，使用净利润估算
            net_profit = latest_data.get("net_profit", 0)
            free_cashflow = net_profit * 0.8  # 假设80%的净利润转化为现金流

        # 计算增长率（基于历史数据）
        revenue_growth = self._calculate_historical_growth_rate(financial_data, "revenue")
        fcf_growth = min(revenue_growth, 0.15)  # 限制增长率上限为15%

        # 预测现金流
        projected_cashflows = []
        current_fcf = free_cashflow

        for year in range(1, projection_years + 1):
            # 假设现金流增长逐渐放缓
            growth_rate = fcf_growth * (1 - year / (projection_years + 1))
            current_fcf *= 1 + growth_rate
            projected_cashflows.append(current_fcf)

        # 计算WACC
        wacc = self._calculate_wacc(financial_data)

        # 计算终端价值
        terminal_growth = self.dcf_params["terminal_growth"]
        terminal_value = projected_cashflows[-1] * (1 + terminal_growth) / (wacc - terminal_growth)

        # 计算现值
        intrinsic_value = terminal_value
        for i in range(len(projected_cashflows) - 1, -1, -1):
            intrinsic_value = projected_cashflows[i] + intrinsic_value / (1 + wacc)
            projected_cashflows[i] = intrinsic_value  # 更新为现值

        # 计算上涨潜力
        upside_potential = (intrinsic_value - current_price) / current_price * 100

        # 估算置信度（基于数据质量和预测稳定性）
        confidence_level = self._assess_dcf_confidence(financial_data, projected_cashflows)

        return DCFValuation(
            intrinsic_value=intrinsic_value,
            current_price=current_price,
            upside_potential=upside_potential,
            wacc=wacc,
            terminal_growth=terminal_growth,
            projected_cashflows=projected_cashflows,
            confidence_level=confidence_level,
        )

    except Exception as e:
        print(f"Error calculating DCF valuation: {e}")
        return DCFValuation(
            intrinsic_value=current_price * 0.8,  # 保守估值
            current_price=current_price,
            upside_potential=-20.0,
            wacc=self.dcf_params["default_wacc"],
            terminal_growth=self.dcf_params["terminal_growth"],
            projected_cashflows=[current_price * 0.8] * projection_years,
            confidence_level=0.3,
        )


def _calculate_historical_growth_rate(self, data: pd.DataFrame, column: str) -> float:
    """计算历史增长率"""
    if data.empty or column not in data.columns or len(data) < 2:
        return 0.05  # 默认5%增长率

    try:
        values = data[column].dropna()
        if len(values) < 2:
            return 0.05

        # 计算复合增长率
        start_value = values.iloc[0]
        end_value = values.iloc[-1]
        periods = len(values) - 1

        if start_value > 0:
            cagr = (end_value / start_value) ** (1 / periods) - 1
            return max(min(cagr, 0.25), -0.1)  # 限制在-10%到25%之间
        else:
            return 0.05

    except Exception:
        return 0.05


def _calculate_wacc(self, financial_data: pd.DataFrame) -> float:
    """计算WACC"""
    # 简化的WACC计算
    risk_free_rate = 0.03  # 无风险利率
    market_risk_premium = 0.06  # 市场风险溢价
    beta = 1.2  # 假设beta值

    # 估算股权成本
    cost_of_equity = risk_free_rate + beta * market_risk_premium

    # 估算债务成本
    interest_expense = financial_data["interest_expense"].mean() if "interest_expense" in financial_data.columns else 0
    total_debt = financial_data["total_assets"].mean() * 0.4 if "total_assets" in financial_data.columns else 1000000
    cost_of_debt = interest_expense / total_debt if total_debt > 0 else 0.04

    # 资本结构
    total_assets = financial_data["total_assets"].mean() if "total_assets" in financial_data.columns else 2000000
    equity = financial_data["equity"].mean() if "equity" in financial_data.columns else total_assets * 0.5
    debt_ratio = (total_assets - equity) / total_assets if total_assets > 0 else 0.4

    # WACC计算
    tax_rate = 0.25  # 假设税率
    wacc = (equity / total_assets) * cost_of_equity + (debt_ratio) * cost_of_debt * (1 - tax_rate)

    return max(min(wacc, 0.15), 0.06)  # 限制在6%-15%之间


def _assess_dcf_confidence(self, financial_data: pd.DataFrame, projected_cashflows: List[float]) -> float:
    """评估DCF置信度"""
    confidence = 1.0

    # 数据质量因素
    if financial_data.empty:
        confidence *= 0.5
    elif len(financial_data) < 4:
        confidence *= 0.8

    # 现金流稳定性因素
    if len(projected_cashflows) > 1:
        cashflow_volatility = np.std(projected_cashflows) / np.mean(projected_cashflows)
        confidence *= max(0.5, 1 - cashflow_volatility)

    # 财务健康因素
    if not financial_data.empty:
        latest_profit = financial_data["net_profit"].iloc[-1] if "net_profit" in financial_data.columns else 0
        if latest_profit <= 0:
            confidence *= 0.7

    return max(0.2, confidence)


def _calculate_relative_valuation(
    self, financial_data: pd.DataFrame, current_price: float, stock_code: str
) -> RelativeValuation:
    """计算相对估值"""
    try:
        # 获取最新财务数据
        latest_data = financial_data.iloc[-1] if not financial_data.empty else {}

        # 计算PE比率
        eps = latest_data.get("eps", 1.0)
        pe_ratio = current_price / eps if eps > 0 else float("inf")

        # 计算PB比率
        bvps = latest_data.get("bvps", 1.0)
        pb_ratio = current_price / bvps if bvps > 0 else float("inf")

        # 计算PS比率（简化）
        revenue = latest_data.get("revenue", 1000000)
        shares_outstanding = 100000  # 假设流通股本
        ps_ratio = current_price / (revenue / shares_outstanding) if revenue > 0 else float("inf")

        # 计算EV/EBITDA
        ebitda = latest_data.get("ebitda", 100000)
        total_debt = latest_data.get("total_assets", 2000000) * 0.4  # 估算债务
        cash = total_debt * 0.1  # 估算现金
        enterprise_value = current_price * 100000 + total_debt - cash  # 简化计算
        ev_ebitda = enterprise_value / ebitda if ebitda > 0 else float("inf")

        # 计算行业百分位
        industry_pe_percentile = self._calculate_industry_percentile(pe_ratio, "pe", stock_code)
        industry_pb_percentile = self._calculate_industry_percentile(pb_ratio, "pb", stock_code)

        # 判断估值公平性
        pe_fair = 0.4 <= industry_pe_percentile <= 0.6
        pb_fair = 0.4 <= industry_pb_percentile <= 0.6

        if pe_fair and pb_fair:
            valuation_fairness = "fair"
        elif industry_pe_percentile > 0.7 or industry_pb_percentile > 0.7:
            valuation_fairness = "overvalued"
        else:
            valuation_fairness = "undervalued"

        # 可比公司（简化）
        comparable_companies = [f"COMP_{i}" for i in range(1, 6)]

        return RelativeValuation(
            pe_ratio=pe_ratio if pe_ratio != float("inf") else 50.0,
            pb_ratio=pb_ratio if pb_ratio != float("inf") else 3.0,
            ps_ratio=ps_ratio if ps_ratio != float("inf") else 2.0,
            ev_ebitda=ev_ebitda if ev_ebitda != float("inf") else 15.0,
            industry_pe_percentile=industry_pe_percentile,
            industry_pb_percentile=industry_pb_percentile,
            valuation_fairness=valuation_fairness,
            comparable_companies=comparable_companies,
        )

    except Exception as e:
        print(f"Error calculating relative valuation: {e}")
        return RelativeValuation(
            pe_ratio=25.0,
            pb_ratio=2.5,
            ps_ratio=1.8,
            ev_ebitda=12.0,
            industry_pe_percentile=0.5,
            industry_pb_percentile=0.5,
            valuation_fairness="fair",
            comparable_companies=[],
        )


def _calculate_industry_percentile(self, value: float, metric: str, stock_code: str) -> float:
    """计算行业百分位"""
    # 简化的百分位计算
    if metric == "pe":
        industry_avg = self.relative_params["industry_pe_avg"]
        industry_std = industry_avg * 0.3  # 假设30%的标准差
    elif metric == "pb":
        industry_avg = self.relative_params["industry_pb_avg"]
        industry_std = industry_avg * 0.4  # 假设40%的标准差
    else:
        return 0.5

    if industry_std > 0:
        z_score = (value - industry_avg) / industry_std
        percentile = 1 / (1 + np.exp(-z_score))  # Sigmoid函数转换为百分位
        return max(0.01, min(0.99, percentile))
    else:
        return 0.5


def _perform_dupont_analysis(self, financial_data: pd.DataFrame) -> DuPontAnalysis:
    """执行杜邦分析"""
    try:
        # 获取平均财务数据
        avg_data = financial_data.mean()

        # 基本杜邦分析
        net_profit = avg_data.get("net_profit", 0)
        revenue = avg_data.get("revenue", 1)
        total_assets = avg_data.get("total_assets", 1)
        equity = avg_data.get("equity", 1)

        # 利润率
        profit_margin = net_profit / revenue if revenue > 0 else 0

        # 资产周转率
        asset_turnover = revenue / total_assets if total_assets > 0 else 0

        # 权益乘数
        equity_multiplier = total_assets / equity if equity > 0 else 1

        # ROE分解
        roe = profit_margin * asset_turnover * equity_multiplier

        # ROA
        roa = profit_margin * asset_turnover

        # 扩展杜邦分析
        ebitda = avg_data.get("ebitda", net_profit * 1.5)
        interest_expense = avg_data.get("interest_expense", 0)
        tax_expense = avg_data.get("tax_expense", 0)

        # 利息负担
        ebit = ebitda - avg_data.get("depreciation", ebitda * 0.1)
        interest_burden = ebit / (ebit + interest_expense) if (ebit + interest_expense) > 0 else 1

        # 税负
        ebt = ebit - interest_expense
        tax_burden = ebt / (ebt + tax_expense) if (ebt + tax_expense) > 0 else 1

        # 经营利润率
        operating_margin = ebit / revenue if revenue > 0 else 0

        decomposition_factors = {
            "profit_margin": profit_margin,
            "asset_turnover": asset_turnover,
            "equity_multiplier": equity_multiplier,
            "interest_burden": interest_burden,
            "tax_burden": tax_burden,
            "operating_margin": operating_margin,
        }

        return DuPontAnalysis(
            roe=roe,
            profit_margin=profit_margin,
            asset_turnover=asset_turnover,
            equity_multiplier=equity_multiplier,
            roa=roa,
            interest_burden=interest_burden,
            tax_burden=tax_burden,
            operating_margin=operating_margin,
            decomposition_factors=decomposition_factors,
        )

    except Exception as e:
        print(f"Error performing DuPont analysis: {e}")
        return DuPontAnalysis(
            roe=0.08,  # 8%
            profit_margin=0.05,
            asset_turnover=1.2,
            equity_multiplier=1.3,
            roa=0.06,
            interest_burden=0.9,
            tax_burden=0.75,
            operating_margin=0.08,
            decomposition_factors={},
        )


def _calculate_modern_valuation(self, financial_data: pd.DataFrame, current_price: float) -> ModernValuation:
    """计算现代估值方法"""
    try:
        # 简化的期权定价模型
        volatility = self._calculate_historical_volatility(financial_data)
        time_to_maturity = self.modern_params["time_to_maturity"]
        risk_free_rate = self.modern_params["risk_free_rate"]
        dividend_yield = self.modern_params["dividend_yield"]

        # 布莱克-舒尔斯模型（简化）
        d1 = (
            np.log(current_price / current_price)
            + (risk_free_rate - dividend_yield + volatility**2 / 2) * time_to_maturity
        ) / (volatility * np.sqrt(time_to_maturity))
        d2 = d1 - volatility * np.sqrt(time_to_maturity)

        # 假设这是看涨期权价值
        bs_value = current_price * np.exp(-dividend_yield * time_to_maturity) * 0.5  # 简化

        # 风险中性概率
        risk_neutral_prob = (np.exp(risk_free_rate * time_to_maturity) - np.exp(-dividend_yield * time_to_maturity)) / (
            1 - np.exp(-dividend_yield * time_to_maturity)
        )

        return ModernValuation(
            black_scholes_value=bs_value, risk_neutral_probability=risk_neutral_prob, implied_volatility=volatility
        )

    except Exception as e:
        print(f"Error calculating modern valuation: {e}")
        return ModernValuation()


def _calculate_historical_volatility(self, data: pd.DataFrame) -> float:
    """计算历史波动率"""
    try:
        if "net_profit" in data.columns and len(data) > 1:
            returns = data["net_profit"].pct_change().dropna()
            volatility = returns.std() * np.sqrt(4)  # 季度数据年化
            return min(volatility, 0.5)  # 限制最大波动率
        else:
            return 0.2  # 默认波动率
    except Exception:
        return 0.2


def _calculate_valuation_consensus(
    self, dcf: Optional[DCFValuation], relative: Optional[RelativeValuation], current_price: float
) -> ValuationConsensus:
    """计算估值共识"""
    try:
        valuations = []

        # DCF估值
        if dcf:
            valuations.append(("dcf", dcf.intrinsic_value, dcf.confidence_level))

        # 相对估值（使用行业百分位的倒数作为估值）
        if relative:
            # 估值越低（百分位越小），价值越高
            relative_value = current_price * (1 - (relative.industry_pe_percentile - 0.5) * 0.4)
            valuations.append(("relative", relative_value, 0.7))

        if not valuations:
            return ValuationConsensus(
                dcf_valuation=current_price,
                relative_valuation=current_price,
                market_price=current_price,
                consensus_value=current_price,
                valuation_gap=0.0,
                confidence_score=0.5,
                recommendation="hold",
            )

        # 加权平均估值
        total_weight = sum(weight for _, _, weight in valuations)
        consensus_value = (
            sum(value * weight for _, value, weight in valuations) / total_weight if total_weight > 0 else current_price
        )

        # 估值差距
        valuation_gap = (consensus_value - current_price) / current_price * 100

        # 置信度得分
        confidence_score = sum(weight for _, _, weight in valuations) / len(valuations)

        # 投资建议
        if valuation_gap > 20:
            recommendation = "strong_buy"
        elif valuation_gap > 10:
            recommendation = "buy"
        elif valuation_gap > -10:
            recommendation = "hold"
        elif valuation_gap > -20:
            recommendation = "sell"
        else:
            recommendation = "strong_sell"

        return ValuationConsensus(
            dcf_valuation=dcf.intrinsic_value if dcf else current_price,
            relative_valuation=relative_value if relative else current_price,
            market_price=current_price,
            consensus_value=consensus_value,
            valuation_gap=valuation_gap,
            confidence_score=confidence_score,
            recommendation=recommendation,
        )

    except Exception as e:
        print(f"Error calculating valuation consensus: {e}")
        return ValuationConsensus(
            dcf_valuation=current_price,
            relative_valuation=current_price,
            market_price=current_price,
            consensus_value=current_price,
            valuation_gap=0.0,
            confidence_score=0.5,
            recommendation="hold",
        )


def _calculate_valuation_scores(
    self,
    dcf: Optional[DCFValuation],
    relative: Optional[RelativeValuation],
    dupont: Optional[DuPontAnalysis],
    consensus: Optional[ValuationConsensus],
) -> Dict[str, float]:
    """计算估值分析得分"""
    scores = {}

    try:
        # DCF估值得分
        if dcf:
            upside_score = max(0, min(dcf.upside_potential / 50, 1))  # 上涨潜力标准化
            confidence_score = dcf.confidence_level
            scores["dcf_score"] = (upside_score + confidence_score) / 2
        else:
            scores["dcf_score"] = 0.5

        # 相对估值得分
        if relative:
            # 估值越低得分越高
            pe_score = 1 - relative.industry_pe_percentile
            pb_score = 1 - relative.industry_pb_percentile
            scores["relative_score"] = (pe_score + pb_score) / 2
        else:
            scores["relative_score"] = 0.5

        # 杜邦分析得分
        if dupont:
            roe_score = min(dupont.roe / 0.20, 1)  # ROE标准化
            profit_score = min(dupont.profit_margin / 0.10, 1)  # 利润率标准化
            efficiency_score = min(dupont.asset_turnover / 2.0, 1)  # 周转率标准化
            scores["dupont_score"] = (roe_score + profit_score + efficiency_score) / 3
        else:
            scores["dupont_score"] = 0.5

        # 共识估值得分
        if consensus:
            gap_score = 1 - abs(consensus.valuation_gap) / 50  # 估值差距标准化
            confidence_score = consensus.confidence_score
            scores["consensus_score"] = (gap_score + confidence_score) / 2
        else:
            scores["consensus_score"] = 0.5

        # 综合得分
        weights = {"dcf_score": 0.3, "relative_score": 0.3, "dupont_score": 0.2, "consensus_score": 0.2}

        overall_score = sum(scores.get(key, 0) * weight for key, weight in weights.items())
        scores["overall_score"] = overall_score

    except Exception as e:
        print(f"Error calculating valuation scores: {e}")
        scores = {"overall_score": 0.5, "error": True}

    return scores


def _generate_valuation_signals(
    self,
    dcf: Optional[DCFValuation],
    relative: Optional[RelativeValuation],
    consensus: Optional[ValuationConsensus],
) -> List[Dict[str, Any]]:
    """生成估值信号"""
    signals = []

    # DCF信号
    if dcf and dcf.confidence_level > 0.6:
        if dcf.upside_potential > 30:
            signals.append(
                {
                    "type": "dcf_strong_buy",
                    "severity": "high",
                    "message": f"DCF显示显著低估 - 上涨潜力: {dcf.upside_potential:.1f}%",
                    "details": {
                        "intrinsic_value": dcf.intrinsic_value,
                        "current_price": dcf.current_price,
                        "upside_potential": dcf.upside_potential,
                        "confidence": dcf.confidence_level,
                    },
                }
            )
        elif dcf.upside_potential < -20:
            signals.append(
                {
                    "type": "dcf_overvalued",
                    "severity": "medium",
                    "message": f"DCF显示显著高估 - 下跌风险: {abs(dcf.upside_potential):.1f}%",
                    "details": {
                        "intrinsic_value": dcf.intrinsic_value,
                        "current_price": dcf.current_price,
                        "upside_potential": dcf.upside_potential,
                    },
                }
            )

    # 相对估值信号
    if relative:
        if relative.valuation_fairness == "undervalued":
            signals.append(
                {
                    "type": "relative_undervalued",
                    "severity": "medium",
                    "message": f"相对估值显示低估 - PE百分位: {relative.industry_pe_percentile:.2f}",
                    "details": {
                        "pe_percentile": relative.industry_pe_percentile,
                        "pb_percentile": relative.industry_pb_percentile,
                        "valuation_fairness": relative.valuation_fairness,
                    },
                }
            )
        elif relative.valuation_fairness == "overvalued":
            signals.append(
                {
                    "type": "relative_overvalued",
                    "severity": "medium",
                    "message": f"相对估值显示高估 - PE百分位: {relative.industry_pe_percentile:.2f}",
                    "details": {
                        "pe_percentile": relative.industry_pe_percentile,
                        "pb_percentile": relative.industry_pb_percentile,
                        "valuation_fairness": relative.valuation_fairness,
                    },
                }
            )

    # 共识信号
    if consensus and consensus.confidence_score > 0.7:
        if consensus.recommendation in ["strong_buy", "buy"]:
            signals.append(
                {
                    "type": "valuation_consensus_buy",
                    "severity": "high" if consensus.recommendation == "strong_buy" else "medium",
                    "message": f"估值共识: {consensus.recommendation} - 估值差距: {consensus.valuation_gap:.1f}%",
                    "details": {
                        "consensus_value": consensus.consensus_value,
                        "market_price": consensus.market_price,
                        "valuation_gap": consensus.valuation_gap,
                        "confidence": consensus.confidence_score,
                    },
                }
            )
        elif consensus.recommendation in ["strong_sell", "sell"]:
            signals.append(
                {
                    "type": "valuation_consensus_sell",
                    "severity": "high" if consensus.recommendation == "strong_sell" else "medium",
                    "message": f"估值共识: {consensus.recommendation} - 估值差距: {consensus.valuation_gap:.1f}%",
                    "details": {
                        "consensus_value": consensus.consensus_value,
                        "market_price": consensus.market_price,
                        "valuation_gap": consensus.valuation_gap,
                    },
                }
            )

    return signals


def _generate_valuation_recommendations(
    self, consensus: Optional[ValuationConsensus], dupont: Optional[DuPontAnalysis]
) -> Dict[str, Any]:
    """生成估值建议"""
    recommendations = {}

    try:
        # 基于估值共识的建议
        if consensus:
            if consensus.recommendation == "strong_buy":
                primary_signal = "strong_buy"
                action = f"强烈推荐买入 - 估值共识显示上涨潜力{consensus.valuation_gap:.1f}%"
                confidence = "high"
            elif consensus.recommendation == "buy":
                primary_signal = "buy"
                action = f"建议买入 - 估值显示{consensus.valuation_gap:.1f}%上涨空间"
                confidence = "medium"
            elif consensus.recommendation == "hold":
                primary_signal = "hold"
                action = "建议观望 - 估值相对合理"
                confidence = "medium"
            elif consensus.recommendation == "sell":
                primary_signal = "sell"
                action = f"建议卖出 - 估值显示{abs(consensus.valuation_gap):.1f}%下跌风险"
                confidence = "medium"
            else:
                primary_signal = "strong_sell"
                action = f"强烈建议卖出 - 估值严重高估{abs(consensus.valuation_gap):.1f}%"
                confidence = "high"
        else:
            primary_signal = "hold"
            action = "估值分析不足，建议结合其他指标判断"
            confidence = "low"

        # 考虑杜邦分析
        if dupont:
            if dupont.roe > 0.15:
                action += " (ROE优秀，基本面支撑较好)"
            elif dupont.roe < 0.08:
                action += " (ROE偏低，需关注盈利能力)"

            if dupont.equity_multiplier > 2.5:
                action += " (财务杠杆较高，风险较大)"
            elif dupont.equity_multiplier < 1.5:
                action += " (财务杠杆保守，稳定性较好)"

        recommendations.update(
            {
                "primary_signal": primary_signal,
                "recommended_action": action,
                "confidence_level": confidence,
                "valuation_metrics": {
                    "consensus_value": consensus.consensus_value if consensus else None,
                    "valuation_gap": consensus.valuation_gap if consensus else None,
                    "confidence_score": consensus.confidence_score if consensus else None,
                },
                "fundamental_health": (
                    {
                        "roe": dupont.roe if dupont else None,
                        "profit_margin": dupont.profit_margin if dupont else None,
                        "asset_turnover": dupont.asset_turnover if dupont else None,
                    }
                    if dupont
                    else None
                ),
            }
        )

    except Exception as e:
        print(f"Error generating valuation recommendations: {e}")
        recommendations = {
            "primary_signal": "hold",
            "recommended_action": "分析过程中出现错误，建议观望",
            "confidence_level": "low",
        }

    return recommendations


def _assess_valuation_risk(
    self,
    dcf: Optional[DCFValuation],
    relative: Optional[RelativeValuation],
    consensus: Optional[ValuationConsensus],
) -> Dict[str, Any]:
    """评估估值风险"""
    risk_assessment = {}

    try:
        # DCF风险
        dcf_risk = "low"
        if dcf:
            if dcf.confidence_level < 0.5:
                dcf_risk = "high"  # DCF置信度低
            elif abs(dcf.upside_potential) > 50:
                dcf_risk = "medium"  # 估值偏差较大
        else:
            dcf_risk = "medium"

        # 相对估值风险
        relative_risk = "low"
        if relative:
            pe_extreme = relative.industry_pe_percentile > 0.9 or relative.industry_pe_percentile < 0.1
            pb_extreme = relative.industry_pb_percentile > 0.9 or relative.industry_pb_percentile < 0.1

            if pe_extreme and pb_extreme:
                relative_risk = "high"
            elif pe_extreme or pb_extreme:
                relative_risk = "medium"

        # 共识风险
        consensus_risk = "low"
        if consensus:
            if consensus.confidence_score < 0.6:
                consensus_risk = "high"
            elif abs(consensus.valuation_gap) > 30:
                consensus_risk = "medium"

        # 综合风险等级
        risk_scores = {"high": 3, "medium": 2, "low": 1}
        avg_risk_score = np.mean(
            [risk_scores.get(dcf_risk, 1), risk_scores.get(relative_risk, 1), risk_scores.get(consensus_risk, 1)]
        )

        if avg_risk_score > 2.5:
            overall_risk = "high"
        elif avg_risk_score > 1.5:
            overall_risk = "medium"
        else:
            overall_risk = "low"

        risk_assessment.update(
            {
                "overall_risk_level": overall_risk,
                "dcf_risk": dcf_risk,
                "relative_risk": relative_risk,
                "consensus_risk": consensus_risk,
                "risk_factors": [
                    "DCF估值置信度低" if dcf_risk == "high" else None,
                    "相对估值极端偏离" if relative_risk == "high" else None,
                    "估值共识分歧较大" if consensus_risk == "high" else None,
                ],
                "risk_factors": [
                    f
                    for f in [
                        "DCF估值置信度低" if dcf_risk == "high" else None,
                        "相对估值极端偏离" if relative_risk == "high" else None,
                        "估值共识分歧较大" if consensus_risk == "high" else None,
                    ]
                    if f is not None
                ],
            }
        )

    except Exception as e:
        print(f"Error assessing valuation risk: {e}")
        risk_assessment = {"overall_risk_level": "unknown", "error": str(e)}

    return risk_assessment


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.FINANCIAL_VALUATION,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"财务估值分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )
