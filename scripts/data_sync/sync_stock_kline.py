"""
股票K线数据同步脚本
从数据源获取股票K线数据并同步到数据库
"""

import sys
import os
import argparse
import logging
from datetime import datetime, timedelta

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
        logging.FileHandler("logs/data_sync/stock_kline_sync.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def get_latest_trade_date_for_symbol(
    db_access: PostgreSQLDataAccess, symbol: str
) -> str:
    """
    获取指定股票在数据库中的最新交易日期

    Args:
        db_access: 数据库访问对象
        symbol: 股票代码

    Returns:
        最新交易日期，格式为YYYY-MM-DD
    """
    try:
        # 查询该股票的最新交易日期
        result_df = db_access.query(
            table_name="daily_kline",
            columns=["MAX(trade_date) as latest_date"],
            where=f"symbol = '{symbol}'",
        )

        if not result_df.empty and result_df.iloc[0]["latest_date"]:
            latest_date = result_df.iloc[0]["latest_date"]
            return latest_date.strftime("%Y-%m-%d")
        else:
            # 如果没有历史数据，返回一个较早的日期
            return "2020-01-01"
    except Exception as e:
        logger.warning(f"获取股票 {symbol} 最新交易日期失败: {e}")
        # 如果查询失败，返回一个较早的日期
        return "2020-01-01"


def sync_stock_kline_data(full_sync: bool = False):
    """
    同步股票K线数据

    Args:
        full_sync: 是否执行全量同步（默认增量同步）
    """
    logger.info("开始同步股票K线数据")
    logger.info(f"同步模式: {'全量同步' if full_sync else '增量同步'}")

    try:
        # 初始化数据源和数据库访问
        data_source = BaseDataSource()
        db_access = PostgreSQLDataAccess()

        # 获取所有股票代码
        logger.info("正在获取数据库中的股票列表...")
        stocks_df = db_access.query("symbols_info", columns=["symbol"])

        if stocks_df.empty:
            logger.warning("数据库中没有股票信息，无法同步K线数据")
            return

        symbols = stocks_df["symbol"].tolist()
        logger.info(f"获取到 {len(symbols)} 只股票")

        # 统计信息
        total_new_records = 0
        successful_stocks = 0
        failed_stocks = 0

        # 遍历每只股票同步K线数据
        for i, symbol in enumerate(symbols):
            try:
                logger.info(
                    f"[{i + 1}/{len(symbols)}] 正在同步股票 {symbol} 的K线数据..."
                )

                # 确定同步日期范围
                if full_sync:
                    # 全量同步：从2020-01-01开始
                    start_date = "2020-01-01"
                    end_date = datetime.now().strftime("%Y-%m-%d")
                    logger.info(f"全量同步: {start_date} 到 {end_date}")
                else:
                    # 增量同步：从数据库中该股票的最新日期开始
                    latest_date = get_latest_trade_date_for_symbol(db_access, symbol)
                    # 从最新日期的下一天开始同步
                    start_date_obj = datetime.strptime(
                        latest_date, "%Y-%m-%d"
                    ) + timedelta(days=1)
                    start_date = start_date_obj.strftime("%Y-%m-%d")
                    end_date = datetime.now().strftime("%Y-%m-%d")
                    logger.info(f"增量同步: {start_date} 到 {end_date}")

                # 如果开始日期大于结束日期，跳过
                if start_date > end_date:
                    logger.info(f"股票 {symbol} 已是最新数据，无需同步")
                    successful_stocks += 1
                    continue

                # 从数据源获取K线数据
                kline_data_list = data_source.get_stock_kline_data(
                    symbol, start_date, end_date
                )

                if not kline_data_list:
                    logger.info(f"股票 {symbol} 在指定日期范围内没有数据")
                    successful_stocks += 1
                    continue

                logger.info(f"获取到股票 {symbol} 的 {len(kline_data_list)} 条K线数据")

                # 转换为DataFrame
                df = pd.DataFrame(kline_data_list)

                # 确保数据类型正确
                if not df.empty:
                    df["trade_date"] = pd.to_datetime(df["trade_date"])
                    df["open"] = df["open"].astype(float)
                    df["high"] = df["high"].astype(float)
                    df["low"] = df["low"].astype(float)
                    df["close"] = df["close"].astype(float)
                    df["volume"] = df["volume"].astype(int)
                    df["amount"] = df["amount"].astype(float)

                    # 插入到数据库
                    rows_inserted = db_access.insert_dataframe("daily_kline", df)
                    logger.info(f"成功插入股票 {symbol} 的 {rows_inserted} 条K线数据")
                    total_new_records += rows_inserted
                    successful_stocks += 1
                else:
                    logger.info(f"股票 {symbol} 没有需要插入的数据")
                    successful_stocks += 1

            except Exception as e:
                logger.error(f"同步股票 {symbol} 的K线数据失败: {e}")
                failed_stocks += 1
                # 继续处理下一只股票
                continue

        # 统计信息
        stats = {
            "total_stocks": len(symbols),
            "successful_stocks": successful_stocks,
            "failed_stocks": failed_stocks,
            "total_new_records": total_new_records,
            "sync_time": datetime.now().isoformat(),
            "sync_mode": "full" if full_sync else "incremental",
        }

        logger.info(f"K线数据同步完成: {stats}")
        return stats

    except Exception as e:
        logger.error(f"同步股票K线数据失败: {e}")
        raise e


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="股票K线数据同步脚本")
    parser.add_argument(
        "--full", action="store_true", help="执行全量同步（默认增量同步）"
    )

    args = parser.parse_args()

    # 确保日志目录存在
    os.makedirs("logs/data_sync", exist_ok=True)

    try:
        stats = sync_stock_kline_data(full_sync=args.full)
        logger.info(f"股票K线数据同步完成: {stats}")
        print(f"股票K线数据同步完成: {stats}")
    except Exception as e:
        logger.error(f"股票K线数据同步失败: {e}")
        print(f"股票K线数据同步失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
