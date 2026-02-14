"""Decision Models - CANSLIM 投资模型"""

import numpy as np
import pandas as pd

from .dataclasses import CANSLIMModelScore


class CANSLIMModelMixin:
    """William O'Neil CANSLIM 策略方法集"""

def _analyze_canslim_model(self, financial_data: pd.DataFrame, price_data: pd.DataFrame) -> CANSLIMModelScore:
    """分析CAN SLIM模型"""
    try:
        # C: 当前收益
        current_earnings = self._calculate_canslim_current_earnings(financial_data)

        # A: 年度收益
        annual_earnings = self._calculate_canslim_annual_earnings(financial_data)

        # N: 新高新低
        new_highs = self._calculate_canslim_new_highs(price_data)

        # S: 供给需求
        supply_demand = self._calculate_canslim_supply_demand(price_data)

        # L: 领导地位
        leadership = self._calculate_canslim_leadership(financial_data, price_data)

        # I: 机构赞助
        institutional_sponsorship = self._calculate_canslim_institutional_sponsorship(financial_data)

        # M: 市场方向
        market_direction = self._calculate_canslim_market_direction(price_data)

        # 综合得分
        weights = [0.15, 0.15, 0.15, 0.10, 0.15, 0.15, 0.15]
        overall_score = np.average(
            [
                current_earnings,
                annual_earnings,
                new_highs,
                supply_demand,
                leadership,
                institutional_sponsorship,
                market_direction,
            ],
            weights=weights,
        )

        # 投资建议
        investment_recommendation = self._get_canslim_recommendation(overall_score)

        return CANSLIMModelScore(
            current_earnings=current_earnings,
            annual_earnings=annual_earnings,
            new_highs=new_highs,
            supply_demand=supply_demand,
            leadership=leadership,
            institutional_sponsorship=institutional_sponsorship,
            market_direction=market_direction,
            overall_score=overall_score,
            investment_recommendation=investment_recommendation,
        )

    except Exception as e:
        print(f"Error in CAN SLIM model analysis: {e}")
        return CANSLIMModelScore(0, 0, 0, 0, 0, 0, 0, 0, "无法评估")


def _calculate_canslim_current_earnings(self, data: pd.DataFrame) -> float:
    """计算CAN SLIM当前收益"""
    score = 0

    try:
        # 季度收益增长
        if "eps" in data.columns:
            eps_values = data["eps"].dropna()
            if len(eps_values) >= 2:
                latest_eps = eps_values.iloc[-1]
                prev_eps = eps_values.iloc[-2]

                if prev_eps > 0:
                    qtr_growth = (latest_eps - prev_eps) / prev_eps
                    if qtr_growth > 0.25:  # 25%以上增长
                        score += 40
                    elif qtr_growth > 0.15:
                        score += 30
                    elif qtr_growth > 0.05:
                        score += 20

        # 收益惊喜程度
        if len(data) >= 4:
            recent_avg_eps = data["eps"].tail(4).mean()
            older_avg_eps = data["eps"].head(4).mean() if len(data) >= 8 else data["eps"].mean()

            if older_avg_eps > 0:
                eps_acceleration = (recent_avg_eps - older_avg_eps) / older_avg_eps
                if eps_acceleration > 0.20:
                    score += 35
                elif eps_acceleration > 0.10:
                    score += 25

        # 收益质量
        if "cash_flow" in data.columns and "net_profit" in data.columns:
            cf_to_profit = (data["cash_flow"] / data["net_profit"]).dropna().tail(4).mean()
            if cf_to_profit > 1.0:
                score += 25

    except Exception as e:
        print(f"Error calculating current earnings: {e}")

    return min(score, 100)


