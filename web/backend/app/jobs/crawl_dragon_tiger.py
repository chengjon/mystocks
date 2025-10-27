"""
Dragon Tiger List Data Crawler
龙虎榜数据采集

功能：
1. 从东方财富网 API 获取龙虎榜数据
2. 保存数据到 PostgreSQL 的 dragon_tiger_list 表
3. 支持指定日期范围的数据采集
4. 自动去重和更新

数据源：东方财富网 - 数据中心 - 龙虎榜单
API: https://datacenter-web.eastmoney.com/api/data/v1/get
"""

import requests
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import text

from app.core.database import get_postgresql_session

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DragonTigerCrawler:
    """龙虎榜数据爬虫"""

    def __init__(self):
        self.base_url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        self.timeout = 10

    def fetch_dragon_tiger_data(self, trade_date: str) -> List[Dict[str, Any]]:
        """
        从东方财富网获取指定日期的龙虎榜数据

        Args:
            trade_date: 交易日期，格式 YYYY-MM-DD

        Returns:
            龙虎榜数据列表
        """
        params = {
            "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
            "columns": "ALL",
            "filter": f"(TRADE_DATE='{trade_date}')",
            "pageNumber": 1,
            "pageSize": 500,
            "sortColumns": "BILLBOARD_NET_AMT",
            "sortTypes": "-1",
            "source": "WEB"
        }

        try:
            logger.info(f"Fetching dragon tiger data for {trade_date}")
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if data.get("success") and data.get("result"):
                records = data["result"].get("data", [])
                logger.info(f"Fetched {len(records)} dragon tiger records for {trade_date}")
                return records
            else:
                logger.warning(f"No dragon tiger data for {trade_date}: {data.get('message')}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed for {trade_date}: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch dragon tiger data for {trade_date}: {e}")
            return []

    def save_to_postgresql(self, data_list: List[Dict[str, Any]], trade_date: str) -> int:
        """
        保存龙虎榜数据到 PostgreSQL

        Args:
            data_list: 龙虎榜数据列表
            trade_date: 交易日期

        Returns:
            成功保存的记录数
        """
        if not data_list:
            logger.info(f"No dragon tiger data to save for {trade_date}")
            return 0

        session = get_postgresql_session()

        try:
            # 先删除当天旧数据（保证数据更新）
            delete_query = text("DELETE FROM dragon_tiger_list WHERE trade_date = :trade_date")
            result = session.execute(delete_query, {"trade_date": trade_date})
            deleted_count = result.rowcount
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} old records for {trade_date}")

            # 插入新数据 - 使用实际的表字段名
            insert_query = text("""
                INSERT INTO dragon_tiger_list
                (symbol, stock_name, trade_date, reason, total_buy_amount, total_sell_amount, net_amount, detail_data)
                VALUES
                (:symbol, :stock_name, :trade_date, :reason, :total_buy_amount, :total_sell_amount, :net_amount, CAST(:detail_data AS jsonb))
            """)

            saved_count = 0
            for item in data_list:
                try:
                    # 字段映射：东方财富网字段 -> PostgreSQL 字段
                    # 将 close_price 和 change_percent 存储到 detail_data (jsonb) 中
                    detail_data = {
                        "close_price": item.get("CLOSE_PRICE"),
                        "change_percent": item.get("CHANGE_RATE"),
                        "reason_code": item.get("BOARD_CODE"),
                    }

                    params = {
                        "symbol": item.get("SECURITY_CODE"),
                        "stock_name": item.get("SECURITY_NAME_ABBR"),
                        "trade_date": trade_date,
                        "reason": item.get("EXPLANATION", ""),
                        "total_buy_amount": item.get("BILLBOARD_BUY_AMT", 0),
                        "total_sell_amount": item.get("BILLBOARD_SELL_AMT", 0),
                        "net_amount": item.get("BILLBOARD_NET_AMT", 0),
                        "detail_data": json.dumps(detail_data, ensure_ascii=False)
                    }

                    session.execute(insert_query, params)
                    session.commit()  # Commit immediately after each insert
                    saved_count += 1

                except Exception as e:
                    session.rollback()  # Rollback only this insert
                    error_msg = str(e)
                    # 忽略唯一约束冲突（同一股票可能有多个上榜原因）
                    if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
                        logger.debug(f"Skipping duplicate record {item.get('SECURITY_CODE')}")
                    else:
                        logger.error(f"Failed to save record {item.get('SECURITY_CODE')}: {e}")
                    continue

            logger.info(f"✅ Successfully saved {saved_count} dragon tiger records for {trade_date}")
            return saved_count

        except Exception as e:
            session.rollback()
            logger.error(f"Transaction failed for {trade_date}: {e}")
            return 0

        finally:
            session.close()

    def crawl_date_range(self, start_date: Optional[str] = None, end_date: Optional[str] = None, days: int = 3) -> Dict[str, int]:
        """
        爬取指定日期范围的龙虎榜数据

        Args:
            start_date: 开始日期 YYYY-MM-DD（可选）
            end_date: 结束日期 YYYY-MM-DD（可选）
            days: 如果未指定日期范围，则爬取最近 N 天的数据（默认 3 天）

        Returns:
            每日保存记录数的字典
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        if start_date is None:
            start_dt = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=days-1)
            start_date = start_dt.strftime("%Y-%m-%d")

        logger.info(f"Starting dragon tiger crawler for date range: {start_date} to {end_date}")

        results = {}
        current_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        while current_dt <= end_dt:
            trade_date = current_dt.strftime("%Y-%m-%d")

            # 获取数据
            data_list = self.fetch_dragon_tiger_data(trade_date)

            # 保存数据
            saved_count = self.save_to_postgresql(data_list, trade_date)
            results[trade_date] = saved_count

            # 移动到下一天
            current_dt += timedelta(days=1)

        # 输出总结
        total_records = sum(results.values())
        logger.info(f"Crawling completed. Total records saved: {total_records}")
        logger.info(f"Daily breakdown: {results}")

        return results

    def run_daily_crawler(self) -> Dict[str, int]:
        """
        每日执行的爬虫任务（爬取最近3天数据）

        Returns:
            每日保存记录数的字典
        """
        logger.info("Starting daily dragon tiger crawler")
        return self.crawl_date_range(days=3)


def main():
    """主函数：测试爬虫"""
    crawler = DragonTigerCrawler()

    # 爬取最近3天的数据
    results = crawler.run_daily_crawler()

    print("\n" + "="*50)
    print("龙虎榜数据采集完成")
    print("="*50)
    for date, count in results.items():
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {date}: {count} records")
    print("="*50)


if __name__ == "__main__":
    main()
