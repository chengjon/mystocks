#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试和验证 save_realtime_data.py 程序
展示完整的数据库保存工作流程
"""

import sys
import os
import pandas as pd

# 将项目根目录添加到模块搜索路径中
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from scripts.runtime.save_realtime_data import (
    RealtimeDataSaver,
    save_realtime_data_to_db,
)
from src.storage.database.database_manager import DatabaseType


def test_basic_save():
    """测试基本的数据保存功能"""
    print("=== 测试基本数据保存功能 ===")

    # 使用默认配置进行测试
    success = save_realtime_data_to_db(
        market_symbol="hs",
        database_type=DatabaseType.MYSQL,
        database_name="test_db",
        table_name="test_realtime_data",
        update_mode="replace",
    )

    if success:
        print("✅ 基本数据保存测试通过")
    else:
        print("❌ 基本数据保存测试失败")

    return success


def test_saver_class():
    """测试 RealtimeDataSaver 类的功能"""
    print("\n=== 测试 RealtimeDataSaver 类 ===")

    # 创建数据保存器实例
    saver = RealtimeDataSaver(
        database_type=DatabaseType.MYSQL,
        database_name="test_db",
        table_name="class_test_realtime_data",
        update_mode="append",
    )

    try:
        # 执行保存操作
        success = saver.save_realtime_data("hs")

        if success:
            print("✅ RealtimeDataSaver 类测试通过")
        else:
            print("❌ RealtimeDataSaver 类测试失败")

        return success

    finally:
        # 清理资源
        saver.cleanup()


def test_dataframe_preparation():
    """测试数据准备和处理功能"""
    print("\n=== 测试数据准备功能 ===")

    # 创建模拟数据
    test_data = pd.DataFrame(
        {
            "股票代码": ["600000", "000001", "000002"],
            "股票名称": ["浦发银行", "平安银行", "万科A"],
            "最新价": [10.50, 15.30, 20.80],
            "涨跌幅": [0.02, -0.01, 0.05],
            "成交量": [1000000, 2000000, 1500000],
        }
    )

    saver = RealtimeDataSaver()

    try:
        # 测试数据验证
        is_valid = saver._validate_dataframe(test_data)
        print(f"数据验证结果: {'通过' if is_valid else '失败'}")

        # 测试数据准备
        prepared_data = saver._prepare_dataframe(test_data)
        print(f"数据准备完成: {len(prepared_data)} 行, {len(prepared_data.columns)} 列")
        print("准备后的列名:", list(prepared_data.columns))

        # 测试表结构生成
        columns = saver._generate_table_columns(prepared_data)
        print(f"生成表结构: {len(columns)} 个字段")

        print("✅ 数据准备功能测试通过")
        return True

    except Exception as e:
        print(f"❌ 数据准备功能测试失败: {e}")
        return False

    finally:
        saver.cleanup()


def test_different_modes():
    """测试不同的数据更新模式"""
    print("\n=== 测试不同更新模式 ===")

    modes = ["replace", "append", "ignore"]
    results = {}

    for mode in modes:
        print(f"\n测试 {mode} 模式...")
        try:
            success = save_realtime_data_to_db(
                market_symbol="hs",
                database_type=DatabaseType.MYSQL,
                database_name="test_db",
                table_name=f"test_{mode}_data",
                update_mode=mode,
            )
            results[mode] = success
            print(
                f"{'✅' if success else '❌'} {mode} 模式测试{'通过' if success else '失败'}"
            )

        except Exception as e:
            results[mode] = False
            print(f"❌ {mode} 模式测试出错: {e}")

    return results


def test_error_handling():
    """测试错误处理机制"""
    print("\n=== 测试错误处理机制 ===")

    # 测试无效市场代码
    print("测试无效市场代码...")
    try:
        saver = RealtimeDataSaver()
        success = saver.save_realtime_data("invalid_market")
        print(f"无效市场代码处理: {'正确' if not success else '错误'}")
    except Exception as e:
        print(f"无效市场代码异常处理: {e}")
    finally:
        saver.cleanup()

    # 测试无效数据库连接
    print("\n测试无效数据库配置...")
    try:
        saver = RealtimeDataSaver(
            database_type=DatabaseType.MYSQL,
            database_name="nonexistent_db",
            table_name="test_table",
        )
        success = saver.save_realtime_data("hs")
        print(f"无效数据库处理: {'正确' if not success else '错误'}")
    except Exception as e:
        print(f"无效数据库异常处理: {e}")
    finally:
        saver.cleanup()

    print("✅ 错误处理机制测试完成")


def run_comprehensive_test():
    """运行综合测试"""
    print("开始运行 save_realtime_data.py 综合测试")
    print("=" * 50)

    test_results = {}

    # 1. 基本功能测试
    test_results["basic_save"] = test_basic_save()

    # 2. 类功能测试
    test_results["saver_class"] = test_saver_class()

    # 3. 数据准备测试
    test_results["data_preparation"] = test_dataframe_preparation()

    # 4. 不同模式测试
    test_results["different_modes"] = test_different_modes()

    # 5. 错误处理测试
    test_error_handling()

    # 测试结果总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print("=" * 50)

    passed_tests = 0
    total_tests = 0

    for test_name, result in test_results.items():
        if isinstance(result, dict):
            # 处理多模式测试结果
            for mode, mode_result in result.items():
                total_tests += 1
                if mode_result:
                    passed_tests += 1
                    print(f"✅ {test_name}_{mode}: 通过")
                else:
                    print(f"❌ {test_name}_{mode}: 失败")
        else:
            total_tests += 1
            if result:
                passed_tests += 1
                print(f"✅ {test_name}: 通过")
            else:
                print(f"❌ {test_name}: 失败")

    print(f"\n测试统计: {passed_tests}/{total_tests} 通过")
    print(f"通过率: {passed_tests / total_tests * 100:.1f}%")

    if passed_tests == total_tests:
        print("🎉 所有测试通过!")
    else:
        print("⚠️  部分测试失败，请检查日志")


if __name__ == "__main__":
    run_comprehensive_test()