def _calculate_canslim_annual_earnings(self, data: pd.DataFrame) -> float:
    """计算CAN SLIM年度收益"""
    score = 0

    try:
        if "eps" in data.columns and len(data) >= 4:
            # 年度EPS增长
            annual_eps = data.groupby(data.index.year)["eps"].last() if hasattr(data.index, "year") else data["eps"]
            if len(annual_eps) >= 2:
                eps_growth = annual_eps.pct_change().dropna()
                avg_growth = eps_growth.mean()

                if avg_growth > 0.25:
                    score += 50
                elif avg_growth > 0.15:
                    score += 40
                elif avg_growth > 0.08:
                    score += 30
                elif avg_growth > 0:
                    score += 20

            # EPS增长加速
            if len(eps_growth) >= 3:
                recent_growth = eps_growth.tail(2).mean()
                older_growth = eps_growth.head(len(eps_growth) - 2).mean() if len(eps_growth) > 2 else eps_growth.mean()

                if recent_growth > older_growth * 1.2:
                    score += 30
                elif recent_growth > older_growth:
                    score += 20

    except Exception as e:
        print(f"Error calculating annual earnings: {e}")

    return min(score, 100)


def _calculate_canslim_new_highs(self, data: pd.DataFrame) -> float:
    """计算CAN SLIM新高新低"""
    score = 0

    try:
        if not data.empty and len(data) >= 20:
            current_price = data["close"].iloc[-1]
            recent_high = data["high"].rolling(window=20).max().iloc[-1]

            # 接近52周高点
            high_ratio = current_price / recent_high
            if high_ratio > 0.95:
                score += 40
            elif high_ratio > 0.90:
                score += 30
            elif high_ratio > 0.85:
                score += 20

            # 突破新高
            if current_price >= recent_high:
                score += 30

            # 相对强度
            market_data = data.copy()  # 简化为个股数据作为市场数据
            relative_strength = (data["close"] / market_data["close"]).rolling(window=20).mean().iloc[-1]
            if relative_strength > 1.1:
                score += 30
            elif relative_strength > 1.05:
                score += 20

    except Exception as e:
        print(f"Error calculating new highs: {e}")

    return min(score, 100)


def _calculate_canslim_supply_demand(self, data: pd.DataFrame) -> float:
    """计算CAN SLIM供给需求"""
    score = 0

    try:
        if not data.empty and len(data) >= 20:
            # 成交量放大
            volume_ma = data["volume"].rolling(window=20).mean()
            recent_volume = data["volume"].tail(5).mean()
            avg_volume = volume_ma.iloc[-1]

            volume_ratio = recent_volume / avg_volume
            if volume_ratio > 2.0:
                score += 35
            elif volume_ratio > 1.5:
                score += 25
            elif volume_ratio > 1.2:
                score += 15

            # 价格上涨配合成交量
            price_change = data["close"].pct_change().tail(5).mean()
            if price_change > 0.05 and volume_ratio > 1.2:
                score += 30
            elif price_change > 0 and volume_ratio > 1.0:
                score += 20

            # 筹码集中度 (简化为成交量稳定性)
            volume_std = data["volume"].tail(20).std()
            volume_mean = data["volume"].tail(20).mean()
            volume_cv = volume_std / volume_mean if volume_mean > 0 else 0

            if volume_cv < 0.5:  # 成交量稳定
                score += 20
            elif volume_cv < 0.8:
                score += 10

    except Exception as e:
        print(f"Error calculating supply demand: {e}")

    return min(score, 100)


