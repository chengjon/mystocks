"""Decision Models - 数据类定义"""

from dataclasses import dataclass
from typing import List


@dataclass
class BuffettModelScore:
    """巴菲特模型评分"""

    business_quality: float  # 企业质量 (0-100)
    management_quality: float  # 管理质量 (0-100)
    financial_health: float  # 财务健康 (0-100)
    competitive_advantage: float  # 竞争优势 (0-100)
    valuation_attractiveness: float  # 估值吸引力 (0-100)
    overall_score: float  # 综合得分 (0-100)
    investment_recommendation: str  # 投资建议


@dataclass
class CANSLIMModelScore:
    """CAN SLIM模型评分"""

    current_earnings: float  # 当前收益 (0-100)
    annual_earnings: float  # 年度收益 (0-100)
    new_highs: float  # 新高新低 (0-100)
    supply_demand: float  # 供给需求 (0-100)
    leadership: float  # 领导地位 (0-100)
    institutional_sponsorship: float  # 机构赞助 (0-100)
    market_direction: float  # 市场方向 (0-100)
    overall_score: float  # 综合得分 (0-100)
    investment_recommendation: str  # 投资建议


@dataclass
class FisherModelScore:
    """费雪模型评分"""

    business_potential: float  # 业务潜力 (0-100)
    research_development: float  # 研发能力 (0-100)
    management_quality: float  # 管理质量 (0-100)
    profit_margin: float  # 利润率 (0-100)
    growth_potential: float  # 增长潜力 (0-100)
    long_term_vision: float  # 长期视野 (0-100)
    overall_score: float  # 综合得分 (0-100)
    investment_recommendation: str  # 投资建议


@dataclass
class ModelValidationResult:
    """模型验证结果"""

    model_name: str
    backtest_period: int  # 回测周期（月）
    win_rate: float  # 胜率 (0-1)
    avg_return: float  # 平均收益率
    max_drawdown: float  # 最大回撤
    sharpe_ratio: float  # 夏普比率
    confidence_level: float  # 置信水平 (0-1)
    validation_score: float  # 验证得分 (0-100)


@dataclass
class DecisionSynthesis:
    """决策综合"""

    buffett_score: float  # 巴菲特模型权重得分
    canslim_score: float  # CAN SLIM模型权重得分
    fisher_score: float  # 费雪模型权重得分
    consensus_score: float  # 共识得分 (0-100)
    confidence_level: float  # 置信水平 (0-1)
    final_recommendation: str  # 最终建议
    risk_adjusted_score: float  # 风险调整得分
    decision_factors: List[str]  # 决策因素


