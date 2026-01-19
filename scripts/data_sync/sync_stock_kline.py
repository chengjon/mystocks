"""
股票K线数据同步脚本 (Saga事务版)
从数据源获取股票K线数据并同步到数据库
支持跨库分布式事务保证数据一致性
"""

import sys
import os
import argparse
import logging
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from scripts.data_sync.base_data_source import BaseDataSource
from src.unified_manager import MyStocksUnifiedManager
from src.core.data_classification import DataClassification
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
    manager: MyStocksUnifiedManager, symbol: str
) -> str:
    """
    获取指定股票在数据库中的最新交易日期

    Args:
        manager: MyStocks统一管理器
        symbol: 股票代码

    Returns:
        最新交易日期，格式为YYYY-MM-DD
    """
    try:
        # 查询该股票的最新交易日期
        result_df = manager.load_data_by_classification(
            classification=DataClassification.DAILY_KLINE,
            table_name="daily_kline",
            filters={"columns": ["MAX(trade_date) as latest_date"]},
        )

        # 手动添加WHERE条件（需要改进UnifiedManager的API）
        if not result_df.empty and "latest_date" in result_df.columns:
            # 应用symbol过滤
            filtered_df = result_df[result_df["symbol"] == symbol] if "symbol" in result_df.columns else result_df
            if not filtered_df.empty and filtered_df.iloc[0]["latest_date"]:
                latest_date = filtered_df.iloc[0]["latest_date"]
                return latest_date.strftime("%Y-%m-%d") if hasattr(latest_date, 'strftime') else str(latest_date)[:10]

        # 如果没有历史数据，返回一个较早的日期
        return "2020-01-01"
    except Exception as e:
        logger.warning(f"获取股票 {symbol} 最新交易日期失败: {e}")
        # 如果查询失败，返回一个较早的日期
        return "2020-01-01"


def create_metadata_callback(symbol: str, trade_date: str):
    """
    创建元数据更新回调函数（用于Saga事务）

    Args:
        symbol: 股票代码
        trade_date: 交易日期

    Returns:
        Callable: 元数据更新回调函数
    """
    def metadata_update_func(pg_session):
        """
        更新PostgreSQL中的元数据表

        Args:
            pg_session: PostgreSQL session对象
        """
        try:
            # 这里可以更新symbol的last_sync_time等元数据
            # 例如：UPDATE symbols_info SET last_sync_time = NOW() WHERE symbol = '...'
            logger.debug(f"更新元数据: symbol={symbol}, trade_date={trade_date}")
            # 实际SQL示例:
            # pg_session.execute(
            #     "UPDATE symbols_info SET last_sync_time = NOW() WHERE symbol = :symbol",
            #     {"symbol": symbol}
            # )
        except Exception as e:
            logger.error(f"更新元数据失败: {e}")
            raise

    return metadata_update_func


def sync_stock_kline_data(full_sync: bool = False, use_saga: bool = True):
    """
    同步股票K线数据（支持Saga分布式事务）

    Args:
        full_sync: 是否执行全量同步（默认增量同步）
        use_saga: 是否使用Saga事务（默认启用）
    """
    logger.info("开始同步股票K线数据")
    logger.info(f"同步模式: {'全量同步' if full_sync else '增量同步'}")
    logger.info(f"事务模式: {'Saga分布式事务' if use_saga else '传统事务'}")

    try:
        # 初始化统一管理器
        manager = MyStocksUnifiedManager()
        data_source = BaseDataSource()

        # 获取所有股票代码
        logger.info("正在获取数据库中的股票列表...")
        stocks_df = manager.load_data_by_classification(
            classification=DataClassification.REFERENCE_DATA,
            table_name="symbols_info",
            filters={"columns": ["symbol"]}
        )

        if stocks_df is None or stocks_df.empty:
            logger.warning("数据库中没有股票信息，无法同步K线数据")
            return

        symbols = stocks_df["symbol"].tolist()
        logger.info(f"获取到 {len(symbols)} 只股票")

        # 统计信息
        total_new_records = 0
        successful_stocks = 0
        failed_stocks = 0
        saga_success_count = 0
        saga_rollback_count = 0

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
                    latest_date = get_latest_trade_date_for_symbol(manager, symbol)
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

                    # 使用Saga事务保存数据
                    if use_saga:
                        # 创建元数据回调
                        metadata_callback = create_metadata_callback(symbol, start_date)

                        # 使用Saga协调器保存数据（TDengine + PG）
                        success = manager.save_data_by_classification(
                            classification=DataClassification.DAILY_KLINE,
                            data=df,
                            table_name="daily_kline",
                            use_saga=True,
                            metadata_callback=metadata_callback
                        )

                        if success:
                            logger.info(f"✅ Saga事务成功: {symbol} - {len(df)} 条K线数据")
                            saga_success_count += 1
                        else:
                            logger.warning(f"⚠️ Saga事务失败: {symbol}")
                            saga_rollback_count += 1
                    else:
                        # 传统模式（不使用Saga）
                        success = manager.save_data_by_classification(
                            classification=DataClassification.DAILY_KLINE,
                            data=df,
                            table_name="daily_kline"
                        )

                    if success:
                        total_new_records += len(df)
                        successful_stocks += 1
                    else:
                        failed_stocks += 1

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
            "saga_success_count": saga_success_count if use_saga else 0,
            "saga_rollback_count": saga_rollback_count if use_saga else 0,
            "sync_time": datetime.now().isoformat(),
            "sync_mode": "full" if full_sync else "incremental",
            "transaction_mode": "saga" if use_saga else "traditional",
        }

        logger.info(f"K线数据同步完成: {stats}")

        # 如果使用Saga，输出额外的统计
        if use_saga and saga_success_count > 0:
            saga_success_rate = (saga_success_count / (saga_success_count + saga_rollback_count)) * 100
            logger.info(f"Saga事务成功率: {saga_success_rate:.2f}% ({saga_success_count}/{saga_success_count + saga_rollback_count})")

        return stats

    except Exception as e:
        logger.error(f"同步股票K线数据失败: {e}")
        raise e


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="股票K线数据同步脚本 (Saga事务版)")
    parser.add_argument(
        "--full", action="store_true", help="执行全量同步（默认增量同步）"
    )
    parser.add_argument(
        "--no-saga", action="store_true", help="禁用Saga事务，使用传统模式"
    )

    args = parser.parse_args()

    # 确保日志目录存在
    os.makedirs("logs/data_sync", exist_ok=True)

    try:
        stats = sync_stock_kline_data(full_sync=args.full, use_saga=not args.no_saga)
        logger.info(f"股票K线数据同步完成: {stats}")
        print(f"✅ 股票K线数据同步完成: {stats}")
        return 0
    except Exception as e:
        logger.error(f"股票K线数据同步失败: {e}")
        print(f"❌ 股票K线数据同步失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
