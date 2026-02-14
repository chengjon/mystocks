"""Decision Models - 费雪成长投资模型"""

import numpy as np
import pandas as pd

from .dataclasses import FisherModelScore


class FisherModelMixin:
    """Philip Fisher 成长投资方法集"""

def _analyze_fisher_model(self, financial_data: pd.DataFrame, price_data: pd.DataFrame) -> FisherModelScore:
    """分析费雪模型"""
    try:
        # 业务潜力
        business_potential = self._calculate_fisher_business_potential(financial_data)

        # 研发能力
        research_development = self._calculate_fisher_rd_capability(financial_data)

        # 管理质量
        management_quality = self._calculate_fisher_management_quality(financial_data)

        # 利润率
        profit_margin = self._calculate_fisher_profit_margin(financial_data)

        # 增长潜力
        growth_potential = self._calculate_fisher_growth_potential(financial_data, price_data)

        # 长期视野
        long_term_vision = self._calculate_fisher_long_term_vision(financial_data)

        # 综合得分
        weights = [0.20, 0.15, 0.20, 0.15, 0.15, 0.15]
        overall_score = np.average(
            [
                business_potential,
                research_development,
                management_quality,
                profit_margin,
                growth_potential,
                long_term_vision,
            ],
            weights=weights,
        )

        # 投资建议
        investment_recommendation = self._get_fisher_recommendation(overall_score)

        return FisherModelScore(
            business_potential=business_potential,
            research_development=research_development,
            management_quality=management_quality,
            profit_margin=profit_margin,
            growth_potential=growth_potential,
            long_term_vision=long_term_vision,
            overall_score=overall_score,
            investment_recommendation=investment_recommendation,
        )

    except Exception as e:
        print(f"Error in Fisher model analysis: {e}")
        return FisherModelScore(0, 0, 0, 0, 0, 0, 0, "无法评估")


def _calculate_fisher_business_potential(self, data: pd.DataFrame) -> float:
    """计算费雪业务潜力"""
    score = 0

    try:
        # 市场地位和增长空间
        if "revenue" in data.columns:
            revenue_growth = data["revenue"].pct_change().dropna()
            if len(revenue_growth) >= 4:
                avg_growth = revenue_growth.mean()
                if avg_growth > 0.20:
                    score += 30
                elif avg_growth > 0.10:
                    score += 25
                elif avg_growth > 0.05:
                    score += 20

        # 行业地位 (简化为市场份额估算)
        if "revenue" in data.columns:
            # 简化为营收稳定性
            revenue_cv = data["revenue"].dropna().std() / data["revenue"].dropna().mean()
            stability_score = 1 - revenue_cv
            score += min(stability_score * 40, 40)

        # 竞争优势
        if "roe" in data.columns:
            avg_roe = data["roe"].dropna().mean()
            if avg_roe > 0.18:
                score += 30
            elif avg_roe > 0.12:
                score += 20

    except Exception as e:
        print(f"Error calculating business potential: {e}")

    return min(score, 100)


def _calculate_fisher_rd_capability(self, data: pd.DataFrame) -> float:
    """计算费雪研发能力"""
    # 简化为利润率的一致性和增长
    score = 0

    try:
        if "net_profit" in data.columns and len(data) >= 4:
            # 利润增长的一致性
            profit_growth = data["net_profit"].pct_change().dropna()
            positive_growth_ratio = (profit_growth > 0).sum() / len(profit_growth)
            score += positive_growth_ratio * 50

            # 创新能力 (简化为利润率稳定性)
            profit_margin = (data["net_profit"] / data["revenue"]).dropna()
            margin_stability = 1 - profit_margin.std() / profit_margin.mean() if profit_margin.mean() > 0 else 0
            score += min(margin_stability * 50, 50)

    except Exception as e:
        print(f"Error calculating RD capability: {e}")

    return min(score, 100)


def _calculate_fisher_management_quality(self, data: pd.DataFrame) -> float:
    """计算费雪管理质量"""
    score = 0

    try:
        # 资本配置效率
        if all(col in data.columns for col in ["net_profit", "total_assets", "total_liabilities"]):
            invested_capital = data["total_assets"] - data["total_liabilities"]
            roic = (data["net_profit"] / invested_capital).dropna().mean()

            if roic > 0.15:
                score += 40
            elif roic > 0.10:
                score += 30
            elif roic > 0.05:
                score += 20

        # 股东利益保护
        if "eps" in data.columns:
            eps_values = data["eps"].dropna()
            if len(eps_values) >= 4:
                eps_growth = eps_values.pct_change().dropna()
                consistent_growth = (eps_growth > 0).sum() / len(eps_growth)
                score += consistent_growth * 30

        # 长期战略眼光
        if "cash_flow" in data.columns and "net_profit" in data.columns:
            cf_consistency = ((data["cash_flow"] > 0) & (data["net_profit"] > 0)).sum() / len(data)
            score += cf_consistency * 30

    except Exception as e:
        print(f"Error calculating management quality: {e}")

    return min(score, 100)


