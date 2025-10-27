"""
Fund Flow Data Crawler
资金流向数据采集

功能：
1. 从东方财富网 API 获取行业资金流向数据
2. 保存数据到 PostgreSQL 的 market_fund_flow 表
3. 支持多种行业分类标准 (csrc, sw_l1, sw_l2)
4. 自动去重和更新

数据源：东方财富网 - 数据中心 - 资金流向 - 板块资金流
API: http://push2.eastmoney.com/api/qt/clist/get
"""

import requests
import logging
import json
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


class FundFlowCrawler:
    """行业资金流向爬虫"""

    def __init__(self):
        self.base_url = "http://push2.eastmoney.com/api/qt/clist/get"
        self.timeout = 10

        # 行业分类类型映射
        self.sector_type_map = {
            "csrc": "2",      # 证监会行业分类
            "sw_l1": "3",     # 申万一级行业
            "sw_l2": "1",     # 申万二级行业 (概念板块作为替代)
        }

    def fetch_fund_flow_data(self, industry_type: str = "csrc") -> List[Dict[str, Any]]:
        """
        从东方财富网获取行业资金流向数据

        Args:
            industry_type: 行业分类标准 (csrc/sw_l1/sw_l2)

        Returns:
            资金流向数据列表
        """
        if industry_type not in self.sector_type_map:
            logger.error(f"Invalid industry_type: {industry_type}")
            return []

        # 使用"今日"数据的字段映射
        params = {
            "pn": 1,  # page number
            "pz": 500,  # page size
            "po": "1",
            "np": "1",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
            "fltt": "2",
            "invt": "2",
            "fid0": "f62",  # 按主力净流入排序
            "fs": f"m:90 t:{self.sector_type_map[industry_type]}",  # 板块类型
            "stat": "1",  # 今日
            "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            logger.info(f"Fetching fund flow data for industry_type={industry_type}")
            response = requests.get(self.base_url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            # API 可能返回 JSONP 格式，需要提取 JSON
            text_data = response.text
            if "jQuery" in text_data or "(" in text_data:
                # 提取 JSON: jQuery...({...})
                json_str = text_data[text_data.find("{") : text_data.rfind("}")+1]
                data_json = json.loads(json_str)
            else:
                data_json = response.json()

            if data_json.get("data") and data_json["data"].get("diff"):
                records = data_json["data"]["diff"]
                logger.info(f"Fetched {len(records)} fund flow records for {industry_type}")
                return records
            else:
                logger.warning(f"No fund flow data for {industry_type}: {data_json.get('message')}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed for {industry_type}: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch fund flow data for {industry_type}: {e}")
            return []

    def save_to_postgresql(self, data_list: List[Dict[str, Any]], industry_type: str, trade_date: str) -> int:
        """
        保存资金流向数据到 PostgreSQL

        Args:
            data_list: 资金流向数据列表
            industry_type: 行业分类标准
            trade_date: 交易日期

        Returns:
            成功保存的记录数
        """
        if not data_list:
            logger.info(f"No fund flow data to save for {industry_type} on {trade_date}")
            return 0

        session = get_postgresql_session()

        try:
            # 先删除当天同类型的旧数据
            delete_query = text(
                "DELETE FROM market_fund_flow WHERE trade_date = :trade_date AND industry_type = :industry_type"
            )
            result = session.execute(delete_query, {"trade_date": trade_date, "industry_type": industry_type})
            deleted_count = result.rowcount
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} old records for {trade_date} ({industry_type})")

            # 插入新数据
            insert_query = text("""
                INSERT INTO market_fund_flow
                (trade_date, industry_code, industry_name, industry_type,
                 net_inflow, main_inflow, retail_inflow, total_inflow, total_outflow)
                VALUES
                (:trade_date, :industry_code, :industry_name, :industry_type,
                 :net_inflow, :main_inflow, :retail_inflow, :total_inflow, :total_outflow)
            """)

            saved_count = 0
            for item in data_list:
                try:
                    # 字段映射：东方财富网字段 -> PostgreSQL 字段
                    main_net_inflow = item.get("f62", 0) or 0  # 主力净流入
                    retail_net_inflow = item.get("f84", 0) or 0  # 小单净流入

                    # 计算总流入和总流出（简化计算，基于净额）
                    # 主力净流入 = 主力流入 - 主力流出
                    # 如果净流入>0，流入 = 净流入，流出 = 0
                    # 如果净流入<0，流入 = 0，流出 = abs(净流入)
                    total_inflow = max(main_net_inflow, 0)
                    total_outflow = abs(min(main_net_inflow, 0))

                    params = {
                        "trade_date": trade_date,
                        "industry_code": item.get("f12"),  # 代码
                        "industry_name": item.get("f14"),  # 名称
                        "industry_type": industry_type,
                        "net_inflow": main_net_inflow,  # 主力净流入
                        "main_inflow": main_net_inflow,  # 主力净流入
                        "retail_inflow": retail_net_inflow,  # 小单净流入
                        "total_inflow": total_inflow,
                        "total_outflow": total_outflow,
                    }

                    session.execute(insert_query, params)
                    session.commit()  # Commit immediately after each insert
                    saved_count += 1

                except Exception as e:
                    session.rollback()  # Rollback only this insert
                    error_msg = str(e)
                    # 忽略唯一约束冲突
                    if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
                        logger.debug(f"Skipping duplicate record {item.get('f12')}")
                    else:
                        logger.error(f"Failed to save record {item.get('f12')}: {e}")
                    continue

            logger.info(f"✅ Successfully saved {saved_count} fund flow records for {trade_date} ({industry_type})")
            return saved_count

        except Exception as e:
            session.rollback()
            logger.error(f"Transaction failed for {trade_date} ({industry_type}): {e}")
            return 0

        finally:
            session.close()

    def run_daily_crawler(self, industry_types: List[str] = None) -> Dict[str, int]:
        """
        每日执行的爬虫任务（获取今日数据）

        Args:
            industry_types: 要爬取的行业分类列表，默认 ["csrc"]

        Returns:
            每个行业分类保存记录数的字典
        """
        if industry_types is None:
            industry_types = ["csrc"]  # 默认只爬取证监会行业分类

        logger.info("Starting daily fund flow crawler")
        trade_date = datetime.now().strftime("%Y-%m-%d")

        results = {}
        for industry_type in industry_types:
            # 获取数据
            data_list = self.fetch_fund_flow_data(industry_type)

            # 保存数据
            saved_count = self.save_to_postgresql(data_list, industry_type, trade_date)
            results[industry_type] = saved_count

        # 输出总结
        total_records = sum(results.values())
        logger.info(f"Crawling completed. Total records saved: {total_records}")
        logger.info(f"Breakdown: {results}")

        return results


def main():
    """主函数：测试爬虫"""
    crawler = FundFlowCrawler()

    # 爬取证监会行业分类的资金流向数据
    results = crawler.run_daily_crawler(industry_types=["csrc"])

    print("\n" + "="*50)
    print("资金流向数据采集完成")
    print("="*50)
    for industry_type, count in results.items():
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {industry_type}: {count} records")
    print("="*50)


if __name__ == "__main__":
    main()
