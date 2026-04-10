"""
投资决策模型分析器

基于巴菲特、CANSLIM、费雪三大投资哲学的综合决策分析。
实际模型实现已拆分至 models/ 子包。
"""

from datetime import datetime

import numpy as np
import pandas as pd

from src.advanced_analysis import BaseAnalyzer, AnalysisResult, AnalysisType

from .models import (
    BuffettModelMixin,
    CANSLIMModelMixin,
    DecisionSynthesisMixin,
    FisherModelMixin,
)

class DecisionModelsAnalyzer(BuffettModelMixin, CANSLIMModelMixin, FisherModelMixin, DecisionSynthesisMixin, BaseAnalyzer):
    """
    交易决策模型分析器

    提供经典投资决策模型的量化实现，包括：
    - 巴菲特价值投资模型
    - 欧内尔CAN SLIM成长投资模型
    - 费雪长期投资模型
    - 多模型决策综合和验证
    - 模型回测和性能评估
    """

    def __init__(self, data_manager, gpu_manager=None):
        """初始化分析器"""
        super().__init__(data_manager, gpu_manager)

        # 模型权重配置
        self.model_weights = {
            "buffett": 0.4,  # 巴菲特模型权重
            "canslim": 0.35,  # CAN SLIM模型权重
            "fisher": 0.25,  # 费雪模型权重
        }

        # 模型阈值配置
        self.model_thresholds = {"strong_buy": 80, "buy": 65, "hold": 45, "sell": 30, "strong_sell": 20}

        # 风险调整参数
        self.risk_params = {
            "volatility_penalty": 0.1,  # 波动率惩罚系数
            "liquidity_bonus": 0.05,  # 流动性奖励系数
            "market_risk_adjustment": 0.15,  # 市场风险调整系数
        }

    def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
        """
        执行交易决策模型分析

        Args:
            stock_code: 股票代码
            **kwargs: 分析参数
                - include_buffett: 是否包含巴菲特模型 (默认: True)
                - include_canslim: 是否包含CAN SLIM模型 (默认: True)
                - include_fisher: 是否包含费雪模型 (默认: True)
                - include_validation: 是否包含模型验证 (默认: True)
                - risk_adjusted: 是否进行风险调整 (默认: True)

        Returns:
            AnalysisResult: 分析结果
        """
        include_buffett = kwargs.get("include_buffett", True)
        include_canslim = kwargs.get("include_canslim", True)
        include_fisher = kwargs.get("include_fisher", True)
        include_validation = kwargs.get("include_validation", True)
        risk_adjusted = kwargs.get("risk_adjusted", True)

        try:
            # 获取基础数据
            financial_data = self._get_financial_data(stock_code, periods=12)  # 12个月数据
            price_data = self._get_historical_data(stock_code, days=365, data_type="1d")

            if financial_data.empty or price_data.empty:
                return self._create_error_result(stock_code, "Insufficient data for decision model analysis")

            # 执行各模型分析
            buffett_score = None
            if include_buffett:
                buffett_score = self._analyze_buffett_model(financial_data, price_data)

            canslim_score = None
            if include_canslim:
                canslim_score = self._analyze_canslim_model(financial_data, price_data)

            fisher_score = None
            if include_fisher:
                fisher_score = self._analyze_fisher_model(financial_data, price_data)

            # 模型验证
            model_validations = []
            if include_validation:
                if buffett_score:
                    buffett_validation = self._validate_buffett_model(financial_data, price_data)
                    model_validations.append(buffett_validation)

                if canslim_score:
                    canslim_validation = self._validate_canslim_model(financial_data, price_data)
                    model_validations.append(canslim_validation)

                if fisher_score:
                    fisher_validation = self._validate_fisher_model(financial_data, price_data)
                    model_validations.append(fisher_validation)

            # 决策综合
            decision_synthesis = self._synthesize_decision_models(
                buffett_score, canslim_score, fisher_score, model_validations, risk_adjusted
            )

            # 计算综合得分
            scores = self._calculate_decision_scores(
                buffett_score, canslim_score, fisher_score, decision_synthesis, model_validations
            )

            # 生成信号
            signals = self._generate_decision_signals(
                buffett_score, canslim_score, fisher_score, decision_synthesis, model_validations
            )

            # 投资建议
            recommendations = self._generate_decision_recommendations(decision_synthesis)

            # 风险评估
            risk_assessment = self._assess_decision_risk(buffett_score, canslim_score, fisher_score, model_validations)

            # 元数据
            metadata = {
                "stock_code": stock_code,
                "models_used": [
                    name
                    for name, flag in [
                        ("buffett", include_buffett),
                        ("canslim", include_canslim),
                        ("fisher", include_fisher),
                    ]
                    if flag
                ],
                "validation_performed": include_validation,
                "risk_adjusted": risk_adjusted,
                "consensus_score": decision_synthesis.consensus_score if decision_synthesis else 0,
                "final_recommendation": decision_synthesis.final_recommendation if decision_synthesis else "unknown",
                "analysis_timestamp": datetime.now(),
            }

            return AnalysisResult(
                analysis_type=AnalysisType.DECISION_MODELS,
                stock_code=stock_code,
                timestamp=datetime.now(),
                scores=scores,
                signals=signals,
                recommendations=recommendations,
                risk_assessment=risk_assessment,
                metadata=metadata,
                raw_data={
                    "financial_data": financial_data if kwargs.get("include_raw_data", False) else None,
                    "price_data": price_data if kwargs.get("include_raw_data", False) else None,
                },
            )

        except Exception as e:
            return self._create_error_result(stock_code, str(e))


    def _get_financial_data(self, stock_code: str, periods: int) -> pd.DataFrame:
        """获取财务数据"""
        try:
            from src.data_sources.factory import get_relational_source

            relational_source = get_relational_source(source_type="mock")

            financial_data = relational_source.get_financial_data(stock_code=stock_code, periods=periods)

            if financial_data.empty:
                financial_data = self._generate_mock_financial_data(stock_code, periods)

            return financial_data

        except Exception as e:
            print(f"Error getting financial data for {stock_code}: {e}")
            return self._generate_mock_financial_data(stock_code, periods)


    def _generate_mock_financial_data(self, stock_code: str, periods: int) -> pd.DataFrame:
        """生成模拟财务数据"""
        np.random.seed(hash(stock_code) % 2**32)

        data = []
        base_revenue = np.random.uniform(50000000, 500000000)  # 基础营收
        base_net_profit = base_revenue * np.random.uniform(0.08, 0.18)  # 净利润率

        for i in range(periods):
            # 添加增长趋势
            growth_factor = 1 + 0.02 * i + np.random.normal(0, 0.05)
            revenue = base_revenue * growth_factor
            net_profit = base_net_profit * growth_factor

            # 计算各种财务指标
            eps = net_profit / 1000000  # 每股收益
            bvps = net_profit * np.random.uniform(2, 4) / 1000000  # 每股净资产
            roe = net_profit / (bvps * 1000000)  # ROE
            pe_ratio = np.random.uniform(15, 45)  # PE
            pb_ratio = np.random.uniform(1.5, 4.5)  # PB

            data.append(
                {
                    "period": f"Q{(i % 4) + 1} {2023 + i // 4}",
                    "revenue": revenue,
                    "net_profit": net_profit,
                    "eps": eps,
                    "bvps": bvps,
                    "roe": roe,
                    "pe_ratio": pe_ratio,
                    "pb_ratio": pb_ratio,
                    "total_assets": revenue * np.random.uniform(1.5, 3.0),
                    "total_liabilities": revenue * np.random.uniform(0.3, 1.0),
                    "cash_flow": net_profit * np.random.uniform(1.0, 1.5),
                }
            )

        return pd.DataFrame(data)


