"""Valuation data models for `dcf_valuation.py`."""

from dataclasses import dataclass
from typing import Dict, List, Optional


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
