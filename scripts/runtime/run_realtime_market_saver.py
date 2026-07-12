#!/usr/bin/env python3
"""MyStocks 沪深市场A股实时数据保存系统 - Saga事务版
通过customer_adapter统一管理efinance数据获取，按自动路由保存到PostgreSQL + TDengine
支持跨库分布式事务保证数据一致性

执行说明：
# 使用Saga事务（默认）
python run_realtime_market_saver.py [--interval 60] [--count 1]

# 禁用Saga，使用传统模式
python run_realtime_market_saver.py --no-saga

# 仅测试适配器
python run_realtime_market_saver.py --test-adapter

作者: MyStocks项目组
日期: 2025-09-24
更新: 2026-01-03 (Saga事务集成)
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime


# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 导入MyStocks核心模块
# 导入改进的customer适配器
from src.adapters.customer_adapter import CustomerDataSource
from src.core.data_classification import DataClassification
from src.core.data_manager import DataManager
from src.unified_manager import MyStocksUnifiedManager


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("realtime_market_saver.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


def create_metadata_callback(timestamp: str):
    """创建元数据更新回调函数（用于Saga事务）

    Args:
        timestamp: 时间戳字符串

    Returns:
        Callable: 元数据更新回调函数

    """

    def metadata_update_func(pg_session):
        """更新PostgreSQL中的实时行情元数据表

        Args:
            pg_session: PostgreSQL session对象

        """
        try:
            # 这里可以更新实时行情的元数据
            logger.debug(f"更新实时行情元数据: timestamp={timestamp}")
            # 实际SQL示例:
            # pg_session.execute(
            #     "UPDATE realtime_quotes_metadata SET last_update_time = NOW() "
            #     "WHERE snapshot_time = :timestamp",
            #     {"timestamp": timestamp}
            # )
        except Exception as e:
            logger.error(f"更新元数据失败: {e}")
            raise

    return metadata_update_func


def get_realtime_market_data_via_adapter():
    """使用customer_adapter获取沪深A股实时行情数据"""
    logger = logging.getLogger(__name__)

    try:
        logger.info("📊 初始化Customer适配器...")

        # 创建customer适配器实例，启用列名标准化
        adapter = CustomerDataSource(use_column_mapping=True)

        logger.info("📈 开始获取沪深A股实时行情数据...")

        # 使用专门的方法获取市场实时行情
        data = adapter.get_market_realtime_quotes()

        if data is None or data.empty:
            logger.warning("⚠️ 未获取到实时行情数据")
            return None

        logger.info(f"✅ 成功获取 {len(data)} 只股票的实时行情数据")
        logger.info(f"📋 数据列名: {list(data.columns)}")

        return data

    except Exception as e:
        logger.error(f"❌ 通过customer_adapter获取实时行情数据失败: {e!s}")
        return None


def save_to_auto_routing(data, manager, use_saga=True):
    """使用自动路由保存数据到合适的数据库（支持Saga事务）

    Args:
        data: 实时行情数据
        manager: MyStocks统一管理器
        use_saga: 是否使用Saga分布式事务（默认True）

    Returns:
        bool: 保存是否成功

    """
    logger = logging.getLogger(__name__)

    try:
        # 实时行情数据使用INDEX_QUOTES分类
        # 这样避免了与日线数据的字段冲突问题
        classification = DataClassification.INDEX_QUOTES  # 使用指数行情分类

        target_db = DataManager().get_target_database(classification)
        logger.info("🎯 使用自动路由保存数据")
        logger.info(f"📊 数据分类: {classification.value}")
        logger.info(f"📍 目标数据库: {target_db.value}")
        logger.info(f"🔄 事务模式: {'Saga分布式事务' if use_saga else '传统事务'}")

        # 获取当前时间戳作为元数据
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if use_saga:
            # 创建元数据回调函数
            metadata_callback = create_metadata_callback(timestamp)

            # 使用Saga事务保存数据
            success = manager.save_data_by_classification(
                data=data,
                classification=classification,
                table_name="realtime_market_quotes",
                use_saga=True,
                metadata_callback=metadata_callback,
            )

            if success:
                logger.info(f"✅ Saga事务成功: {len(data)} 条实时行情数据到 {target_db.value}")
            else:
                logger.warning("⚠️ Saga事务失败，已触发补偿机制")
        else:
            # 传统模式（不使用Saga）
            success = manager.save_data_by_classification(
                data=data,
                classification=classification,
                table_name="realtime_market_quotes",
            )

            if success:
                logger.info(f"✅ 成功保存 {len(data)} 条实时行情数据到 {target_db.value}")
            else:
                logger.error("❌ 保存实时行情数据失败")

        return success

    except Exception as e:
        logger.error(f"❌ 自动路由保存数据时出错: {e!s}")
        return False


def run_single_fetch_and_save(use_saga=True):
    """执行单次数据获取和保存（支持Saga事务）

    Args:
        use_saga: 是否使用Saga分布式事务（默认True）

    Returns:
        bool: 执行是否成功

    """
    logger = logging.getLogger(__name__)

    try:
        # 初始化统一管理器
        logger.info("🔧 初始化MyStocks统一管理器...")
        manager = MyStocksUnifiedManager()

        # 获取实时数据
        data = get_realtime_market_data_via_adapter()

        if data is not None:
            # 保存数据
            success = save_to_auto_routing(data, manager, use_saga=use_saga)
            return success
        logger.error("❌ 未能获取到数据，跳过保存")
        return False

    except Exception as e:
        logger.error(f"❌ 执行过程中出现错误: {e!s}")
        return False


def main():
    """主启动函数"""
    print("=" * 70)
    print("🚀 MyStocks 沪深市场A股实时数据保存系统")
    print("📋 使用customer_adapter + efinance + 自动数据路由 → PostgreSQL")
    print("=" * 70)

    parser = argparse.ArgumentParser(
        description="MyStocks 沪深市场A股实时数据保存系统",
        epilog="""
