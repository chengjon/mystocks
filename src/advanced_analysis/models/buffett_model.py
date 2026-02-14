"""Decision Models - 巴菲特投资模型"""

import numpy as np
import pandas as pd

from .dataclasses import BuffettModelScore


class BuffettModelMixin:
    """巴菲特投资哲学模型方法集"""

def _analyze_buffett_model(self, financial_data: pd.DataFrame, price_data: pd.DataFrame) -> BuffettModelScore:
    """分析巴菲特模型"""
    try:
        # 企业质量评分
        business_quality = self._calculate_buffett_business_quality(financial_data)

        # 管理质量评分
        management_quality = self._calculate_buffett_management_quality(financial_data)

        # 财务健康评分
        financial_health = self._calculate_buffett_financial_health(financial_data)

        # 竞争优势评分
        competitive_advantage = self._calculate_buffett_competitive_advantage(financial_data)

        # 估值吸引力评分
        valuation_attractiveness = self._calculate_buffett_valuation_attractiveness(financial_data, price_data)

        # 综合得分
        weights = [0.25, 0.20, 0.20, 0.20, 0.15]
        overall_score = np.average(
            [
                business_quality,
                management_quality,
                financial_health,
                competitive_advantage,
                valuation_attractiveness,
            ],
            weights=weights,
        )

        # 投资建议
        investment_recommendation = self._get_buffett_recommendation(overall_score)

        return BuffettModelScore(
            business_quality=business_quality,
            management_quality=management_quality,
            financial_health=financial_health,
            competitive_advantage=competitive_advantage,
            valuation_attractiveness=valuation_attractiveness,
            overall_score=overall_score,
            investment_recommendation=investment_recommendation,
        )

    except Exception as e:
        print(f"Error in Buffett model analysis: {e}")
        return BuffettModelScore(0, 0, 0, 0, 0, 0, "无法评估")


def _calculate_buffett_business_quality(self, data: pd.DataFrame) -> float:
    """计算巴菲特企业质量评分"""
    score = 0

    try:
        # ROE稳定性
        if "roe" in data.columns:
            roe_values = data["roe"].dropna()
            if len(roe_values) >= 4:
                roe_stability = 1 - roe_values.std() / roe_values.mean() if roe_values.mean() > 0 else 0
                score += min(roe_stability * 30, 30)

        # 利润率稳定性
        if "net_profit" in data.columns and "revenue" in data.columns:
            profit_margin = (data["net_profit"] / data["revenue"]).dropna()
            if len(profit_margin) >= 4:
                margin_stability = 1 - profit_margin.std() / profit_margin.mean() if profit_margin.mean() > 0 else 0
                score += min(margin_stability * 25, 25)

        # 现金流质量
        if "cash_flow" in data.columns and "net_profit" in data.columns:
            cash_flow_ratio = (data["cash_flow"] / data["net_profit"]).dropna()
            avg_cf_ratio = cash_flow_ratio.mean()
            if avg_cf_ratio > 1.2:
                score += 25
            elif avg_cf_ratio > 1.0:
                score += 20

        # 债务水平
        if "total_liabilities" in data.columns and "total_assets" in data.columns:
            debt_ratio = (data["total_liabilities"] / data["total_assets"]).dropna().mean()
            if debt_ratio < 0.4:
                score += 20
            elif debt_ratio < 0.6:
                score += 15

    except Exception as e:
        print(f"Error calculating business quality: {e}")

    return min(score, 100)


def _calculate_buffett_management_quality(self, data: pd.DataFrame) -> float:
    """计算巴菲特管理质量评分"""
    score = 0

    try:
        # 资本配置效率 (ROIC)
        if all(col in data.columns for col in ["net_profit", "total_assets", "total_liabilities"]):
            invested_capital = data["total_assets"] - data["total_liabilities"]
            roic = (data["net_profit"] / invested_capital).dropna()
            avg_roic = roic.mean()

            if avg_roic > 0.15:
                score += 40
            elif avg_roic > 0.10:
                score += 30
            elif avg_roic > 0.05:
                score += 20

        # 盈利增长稳定性
        if "net_profit" in data.columns:
            profit_growth = data["net_profit"].pct_change().dropna()
            if len(profit_growth) >= 4:
                growth_stability = (
                    1 - profit_growth.std() / abs(profit_growth.mean()) if profit_growth.mean() != 0 else 0
                )
                score += min(growth_stability * 30, 30)

        # 股东利益保护
        if "eps" in data.columns:
            eps_growth = data["eps"].pct_change().dropna()
            if len(eps_growth) >= 4:
                positive_growth = (eps_growth > 0).sum() / len(eps_growth)
                score += positive_growth * 30

    except Exception as e:
        print(f"Error calculating management quality: {e}")

    return min(score, 100)


