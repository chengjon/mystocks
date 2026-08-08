"""Tail helpers for `dcf_valuation.py`."""

import logging
from typing import Optional

import numpy as np
import pandas as pd

from src.advanced_analysis.financial_valuation_analyzer._dcf_valuation_models import (
    DCFValuation,
    RelativeValuation,
    ValuationConsensus,
)

logger = logging.getLogger(__name__)


class FinancialValuationAnalyzerTailMixin:
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
            logger.error("Error calculating valuation consensus: %s", e)
            return ValuationConsensus(
                dcf_valuation=current_price,
                relative_valuation=current_price,
                market_price=current_price,
                consensus_value=current_price,
                valuation_gap=0.0,
                confidence_score=0.5,
                recommendation="hold",
            )
