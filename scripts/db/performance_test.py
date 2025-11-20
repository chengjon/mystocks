#!/usr/bin/env python3
"""
分时线同步性能测试脚本

比较串行和并行同步的性能差异
"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from scripts.data_sync.sync_minute_kline import sync_minute_kline_data


def test_sync_performance():
    """测试同步性能"""
    print("开始分时线同步性能测试...")
    print("=" * 50)
    
    # 测试参数
    periods = ['1m']  # 只测试1分钟周期以加快测试速度
    stock_limit = 5   # 限制5只股票
    max_workers_list = [1, 5, 10]  # 不同的并行度
    
    results = []
    
    for max_workers in max_workers_list:
        print(f"\n测试并行度: {max_workers}")
        print("-" * 30)
        
        start_time = time.time()
        
        try:
            stats = sync_minute_kline_data(
                periods=periods, 
                stock_limit=stock_limit, 
                max_workers=max_workers
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            result = {
                "max_workers": max_workers,
                "duration": duration,
                "stats": stats
            }
            results.append(result)
            
            print(f"  同步耗时: {duration:.2f} 秒")
            print(f"  成功股票数: {stats['successful_stocks']}/{stats['total_stocks']}")
            print(f"  总记录数: {stats['total_records']}")
            
        except Exception as e:
            print(f"  测试失败: {e}")
            end_time = time.time()
            duration = end_time - start_time
            results.append({
                "max_workers": max_workers,
                "duration": duration,
                "error": str(e)
            })
    
    # 输出性能对比报告
    print("\n" + "=" * 50)
    print("性能测试报告")
    print("=" * 50)
    
    for result in results:
        if "error" in result:
            print(f"并行度 {result['max_workers']}: 失败 - {result['error']}")
        else:
            print(f"并行度 {result['max_workers']}: {result['duration']:.2f} 秒 "
                  f"({result['stats']['successful_stocks']}/{result['stats']['total_stocks']} 股票成功)")
    
    # 计算性能提升
    if len(results) >= 2:
        serial_duration = results[0]["duration"]
        parallel_duration = results[-1]["duration"]
        speedup = serial_duration / parallel_duration if parallel_duration > 0 else 0
        print(f"\n性能提升: {speedup:.2f}x (从 {serial_duration:.2f}s 到 {parallel_duration:.2f}s)")


if __name__ == "__main__":
    test_sync_performance()