"""Shared methods for `dcf_valuation.py`."""

import logging
from datetime import datetime
from typing import List, Optional

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType
from src.advanced_analysis.financial_valuation_analyzer._dcf_valuation_models import (
    DCFValuation,
    DuPontAnalysis,
    ModernValuation,
    RelativeValuation,
    ValuationConsensus,
)
from src.advanced_analysis.financial_valuation_analyzer._dcf_valuation_tail import FinancialValuationAnalyzerTailMixin

logger = logging.getLogger(__name__)


class FinancialValuationAnalyzerMixin(FinancialValuationAnalyzerTailMixin):
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
                logger.error("Error getting financial data for %s: %s", stock_code, e)
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
                logger.error("Error getting current price for %s: %s", stock_code, e)

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
                logger.error("Error calculating DCF valuation: %s", e)
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
                logger.error("Error calculating relative valuation: %s", e)
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
                logger.error("Error performing DuPont analysis: %s", e)
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
                logger.error("Error calculating modern valuation: %s", e)
                return ModernValuation()
