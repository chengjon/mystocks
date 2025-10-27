"""
Chip Race Data Crawler
竞价抢筹数据采集

功能：
1. 从通达信 API 获取竞价抢筹数据 (早盘+尾盘)
2. 保存数据到 PostgreSQL 的 chip_race_data 表
3. 支持早盘抢筹 (period=0) 和尾盘抢筹 (period=1)
4. 自动去重和更新

数据源：通达信 - 竞价抢筹
API: http://excalc.icfqs.com:7616/TQLEX?Entry=HQServ.hq_nlp
Token: 6679f5cadca97d68245a086793fc1bfc0a50b487487c812f
"""

import requests
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy import text

from app.core.database import get_postgresql_session

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChipRaceCrawler:
    """竞价抢筹爬虫"""

    def __init__(self):
        self.base_url = "http://excalc.icfqs.com:7616/TQLEX?Entry=HQServ.hq_nlp"
        self.token = "6679f5cadca97d68245a086793fc1bfc0a50b487487c812f"
        self.timeout = 10

    def fetch_chip_race_data(self, period: int = 0, trade_date: str = None) -> List[Dict[str, Any]]:
        """
        从通达信 API 获取竞价抢筹数据

        Args:
            period: 0=早盘抢筹, 1=尾盘抢筹
            trade_date: 交易日期 (格式: YYYYMMDD)，None=今日

        Returns:
            竞价抢筹数据列表
        """
        params = [{
            "funcId": 20,
            "offset": 0,
            "count": 100,
            "sort": 1,  # 按抢筹委托金额排序
            "period": period,
            "Token": self.token,
            "modname": "JJQC"
        }]

        if trade_date:
            params[0]["date"] = trade_date

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 TdxW",
        }

        try:
            period_name = "早盘" if period == 0 else "尾盘"
            logger.info(f"Fetching chip race data for {period_name}")

            response = requests.post(self.base_url, json=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            data_json = response.json()

            if "datas" in data_json and data_json["datas"]:
                records = data_json["datas"]
                logger.info(f"Fetched {len(records)} {period_name} chip race records")
                return records
            else:
                logger.warning(f"No chip race data for {period_name}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed for period={period}: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch chip race data for period={period}: {e}")
            return []

    def save_to_postgresql(self, data_list: List[List], race_type: str, trade_date: str) -> int:
        """
        保存竞价抢筹数据到 PostgreSQL

        Args:
            data_list: 竞价抢筹数据列表 (from TDX API)
            race_type: "open" 或 "end"
            trade_date: 交易日期

        Returns:
            成功保存的记录数
        """
        if not data_list:
            logger.info(f"No chip race data to save for {race_type} on {trade_date}")
            return 0

        session = get_postgresql_session()

        try:
            # 先删除当天同类型的旧数据
            delete_query = text(
                "DELETE FROM chip_race_data WHERE trade_date = :trade_date AND race_type = :race_type"
            )
            result = session.execute(delete_query, {"trade_date": trade_date, "race_type": race_type})
            deleted_count = result.rowcount
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} old {race_type} records for {trade_date}")

            # 插入新数据
            insert_query = text("""
                INSERT INTO chip_race_data
                (symbol, name, trade_date, race_type,
                 latest_price, change_percent, prev_close, open_price, close_price,
                 race_amount, race_amplitude, race_commission, race_transaction, race_ratio,
                 bid_volume, ask_volume, net_volume, strength)
                VALUES
                (:symbol, :name, :trade_date, :race_type,
                 :latest_price, :change_percent, :prev_close, :open_price, :close_price,
                 :race_amount, :race_amplitude, :race_commission, :race_transaction, :race_ratio,
                 :bid_volume, :ask_volume, :net_volume, :strength)
            """)

            saved_count = 0
            for item in data_list:
                try:
                    # TDX API 返回格式：
                    # [代码, 名称, 昨收, 今开, 开盘金额/收盘金额, 抢筹幅度, 抢筹委托金额, 抢筹成交金额, 最新价, _]
                    symbol = item[0]
                    name = item[1]
                    prev_close = item[2] / 10000  # 昨收需要除以10000
                    open_price = item[3] / 10000  # 今开需要除以10000
                    race_amount = item[4]  # 开盘金额/收盘金额
                    race_amplitude = item[5] * 100  # 抢筹幅度转百分比
                    race_commission = item[6]  # 抢筹委托金额
                    race_transaction = item[7]  # 抢筹成交金额
                    latest_price = item[8]  # 最新价

                    # 计算字段
                    change_percent = round(((latest_price / prev_close) - 1) * 100, 2) if prev_close > 0 else 0
                    race_ratio = round((race_transaction / race_amount) * 100, 2) if race_amount > 0 else 0

                    params = {
                        "symbol": symbol,
                        "name": name,
                        "trade_date": trade_date,
                        "race_type": race_type,
                        "latest_price": latest_price,
                        "change_percent": change_percent,
                        "prev_close": prev_close,
                        "open_price": open_price,
                        "close_price": latest_price,  # 收盘价 = 最新价
                        "race_amount": race_amount,
                        "race_amplitude": race_amplitude,
                        "race_commission": race_commission,
                        "race_transaction": race_transaction,
                        "race_ratio": race_ratio,
                        # API 兼容字段
                        "bid_volume": int(race_commission),
                        "ask_volume": int(race_transaction),
                        "net_volume": int(race_commission - race_transaction),
                        "strength": race_ratio,
                    }

                    session.execute(insert_query, params)
                    session.commit()  # Commit immediately after each insert
                    saved_count += 1

                except Exception as e:
                    session.rollback()  # Rollback only this insert
                    error_msg = str(e)
                    # 忽略唯一约束冲突
                    if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
                        logger.debug(f"Skipping duplicate record {symbol}")
                    else:
                        logger.error(f"Failed to save record {symbol}: {e}")
                    continue

            logger.info(f"✅ Successfully saved {saved_count} {race_type} chip race records for {trade_date}")
            return saved_count

        except Exception as e:
            session.rollback()
            logger.error(f"Transaction failed for {trade_date} ({race_type}): {e}")
            return 0

        finally:
            session.close()

    def run_daily_crawler(self, race_types: List[str] = None) -> Dict[str, int]:
        """
        每日执行的爬虫任务（获取早盘和尾盘抢筹数据）

        Args:
            race_types: 要爬取的类型列表，默认 ["open", "end"]

        Returns:
            每个类型保存记录数的字典
        """
        if race_types is None:
            race_types = ["open", "end"]  # 默认爬取早盘和尾盘

        logger.info("Starting daily chip race crawler")
        trade_date = datetime.now().strftime("%Y-%m-%d")

        results = {}
        for race_type in race_types:
            period = 0 if race_type == "open" else 1

            # 获取数据
            data_list = self.fetch_chip_race_data(period=period)

            # 保存数据
            saved_count = self.save_to_postgresql(data_list, race_type, trade_date)
            results[race_type] = saved_count

        # 输出总结
        total_records = sum(results.values())
        logger.info(f"Crawling completed. Total records saved: {total_records}")
        logger.info(f"Breakdown: {results}")

        return results


def main():
    """主函数：测试爬虫"""
    crawler = ChipRaceCrawler()

    # 爬取早盘和尾盘抢筹数据
    results = crawler.run_daily_crawler()

    print("\n" + "="*50)
    print("竞价抢筹数据采集完成")
    print("="*50)
    for race_type, count in results.items():
        status = "✅" if count > 0 else "⚠️"
        type_name = "早盘抢筹" if race_type == "open" else "尾盘抢筹"
        print(f"{status} {type_name}: {count} records")
    print("="*50)


if __name__ == "__main__":
    main()
