#!/usr/bin/env python3
"""
数据格式转换工具测试套件 - 完整覆盖data_format_converter模块
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
import os
import time
import pandas as pd
from datetime import datetime, date
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

# 导入被测试的模块
from src.utils.data_format_converter import (
    normalize_stock_data_format,
    normalize_api_response_format,
    normalize_stock_list_format,
    normalize_indicator_data_format,
    test_format_normalization,
)


class TestNormalizeStockDataFormat:
    """normalize_stock_data_format函数测试类"""

    def test_basic_field_mapping(self):
        """测试基本字段映射功能"""
        # 创建测试数据
        df = pd.DataFrame(
            {
                "symbol": ["600000"],
                "stock_name": ["浦发银行"],
                "sector": ["金融"],
                "exchange": ["SH"],
                "listing_date": ["1999-11-10"],
                "trade_date": ["2025-01-01"],
                "open": [10.0],
                "close": [11.0],
                "volume": [1000000],
            }
        )

        result = normalize_stock_data_format(df)

        # 验证字段映射
        assert "name" in result.columns
        assert "industry" in result.columns
        assert "market" in result.columns
        assert "list_date" in result.columns
        assert "date" in result.columns

        # 验证值
        assert result.iloc[0]["name"] == "浦发银行"
        assert result.iloc[0]["industry"] == "金融"
        assert result.iloc[0]["market"] == "SH"

    def test_empty_dataframe(self):
        """测试空DataFrame处理"""
        empty_df = pd.DataFrame()
        result = normalize_stock_data_format(empty_df)

        assert result.empty

    def test_date_conversion(self):
        """测试日期字段转换"""
        df = pd.DataFrame(
            {"symbol": ["600000"], "date": ["2025-01-01"], "list_date": ["1999-11-10"]}
        )

        result = normalize_stock_data_format(df)

        # 验证日期转换
        assert pd.api.types.is_datetime64_any_dtype(result["date"])
        assert pd.api.types.is_datetime64_any_dtype(result["list_date"])

    def test_numeric_conversion(self):
        """测试数值字段转换"""
        df = pd.DataFrame(
            {
                "symbol": ["600000"],
                "open": ["10.5"],
                "high": ["11.0"],
                "low": ["9.5"],
                "close": ["10.8"],
                "volume": ["1000000"],
            }
        )

        result = normalize_stock_data_format(df)

        # 验证数值转换（volume不在源代码的数值转换列表中，所以保持object类型）
        assert pd.api.types.is_numeric_dtype(result["open"])
        assert pd.api.types.is_numeric_dtype(result["high"])
        assert pd.api.types.is_numeric_dtype(result["low"])
        assert pd.api.types.is_numeric_dtype(result["close"])
        # volume字段不会被转换为数值类型，因为源代码只处理特定的数值字段
        assert result["volume"].dtype == "object"

    def test_numeric_conversion_exception_handling(self):
        """测试数值转换异常处理（覆盖第119-121行）"""
        # 创建会触发异常的数值字段
        df = pd.DataFrame(
            {
                "symbol": ["600000"],
                "open": ["10.5"],
                "high": ["invalid_value"],  # 这会触发异常但被except捕获
                "low": ["9.5"],
            }
        )

        result = normalize_stock_data_format(df)

        # 验证异常处理：high字段应该被转为NaN因为errors='coerce'
        import numpy as np

        assert pd.isna(result.iloc[0]["high"])
        # 其他正常字段应该被转换
        assert pd.api.types.is_numeric_dtype(result["open"])

    def test_invalid_date_handling(self):
        """测试无效日期处理"""
        df = pd.DataFrame(
            {
                "symbol": ["600000"],
                "date": ["invalid_date"],
                "list_date": ["not_a_date"],
            }
        )

        result = normalize_stock_data_format(df)

        # 无效日期应该保持原值或被正确处理
        assert not pd.api.types.is_datetime64_any_dtype(result["date"])

    def test_invalid_numeric_handling(self):
        """测试无效数值处理"""
        df = pd.DataFrame(
            {"symbol": ["600000"], "open": ["not_a_number"], "close": ["12.5"]}
        )

        result = normalize_stock_data_format(df)

        # 无效数值应该被转换为NaN
        assert pd.isna(result.iloc[0]["open"])
        assert result.iloc[0]["close"] == 12.5

    def test_field_default_values(self):
        """测试字段默认值设置"""
        df = pd.DataFrame(
            {
                "symbol": ["600000"],
                # 缺少关键字段
            }
        )

        result = normalize_stock_data_format(df)

        # 验证默认值设置
        assert "name" in result.columns
        assert "industry" in result.columns

    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        # 创建大数据集
        data = {
            "symbol": [f"60000{i}" for i in range(1000)],
            "stock_name": [f"股票{i}" for i in range(1000)],
            "exchange": ["SH"] * 1000,
            "open": [10.0 + i * 0.1 for i in range(1000)],
        }
        df = pd.DataFrame(data)

        start_time = time.time()
        result = normalize_stock_data_format(df)
        elapsed = time.time() - start_time

        assert len(result) == 1000
        assert elapsed < 1.0  # 应该在1秒内完成

    def test_complex_field_mapping(self):
        """测试复杂字段映射"""
        df = pd.DataFrame(
            {
                "symbol": ["600000"],
                "cname": ["中文名称"],
                "area": ["上海"],
                "location": ["上海地区"],
                "ipo_date": ["2000-01-01"],
                "turnover": ["15.5%"],
            }
        )

        result = normalize_stock_data_format(df)

        # 验证多重字段映射（根据源码逻辑，cname会被映射为name，但location不会映射因为area已存在）
        assert result.iloc[0]["name"] == "中文名称"  # cname -> name
        assert (
            result.iloc[0]["area"] == "上海"
        )  # area保持原值，因为location不会覆盖已存在的area
        assert result.iloc[0]["list_date"] is not None


class TestNormalizeApiResponseFormat:
    """normalize_api_response_format函数测试类"""

    def test_basic_api_response(self):
        """测试基本API响应格式"""
        data = {
            "code": 0,
            "message": "success",
            "data": {"symbol": "600000", "name": "浦发银行"},
        }

        result = normalize_api_response_format(data)

        assert isinstance(result, dict)
        assert "code" in result
        assert "message" in result
        assert "data" in result

    def test_nested_structure_normalization(self):
        """测试嵌套结构标准化"""
        data = {
            "result": {
                "stock_basic": {
                    "symbol": "600000",
                    "stock_name": "浦发银行",
                    "exchange": "SH",
                },
                "market_data": {"current_price": "10.5", "change_pct": "2.5%"},
            }
        }

        result = normalize_api_response_format(data)

        assert "result" in result
        assert isinstance(result["result"], dict)

    def test_list_data_normalization(self):
        """测试列表数据标准化"""
        data = {
            "data": [
                {"symbol": "600000", "name": "浦发银行"},
                {"symbol": "000001", "name": "平安银行"},
            ]
        }

        result = normalize_api_response_format(data)

        assert "data" in result
        assert isinstance(result["data"], list)

    def test_error_response_handling(self):
        """测试错误响应处理"""
        data = {"code": -1, "error": "Invalid request", "msg": "参数错误"}

        result = normalize_api_response_format(data)

        # 错误响应也应该被正确处理
        assert isinstance(result, dict)
        assert result.get("code") == -1

    def test_non_dict_input_handling(self):
        """测试非字典输入处理（覆盖第137行）"""
        # 测试非dict输入
        result = normalize_api_response_format("not a dict")
        assert result == "not a dict"

        # 测试None输入
        result = normalize_api_response_format(None)
        assert result is None

        # 测试列表输入
        result = normalize_api_response_format([1, 2, 3])
        assert result == [1, 2, 3]

    def test_api_response_dataframe_processing(self):
        """测试API响应中DataFrame处理（覆盖第143行）"""
        df = pd.DataFrame({"symbol": ["600000"], "cname": "测试名称"})

        api_response = {
            "code": 0,
            "data": df,  # DataFrame类型
        }

        result = normalize_api_response_format(api_response)

        assert "data" in result
        assert isinstance(result["data"], pd.DataFrame)
        assert "name" in result["data"].columns  # cname应该被重命名为name

    def test_api_response_list_processing(self):
        """测试API响应中list处理（覆盖第150-151行）"""
        api_response = {
            "code": 0,
            "data": [
                {"symbol": "600000", "cname": "测试1"},
                {"symbol": "000001", "cname": "测试2"},
            ],
        }

        result = normalize_api_response_format(api_response)

        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "测试1"  # cname被重命名为name

    def test_api_response_other_data_types(self):
        """测试API响应中其他数据类型处理（覆盖第161行）"""
        api_response = {
            "code": 0,
            "data": "string_data",  # 既不是DataFrame也不是list
        }

        result = normalize_api_response_format(api_response)

        assert "data" in result
        assert result["data"] == "string_data"  # 应该保持原值

    def test_missing_required_fields(self):
        """测试缺少必需字段的处理"""
        data = {
            # 缺少code和message字段
            "data": {"symbol": "600000"}
        }

        result = normalize_api_response_format(data)

        # 应该保持原有结构
        assert "data" in result

    def test_unicode_handling(self):
        """测试Unicode字符处理"""
        data = {
            "data": {
                "symbol": "600000",
                "name": "浦发银行",
                "industry": "金融",
                "description": "这是一个包含特殊字符的描述：测试®™",
            }
        }

        result = normalize_api_response_format(data)

        assert isinstance(result, dict)
        assert "测试®™" in result["data"]["description"]

    def test_large_api_response(self):
        """测试大型API响应处理"""
        # 创建大型响应数据
        large_data = {"data": []}
        for i in range(1000):
            large_data["data"].append(
                {
                    "symbol": f"60000{i}",
                    "name": f"股票{i}",
                    "industry": "金融",
                    "market": "SH",
                }
            )

        start_time = time.time()
        result = normalize_api_response_format(large_data)
        elapsed = time.time() - start_time

        assert len(result["data"]) == 1000
        assert elapsed < 0.5  # 应该在0.5秒内完成


class TestNormalizeStockListFormat:
    """normalize_stock_list_format函数测试类"""

    def test_basic_stock_list(self):
        """测试基本股票列表格式"""
        stock_list = [
            {
                "symbol": "600000",
                "stock_name": "浦发银行",
                "industry": "金融",
                "area": "上海",
                "exchange": "SH",
            },
            {
                "symbol": "000001",
                "cname": "平安银行",
                "sector": "金融",
                "location": "深圳",
            },
        ]

        result = normalize_stock_list_format(stock_list)

        assert isinstance(result, list)
        assert len(result) == 2

        # 验证字段映射
        for stock in result:
            assert "symbol" in stock
            assert "name" in stock
            assert "industry" in stock
            assert "area" in stock
            assert "market" in stock

        # 验证具体值
        assert result[0]["name"] == "浦发银行"
        assert result[1]["name"] == "平安银行"

    def test_missing_fields_default_values(self):
        """测试缺失字段的默认值"""
        stock_list = [
            {
                "symbol": "600000"
                # 缺少其他字段
            }
        ]

        result = normalize_stock_list_format(stock_list)

        assert len(result) == 1
        stock = result[0]

        # 验证默认值
        assert stock["name"] == "未命名"
        assert stock["industry"] == "N/A"
        assert stock["area"] == "N/A"
        assert stock["market"] == "N/A"
        assert stock["list_date"] is None

    def test_non_dict_item_handling(self):
        """测试非字典项的处理"""
        stock_list = [
            {"symbol": "600000", "name": "浦发银行"},
            "not_a_dict",  # 非字典项
            None,  # 空值项
            123,  # 数字项
        ]

        result = normalize_stock_list_format(stock_list)

        assert len(result) == 4
        # 非字典项应该保持原样
        assert result[1] == "not_a_dict"
        assert result[2] is None
        assert result[3] == 123

    def test_complex_data_types(self):
        """测试复杂数据类型处理"""
        stock_list = [
            {
                "symbol": "600000",
                "name": "浦发银行",
                "pe_ratio": 15.5,
                "pb_ratio": 0.8,
                "tags": ["金融", "银行", "大盘股"],
                "metadata": {"source": "akshare", "update_time": "2025-01-01"},
            }
        ]

        result = normalize_stock_list_format(stock_list)

        assert len(result) == 1
        stock = result[0]

        # 复杂数据类型应该保持原样
        assert stock["pe_ratio"] == 15.5
        assert stock["pb_ratio"] == 0.8
        assert stock["tags"] == ["金融", "银行", "大盘股"]
        assert stock["metadata"]["source"] == "akshare"

    def test_unicode_and_special_chars(self):
        """测试Unicode和特殊字符处理"""
        stock_list = [
            {
                "symbol": "600000",
                "name": "浦发银行®",
                "industry": "金融™",
                "description": "包含特殊字符的描述：测试®™专利",
            }
        ]

        result = normalize_stock_list_format(stock_list)

        assert "®" in result[0]["name"]
        assert "™" in result[0]["industry"]
        assert "测试®™专利" in result[0]["description"]

    def test_empty_list(self):
        """测试空列表处理"""
        result = normalize_stock_list_format([])

        assert isinstance(result, list)
        assert len(result) == 0

    def test_large_stock_list(self):
        """测试大型股票列表处理"""
        large_list = []
        for i in range(1000):
            large_list.append(
                {
                    "symbol": f"60000{i}",
                    "stock_name": f"股票{i}",
                    "industry": "金融" if i % 2 == 0 else "科技",
                }
            )

        start_time = time.time()
        result = normalize_stock_list_format(large_list)
        elapsed = time.time() - start_time

        assert len(result) == 1000
        assert elapsed < 0.5  # 应该在0.5秒内完成


class TestNormalizeIndicatorDataFormat:
    """normalize_indicator_data_format函数测试类"""

    def test_basic_indicator_data(self):
        """测试基本指标数据"""
        indicator_data = {
            "symbol": "600000",
            "ma5": 10.5,
            "ma10": 11.0,
            "ma20": 12.0,
            "rsi": 65.5,
            "macd": 0.5,
        }

        result = normalize_indicator_data_format(indicator_data)

        assert isinstance(result, dict)
        assert "symbol" in result
        assert result["symbol"] == "600000"

    def test_nested_indicator_structure(self):
        """测试嵌套指标结构"""
        indicator_data = {
            "symbol": "600000",
            "technical": {
                "ma": {"ma5": 10.5, "ma10": 11.0, "ma20": 12.0},
                "oscillator": {"rsi": 65.5, "stoch": {"k": 80.0, "d": 75.0}},
            },
            "fundamental": {"pe": 15.5, "pb": 0.8},
        }

        result = normalize_indicator_data_format(indicator_data)

        assert "technical" in result
        assert "fundamental" in result
        assert result["symbol"] == "600000"

    def test_array_indicator_data(self):
        """测试数组格式指标数据"""
        indicator_data = {
            "symbol": "600000",
            "ma_values": [10.0, 10.5, 11.0, 11.5, 12.0],
            "volume": [1000000, 1100000, 1200000],
            "dates": ["2025-01-01", "2025-01-02", "2025-01-03"],
        }

        result = normalize_indicator_data_format(indicator_data)

        assert isinstance(result, dict)
        assert "ma_values" in result
        assert "volume" in result
        assert "dates" in result

    def test_invalid_data_types(self):
        """测试无效数据类型"""
        indicator_data = {
            "symbol": None,  # None值
            "ma5": "invalid_number",  # 无效数字
            "data": "not_dict_or_array",  # 非预期类型
        }

        result = normalize_indicator_data_format(indicator_data)

        # 应该保持原数据结构
        assert isinstance(result, dict)
        assert result["symbol"] is None

    def test_empty_indicator_data(self):
        """测试空指标数据"""
        result = normalize_indicator_data_format({})

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_complex_nested_structure(self):
        """测试复杂嵌套结构"""
        indicator_data = {
            "symbol": "600000",
            "indicators": [
                {
                    "name": "MA",
                    "values": {"ma5": 10.5, "ma10": 11.0},
                    "metadata": {"period": 10, "source": "calculated"},
                },
                {
                    "name": "RSI",
                    "values": [65.0, 68.0, 70.0],
                    "metadata": {"period": 14, "overbought": 70},
                },
            ],
        }

        result = normalize_indicator_data_format(indicator_data)

        assert "indicators" in result
        assert isinstance(result["indicators"], list)
        assert len(result["indicators"]) == 2

    def test_indicator_data_non_dict_input(self):
        """测试指标数据非字典输入（覆盖第242行）"""
        # 测试非dict输入
        result = normalize_indicator_data_format("not a dict")
        assert result == "not a dict"

        # 测试None输入
        result = normalize_indicator_data_format(None)
        assert result is None

        # 测试列表输入
        result = normalize_indicator_data_format([1, 2, 3])
        assert result == [1, 2, 3]

    def test_indicator_data_missing_output_name(self):
        """测试指标数据缺少output_name字段（覆盖第255-258行）"""
        indicator_data = {
            "indicators": [
                {
                    "name": "RSI",
                    "values": [
                        {
                            # 缺少output_name字段
                            "value": 123.456
                        },
                        {
                            "value": 456.789,
                            "values": [1, 2, 3],  # 这个字段存在，应该保持不变
                        },
                    ],
                }
            ]
        }

        result = normalize_indicator_data_format(indicator_data)

        # 验证缺少output_name的字段被添加默认值
        assert result["indicators"][0]["values"][0]["output_name"] == "output_0"
        assert (
            result["indicators"][0]["values"][0]["values"] == []
        )  # 缺少values字段时添加空列表

        # 验证所有字段都会被添加output_name（根据源码逻辑）
        assert result["indicators"][0]["values"][1]["output_name"] == "output_1"
        assert result["indicators"][0]["values"][1]["values"] == [1, 2, 3]  # 保持原值

    def test_decimal_precision(self):
        """测试小数精度处理"""
        indicator_data = {
            "symbol": "600000",
            "high_precision": 10.1234567890123456,
            "low_precision": 10.5,
            "zero_value": 0.0,
            "negative_value": -5.2,
        }

        result = normalize_indicator_data_format(indicator_data)

        # 精度应该保持
        assert result["high_precision"] == 10.1234567890123456
        assert result["low_precision"] == 10.5
        assert result["zero_value"] == 0.0
        assert result["negative_value"] == -5.2


class TestEdgeCasesAndErrorHandling:
    """边界条件和异常处理测试类"""

    def test_none_dataframe(self):
        """测试None DataFrame输入"""
        with pytest.raises(Exception):
            normalize_stock_data_format(None)

    def test_non_dataframe_input(self):
        """测试非DataFrame输入"""
        with pytest.raises(Exception):
            normalize_stock_data_format("not_a_dataframe")

    def test_mixed_data_types_in_dataframe(self):
        """测试DataFrame中的混合数据类型"""
        df = pd.DataFrame(
            {
                "symbol": ["600000"],
                "name": [None],
                "price": [10.5],
                "active": [True],
                "metadata": [{"key": "value"}],
            }
        )

        result = normalize_stock_data_format(df)

        # 混合数据类型应该被正确处理
        assert len(result) == 1
        assert pd.isna(result.iloc[0]["name"])

    def test_empty_string_handling(self):
        """测试空字符串处理"""
        df = pd.DataFrame(
            {
                "symbol": ["600000"],
                "name": [""],
                "industry": ["   "],
                "description": ["正常描述"],
            }
        )

        result = normalize_stock_data_format(df)

        # 空字符串应该被保留（源码不处理空字符串，只添加缺失的必需字段）
        assert result.iloc[0]["name"] == ""
        assert result.iloc[0]["industry"] == "   "  # 空格被保留，因为源码不做字符串清理

    def test_extreme_values(self):
        """测试极值处理"""
        df = pd.DataFrame(
            {
                "symbol": ["600000"],
                "volume": [999999999999],
                "pe": [999.999],
                "pb": [0.001],
                "change": [-50.0],
            }
        )

        result = normalize_stock_data_format(df)

        # 极值应该被保留
        assert result.iloc[0]["volume"] == 999999999999
        assert result.iloc[0]["pe"] == 999.999
        assert result.iloc[0]["pb"] == 0.001
        assert result.iloc[0]["change"] == -50.0


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
                }
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
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 处理大量数据
        large_df = pd.DataFrame(
            {
                "symbol": [f"60000{i}" for i in range(5000)],
                "data": [f"data_{i}" for i in range(5000)],
            }
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
            }
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
            }
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
            }
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
        import threading

        # 创建多个处理任务
        def create_test_data(batch_id):
            return pd.DataFrame(
                {
                    "symbol": [f"60000{batch_id}{i}" for i in range(10)],
                    "name": [f"股票{batch_id}{i}" for i in range(10)],
                    "industry": ["金融"] * 10,
                }
            )

        # 并发执行标准化
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(normalize_stock_data_format, create_test_data(i))
                for i in range(5)
            ]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # 验证结果
        assert len(results) == 5
        total_rows = sum(len(df) for df in results)
        assert total_rows == 50


class TestUncoveredCodePaths:
    """专门测试未覆盖代码路径的测试类"""

    def test_numeric_conversion_exception_with_actual_exception(self):
        """测试数值转换抛出异常的路径（覆盖第119-121行）"""
        # Mock pandas to_numeric to raise exception
        import pandas as pd
        from unittest.mock import patch

        df = pd.DataFrame(
            {
                "symbol": ["600000"],
                "open": ["10.5"],  # 字符串类型，会触发转换
            }
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
            }
        ]

        result = normalize_stock_list_format(stock_list)

        assert len(result) == 1
        assert result[0]["symbol"] == "N/A"  # 默认值
        assert result[0]["name"] == "测试股票"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
