import logging
from datetime import datetime, timedelta
from typing import List

logger = logging.getLogger(__name__)


def get_recent_trading_dates(days: int = 10) -> List[str]:
    """
    获取最近N个可能的交易日（粗略估计，排除周末）

    Args:
        days: 需要的交易日数量

    Returns:
        List[str]: 日期列表 (YYYY-MM-DD格式)
    """
    dates = []
    current_date = datetime.now()

    while len(dates) < days:
        # Skip weekends
        if current_date.weekday() < 5:  # Monday=0, Sunday=6
            dates.append(current_date.strftime("%Y-%m-%d"))
        current_date -= timedelta(days=1)

    return dates


def is_trading_day(date: datetime) -> bool:
    """
    判断给定日期是否为交易日（排除周末）。
    更精确的判断需要节假日数据。
    """
    return date.weekday() < 5  # Monday-Friday
