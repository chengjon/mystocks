#!/usr/bin/env python3
"""
数据源格式兼容性校验工具测试套件 - 完整覆盖data_source_validator模块
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
import time
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 首先Mock掉有问题的导入，避免循环依赖
sys.modules["src.storage.database.connection_manager"] = Mock()
sys.modules["src.data_access"] = Mock()
sys.modules["src.database.database_service"] = Mock()
sys.modules["src.factories.data_source_factory"] = Mock()

import pytest

# 导入被测试的模块
from src.utils.data_source_validator import (
    compare_data_structure,
    validate_data_source_compatibility,
    run_compatibility_check,
)


class TestCompareDataStructure:
    """compare_data_structure函数测试类"""

    def test_basic_type_matching(self):
        """测试基本类型匹配"""
        # 测试相同的基本类型
        assert compare_data_structure("hello", "world") == []
        assert compare_data_structure(123, 456) == []
        assert compare_data_structure(True, False) == []
        assert compare_data_structure(None, None) == []

    def test_type_mismatch_detection(self):
        """测试类型不匹配检测"""
        # 测试不同类型
        errors = compare_data_structure("string", 123)
        assert len(errors) == 1
        assert "类型不一致" in errors[0]
        assert "Mock: <class 'str'>" in errors[0]
        assert "Real: <class 'int'>" in errors[0]

    def test_dict_structure_comparison(self):
        """测试字典结构比较"""
        # 完全相同的字典
        dict1 = {"a": 1, "b": 2}
        dict2 = {"a": 10, "b": 20}
        errors = compare_data_structure(dict1, dict2)
        assert errors == []  # 结构相同，值不同不算错误

        # 字典键不一致
        dict1 = {"a": 1, "b": 2, "c": 3}
        dict2 = {"a": 1, "b": 2, "d": 4}
        errors = compare_data_structure(dict1, dict2)
        assert len(errors) == 2
        assert any("真实数据缺少字段" in error and "['c']" in error for error in errors)
        assert any("Mock数据缺少字段" in error and "['d']" in error for error in errors)

    def test_nested_dict_comparison(self):
        """测试嵌套字典比较"""
        # 嵌套字典结构
        dict1 = {"level1": {"level2": {"data": "value"}, "simple": 123}}
        dict2 = {"level1": {"level2": {"data": "different_value"}, "simple": 456}}
        errors = compare_data_structure(dict1, dict2)
        assert errors == []  # 结构相同，值不同不算错误

        # 嵌套字典结构不一致
        dict1["level1"]["level2"]["extra"] = "extra_field"
        errors = compare_data_structure(dict1, dict2)
        assert len(errors) == 1
        assert "level1.level2" in errors[0]
        assert "真实数据缺少字段" in errors[0]

    def test_list_comparison(self):
        """测试列表比较"""
        # 相同长度的列表
        list1 = [1, 2, 3]
        list2 = [4, 5, 6]
        errors = compare_data_structure(list1, list2)
        assert errors == []  # 长度相同，值不同不算错误

        # 不同长度的列表
        list1 = [1, 2, 3, 4]
        list2 = [1, 2]
        errors = compare_data_structure(list1, list2)
        assert len(errors) == 1
        assert "列表长度不一致" in errors[0]
        assert "Mock: 4" in errors[0]
        assert "Real: 2" in errors[0]

    def test_nested_list_comparison(self):
        """测试嵌套列表比较"""
        # 嵌套列表
        list1 = [[1, 2], [3, 4]]
        list2 = [[5, 6], [7, 8]]
        errors = compare_data_structure(list1, list2)
        assert errors == []

        # 嵌套列表长度不一致
        list1 = [[1, 2, 3], [4, 5]]
        list2 = [[6, 7], [8, 9]]
        errors = compare_data_structure(list1, list2)
        assert len(errors) == 1
        assert "[0]" in errors[0]
        assert "列表长度不一致" in errors[0]

    def test_dataframe_comparison(self):
        """测试DataFrame比较"""
        # 相同结构的DataFrame
        df1 = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        df2 = pd.DataFrame({"col1": [5, 6], "col2": [7, 8]})
        errors = compare_data_structure(df1, df2)
        assert errors == []  # 列结构相同，值不同不算错误

        # 列名不一致的DataFrame
        df1 = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        df2 = pd.DataFrame({"col1": [5, 6], "col3": [7, 8]})
        errors = compare_data_structure(df1, df2)
        assert len(errors) == 2
        assert any(
            "真实DataFrame缺少列" in error and "['col2']" in error for error in errors
        )
        assert any(
            "Mock DataFrame缺少列" in error and "['col3']" in error for error in errors
        )

    def test_dataframe_type_mismatch(self):
        """测试DataFrame类型不匹配"""
        df = pd.DataFrame({"col1": [1, 2]})
        dict_data = {"col1": [1, 2]}
        errors = compare_data_structure(df, dict_data)
        assert len(errors) == 1
        assert "类型不一致" in errors[0]
        assert "DataFrame" in errors[0]
        # 精确匹配第74行的错误消息格式 (注意源代码使用简化的"DataFrame")
        assert "Mock: DataFrame, Real: <class 'dict'>" in errors[0]

        # 测试相反的情况，这会触发第26行的类型检查而不是第74行
        errors2 = compare_data_structure(dict_data, df)
        assert len(errors2) == 1
        assert "类型不一致" in errors2[0]
        assert (
            "Mock: <class 'dict'>, Real: <class 'pandas.core.frame.DataFrame'>"
            in errors2[0]
        )

        # 专门测试第74行：DataFrame vs 非DataFrame，field_path为空
        df2 = pd.DataFrame({"col1": [1, 2]})
        simple_list = [1, 2, 3]
        errors3 = compare_data_structure(df2, simple_list)
        assert len(errors3) == 1
        assert "Mock: DataFrame, Real: <class 'list'>" in errors3[0]

    def test_complex_nested_structure(self):
        """测试复杂嵌套结构"""
        # 复杂的嵌套结构
        complex1 = {
            "data": [
                {"id": 1, "values": [10, 20, 30]},
                {"id": 2, "values": [40, 50, 60]},
            ],
            "metadata": {"count": 2, "source": "test"},
        }
        complex2 = {
            "data": [
                {"id": 3, "values": [70, 80, 90]},
                {"id": 4, "values": [100, 110, 120]},
            ],
            "metadata": {"count": 2, "source": "production"},
        }
        errors = compare_data_structure(complex1, complex2)
        assert errors == []  # 结构完全相同

    def test_field_path_tracking(self):
        """测试字段路径跟踪"""
        dict1 = {"level1": {"level2": {"target": "value"}}}
        dict2 = {"level1": {"level2": {"target": "value", "extra": "field"}}}

        errors = compare_data_structure(dict1, dict2, "root")
        assert len(errors) == 1
        assert "root.level1.level2" in errors[0]

    def test_empty_structures(self):
        """测试空结构"""
        # 空字典和空列表
        assert compare_data_structure({}, {}) == []
        assert compare_data_structure([], []) == []
        assert compare_data_structure({}, []) != []  # 不同类型

    def test_mixed_type_nested_structures(self):
        """测试混合类型嵌套结构"""
        mixed1 = {
            "strings": ["a", "b", "c"],
            "numbers": [1, 2, 3],
            "nested": {"data": {"x": 1, "y": 2}, "list": [True, False]},
        }
        mixed2 = {
            "strings": ["d", "e", "f"],
            "numbers": [4, 5, 6],
            "nested": {"data": {"x": 3, "y": 4}, "list": [False, True]},
        }
        errors = compare_data_structure(mixed1, mixed2)
        assert errors == []  # 结构相同


class TestValidateDataSourceCompatibility:
    """validate_data_source_compatibility函数测试类"""

    @patch("src.utils.data_source_validator.MockDataSource")
    @patch("src.utils.data_source_validator.RealDataSource")
    def test_successful_validation(self, mock_real_class, mock_mock_class):
        """测试成功的验证"""
        # 创建Mock实例
        mock_source = Mock()
        real_source = Mock()

        # 设置方法返回值 - 所有方法返回相同结构
        common_return = {"status": "ok", "data": [1, 2, 3]}
        for method_name in [
            "get_stock_detail",
            "get_real_time_quote",
            "get_all_indicators",
            "get_trend_indicators",
            "get_momentum_indicators",
            "get_volatility_indicators",
            "get_volume_indicators",
            "get_trading_signals",
            "get_kline_data",
            "get_pattern_recognition",
            "get_monitoring_summary",
            "get_monitoring_status",
        ]:
            getattr(mock_source, method_name).return_value = common_return
            getattr(real_source, method_name).return_value = common_return

        # 设置带参数的方法
        getattr(mock_source, "get_stock_list").return_value = common_return
        getattr(real_source, "get_stock_list").return_value = common_return
        getattr(mock_source, "get_realtime_alerts").return_value = common_return
        getattr(real_source, "get_realtime_alerts").return_value = common_return

        # 执行验证
        result = validate_data_source_compatibility(mock_source, real_source)

        # 验证结果
        assert result["overall_status"] == "success"
        assert len(result["errors"]) == 0
        assert len(result["details"]) == 13  # 所有方法都应该被测试

        # 验证每个方法的详情
        for method_detail in result["details"].values():
            assert method_detail["status"] == "success"
            assert method_detail["message"] == "格式一致"

    @patch("src.utils.data_source_validator.MockDataSource")
    @patch("src.utils.data_source_validator.RealDataSource")
    def test_validation_with_structure_mismatch(self, mock_real_class, mock_mock_class):
        """测试结构不匹配的验证"""
        mock_source = Mock()
        real_source = Mock()

        # 设置返回值以产生结构不匹配
        mock_return = {"field1": "value1", "field2": "value2"}
        real_return = {"field1": "value1", "field3": "value3"}  # 字段2和3不同

        # 设置所有方法返回不匹配的结构
        for method_name in [
            "get_stock_detail",
            "get_real_time_quote",
            "get_all_indicators",
        ]:
            getattr(mock_source, method_name).return_value = mock_return
            getattr(real_source, method_name).return_value = real_return

        # 设置其他方法返回匹配的结构
        matching_return = {"status": "ok"}
        for method_name in [
            "get_trend_indicators",
            "get_momentum_indicators",
            "get_volatility_indicators",
        ]:
            getattr(mock_source, method_name).return_value = matching_return
            getattr(real_source, method_name).return_value = matching_return

        # 设置带参数的方法
        getattr(mock_source, "get_stock_list").return_value = matching_return
        getattr(real_source, "get_stock_list").return_value = matching_return
        getattr(mock_source, "get_realtime_alerts").return_value = matching_return
        getattr(real_source, "get_realtime_alerts").return_value = matching_return

        # 剩余方法
        remaining_methods = [
            "get_volume_indicators",
            "get_trading_signals",
            "get_kline_data",
            "get_pattern_recognition",
            "get_monitoring_summary",
            "get_monitoring_status",
        ]
        for method_name in remaining_methods:
            getattr(mock_source, method_name).return_value = matching_return
            getattr(real_source, method_name).return_value = matching_return

        # 执行验证
        result = validate_data_source_compatibility(mock_source, real_source)

        # 验证结果
        assert result["overall_status"] == "failed"
        assert len(result["errors"]) == 6  # 3个方法 * 2个字段错误 = 6个错误
        assert len(result["details"]) == 13

        # 验证失败的方法
        failed_methods = [
            "get_stock_detail",
            "get_real_time_quote",
            "get_all_indicators",
        ]
        for method_name in failed_methods:
            assert result["details"][method_name]["status"] == "failed"
            assert len(result["details"][method_name]["errors"]) == 2

    @patch("src.utils.data_source_validator.MockDataSource")
    @patch("src.utils.data_source_validator.RealDataSource")
    def test_validation_with_exceptions(self, mock_real_class, mock_mock_class):
        """测试异常情况的验证"""
        mock_source = Mock()
        real_source = Mock()

        # 让某些方法抛出异常
        exception_methods = ["get_stock_detail", "get_real_time_quote"]
        for method_name in exception_methods:
            getattr(mock_source, method_name).side_effect = Exception("Mock error")
            getattr(real_source, method_name).side_effect = Exception("Real error")

        # 设置其他方法正常返回
        normal_return = {"status": "ok"}
        for method_name in [
            "get_all_indicators",
            "get_trend_indicators",
            "get_momentum_indicators",
            "get_volatility_indicators",
            "get_trading_signals",
            "get_kline_data",
            "get_pattern_recognition",
            "get_monitoring_summary",
            "get_monitoring_status",
        ]:
            getattr(mock_source, method_name).return_value = normal_return
            getattr(real_source, method_name).return_value = normal_return

        # 设置带参数的方法
        getattr(mock_source, "get_stock_list").return_value = normal_return
        getattr(real_source, "get_stock_list").return_value = normal_return
        getattr(mock_source, "get_realtime_alerts").return_value = normal_return
        getattr(real_source, "get_realtime_alerts").return_value = normal_return

        # 执行验证
        result = validate_data_source_compatibility(mock_source, real_source)

        # 验证结果
        assert result["overall_status"] == "failed"
        assert len(result["errors"]) == 2  # 2个方法抛出异常
        assert len(result["details"]) == 13

        # 验证异常方法
        for method_name in exception_methods:
            assert result["details"][method_name]["status"] == "error"
            assert (
                "执行失败" in result["details"][method_name]["error"]
                or "Mock error" in result["details"][method_name]["error"]
            )

    def test_custom_test_stock_parameter(self):
        """测试自定义测试股票参数"""
        mock_source = Mock()
        real_source = Mock()

        # 设置返回值
        mock_source.get_stock_detail.return_value = {"symbol": "AAPL"}
        real_source.get_stock_detail.return_value = {"symbol": "AAPL"}

        # 所有方法返回相同的简单值
        simple_return = {"test": "data"}
        for method_name in [
            "get_real_time_quote",
            "get_all_indicators",
            "get_trend_indicators",
            "get_momentum_indicators",
            "get_volatility_indicators",
            "get_trading_signals",
            "get_kline_data",
            "get_pattern_recognition",
            "get_monitoring_summary",
            "get_monitoring_status",
        ]:
            getattr(mock_source, method_name).return_value = simple_return
            getattr(real_source, method_name).return_value = simple_return

        # 带参数的方法
        getattr(mock_source, "get_stock_list").return_value = simple_return
        getattr(real_source, "get_stock_list").return_value = simple_return
        getattr(mock_source, "get_realtime_alerts").return_value = simple_return
        getattr(real_source, "get_realtime_alerts").return_value = simple_return

        # 使用自定义股票代码执行验证
        result = validate_data_source_compatibility(mock_source, real_source, "AAPL")

        # 验证调用
        mock_source.get_stock_detail.assert_called_once_with("AAPL")
        real_source.get_stock_detail.assert_called_once_with("AAPL")
        assert result["overall_status"] == "success"

    def test_empty_data_sources(self):
        """测试空数据源"""
        mock_source = Mock()
        real_source = Mock()

        # 所有方法返回空数据
        empty_return = {}
        for method_name in [
            "get_stock_detail",
            "get_real_time_quote",
            "get_all_indicators",
            "get_trend_indicators",
            "get_momentum_indicators",
            "get_volatility_indicators",
        ]:
            getattr(mock_source, method_name).return_value = empty_return
            getattr(real_source, method_name).return_value = empty_return

        # 带参数的方法
        getattr(mock_source, "get_stock_list").return_value = empty_return
        getattr(real_source, "get_stock_list").return_value = empty_return
        getattr(mock_source, "get_realtime_alerts").return_value = empty_return
        getattr(real_source, "get_realtime_alerts").return_value = empty_return

        # 剩余方法
        remaining_methods = [
            "get_volume_indicators",
            "get_trading_signals",
            "get_kline_data",
            "get_pattern_recognition",
            "get_monitoring_summary",
            "get_monitoring_status",
        ]
        for method_name in remaining_methods:
            getattr(mock_source, method_name).return_value = empty_return
            getattr(real_source, method_name).return_value = empty_return

        result = validate_data_source_compatibility(mock_source, real_source)
        assert result["overall_status"] == "success"


class TestRunCompatibilityCheck:
    """run_compatibility_check函数测试类"""

    @patch("src.utils.data_source_validator.validate_data_source_compatibility")
    @patch("src.utils.data_source_validator.MockDataSource")
    @patch("src.utils.data_source_validator.RealDataSource")
    def test_successful_check_function_only(
        self, mock_real_class, mock_mock_class, mock_validate
    ):
        """测试成功的检查（不包含sys.exit验证）"""
        # 模拟成功的验证结果
        mock_validate.return_value = {
            "overall_status": "success",
            "errors": [],
            "details": {"method1": {"status": "success"}},
        }

        # 执行检查
        result = run_compatibility_check()

        # 验证结果
        assert result["overall_status"] == "success"
        mock_validate.assert_called_once()

    @patch("src.utils.data_source_validator.validate_data_source_compatibility")
    @patch("src.utils.data_source_validator.MockDataSource")
    @patch("src.utils.data_source_validator.RealDataSource")
    def test_failed_check_function_only(
        self, mock_real_class, mock_mock_class, mock_validate
    ):
        """测试失败的检查（不包含sys.exit验证）"""
        # 模拟失败的验证结果
        mock_validate.return_value = {
            "overall_status": "failed",
            "errors": ["Error 1", "Error 2"],
            "details": {
                "method1": {"status": "failed", "errors": ["Structure mismatch"]}
            },
        }

        # 执行检查
        result = run_compatibility_check()

        # 验证结果
        assert result["overall_status"] == "failed"
        assert len(result["errors"]) == 2
        mock_validate.assert_called_once()

    @patch("src.utils.data_source_validator.validate_data_source_compatibility")
    @patch("src.utils.data_source_validator.MockDataSource")
    @patch("src.utils.data_source_validator.RealDataSource")
    def test_data_source_creation(
        self, mock_real_class, mock_mock_class, mock_validate
    ):
        """测试数据源实例创建"""
        # 模拟数据源类
        mock_instance = Mock()
        mock_mock_class.return_value = mock_instance
        mock_real_class.return_value = mock_instance

        # 模拟验证结果
        mock_validate.return_value = {
            "overall_status": "success",
            "errors": [],
            "details": {},
        }

        # 执行检查
        run_compatibility_check()

        # 验证数据源实例被创建
        mock_mock_class.assert_called_once()
        mock_real_class.assert_called_once()
        mock_validate.assert_called_once_with(mock_instance, mock_instance)


from scripts._test_data_source_validator_tail import (
    TestIntegrationScenarios,
    TestPerformanceAndScalability,
)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
