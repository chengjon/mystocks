"""
股票基础信息同步脚本
从数据源获取股票基础信息并同步到数据库
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from scripts.data_sync.base_data_source import BaseDataSource
from src.data_access.postgresql_access import PostgreSQLDataAccess
import pandas as pd

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/data_sync/stock_basic_sync.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def sync_stock_basic_info(full_sync: bool = False):
    """
    同步股票基础信息

    Args:
        full_sync: 是否执行全量同步（默认增量同步）
    """
    logger.info("开始同步股票基础信息")
    logger.info(f"同步模式: {'全量同步' if full_sync else '增量同步'}")

    try:
        # 初始化数据源和数据库访问
        data_source = BaseDataSource()
        db_access = PostgreSQLDataAccess()

        # 从数据源获取股票基础信息
        logger.info("正在从数据源获取股票基础信息...")
        stock_info_list = data_source.get_stock_basic_info()
        logger.info(f"从数据源获取到 {len(stock_info_list)} 条股票信息")

        # 获取行业信息（可选）
        try:
            industry_info_list = data_source.get_stock_industry_info()
            # 将行业信息映射到股票信息
            industry_map = {
                info["symbol"]: info["industry"] for info in industry_info_list
            }
            logger.info(f"获取到 {len(industry_info_list)} 条行业信息")
        except Exception as e:
            logger.warning(f"获取行业信息失败: {e}")
            industry_map = {}

        # 准备数据
        for stock_info in stock_info_list:
            # 添加行业信息（如果有的话）
            if stock_info["symbol"] in industry_map:
                stock_info["industry"] = industry_map[stock_info["symbol"]]

        # 转换为DataFrame
        df = pd.DataFrame(stock_info_list)

        # 如果有行业信息，使用行业信息更新DataFrame
        if industry_map:
            df["industry"] = df["symbol"].map(industry_map).fillna(df["industry"])

        # 处理数据格式
        if "list_date" in df.columns:
            # 将空字符串或None替换为默认值
            df["list_date"] = df["list_date"].replace("", None)

        # 增量同步逻辑
        if not full_sync:
            # 查询数据库中已有的股票代码
            try:
                existing_stocks_df = db_access.query("symbols_info", columns=["symbol"])
                existing_symbols = (
                    set(existing_stocks_df["symbol"].tolist())
                    if not existing_stocks_df.empty
                    else set()
                )
                logger.info(f"数据库中已有 {len(existing_symbols)} 只股票")

                # 过滤出新增的股票
                new_stocks_df = df[~df["symbol"].isin(existing_symbols)]
                logger.info(f"新增股票数: {len(new_stocks_df)}")

                # 过滤出可能需要更新的股票
                existing_stocks_df = df[df["symbol"].isin(existing_symbols)]
                logger.info(f"需要检查更新的股票数: {len(existing_stocks_df)}")

                # 对于已存在的股票，我们简单地执行upsert操作
                if not df.empty:
                    # 使用upsert操作更新数据（只更新存在的字段）
                    try:
                        rows_affected = db_access.upsert_dataframe(
                            table_name="symbols_info",
                            df=df,
                            conflict_columns=["symbol"],
                            update_columns=[
                                "name",
                                "industry",
                                "area",
                                "market",
                                "list_date",
                            ],
                        )
                        logger.info(f"成功同步 {rows_affected} 条股票记录到数据库")
                    except Exception as e:
                        logger.error(f"使用upsert同步股票信息失败: {e}")
                        # 如果upsert失败，尝试使用insert_dataframe
                        try:
                            rows_inserted = db_access.insert_dataframe(
                                "symbols_info", df
                            )
                            logger.info(f"成功插入 {rows_inserted} 条股票记录到数据库")
                        except Exception as insert_error:
                            logger.error(f"插入股票信息也失败: {insert_error}")
                            raise insert_error
                else:
                    logger.info("没有需要同步的股票数据")
            except Exception as e:
                logger.error(f"查询数据库中已有股票失败: {e}")
                # 如果查询失败，执行全量插入（可能有风险）
                logger.warning("执行全量插入（可能存在重复数据）")
                if not df.empty:
                    rows_inserted = db_access.insert_dataframe("symbols_info", df)
                    logger.info(f"成功插入 {rows_inserted} 条股票记录到数据库")
        else:
            # 全量同步 - 直接替换所有数据
            logger.info("执行全量同步，清空现有数据后重新插入")
            try:
                # 清空表数据
                db_access.delete("symbols_info", "1=1")
                logger.info("已清空symbols_info表")

                # 插入新数据
                if not df.empty:
                    rows_inserted = db_access.insert_dataframe("symbols_info", df)
                    logger.info(f"成功插入 {rows_inserted} 条股票记录到数据库")
            except Exception as e:
                logger.error(f"全量同步失败: {e}")
                raise e

        # 统计信息
        total_count = len(df)
        logger.info(f"同步完成 - 总股票数: {total_count}")

        # 记录统计信息
        stats = {
            "total_count": total_count,
            "sync_time": datetime.now().isoformat(),
            "sync_mode": "full" if full_sync else "incremental",
        }

        return stats

    except Exception as e:
        logger.error(f"同步股票基础信息失败: {e}")
        raise e


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="股票基础信息同步脚本")
    parser.add_argument(
        "--full", action="store_true", help="执行全量同步（默认增量同步）"
    )

    args = parser.parse_args()

    # 确保日志目录存在
    os.makedirs("logs/data_sync", exist_ok=True)

    try:
        stats = sync_stock_basic_info(full_sync=args.full)
        logger.info(f"股票基础信息同步完成: {stats}")
        print(f"股票基础信息同步完成: {stats}")
    except Exception as e:
        logger.error(f"股票基础信息同步失败: {e}")
        print(f"股票基础信息同步失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