def _calculate_fisher_profit_margin(self, data: pd.DataFrame) -> float:
    """计算费雪利润率"""
    score = 0

    try:
        if "net_profit" in data.columns and "revenue" in data.columns:
            profit_margins = (data["net_profit"] / data["revenue"]).dropna()

            if not profit_margins.empty:
                avg_margin = profit_margins.mean()

                # 高利润率
                if avg_margin > 0.15:
                    score += 40
                elif avg_margin > 0.10:
                    score += 30
                elif avg_margin > 0.05:
                    score += 20

                # 利润率稳定性
                margin_stability = 1 - profit_margins.std() / avg_margin if avg_margin > 0 else 0
                score += min(margin_stability * 40, 40)

                # 利润率趋势
                if len(profit_margins) >= 4:
                    recent_avg = profit_margins.tail(2).mean()
                    older_avg = profit_margins.head(2).mean()
                    if recent_avg > older_avg:
                        score += 20

    except Exception as e:
        print(f"Error calculating profit margin: {e}")

    return min(score, 100)


def _calculate_fisher_growth_potential(self, financial_data: pd.DataFrame, price_data: pd.DataFrame) -> float:
    """计算费雪增长潜力"""
    score = 0

    try:
        # 营收增长潜力
        if "revenue" in financial_data.columns:
            revenue_growth = financial_data["revenue"].pct_change().dropna()
            if len(revenue_growth) >= 4:
                avg_growth = revenue_growth.mean()
                growth_acceleration = revenue_growth.diff().mean()

                if avg_growth > 0.15:
                    score += 30
                elif avg_growth > 0.08:
                    score += 20

                if growth_acceleration > 0:
                    score += 20

        # 市场增长空间
        if not price_data.empty and len(price_data) >= 20:
            # 简化为技术趋势
            price_trend = price_data["close"].pct_change(20).iloc[-1]
            if price_trend > 0.10:
                score += 30
            elif price_trend > 0.05:
                score += 20

        # 行业增长前景
        # 简化为财务稳定性和盈利能力
        if "roe" in financial_data.columns:
            roe_trend = financial_data["roe"].dropna()
            if len(roe_trend) >= 4:
                roe_improvement = roe_trend.iloc[-1] > roe_trend.iloc[0]
                if roe_improvement:
                    score += 30

    except Exception as e:
        print(f"Error calculating growth potential: {e}")

    return min(score, 100)


def _calculate_fisher_long_term_vision(self, data: pd.DataFrame) -> float:
    """计算费雪长期视野"""
    score = 0

    try:
        # 长期资本支出
        if "cash_flow" in data.columns:
            # 简化为现金流稳定性
            cf_volatility = data["cash_flow"].dropna().std() / data["cash_flow"].dropna().mean()
            if data["cash_flow"].dropna().mean() > 0:
                cf_stability = 1 - cf_volatility
                score += min(cf_stability * 40, 40)

        # 资产质量
        if "total_assets" in data.columns:
            asset_growth = data["total_assets"].pct_change().dropna()
            if len(asset_growth) >= 4:
                consistent_growth = (asset_growth > 0).sum() / len(asset_growth)
                score += consistent_growth * 30

        # 股东价值创造
        if "eps" in data.columns:
            eps_trend = data["eps"].dropna()
            if len(eps_trend) >= 4:
                long_term_growth = (eps_trend.iloc[-1] / eps_trend.iloc[0]) ** (1 / (len(eps_trend) - 1)) - 1
                if long_term_growth > 0.08:
                    score += 30
                elif long_term_growth > 0.05:
                    score += 20

    except Exception as e:
        print(f"Error calculating long term vision: {e}")

    return min(score, 100)


def _get_fisher_recommendation(self, score: float) -> str:
    """获取费雪模型投资建议"""
    if score >= self.model_thresholds["strong_buy"]:
        return "强烈推荐买入 - 符合费雪长期投资标准"
    elif score >= self.model_thresholds["buy"]:
        return "推荐买入 - 基本符合费雪投资理念"
    elif score >= self.model_thresholds["hold"]:
        return "谨慎持有 - 有长期投资价值"
    elif score >= self.model_thresholds["sell"]:
        return "建议卖出 - 不符合费雪投资标准"
    else:
        return "强烈建议卖出 - 严重不符合费雪投资原则"


# 模型验证和综合方法需要继续实现...