def _calculate_canslim_leadership(self, financial_data: pd.DataFrame, price_data: pd.DataFrame) -> float:
    """计算CAN SLIM领导地位"""
    score = 0

    try:
        # 相对强度
        if not price_data.empty and len(price_data) >= 20:
            # 简化为个股表现
            momentum = price_data["close"].pct_change(20).iloc[-1]
            if momentum > 0.15:
                score += 30
            elif momentum > 0.10:
                score += 25
            elif momentum > 0.05:
                score += 20

        # 行业地位
        if "revenue" in financial_data.columns:
            # 简化为营收规模
            avg_revenue = financial_data["revenue"].dropna().mean()
            if avg_revenue > 1000000000:  # 百亿营收
                score += 30
            elif avg_revenue > 500000000:
                score += 25
            elif avg_revenue > 100000000:
                score += 20

        # 创新能力 (简化为利润率)
        if "net_profit" in financial_data.columns and "revenue" in financial_data.columns:
            profit_margin = (financial_data["net_profit"] / financial_data["revenue"]).dropna().mean()
            if profit_margin > 0.15:
                score += 20
            elif profit_margin > 0.10:
                score += 15
            elif profit_margin > 0.05:
                score += 10

        # 市场认可度 (简化为PE合理性)
        if "pe_ratio" in financial_data.columns:
            avg_pe = financial_data["pe_ratio"].dropna().mean()
            if 15 <= avg_pe <= 30:
                score += 30
            elif 10 <= avg_pe <= 40:
                score += 20

    except Exception as e:
        print(f"Error calculating leadership: {e}")

    return min(score, 100)


def _calculate_canslim_institutional_sponsorship(self, data: pd.DataFrame) -> float:
    """计算CAN SLIM机构赞助"""
    # 简化为财务稳定性和增长性
    score = 0

    try:
        # 盈利稳定性
        if "net_profit" in data.columns:
            profit_std = data["net_profit"].dropna().std()
            profit_mean = data["net_profit"].dropna().mean()

            if profit_mean > 0:
                cv = profit_std / profit_mean
                if cv < 0.3:
                    score += 40
                elif cv < 0.5:
                    score += 30
                elif cv < 0.8:
                    score += 20

        # 机构偏好 (简化为ROE)
        if "roe" in data.columns:
            avg_roe = data["roe"].dropna().mean()
            if avg_roe > 0.15:
                score += 35
            elif avg_roe > 0.10:
                score += 25
            elif avg_roe > 0.05:
                score += 15

        # 现金流稳定性
        if "cash_flow" in data.columns:
            cf_positive_ratio = (data["cash_flow"] > 0).sum() / len(data)
            score += cf_positive_ratio * 25

    except Exception as e:
        print(f"Error calculating institutional sponsorship: {e}")

    return min(score, 100)


def _calculate_canslim_market_direction(self, data: pd.DataFrame) -> float:
    """计算CAN SLIM市场方向"""
    score = 50  # 中性开始

    try:
        if not data.empty and len(data) >= 20:
            # 市场趋势
            market_trend = data["close"].pct_change(20).iloc[-1]
            if market_trend > 0.10:
                score += 25
            elif market_trend > 0.05:
                score += 15
            elif market_trend < -0.05:
                score -= 15
            elif market_trend < -0.10:
                score -= 25

            # 市场波动率
            market_volatility = data["close"].pct_change().std() * np.sqrt(252)
            if market_volatility < 0.20:
                score += 15  # 低波动有利于个股表现
            elif market_volatility > 0.40:
                score -= 15  # 高波动增加风险

            # 个股相对强度
            # 简化为个股表现
            relative_strength = data["close"].pct_change(10).iloc[-1]
            if relative_strength > 0.08:
                score += 10
            elif relative_strength < -0.08:
                score -= 10

    except Exception as e:
        print(f"Error calculating market direction: {e}")

    return max(0, min(100, score))


def _get_canslim_recommendation(self, score: float) -> str:
    """获取CAN SLIM模型投资建议"""
    if score >= self.model_thresholds["strong_buy"]:
        return "强烈推荐买入 - 完全符合CAN SLIM标准"
    elif score >= self.model_thresholds["buy"]:
        return "推荐买入 - 大部分符合CAN SLIM标准"
    elif score >= self.model_thresholds["hold"]:
        return "谨慎观望 - 部分符合CAN SLIM标准"
    elif score >= self.model_thresholds["sell"]:
        return "建议卖出 - 不符合CAN SLIM标准"
    else:
        return "强烈建议卖出 - 严重不符合CAN SLIM标准"


