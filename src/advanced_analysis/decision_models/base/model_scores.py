"""
决策模型评分系统 - 数据类

包含所有投资模型的评分数据结构和计算方法
"""

from dataclasses import dataclass, field
from typing import Dict
from datetime import datetime


@dataclass
class ModelScoreConfig:
    """模型评分配置"""

    # 基本配置
    enable_weights: bool = True
    enable_filters: bool = True

    # 权重配置（总和 = 100）
    valuation_weight: float = 30.0  # 估值权重
    growth_weight: float = 40.0  # 成长权重
    quality_weight: float = 20.0  # 质量权重
    technical_weight: float = 10.0  # 技术权重

    # 评分范围
    min_score: float = 0.0
    max_score: float = 100.0


@dataclass
class ValuationScore:
    """估值评分"""

    pe_ratio: float = 0.0  # PE比率
    pb_ratio: float = 0.0  # PB比率
    ps_ratio: float = 0.0  # PS比率
    ev_ebitda: float = 0.0  # EV/EBITDA
    peg_ratio: float = 0.0  # PEG比率

    # 计算的评分
    score: float = 0.0
    rating: str = "N/A"
    percentile: float = 0.0  # 行业百分位

    def calculate_score(self, config: ModelScoreConfig) -> float:
        """计算估值评分"""
        # 简化的估值评分计算
        score = 0.0

        # PE比率评分（越低越好）
        if self.pe_ratio > 0:
            pe_score = max(0, 100 - self.pe_ratio)
            score += pe_score * config.valuation_weight / 100

        # PB比率评分（越低越好）
        if self.pb_ratio > 0:
            pb_score = max(0, 100 - self.pb_ratio)
            score += pb_score * config.valuation_weight / 100

        # 限制在0-100之间
        self.score = max(config.min_score, min(config.max_score, score))

        # 计算评级
        if self.score >= 80:
            self.rating = "A"
        elif self.score >= 60:
            self.rating = "B"
        elif self.score >= 40:
            self.rating = "C"
        else:
            self.rating = "D"

        return self.score


@dataclass
class GrowthScore:
    """成长评分"""

    revenue_growth: float = 0.0  # 营收增长率
    profit_growth: float = 0.0  # 利润增长率
    eps_growth: float = 0.0  # EPS增长率

    # 计算的评分
    score: float = 0.0
    rating: str = "N/A"
    trend: str = "stable"  # trend: rising, stable, declining

    def calculate_score(self, config: ModelScoreConfig) -> float:
        """计算成长评分"""
        score = 0.0

        # 营收增长率评分（越高越好）
        if self.revenue_growth > 0:
            revenue_score = min(100, self.revenue_growth * 2)
            score += revenue_score * config.growth_weight / 100

        # 利润增长率评分（越高越好）
        if self.profit_growth > 0:
            profit_score = min(100, self.profit_growth * 2)
            score += profit_score * config.growth_weight / 100

        # EPS增长率评分（越高越好）
        if self.eps_growth > 0:
            eps_score = min(100, self.eps_growth * 2)
            score += eps_score * config.growth_weight / 100

        # 限制在0-100之间
        self.score = max(config.min_score, min(config.max_score, score))

        # 计算趋势
        if self.score >= 70:
            self.trend = "rising"
        elif self.score >= 40:
            self.trend = "stable"
        else:
            self.trend = "declining"

        # 计算评级
        if self.score >= 80:
            self.rating = "A"
        elif self.score >= 60:
            self.rating = "B"
        elif self.score >= 40:
            self.rating = "C"
        else:
            self.rating = "D"

        return self.score


@dataclass
class QualityScore:
    """质量评分"""

    roe: float = 0.0  # 净资产收益率
    roa: float = 0.0  # 资产收益率
    gross_margin: float = 0.0  # 毛利率
    operating_margin: float = 0.0  # 营业利润率
    net_margin: float = 0.0  # 净利率

    # 计算的评分
    score: float = 0.0
    rating: str = "N/A"
    stability_score: float = 0.0  # 稳定性评分

    def calculate_score(self, config: ModelScoreConfig) -> float:
        """计算质量评分"""
        score = 0.0

        # ROE评分（越高越好）
        if self.roe > 0:
            roe_score = min(100, self.roe * 2)
            score += roe_score * config.quality_weight / 100

        # ROA评分（越高越好）
        if self.roa > 0:
            roa_score = min(100, self.roa * 2)
            score += roa_score * config.quality_weight / 100

        # 毛利率评分（越高越好）
        if self.gross_margin > 0:
            gross_score = min(100, self.gross_margin)
            score += gross_score * config.quality_weight / 100

        # 营业利润率评分（越高越好）
        if self.operating_margin > 0:
            operating_score = min(100, self.operating_margin)
            score += operating_score * config.quality_weight / 100

        # 净利率评分（越高越好）
        if self.net_margin > 0:
            net_score = min(100, self.net_margin)
            score += net_score * config.quality_weight / 100

        # 计算稳定性评分（基于各指标的一致性）
        metrics = [self.roe, self.roa, self.gross_margin, self.operating_margin, self.net_margin]
        valid_metrics = [m for m in metrics if m > 0]

        if valid_metrics:
            std_dev = (
                sum((m - sum(valid_metrics) / len(valid_metrics)) ** 2 for m in valid_metrics) / len(valid_metrics)
            ) ** 0.5
            self.stability_score = max(0, 100 - std_dev * 10)
            score += self.stability_score * config.quality_weight / 100

        # 限制在0-100之间
        self.score = max(config.min_score, min(config.max_score, score))

        # 计算评级
        if self.score >= 80:
            self.rating = "A"
        elif self.score >= 60:
            self.rating = "B"
        elif self.score >= 40:
            self.rating = "C"
        else:
            self.rating = "D"

        return self.score


