#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 沪深市场A股实时数据保存系统 - 使用efinance和自动路由
通过customer_adapter统一管理efinance数据获取，按自动路由保存到PostgreSQL

执行说明：
python run_realtime_market_saver.py [--interval 60] [--count 1]

作者: MyStocks项目组
日期: 2025-09-24
"""

import os
import sys
import time
import argparse
import logging
import pandas as pd
from datetime import datetime

# 导入MyStocks核心模块
from src.core import DataClassification, DataStorageStrategy
from unified_manager import MyStocksUnifiedManager

# 导入改进的customer适配器
from src.adapters.customer_adapter import CustomerDataSource


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
        logger.error(f"❌ 通过customer_adapter获取实时行情数据失败: {str(e)}")
        return None


def save_to_auto_routing(data, manager):
    """使用自动路由保存数据到合适的数据库"""
    logger = logging.getLogger(__name__)

    try:
        # 实时行情数据使用INDEX_QUOTES分类
        # 这样避免了与日线数据的字段冲突问题
        classification = DataClassification.INDEX_QUOTES  # 使用指数行情分类

        target_db = DataStorageStrategy.get_target_database(classification)
        logger.info(f"🎯 使用自动路由保存数据")
        logger.info(f"📊 数据分类: {classification.value}")
        logger.info(f"📍 目标数据库: {target_db.value}")

        # 使用统一管理器保存数据
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
        logger.error(f"❌ 自动路由保存数据时出错: {str(e)}")
        return False


def run_single_fetch_and_save():
    """执行单次数据获取和保存"""
    logger = logging.getLogger(__name__)

    try:
        # 初始化统一管理器
        logger.info("🔧 初始化MyStocks统一管理器...")
        manager = MyStocksUnifiedManager()

        # 获取实时数据
        data = get_realtime_market_data_via_adapter()

        if data is not None:
            # 保存数据
            success = save_to_auto_routing(data, manager)
            return success
        else:
            logger.error("❌ 未能获取到数据，跳过保存")
            return False

    except Exception as e:
        logger.error(f"❌ 执行过程中出现错误: {str(e)}")
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
        "--interval", type=int, default=60, help="数据获取间隔（秒），默认60秒"
    )

    parser.add_argument(
        "--count", type=int, default=1, help="运行次数，默认1次，-1表示持续运行"
    )

    parser.add_argument(
        "--test-adapter", action="store_true", help="仅测试customer_adapter是否正常工作"
    )

    args = parser.parse_args()

    # 设置日志
    logger = setup_logging()

    print(f"📋 配置参数:")
    print(f"  - 获取间隔: {args.interval}秒")
    print(f"  - 运行次数: {'持续运行' if args.count == -1 else f'{args.count}次'}")
    print(f"  - 测试模式: {'是' if args.test_adapter else '否'}")
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

    try:
        while args.count == -1 or run_count < args.count:
            run_count += 1

            logger.info(f"🚀 开始第 {run_count} 次数据获取和保存...")

            success = run_single_fetch_and_save()

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
        logger.error(f"❌ 程序执行过程中出现错误: {str(e)}")

    finally:
        print("=" * 70)
        print("📊 执行统计:")
        print(f"  - 总运行次数: {run_count}")
        print(f"  - 成功次数: {success_count}")
        print(f"  - 失败次数: {run_count - success_count}")
        print(
            f"  - 成功率: {success_count/run_count*100:.1f}%"
            if run_count > 0
            else "  - 成功率: N/A"
        )
        print("=" * 70)
        logger.info("🏁 程序执行完毕")


if __name__ == "__main__":
    main()
