"""K 线 fallback 数据辅助函数。"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional


def build_fallback_kline(
    normalized_code: str,
    period: str,
    adjust: str,
    end_date: Optional[str] = None,
) -> dict:
    """Build deterministic fallback kline data for UI/runtime availability."""
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end_dt = datetime.now()

    points = []
    previous_close = 100.0
    count = 60
    start_dt = end_dt - timedelta(days=count - 1)

    for index in range(count):
        date_obj = start_dt + timedelta(days=index)
        trend = index * 0.08
        seasonal = ((index % 10) - 5) * 0.25
        close_price = round(max(1.0, 100 + trend + seasonal), 2)
        open_price = round(previous_close, 2)
        high_price = round(max(open_price, close_price) * 1.01, 2)
        low_price = round(min(open_price, close_price) * 0.99, 2)
        volume = 1_200_000 + index * 5_000
        amount = round(close_price * volume, 2)

        if previous_close > 0:
            amplitude = round(((high_price - low_price) / previous_close) * 100, 2)
            change_percent = round(((close_price - previous_close) / previous_close) * 100, 2)
        else:
            amplitude = 0.0
            change_percent = 0.0

        points.append(
            {
                "date": date_obj.strftime("%Y-%m-%d"),
                "timestamp": int(date_obj.timestamp()),
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": int(volume),
                "amount": amount,
                "amplitude": amplitude,
                "change_percent": change_percent,
            },
        )
        previous_close = close_price

    points.reverse()
    return {
        "stock_code": normalized_code,
        "stock_name": f"Fallback-{normalized_code.split('.', maxsplit=1)[0]}",
        "period": period,
        "adjust": adjust,
        "data": points,
        "count": len(points),
        "source": "fallback",
    }
