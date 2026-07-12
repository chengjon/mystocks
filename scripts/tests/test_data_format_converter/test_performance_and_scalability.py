#!/usr/bin/env python3
"""数据格式转换工具测试套件 - 完整覆盖data_format_converter模块
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
import time
from pathlib import Path

import pandas as pd


# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# 导入被测试的模块
from src.utils.data_format_converter import (
    normalize_api_response_format,
    normalize_stock_data_format,
    normalize_stock_list_format,
)


class TestPerformanceAndScalability:
    """性能和可扩展性测试类"""

    def test_batch_processing_performance(self):
        """测试批量处理性能"""
        # 创建多个测试DataFrame
        dataframes = []
        for i in range(10):
            df = pd.DataFrame(
                {
                    "symbol": [f"60000{j}" for j in range(100)],
                    "name": [f"股票{j}" for j in range(100)],
                    "industry": ["金融"] * 100,
                },
            )
            dataframes.append(df)

        start_time = time.time()
        results = [normalize_stock_data_format(df) for df in dataframes]
        elapsed = time.time() - start_time

        assert len(results) == 10
        total_rows = sum(len(df) for df in results)
        assert total_rows == 1000
        assert elapsed < 2.0  # 应该在2秒内完成

    def test_large_field_mapping_performance(self):
        """测试大规模字段映射性能"""
        # 创建具有大量列的DataFrame
        data = {}
        for i in range(100):
            data[f"col_{i}"] = ["value"] * 100
        data["symbol"] = ["600000"] * 100
        df = pd.DataFrame(data)

        start_time = time.time()
        result = normalize_stock_data_format(df)
        elapsed = time.time() - start_time

        assert len(result) == 100
        # 原始有100列 + symbol + 5个必需字段(name, industry, area, market, list_date) = 106列
        assert len(result.columns) == 106
        assert elapsed < 1.0  # 应该在1秒内完成

    def test_memory_usage(self):
        """测试内存使用情况"""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 处理大量数据
        large_df = pd.DataFrame(
            {
                "symbol": [f"60000{i}" for i in range(5000)],
                "data": [f"data_{i}" for i in range(5000)],
            },
        )

        result = normalize_stock_data_format(large_df)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # 内存增长应该在合理范围内
        assert memory_increase < 50 * 1024 * 1024  # 小于50MB


class TestIntegrationScenarios:
    """集成场景测试类"""

    def test_complete_data_pipeline(self):
        """测试完整的数据处理流水线"""
        # 模拟从不同数据源获取的原始数据
        raw_df = pd.DataFrame(
            {
                "symbol": ["600000"],  # 使用symbol字段，符合源码的field_mapping
                "stock_name": ["浦发银行"],
                "exchange": ["SH"],
                "trade_date": ["2025-01-01"],
                "open_price": ["10.0"],
                "close_price": ["11.0"],
                "volume": ["1000000"],
            },
        )

        raw_api_response = {
            "code": 0,
            "data": {"symbol": "600000", "cname": "浦发银行", "exchange": "SH"},
        }

        raw_stock_list = [{"code": "600000", "name": "浦发银行", "exchange": "SH"}]

        # 依次应用各种格式转换
        normalized_df = normalize_stock_data_format(raw_df)
        normalized_api = normalize_api_response_format(raw_api_response)
        normalized_list = normalize_stock_list_format(raw_stock_list)

        # 验证转换结果
        assert isinstance(normalized_df, pd.DataFrame)
        assert isinstance(normalized_api, dict)
        assert isinstance(normalized_list, list)

        # 验证数据一致性
        assert "symbol" in normalized_df.columns
        # symbol字段应该保持原值，因为symbol在field_mapping中映射到自己
        assert normalized_df.iloc[0]["symbol"] == "600000"
        # API响应中的data会被转换为DataFrame然后标准化，但API结构需要调整
        assert "data" in normalized_api
        assert normalized_list[0]["symbol"] == "600000"  # stock_list格式转换

    def test_real_world_data_simulation(self):
        """测试真实世界数据模拟"""
        # 模拟真实的股票数据
        realistic_data = pd.DataFrame(
            {
                "symbol": ["600000", "000001", "300750"],
                "stock_name": ["浦发银行", "平安银行", "宁德时代"],
                "industry": ["银行", "银行", "新能源"],
                "exchange": ["SH", "SZ", "SZ"],
                "trade_date": ["2025-01-01", "2025-01-01", "2025-01-01"],
                "open": [10.5, 15.2, 168.0],
                "high": [10.8, 15.5, 170.0],
                "low": [10.2, 15.0, 165.0],
                "close": [10.6, 15.3, 169.5],
                "volume": [1000000, 800000, 500000],
                "turnover": [0.15, 0.12, 0.18],
            },
        )

        result = normalize_stock_data_format(realistic_data)

        # 验证所有股票都被正确处理
        assert len(result) == 3

        # 验证关键字段
        required_fields = [
            "symbol",
            "name",
            "industry",
            "market",
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        for field in required_fields:
            assert field in result.columns

        # 验证数据类型
        assert pd.api.types.is_datetime64_any_dtype(result["date"])
        assert pd.api.types.is_numeric_dtype(result["open"])

    def test_data_quality_validation(self):
        """测试数据质量验证"""
        # 包含各种数据质量问题的数据
        problematic_data = pd.DataFrame(
            {
                "symbol": ["600000", "", None],
                "name": ["浦发银行", "平安银行", None],
                "industry": ["银行", "", "未知行业"],
                "exchange": ["SH", "SZ", "INVALID"],
                "open": [10.5, "invalid", -1.0],  # 无效价格
                "volume": [1000000, -100, 0],  # 无效成交量
            },
        )

        result = normalize_stock_data_format(problematic_data)

        # 验证处理结果
        assert len(result) == 3

        # 验证数据清洗
        assert result.iloc[1]["symbol"] == ""  # 空字符串保留
        assert pd.isna(result.iloc[2]["symbol"])  # None转为NaN
        assert pd.isna(result.iloc[2]["name"])  # None转为NaN
        assert result.iloc[2]["industry"] == "未知行业"  # 无效值保持

    def test_concurrent_processing(self):
        """测试并发处理"""
        import concurrent.futures

        # 创建多个处理任务
        def create_test_data(batch_id):
            return pd.DataFrame(
                {
                    "symbol": [f"60000{batch_id}{i}" for i in range(10)],
                    "name": [f"股票{batch_id}{i}" for i in range(10)],
                    "industry": ["金融"] * 10,
                },
            )

        # 并发执行标准化
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(normalize_stock_data_format, create_test_data(i)) for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # 验证结果
        assert len(results) == 5
        total_rows = sum(len(df) for df in results)
        assert total_rows == 50


class TestUncoveredCodePaths:
    """专门测试未覆盖代码路径的测试类"""

    def test_numeric_conversion_exception_with_actual_exception(self):
        """测试数值转换抛出异常的路径（覆盖第119-121行）"""
        # Mock pandas to_numeric to raise exception
        from unittest.mock import patch

        import pandas as pd

        df = pd.DataFrame(
            {
                "symbol": ["600000"],
                "open": ["10.5"],  # 字符串类型，会触发转换
            },
        )

        with patch("pandas.to_numeric", side_effect=Exception("模拟转换异常")):
            result = normalize_stock_data_format(df)

            # 验证异常被捕获，数据保持原样
            assert len(result) == 1
            assert result["symbol"].iloc[0] == "600000"
            assert result["open"].iloc[0] == "10.5"  # 保持原值

    def test_normalize_stock_list_symbol_missing_field(self):
        """测试股票列表标准化时缺少symbol字段的默认值（覆盖第218行）"""
        stock_list = [
            {
                # 缺少symbol字段
                "name": "测试股票",
                "industry": "金融",
            },
        ]

        result = normalize_stock_list_format(stock_list)

        assert len(result) == 1
        assert result[0]["symbol"] == "N/A"  # 默认值
        assert result[0]["name"] == "测试股票"
