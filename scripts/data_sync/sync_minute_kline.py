"""
分时线数据同步脚本 (并行优化版 + Saga事务)
从TDX适配器获取分时线数据并同步到数据库
使用并行处理提升同步性能，支持Saga分布式事务
"""

import sys
import os
import argparse
import logging
from datetime import datetime, timedelta
from typing import List
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from src.factories.data_source_factory import get_data_source
from src.core.data_classification import DataClassification
from src.unified_manager import MyStocksUnifiedManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/data_sync/minute_kline_sync.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# 线程锁用于保护共享资源
stats_lock = threading.Lock()


def create_metadata_callback(symbol: str, period: str, trade_date: str):
    """
    创建元数据更新回调函数（用于Saga事务）

    Args:
        symbol: 股票代码
        period: K线周期
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
            # 这里可以更新分钟K线的元数据
            logger.debug(f"更新元数据: symbol={symbol}, period={period}, date={trade_date}")
            # 实际SQL示例:
            # pg_session.execute(
            #     "UPDATE minute_kline_metadata SET last_sync_time = NOW() "
            #     "WHERE symbol = :symbol AND period = :period",
            #     {"symbol": symbol, "period": period}
            # )
        except Exception as e:
            logger.error(f"更新元数据失败: {e}")
            raise

    return metadata_update_func


def get_latest_trade_date() -> str:
    """
    获取最新交易日期

    Returns:
        str: 最新交易日期，格式为YYYY-MM-DD
    """
    # 获取当前日期
    today = datetime.now()

    # 如果是周末，返回最近的周五
    if today.weekday() >= 5:  # 5=Saturday, 6=Sunday
        days_back = today.weekday() - 4  # Friday is 4
        latest_date = today - timedelta(days=days_back)
    else:
        latest_date = today

    return latest_date.strftime("%Y-%m-%d")


def sync_single_stock_data(args):
    """
    同步单只股票的分时线数据（支持Saga事务）

    Args:
        args: (symbol, periods, trade_date, data_source, manager, use_saga)

    Returns:
        dict: 同步结果统计
    """
    symbol, periods, trade_date, data_source, manager, use_saga = args

    # 提取纯股票代码（去除市场后缀）
    pure_symbol = symbol.split(".")[0] if "." in symbol else symbol

    logger.info(f"正在同步股票 {symbol} ({pure_symbol}) 的分时线数据...")
    logger.info(f"事务模式: {'Saga分布式事务' if use_saga else '传统事务'}")

    total_records = 0
    successful_periods = 0
    failed_periods = 0
    saga_success_count = 0
    saga_rollback_count = 0

    for period in periods:
        try:
            logger.info(f"  同步 {period} 周期数据...")

            # 从TDX适配器获取分钟K线数据
            kline_df = data_source.get_minute_kline(
                pure_symbol, period, trade_date, trade_date
            )

            if kline_df is None or kline_df.empty:
                logger.info(f"    股票 {symbol} 在 {trade_date} 没有 {period} 数据")
                continue

            logger.info(f"    获取到 {len(kline_df)} 条 {period} 数据")

            # 添加股票代码和周期信息
            kline_df["symbol"] = symbol
            kline_df["period"] = period

            # 确保数据类型正确
            if "date" in kline_df.columns:
                kline_df["date"] = pd.to_datetime(kline_df["date"])
            if "open" in kline_df.columns:
                kline_df["open"] = kline_df["open"].astype(float)
            if "high" in kline_df.columns:
                kline_df["high"] = kline_df["high"].astype(float)
            if "low" in kline_df.columns:
                kline_df["low"] = kline_df["low"].astype(float)
            if "close" in kline_df.columns:
                kline_df["close"] = kline_df["close"].astype(float)
            if "volume" in kline_df.columns:
                kline_df["volume"] = kline_df["volume"].astype(int)
            if "amount" in kline_df.columns:
                kline_df["amount"] = kline_df["amount"].astype(float)

            # 保存到数据库（TICK_DATA分类，自动路由到TDengine）
            table_name = (
                f"minute_kline_{period.replace('m', 'min').replace('h', 'hour')}"
            )

            if use_saga:
                # 创建元数据回调
                metadata_callback = create_metadata_callback(symbol, period, trade_date)

                # 使用Saga事务保存
                success = manager.save_data_by_classification(
                    DataClassification.TICK_DATA,
                    kline_df,
                    table_name,
                    use_saga=True,
                    metadata_callback=metadata_callback
                )

                if success:
                    logger.info(
                        f"    ✅ Saga事务成功: {len(kline_df)} 条 {period} 数据到 {table_name}"
                    )
                    saga_success_count += 1
                else:
                    logger.warning(f"    ⚠️ Saga事务失败: {period}")
                    saga_rollback_count += 1
            else:
                # 传统模式
                success = manager.save_data_by_classification(
                    DataClassification.TICK_DATA, kline_df, table_name
                )

            if success:
                total_records += len(kline_df)
                successful_periods += 1
            else:
                logger.error(f"    保存 {period} 数据失败")
                failed_periods += 1

        except Exception as e:
            logger.error(f"  同步股票 {symbol} {period} 数据失败: {e}")
            failed_periods += 1
            # 继续处理下一个周期
            continue

    return {
        "symbol": symbol,
        "total_records": total_records,
        "successful_periods": successful_periods,
        "failed_periods": failed_periods,
        "saga_success_count": saga_success_count if use_saga else 0,
        "saga_rollback_count": saga_rollback_count if use_saga else 0,
        "status": "success" if failed_periods == 0 else "partial",
    }


def sync_minute_kline_data(
    periods: List[str], stock_limit: int = None, max_workers: int = 10, use_saga: bool = True
):
    """
    同步分时线数据（并行优化版 + Saga事务）

    Args:
        periods: List[str] - 要同步的周期列表 (1m/5m/15m/30m/60m)
        stock_limit: int - 限制同步的股票数量（用于测试）
        max_workers: int - 最大并行线程数（默认10）
        use_saga: bool - 是否使用Saga分布式事务（默认启用）
    """
    logger.info(f"开始同步分时线数据，周期: {periods}，最大并行数: {max_workers}")
    logger.info(f"事务模式: {'Saga分布式事务' if use_saga else '传统事务'}")

    try:
        # 初始化数据源和统一管理器
        data_source = get_data_source()
        manager = MyStocksUnifiedManager()

        # 获取股票列表
        logger.info("正在获取股票列表...")
        # 使用统一管理器获取股票基础信息
        stock_df = manager.load_data_by_classification(
            DataClassification.SYMBOLS_INFO, "symbols_info"
        )

        if stock_df is None or stock_df.empty:
            logger.warning("数据库中没有股票信息，无法同步分时线数据")
            return

        symbols = stock_df["symbol"].tolist()
        if stock_limit:
            symbols = symbols[:stock_limit]

        logger.info(f"获取到 {len(symbols)} 只股票")

        # 获取最新交易日期
        trade_date = get_latest_trade_date()
        logger.info(f"同步日期: {trade_date}")

        # 统计信息
        total_records = 0
        successful_stocks = 0
        failed_stocks = 0
        total_periods = 0
        successful_periods = 0
        failed_periods = 0
        saga_success_count = 0
        saga_rollback_count = 0

        # 创建每只股票的处理参数（添加use_saga参数）
        stock_args = [
            (symbol, periods, trade_date, data_source, manager, use_saga) for symbol in symbols
        ]

        # 使用线程池进行并行处理
        logger.info(f"开始并行处理 {len(symbols)} 只股票...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_stock = {
                executor.submit(sync_single_stock_data, args): args[0]
                for args in stock_args
            }

            # 处理完成的任务
            for future in as_completed(future_to_stock):
                symbol = future_to_stock[future]
                try:
                    result = future.result()

                    # 更新统计信息
                    with stats_lock:
                        total_records += result["total_records"]
                        successful_periods += result["successful_periods"]
                        failed_periods += result["failed_periods"]

                        # Saga统计
                        if use_saga:
                            saga_success_count += result.get("saga_success_count", 0)
                            saga_rollback_count += result.get("saga_rollback_count", 0)

                        if result["status"] == "success":
                            successful_stocks += 1
                        else:
                            failed_stocks += 1

                        total_periods += (
                            result["successful_periods"] + result["failed_periods"]
                        )

                    logger.info(
                        f"股票 {symbol} 同步完成: {result['successful_periods']} 成功, {result['failed_periods']} 失败"
                    )

                except Exception as e:
                    stock = future_to_stock[future]
                    logger.error(f"股票 {stock} 同步过程中发生异常: {e}")
                    with stats_lock:
                        failed_stocks += 1
                        failed_periods += len(periods)

        # 统计信息
        stats = {
            "total_stocks": len(symbols),
            "successful_stocks": successful_stocks,
            "failed_stocks": failed_stocks,
            "total_periods": total_periods,
            "successful_periods": successful_periods,
            "failed_periods": failed_periods,
            "total_records": total_records,
            "saga_success_count": saga_success_count if use_saga else 0,
            "saga_rollback_count": saga_rollback_count if use_saga else 0,
            "sync_date": trade_date,
            "transaction_mode": "saga" if use_saga else "traditional",
        }

        logger.info(f"分时线数据同步完成: {stats}")

        # 如果使用Saga，输出额外的统计
        if use_saga and saga_success_count > 0:
            saga_success_rate = (saga_success_count / (saga_success_count + saga_rollback_count)) * 100
            logger.info(f"Saga事务成功率: {saga_success_rate:.2f}% ({saga_success_count}/{saga_success_count + saga_rollback_count})")

        return stats

    except Exception as e:
        logger.error(f"同步分时线数据失败: {e}")
        raise e


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="分时线数据同步脚本 (并行优化版 + Saga事务)")
    parser.add_argument(
        "--periods",
        nargs="+",
        default=["1m", "5m", "15m", "30m", "60m"],
        help="要同步的周期列表 (默认: 1m 5m 15m 30m 60m)",
    )
    parser.add_argument("--limit", type=int, help="限制同步的股票数量（用于测试）")
    parser.add_argument(
        "--max-workers", type=int, default=10, help="最大并行线程数 (默认: 10)"
    )
    parser.add_argument(
        "--no-saga", action="store_true", help="禁用Saga事务，使用传统模式"
    )

    args = parser.parse_args()

    # 确保日志目录存在
    os.makedirs("logs/data_sync", exist_ok=True)

    try:
        stats = sync_minute_kline_data(
            periods=args.periods,
            stock_limit=args.limit,
            max_workers=args.max_workers,
            use_saga=not args.no_saga
        )
        logger.info(f"✅ 分时线数据同步完成: {stats}")
        print(f"✅ 分时线数据同步完成: {stats}")
        return 0
    except Exception as e:
        logger.error(f"❌ 分时线数据同步失败: {e}")
        print(f"❌ 分时线数据同步失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