数据流说明：
• customer_adapter → efinance.stock.get_realtime_quotes() → 获取实时行情
• 列名标准化 → 自动路由分类: DAILY_KLINE → PostgreSQL数据库
• 表名: realtime_market_quotes

更新策略：
• 实时获取：每次运行获取最新数据
• 增量更新：基于时间戳的增量保存
• 双库管理：efinance(主) + easyquotation(备)
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="数据获取间隔（秒），默认60秒",
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="运行次数，默认1次，-1表示持续运行",
    )

    parser.add_argument(
        "--test-adapter",
        action="store_true",
        help="仅测试customer_adapter是否正常工作",
    )

    parser.add_argument(
        "--no-saga",
        action="store_true",
        help="禁用Saga事务，使用传统模式",
    )

    args = parser.parse_args()

    # 设置日志
    logger = setup_logging()

    print("📋 配置参数:")
    print(f"  - 获取间隔: {args.interval}秒")
    print(f"  - 运行次数: {'持续运行' if args.count == -1 else f'{args.count}次'}")
    print(f"  - 测试模式: {'是' if args.test_adapter else '否'}")
    print(f"  - 事务模式: {'传统事务' if args.no_saga else 'Saga分布式事务'}")
    print("=" * 70)

    # 如果是测试模式
    if args.test_adapter:
        logger.info("🧪 进入测试模式，仅测试customer_adapter")
        data = get_realtime_market_data_via_adapter()
        if data is not None:
            print("✅ Customer适配器测试通过")
            print(f"📊 获取到数据: {len(data)}行")
            print(f"📋 列名: {list(data.columns)}")
        else:
            print("❌ Customer适配器测试失败")
        return

    # 正常运行模式
    run_count = 0
    success_count = 0
    use_saga = not args.no_saga  # 根据 --no-saga 参数决定是否使用 Saga

    try:
        while args.count == -1 or run_count < args.count:
            run_count += 1

            logger.info(f"🚀 开始第 {run_count} 次数据获取和保存...")
            logger.info(f"🔄 事务模式: {'Saga分布式事务' if use_saga else '传统事务'}")

            success = run_single_fetch_and_save(use_saga=use_saga)

            if success:
                success_count += 1
                logger.info(f"✅ 第 {run_count} 次执行成功")
            else:
                logger.error(f"❌ 第 {run_count} 次执行失败")

            # 如果不是最后一次，则等待间隔时间
            if args.count == -1 or run_count < args.count:
                logger.info(f"⏱️ 等待 {args.interval} 秒后进行下次获取...")
                time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info("🛑 用户中断，程序停止")
    except Exception as e:
        logger.error(f"❌ 程序执行过程中出现错误: {e!s}")

    finally:
        print("=" * 70)
        print("📊 执行统计:")
        print(f"  - 总运行次数: {run_count}")
        print(f"  - 成功次数: {success_count}")
        print(f"  - 失败次数: {run_count - success_count}")
        print(
            f"  - 成功率: {success_count / run_count * 100:.1f}%" if run_count > 0 else "  - 成功率: N/A",
        )
        print(f"  - 事务模式: {'Saga分布式事务' if use_saga else '传统事务'}")
        print("=" * 70)
        logger.info("🏁 程序执行完毕")


if __name__ == "__main__":
    main()
