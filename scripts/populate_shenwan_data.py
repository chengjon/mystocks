#!/usr/bin/env python3
"""
申万行业资金流向数据采集脚本
Purpose: Fetch and save Shenwan (SW L1/L2) industry fund flow data
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../web/backend"))

import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ShenWanDataPopulator:
    """申万行业数据填充工具"""

    def __init__(self, db_url: str):
        """
        初始化

        Args:
            db_url: PostgreSQL连接URL
        """
        self.base_url = "http://push2.eastmoney.com/api/qt/clist/get"
        self.timeout = 10

        # 行业分类类型映射
        self.sector_type_map = {
            "sw_l1": "3",  # 申万一级行业
            "sw_l2": "1",  # 申万二级行业 (使用概念板块作为替代)
        }

        # 数据库连接
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def fetch_fund_flow_data(self, industry_type: str) -> List[Dict[str, Any]]:
        """
        从东方财富网获取行业资金流向数据

        Args:
            industry_type: sw_l1 或 sw_l2

        Returns:
            资金流向数据列表
        """
        if industry_type not in self.sector_type_map:
            logger.error(f"Invalid industry_type: {industry_type}")
            return []

        params = {
            "pn": 1,
            "pz": 500,
            "po": "1",
            "np": "1",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
            "fltt": "2",
            "invt": "2",
            "fid0": "f62",  # 按主力净流入排序
            "fs": f"m:90 t:{self.sector_type_map[industry_type]}",
            "stat": "1",  # 今日
            "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            logger.info(f"Fetching fund flow data for {industry_type}...")
            response = requests.get(
                self.base_url, params=params, headers=headers, timeout=self.timeout
            )
            response.raise_for_status()

            # 提取 JSON
            text_data = response.text
            if "jQuery" in text_data or "(" in text_data:
                json_str = text_data[text_data.find("{") : text_data.rfind("}") + 1]
                data_json = json.loads(json_str)
            else:
                data_json = response.json()

            if data_json.get("data") and data_json["data"].get("diff"):
                records = data_json["data"]["diff"]
                logger.info(f"✅ Fetched {len(records)} records for {industry_type}")
                return records
            else:
                logger.warning(f"⚠️ No data returned for {industry_type}")
                return []

        except Exception as e:
            logger.error(f"❌ Failed to fetch data for {industry_type}: {e}")
            return []

    def save_to_database(
        self, data_list: List[Dict[str, Any]], industry_type: str, trade_date: str
    ) -> int:
        """
        保存数据到PostgreSQL

        Args:
            data_list: 数据列表
            industry_type: sw_l1 或 sw_l2
            trade_date: 交易日期

        Returns:
            成功保存的记录数
        """
        if not data_list:
            logger.info(f"No data to save for {industry_type}")
            return 0

        session = self.Session()

        try:
            # 先删除当天同类型的旧数据
            delete_query = text(
                "DELETE FROM market_fund_flow WHERE trade_date = :trade_date AND industry_type = :industry_type"
            )
            result = session.execute(
                delete_query, {"trade_date": trade_date, "industry_type": industry_type}
            )
            deleted_count = result.rowcount
            session.commit()

            if deleted_count > 0:
                logger.info(
                    f"Deleted {deleted_count} old records for {trade_date} ({industry_type})"
                )

            # 插入新数据
            insert_query = text(
                """
                INSERT INTO market_fund_flow
                (trade_date, industry_code, industry_name, industry_type,
                 net_inflow, main_inflow, retail_inflow, total_inflow, total_outflow)
                VALUES
                (:trade_date, :industry_code, :industry_name, :industry_type,
                 :net_inflow, :main_inflow, :retail_inflow, :total_inflow, :total_outflow)
            """
            )

            saved_count = 0
            for item in data_list:
                try:
                    main_net_inflow = item.get("f62", 0) or 0
                    retail_net_inflow = item.get("f84", 0) or 0

                    total_inflow = max(main_net_inflow, 0)
                    total_outflow = abs(min(main_net_inflow, 0))

                    params = {
                        "trade_date": trade_date,
                        "industry_code": item.get("f12"),
                        "industry_name": item.get("f14"),
                        "industry_type": industry_type,
                        "net_inflow": main_net_inflow,
                        "main_inflow": main_net_inflow,
                        "retail_inflow": retail_net_inflow,
                        "total_inflow": total_inflow,
                        "total_outflow": total_outflow,
                    }

                    session.execute(insert_query, params)
                    session.commit()
                    saved_count += 1

                except Exception as e:
                    session.rollback()
                    error_msg = str(e)
                    if (
                        "unique constraint" not in error_msg.lower()
                        and "duplicate key" not in error_msg.lower()
                    ):
                        logger.debug(f"Skipping record {item.get('f12')}: {e}")
                    continue

            logger.info(
                f"✅ Saved {saved_count} records for {trade_date} ({industry_type})"
            )
            return saved_count

        except Exception as e:
            session.rollback()
            logger.error(
                f"❌ Transaction failed for {trade_date} ({industry_type}): {e}"
            )
            return 0

        finally:
            session.close()

    def populate_shenwan_data(self) -> Dict[str, int]:
        """
        填充申万行业数据

        Returns:
            每个分类保存的记录数
        """
        logger.info("=" * 60)
        logger.info("开始填充申万行业数据")
        logger.info("=" * 60)

        trade_date = datetime.now().strftime("%Y-%m-%d")
        results = {}

        for industry_type in ["sw_l1", "sw_l2"]:
            # 获取数据
            data_list = self.fetch_fund_flow_data(industry_type)

            # 保存数据
            saved_count = self.save_to_database(data_list, industry_type, trade_date)
            results[industry_type] = saved_count

        # 输出总结
        logger.info("=" * 60)
        logger.info("数据填充完成")
        logger.info("=" * 60)
        total_records = sum(results.values())
        logger.info(f"总计: {total_records} 条记录")
        for industry_type, count in results.items():
            status = "✅" if count > 0 else "⚠️"
            logger.info(f"{status} {industry_type}: {count} 条记录")
        logger.info("=" * 60)

        return results


def main():
    """主函数"""
    # 从环境变量获取数据库配置
    db_host = os.getenv("POSTGRESQL_HOST", "192.168.123.104")
    db_port = os.getenv("POSTGRESQL_PORT", "5438")
    db_user = os.getenv("POSTGRESQL_USER", "postgres")
    db_password = os.getenv("POSTGRESQL_PASSWORD", "c790414J")
    db_name = os.getenv("POSTGRESQL_DATABASE", "mystocks")

    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    try:
        populator = ShenWanDataPopulator(db_url)
        results = populator.populate_shenwan_data()

        # 返回状态码
        total = sum(results.values())
        return 0 if total > 0 else 1

    except Exception as e:
        logger.error(f"❌ Script failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
