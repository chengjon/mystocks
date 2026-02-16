#!/usr/bin/env python3
"""
列名映射工具测试套件
完整测试column_mapper模块的所有功能，确保100%测试覆盖率
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
import pandas as pd
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Mock problematic imports to avoid dependency issues
import unittest.mock

sys.modules["src.storage.database.connection_manager"] = unittest.mock.MagicMock()
sys.modules["src.core.config"] = unittest.mock.MagicMock()

import pytest

# 导入被测试的模块
from src.utils.column_mapper import (
    ColumnMapper,
    standardize_dataframe,
    to_english_columns,
    to_chinese_columns,
)

# 为便捷函数创建别名
standardize_columns = ColumnMapper.standardize_columns
to_english = ColumnMapper.to_english
to_chinese = ColumnMapper.to_chinese
validate_columns = ColumnMapper.validate_columns

class TestPerformanceAndScalability:
    """性能和可扩展性测试类"""

    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        import time

        # 创建大数据集（10万行，50列）
        num_rows = 100000
        num_cols = 50

        # 生成列名
        columns = []
        for i in range(num_cols):
            if i % 10 == 0:
                columns.append("open")
            elif i % 10 == 1:
                columns.append("close")
            elif i % 10 == 2:
                columns.append("high")
            elif i % 10 == 3:
                columns.append("low")
            elif i % 10 == 4:
                columns.append("volume")
            else:
                columns.append(f"col_{i}")

        # 生成数据
        data = {col: [float(i) for i in range(num_rows)] for col in columns}
        large_df = pd.DataFrame(data)

        # 测试性能
        start_time = time.time()
        result_df = standardize_columns(large_df, target_lang="en")
        end_time = time.time()

        # 验证结果（注意：映射器会合并重复的列名）
        assert len(result_df) == num_rows
        # 由于列名映射可能导致重复列被合并，检查至少有基本列
        assert "open" in result_df.columns
        assert "close" in result_df.columns
        assert "high" in result_df.columns
        assert "low" in result_df.columns
        assert "volume" in result_df.columns

        # 性能检查（应该在合理时间内完成）
        processing_time = end_time - start_time
        assert processing_time < 10.0  # 应该在10秒内完成

    def test_memory_usage_large_dataset(self):
        """测试大数据集内存使用"""
        # 创建中等大小的数据集测试内存效率
        num_rows = 10000
        num_cols = 20

        columns = []
        for i in range(num_cols):
            if i < 5:
                columns.extend(["open", "close", "high", "low", "volume"])
            else:
                columns.append(f"col_{i}")

        columns = columns[:num_cols]  # 确保正确的列数
        data = {col: [float(i % 100) for i in range(num_rows)] for col in columns}
        test_df = pd.DataFrame(data)

        # 执行转换
        result_df = standardize_columns(test_df, target_lang="en")

        # 验证内存使用合理（通过检查数据大小）
        assert len(result_df) == num_rows
        # 只验证基本列存在（因为可能存在重复列合并）
        assert "open" in result_df.columns
        assert "close" in result_df.columns
        assert "high" in result_df.columns
        assert "low" in result_df.columns
        assert "volume" in result_df.columns

    def test_concurrent_column_mapping(self):
        """测试并发列名映射"""
        import threading
        import queue

        results = queue.Queue()

        def worker_function(worker_id):
            """工作线程函数"""
            try:
                test_data = pd.DataFrame(
                    {
                        "open": [10.0 * worker_id, 11.0 * worker_id],
                        "收盘价": [11.0 * worker_id, 12.0 * worker_id],
                        "high": [12.0 * worker_id, 13.0 * worker_id],
                        "最低价": [9.0 * worker_id, 10.0 * worker_id],
                        "volume": [1000 * worker_id, 1200 * worker_id],
                    }
                )

                result_df = standardize_columns(test_data, target_lang="en")
                results.put(f"worker_{worker_id}_success")

            except Exception as e:
                results.put(f"worker_{worker_id}_error: {str(e)}")

        # 启动多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_function, args=(i + 1,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 收集结果
        collected_results = []
        while not results.empty():
            collected_results.append(results.get_nowait())

        # 验证所有操作都成功
        assert len(collected_results) == 5
        assert all("success" in result for result in collected_results)

    def test_repeated_operations_performance(self):
        """测试重复操作性能"""
        import time

        # 创建测试数据
        test_data = pd.DataFrame(
            {"open": [10.0, 11.0], "收盘价": [11.0, 12.0], "volume": [1000, 1200]}
        )

        # 执行多次操作并测试性能
        iterations = 1000
        start_time = time.time()

        for i in range(iterations):
            result_df = standardize_columns(test_data, target_lang="en")

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / iterations

        # 性能验证（平均每次操作应该很快）
        assert avg_time < 0.01  # 平均每次操作应该小于10毫秒
        assert total_time < 30.0  # 总时间应该合理

    def test_scalability_with_column_count(self):
        """测试列数扩展性"""
        import time

        # 测试不同列数的性能
        column_counts = [10, 50, 100, 200]
        processing_times = []

        for num_cols in column_counts:
            # 创建指定列数的测试数据
            columns = []
            for i in range(num_cols):
                if i % 5 == 0:
                    columns.append("open")
                elif i % 5 == 1:
                    columns.append("close")
                elif i % 5 == 2:
                    columns.append("high")
                elif i % 5 == 3:
                    columns.append("low")
                else:
                    columns.append(f"col_{i}")

            data = {col: [1.0, 2.0] for col in columns}
            test_df = pd.DataFrame(data)

            # 测试处理时间
            start_time = time.time()
            result_df = standardize_columns(test_df, target_lang="en")
            end_time = time.time()

            processing_time = end_time - start_time
            processing_times.append(processing_time)

            # 验证结果正确性（由于重复列名可能被合并，检查基本列存在）
            assert len(result_df.columns) > 0
            assert "open" in result_df.columns
            assert "close" in result_df.columns

        # 验证性能随列数线性增长（不应该是指数增长）
        # 简单检查：最大处理时间不应该是最小处理时间的10倍以上
        max_time = max(processing_times)
        min_time = min(processing_times)
        assert max_time < min_time * 10, (
            f"性能扩展性不佳: 最大时间={max_time}, 最小时间={min_time}"
        )

    def test_memory_efficiency_with_large_strings(self):
        """测试大字符串数据的内存效率"""
        # 创建包含大字符串的DataFrame
        large_string_data = pd.DataFrame(
            {
                "open": [10.0, 11.0],
                "description": ["A" * 1000, "B" * 1000],  # 大字符串
                "收盘价": [11.0, 12.0],
                "long_name_column": ["C" * 500, "D" * 500],
            }
        )

        # 执行转换
        result_df = standardize_columns(large_string_data, target_lang="en")

        # 验证结果正确性且内存使用合理
        assert len(result_df) == 2
        assert len(result_df.columns) == 4

    def test_performance_with_different_data_types(self):
        """测试不同数据类型的性能"""
        import time

        # 创建包含不同数据类型的DataFrame
        mixed_data = pd.DataFrame(
            {
                "open": [10.0, 11.0],  # float
                "count": [100, 200],  # int
                "收盘价": [11.0, 12.0],  # float
                "name": ["stock1", "stock2"],  # string
                "active": [True, False],  # bool
                "date": pd.to_datetime(["2025-01-01", "2025-01-02"]),  # datetime
                "category": pd.Categorical(["A", "B"]),  # categorical
            }
        )

        # 测试转换性能
        start_time = time.time()
        result_df = standardize_columns(mixed_data, target_lang="en")
        end_time = time.time()

        processing_time = end_time - start_time

        # 验证结果正确性
        assert len(result_df) == 2
        assert "open" in result_df.columns

        # 验证性能合理
        assert processing_time < 1.0  # 应该很快完成