@dataclass
class TechnicalScore:
    """技术分析评分"""

    ma_signal: str = "neutral"  # MA信号
    macd_signal: str = "neutral"  # MACD信号
    rsi_score: float = 0.0  # RSI评分
    bollinger_position: str = "neutral"  # 布林带位置

    # 计算的评分
    score: float = 0.0
    rating: str = "N/A"
    momentum_score: float = 0.0  # 动量评分

    def calculate_score(self, config: ModelScoreConfig) -> float:
        """计算技术评分"""
        score = 0.0

        # MA信号评分
        if self.ma_signal == "bullish":
            ma_score = 80
        elif self.ma_signal == "bearish":
            ma_score = 20
        else:
            ma_score = 50
        score += ma_score * config.technical_weight / 100

        # MACD信号评分
        if self.macd_signal == "bullish":
            macd_score = 80
        elif self.macd_signal == "bearish":
            macd_score = 20
        else:
            macd_score = 50
        score += macd_score * config.technical_weight / 100

        # RSI评分（基于超买超卖）
        if 0 <= self.rsi_score <= 30:
            rsi_score = 80  # 超卖，可能是买入机会
        elif 70 <= self.rsi_score <= 100:
            rsi_score = 20  # 超买，可能是卖出机会
        else:
            rsi_score = 50  # 中性
        score += rsi_score * config.technical_weight / 100

        # 布林带位置评分
        if self.bollinger_position == "upper":
            bollinger_score = 20
        elif self.bollinger_position == "lower":
            bollinger_score = 80
        else:
            bollinger_score = 50
        score += bollinger_score * config.technical_weight / 100

        # 限制在0-100之间
        self.score = max(config.min_score, min(config.max_score, score))

        # 计算评级
        if self.score >= 80:
            self.rating = "A"
        elif self.score >= 60:
            self.rating = "B"
        elif self.score >= 40:
            self.rating = "C"
        else:
            self.rating = "D"

        return self.score


@dataclass
class OverallModelScore:
    """综合模型评分"""

    stock_code: str = ""
    stock_name: str = ""

    # 各项评分
    valuation: ValuationScore = field(default_factory=ValuationScore)
    growth: GrowthScore = field(default_factory=GrowthScore)
    quality: QualityScore = field(default_factory=QualityScore)
    technical: TechnicalScore = field(default_factory=TechnicalScore)

    # 配置
    config: ModelScoreConfig = field(default_factory=ModelScoreConfig)

    # 综合评分
    overall_score: float = 0.0
    overall_rating: str = "N/A"
    percentile: float = 0.0  # 行业百分位

    # 时间戳
    calculated_at: datetime = field(default_factory=datetime.now)

    def calculate_overall_score(self) -> float:
        """计算综合评分"""
        # 计算各项评分
        valuation_score = self.valuation.calculate_score(self.config)
        growth_score = self.growth.calculate_score(self.config)
        quality_score = self.quality.calculate_score(self.config)
        technical_score = self.technical.calculate_score(self.config)

        # 综合评分（加权平均）
        self.overall_score = (
            valuation_score * self.config.valuation_weight / 100
            + growth_score * self.config.growth_weight / 100
            + quality_score * self.config.quality_weight / 100
            + technical_score * self.config.technical_weight / 100
        )

        # 计算综合评级
        if self.overall_score >= 80:
            self.overall_rating = "A"
        elif self.overall_score >= 60:
            self.overall_rating = "B"
        elif self.overall_score >= 40:
            self.overall_rating = "C"
        else:
            self.overall_rating = "D"

        # 更新时间戳
        self.calculated_at = datetime.now()

        return self.overall_score

    def get_score_breakdown(self) -> Dict:
        """获取评分明细"""
        return {
            "stock_code": self.stock_code,
            "stock_name": self.stock_name,
            "valuation": {
                "score": self.valuation.score,
                "rating": self.valuation.rating,
                "percentile": self.valuation.percentile,
            },
            "growth": {"score": self.growth.score, "rating": self.growth.rating, "trend": self.growth.trend},
            "quality": {
                "score": self.quality.score,
                "rating": self.quality.rating,
                "stability": self.quality.stability_score,
            },
            "technical": {
                "score": self.technical.score,
                "rating": self.technical.rating,
                "momentum": self.technical.momentum_score,
            },
            "overall": {
                "score": self.overall_score,
                "rating": self.overall_rating,
                "percentile": self.percentile,
                "calculated_at": self.calculated_at.isoformat(),
            },
        }