def _calculate_buffett_financial_health(self, data: pd.DataFrame) -> float:
    """计算巴菲特财务健康评分"""
    score = 0

    try:
        # 债务比率
        if "total_liabilities" in data.columns and "total_assets" in data.columns:
            debt_ratio = (data["total_liabilities"] / data["total_assets"]).dropna().mean()
            if debt_ratio < 0.3:
                score += 35
            elif debt_ratio < 0.5:
                score += 25
            elif debt_ratio < 0.7:
                score += 15

        # 利息保障倍数
        if "net_profit" in data.columns and "total_liabilities" in data.columns:
            # 简化的利息支出估算
            interest_expense = data["total_liabilities"] * 0.04  # 假设4%的利率
            interest_coverage = (data["net_profit"] / interest_expense).dropna().mean()

            if interest_coverage > 8:
                score += 35
            elif interest_coverage > 5:
                score += 25
            elif interest_coverage > 3:
                score += 15

        # 现金流充足性
        if "cash_flow" in data.columns and "total_liabilities" in data.columns:
            cash_coverage = (data["cash_flow"] / data["total_liabilities"]).dropna().mean()
            if cash_coverage > 0.3:
                score += 30

    except Exception as e:
        print(f"Error calculating financial health: {e}")

    return min(score, 100)


def _calculate_buffett_competitive_advantage(self, data: pd.DataFrame) -> float:
    """计算巴菲特竞争优势评分"""
    score = 0

    try:
        # 毛利率稳定性
        if "revenue" in data.columns and "net_profit" in data.columns:
            gross_margin = (data["net_profit"] / data["revenue"]).dropna()
            if len(gross_margin) >= 4:
                margin_stability = 1 - gross_margin.std() / gross_margin.mean() if gross_margin.mean() > 0 else 0
                score += min(margin_stability * 30, 30)

        # ROE优势
        if "roe" in data.columns:
            avg_roe = data["roe"].dropna().mean()
            if avg_roe > 0.20:
                score += 30
            elif avg_roe > 0.15:
                score += 25
            elif avg_roe > 0.10:
                score += 20

        # 市场地位 (通过规模和增长稳定性体现)
        if "revenue" in data.columns:
            revenue_growth = data["revenue"].pct_change().dropna()
            if len(revenue_growth) >= 4:
                growth_consistency = (revenue_growth > 0).sum() / len(revenue_growth)
                score += growth_consistency * 20

        # 品牌和护城河 (简化为财务稳定性和盈利能力)
        if "roe" in data.columns:
            roe_volatility = data["roe"].dropna().std()
            stability_score = 1 - roe_volatility / data["roe"].dropna().mean() if data["roe"].dropna().mean() > 0 else 0
            score += min(stability_score * 20, 20)

    except Exception as e:
        print(f"Error calculating competitive advantage: {e}")

    return min(score, 100)


def _calculate_buffett_valuation_attractiveness(self, financial_data: pd.DataFrame, price_data: pd.DataFrame) -> float:
    """计算巴菲特估值吸引力评分"""
    score = 100  # 从100分开始扣分

    try:
        # 获取当前估值
        current_price = price_data["close"].iloc[-1] if not price_data.empty else 0

        # 计算合理PE (基于ROE)
        if "roe" in financial_data.columns and "eps" in financial_data.columns:
            avg_roe = financial_data["roe"].dropna().mean()
            avg_eps = financial_data["eps"].dropna().mean()

            if avg_roe > 0 and avg_eps > 0:
                fair_pe = avg_roe * 100 / 0.10  # 假设10%的必要收益率
                current_pe = current_price / avg_eps

                # PE偏离度
                pe_deviation = abs(current_pe - fair_pe) / fair_pe
                score -= min(pe_deviation * 50, 50)

        # PB估值
        if "bvps" in financial_data.columns:
            avg_bvps = financial_data["bvps"].dropna().mean()
            if avg_bvps > 0:
                current_pb = current_price / avg_bvps
                if current_pb > 3:
                    score -= 30
                elif current_pb > 2:
                    score -= 15

        # 现金流估值
        if "cash_flow" in financial_data.columns:
            avg_cf = financial_data["cash_flow"].dropna().mean()
            if avg_cf > 0:
                cf_yield = avg_cf / current_price
                if cf_yield < 0.03:  # 现金流收益率低于3%
                    score -= 20

    except Exception as e:
        print(f"Error calculating valuation attractiveness: {e}")

    return max(score, 0)


def _get_buffett_recommendation(self, score: float) -> str:
    """获取巴菲特模型投资建议"""
    if score >= self.model_thresholds["strong_buy"]:
        return "强烈推荐买入 - 符合巴菲特投资标准"
    elif score >= self.model_thresholds["buy"]:
        return "推荐买入 - 基本符合巴菲特投资理念"
    elif score >= self.model_thresholds["hold"]:
        return "谨慎持有 - 有一定投资价值"
    elif score >= self.model_thresholds["sell"]:
        return "建议卖出 - 不符合巴菲特投资标准"
    else:
        return "强烈建议卖出 - 严重不符合巴菲特投资原则"


