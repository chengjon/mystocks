#!/usr/bin/env python3
"""
获取申万行业模拟数据 (用于开发测试)
Purpose: Fetch Shenwan industry data and create mock data for frontend
"""

import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ShenWanDataFetcher:
    """申万数据获取器"""

    def __init__(self):
        self.base_url = "http://push2.eastmoney.com/api/qt/clist/get"
        self.timeout = 10

        # 行业分类类型映射
        self.sector_type_map = {
            "sw_l1": "3",  # 申万一级行业
            "sw_l2": "1",  # 申万二级行业
        }

    def fetch_fund_flow_data(self, industry_type: str) -> List[Dict[str, Any]]:
        """获取资金流向数据"""
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
            "fid0": "f62",
            "fs": f"m:90 t:{self.sector_type_map[industry_type]}",
            "stat": "1",
            "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            logger.info(f"Fetching {industry_type} data...")
            response = requests.get(
                self.base_url, params=params, headers=headers, timeout=self.timeout
            )
            response.raise_for_status()

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
                logger.warning(f"⚠️ No data for {industry_type}")
                return []

        except Exception as e:
            logger.error(f"❌ Failed to fetch {industry_type}: {e}")
            return []

    def transform_to_api_format(
        self, data_list: List[Dict[str, Any]], industry_type: str, trade_date: str
    ) -> List[Dict[str, Any]]:
        """
        转换为API格式

        Returns:
            [
                {
                    "industry_name": "计算机",
                    "industry_type": "sw_l1",
                    "net_inflow": 18.5,  # 亿元
                    "main_inflow": 12.0,
                    "retail_inflow": 6.5,
                    "trade_date": "2025-10-30",
                    "total_inflow": 18.5,
                    "total_outflow": 0.0
                }
            ]
        """
        result = []
        for item in data_list:
            main_net_inflow = item.get("f62", 0) or 0
            retail_net_inflow = item.get("f84", 0) or 0

            # 转换为亿元
            net_inflow_yi = main_net_inflow / 100000000
            main_inflow_yi = main_net_inflow / 100000000
            retail_inflow_yi = retail_net_inflow / 100000000
            total_inflow_yi = max(main_net_inflow, 0) / 100000000
            total_outflow_yi = abs(min(main_net_inflow, 0)) / 100000000

            result.append(
                {
                    "industry_name": item.get("f14", ""),
                    "industry_type": industry_type,
                    "net_inflow": round(net_inflow_yi, 2),
                    "main_inflow": round(main_inflow_yi, 2),
                    "retail_inflow": round(retail_inflow_yi, 2),
                    "trade_date": trade_date,
                    "total_inflow": round(total_inflow_yi, 2),
                    "total_outflow": round(total_outflow_yi, 2),
                }
            )

        return result

    def fetch_all_shenwan_data(self) -> Dict[str, Any]:
        """
        获取所有申万数据

        Returns:
            {
                "sw_l1": [...],
                "sw_l2": [...]
            }
        """
        logger.info("=" * 60)
        logger.info("开始获取申万行业数据")
        logger.info("=" * 60)

        trade_date = datetime.now().strftime("%Y-%m-%d")
        results = {}

        for industry_type in ["sw_l1", "sw_l2"]:
            raw_data = self.fetch_fund_flow_data(industry_type)
            transformed_data = self.transform_to_api_format(
                raw_data, industry_type, trade_date
            )
            results[industry_type] = transformed_data

            logger.info(f"✅ {industry_type}: {len(transformed_data)} records")

        logger.info("=" * 60)
        logger.info(
            f"数据获取完成! 总计 {sum(len(v) for v in results.values())} 条记录"
        )
        logger.info("=" * 60)

        return results


def main():
    """主函数"""
    fetcher = ShenWanDataFetcher()
    data = fetcher.fetch_all_shenwan_data()

    # 保存到JSON文件
    output_file = (
        "/opt/claude/mystocks_spec/web/backend/app/data/shenwan_fund_flow_mock.json"
    )
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"\n✅ Mock data saved to: {output_file}")

    # 显示样例
    if data.get("sw_l1"):
        logger.info("\n📊 SW L1 样例 (前5条):")
        for item in data["sw_l1"][:5]:
            logger.info(f"  {item['industry_name']}: {item['net_inflow']}亿元")

    if data.get("sw_l2"):
        logger.info("\n📊 SW L2 样例 (前5条):")
        for item in data["sw_l2"][:5]:
            logger.info(f"  {item['industry_name']}: {item['net_inflow']}亿元")


if __name__ == "__main__":
    main()
