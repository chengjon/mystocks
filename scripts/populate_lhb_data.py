#!/usr/bin/env python3
"""
龙虎榜数据填充脚本

功能:
- 获取最近N个交易日的龙虎榜数据
- 通过API刷新端点填充数据
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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
            dates.append(current_date.strftime('%Y-%m-%d'))
        current_date -= timedelta(days=1)

    return dates


def refresh_lhb_for_date(date_str: str, base_url: str = "http://localhost:8000") -> dict:
    """
    刷新指定日期的龙虎榜数据

    Args:
        date_str: 交易日期 (YYYY-MM-DD)
        base_url: API基础URL

    Returns:
        dict: API响应结果
    """
    url = f"{base_url}/api/market/lhb/refresh"
    params = {"trade_date": date_str}

    try:
        response = requests.post(url, params=params, timeout=30)
        response.raise_for_status()
        result = response.json()

        if result.get("success"):
            logger.info(f"✅ {date_str}: {result.get('message', '成功')}")
        else:
            logger.warning(f"⚠️  {date_str}: {result.get('message', '失败')}")

        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ {date_str}: 请求失败 - {e}")
        return {"success": False, "message": str(e)}


def main():
    """主函数"""

    logger.info("=" * 60)
    logger.info("龙虎榜数据填充脚本")
    logger.info("=" * 60)

    # Get recent trading dates (last 10 days excluding weekends)
    dates = get_recent_trading_dates(days=10)
    logger.info(f"准备刷新最近 {len(dates)} 个交易日的龙虎榜数据")

    success_count = 0
    fail_count = 0

    for date_str in dates:
        logger.info(f"正在刷新 {date_str} 的龙虎榜数据...")
        result = refresh_lhb_for_date(date_str)

        if result.get("success"):
            success_count += 1
        else:
            fail_count += 1

    logger.info("=" * 60)
    logger.info(f"数据刷新完成: 成功 {success_count} 天, 失败 {fail_count} 天")
    logger.info("=" * 60)

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
