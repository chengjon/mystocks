"""
股票策略尾部辅助定义。
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import pandas as pd


def create_low_atr_growth_strategy(base_strategy_cls):
    """构建低 ATR 成长策略类。"""

    class LowATRGrowthStrategy(base_strategy_cls):
        """
        策略10: 低ATR成长

        条件：
        1. 必须至少上市交易250日
        2. 最近10个交易日，最高收盘价/最低收盘价>1.1
        3. 最近10个交易日，平均每日涨跌幅(ATR)<10%
        """

        def __init__(self):
            super().__init__(
                name="low_atr_growth",
                name_cn="低ATR成长",
                description="ATR（平均真实波幅）较低但稳定增长",
            )

        def check(
            self,
            symbol: str,
            data: pd.DataFrame,
            date: Optional[datetime] = None,
            threshold: int = 10,
        ) -> bool:
            end_date = date.strftime("%Y-%m-%d") if date else None
            data = self.filter_date(data, end_date)

            if len(data) < 250:
                return False

            if "p_change" not in data.columns:
                data["p_change"] = data["close"].pct_change() * 100

            data = data.tail(n=threshold)
            if len(data) < threshold:
                return False

            highest_close = data["close"].max()
            lowest_close = data["close"].min()
            ratio = (highest_close - lowest_close) / lowest_close
            if ratio <= 1.1:
                return False

            total_change = data["p_change"].abs().sum()
            atr = total_change / len(data)
            return atr <= 10

    return LowATRGrowthStrategy
