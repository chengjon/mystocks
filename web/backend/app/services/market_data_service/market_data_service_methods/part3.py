"""MarketDataService 竞价抢筹查询方法集。"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from app.models.market_data import ChipRaceEndData, ChipRaceOpenData


class MarketDataServiceChipRaceQueryMixin:
    """竞价抢筹查询方法。"""

    def query_chip_race(
        self,
        race_type: str = "open",
        trade_date: Optional[date] = None,
        min_race_amount: Optional[float] = None,
        limit: int = 100,
    ) -> List:
        """查询竞价抢筹数据，默认返回最新可用数据。"""
        db = self.SessionLocal()
        try:
            chip_race_model = ChipRaceOpenData if race_type == "open" else ChipRaceEndData
            query = db.query(chip_race_model)

            if trade_date:
                query = query.filter(chip_race_model.date == trade_date)
            else:
                from sqlalchemy import func

                latest_date = db.query(func.max(chip_race_model.date)).scalar()
                if latest_date:
                    query = query.filter(chip_race_model.date == latest_date)

            if min_race_amount:
                query = query.filter(chip_race_model.deal_amount >= min_race_amount)

            return query.order_by(chip_race_model.deal_amount.desc()).limit(limit).all()

        finally:
            db.close()
