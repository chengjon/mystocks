#!/usr/bin/env python3
"""
分时线同步性能测试脚本

比较串行和并行同步的性能差异
"""

import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 线程锁用于保护共享资源
stats_lock = threading.Lock()


def sync_single_stock_serial(symbol, periods, trade_date, data_source, manager):
    """串行同步单只股票数据（用于性能对比）"""
    logger.info(f"串行处理股票 {symbol}")

    # 模拟数据处理时间（避免实际调用数据源）
    time.sleep(0.1)  # 模拟网络请求和数据处理

    # 模拟保存数据
    time.sleep(0.05)  # 模拟数据库写入

    return {
        "symbol": symbol,
        "records": 100,  # 模拟记录数
        "status": "success",
    }


def sync_single_stock_parallel(args):
    """并行同步单只股票数据（用于性能对比）"""
    symbol, periods, trade_date, data_source, manager = args
    logger.info(f"并行处理股票 {symbol}")

    # 模拟数据处理时间（避免实际调用数据源）
    time.sleep(0.1)  # 模拟网络请求和数据处理

    # 模拟保存数据
    time.sleep(0.05)  # 模拟数据库写入

    return {
        "symbol": symbol,
        "records": 100,  # 模拟记录数
        "status": "success",
    }


def sync_stocks_serial(symbols, periods, trade_date):
    """串行同步多只股票"""
    logger.info(f"开始串行同步 {len(symbols)} 只股票")

    results = []
    total_records = 0
    successful_stocks = 0

    # 模拟数据源和管理器
    data_source = None
    manager = None

    for symbol in symbols:
        try:
            result = sync_single_stock_serial(
                symbol, periods, trade_date, data_source, manager
            )
            results.append(result)
            total_records += result["records"]
            successful_stocks += 1
        except Exception as e:
            logger.error(f"串行处理股票 {symbol} 失败: {e}")

    return {
        "total_stocks": len(symbols),
        "successful_stocks": successful_stocks,
        "total_records": total_records,
        "results": results,
    }


def sync_stocks_parallel(symbols, periods, trade_date, max_workers=5):
    """并行同步多只股票"""
    logger.info(f"开始并行同步 {len(symbols)} 只股票，最大并行数: {max_workers}")

    # 模拟数据源和管理器
    data_source = None
    manager = None

    # 创建每只股票的处理参数
    stock_args = [
        (symbol, periods, trade_date, data_source, manager) for symbol in symbols
    ]

    total_records = 0
    successful_stocks = 0
    results = []

    # 使用线程池进行并行处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_stock = {
            executor.submit(sync_single_stock_parallel, args): args[0]
            for args in stock_args
        }

        # 处理完成的任务
        for future in as_completed(future_to_stock):
            symbol = future_to_stock[future]
            try:
                result = future.result()
                results.append(result)
                total_records += result["records"]
                successful_stocks += 1
                logger.info(f"股票 {symbol} 处理完成")
            except Exception as e:
                logger.error(f"并行处理股票 {symbol} 失败: {e}")

    return {
        "total_stocks": len(symbols),
        "successful_stocks": successful_stocks,
        "total_records": total_records,
        "results": results,
    }


def test_performance_comparison():
    """测试性能对比"""
    print("开始分时线同步性能对比测试...")
    print("=" * 60)

    # 测试参数
    symbols = [f"STOCK{i:06d}.SZ" for i in range(1, 51)]  # 50只股票
    periods = ["1m"]
    trade_date = "2025-11-17"

    # 测试串行处理
    print("\n1. 测试串行处理性能...")
    print("-" * 30)
    start_time = time.time()

    serial_stats = sync_stocks_serial(symbols, periods, trade_date)

    serial_duration = time.time() - start_time
    print(f"串行处理耗时: {serial_duration:.2f} 秒")
    print(
        f"处理股票数: {serial_stats['successful_stocks']}/{serial_stats['total_stocks']}"
    )
    print(f"总记录数: {serial_stats['total_records']}")

    # 测试并行处理（不同并行度）
    parallel_workers = [5, 10, 20]
    parallel_results = []

    for workers in parallel_workers:
        print(f"\n2. 测试并行处理性能 (并行度: {workers})...")
        print("-" * 30)
        start_time = time.time()

        parallel_stats = sync_stocks_parallel(symbols, periods, trade_date, workers)

        parallel_duration = time.time() - start_time
        parallel_results.append(
            {"workers": workers, "duration": parallel_duration, "stats": parallel_stats}
        )

        print(f"并行处理耗时: {parallel_duration:.2f} 秒")
        print(
            f"处理股票数: {parallel_stats['successful_stocks']}/{parallel_stats['total_stocks']}"
        )
        print(f"总记录数: {parallel_stats['total_records']}")

    # 输出性能对比报告
    print("\n" + "=" * 60)
    print("性能对比报告")
    print("=" * 60)

    print(f"串行处理: {serial_duration:.2f} 秒")

    for result in parallel_results:
        workers = result["workers"]
        duration = result["duration"]
        speedup = serial_duration / duration if duration > 0 else 0
        efficiency = speedup / workers if workers > 0 else 0

        print(
            f"并行处理 ({workers} workers): {duration:.2f} 秒 "
            f"(加速比: {speedup:.2f}x, 效率: {efficiency:.2%})"
        )

    # 最佳性能
    best_result = min(parallel_results, key=lambda x: x["duration"])
    best_workers = best_result["workers"]
    best_duration = best_result["duration"]
    best_speedup = serial_duration / best_duration if best_duration > 0 else 0

    print(
        f"\n最佳性能: {best_workers} workers, {best_duration:.2f} 秒 "
        f"(加速比: {best_speedup:.2f}x)"
    )


if __name__ == "__main__":
    test_performance_comparison()
