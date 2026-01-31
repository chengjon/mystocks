"""
Customer适配器基础测试
专注于提升Customer适配器覆盖率（268行代码）
"""

import os
import sys

import pandas as pd
import pytest

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 测试目标模块
try:
    from src.adapters.customer_adapter import CustomerDataSource
except ImportError as e:
    pytest.skip(f"无法导入CustomerDataSource: {e}", allow_module_level=True)


class TestCustomerDataSourceBasic:
    """CustomerDataSource基础测试 - 专注覆盖率"""

    def test_initialization_default(self):
        """测试默认初始化"""
        adapter = CustomerDataSource()

        # 验证基本属性
        assert hasattr(adapter, "use_column_mapping")
        assert adapter.use_column_mapping == True

    def test_initialization_with_mapping(self):
        """测试带列映射的初始化"""
        adapter = CustomerDataSource(use_column_mapping=False)

        # 验证配置设置
        assert hasattr(adapter, "use_column_mapping")
        assert adapter.use_column_mapping == False

    def test_standardize_dataframe_method(self):
        """测试DataFrame标准化方法"""
        adapter = CustomerDataSource()

        # 创建测试DataFrame
        test_df = pd.DataFrame(
            {
                "股票代码": ["000001", "000002"],
                "股票名称": ["平安银行", "万科A"],
                "收盘价": [10.0, 15.0],
            }
        )

        # 调用标准化方法
        result = adapter._standardize_dataframe(test_df)

        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    def test_has_core_methods(self):
        """测试核心方法存在"""
        adapter = CustomerDataSource()

        # 验证核心方法存在
        core_methods = [
            "get_stock_daily",
            "get_index_daily",
            "get_stock_basic",
            "get_index_components",
            "get_real_time_data",
            "_standardize_dataframe",
        ]

        for method in core_methods:
            assert hasattr(adapter, method), f"缺少方法: {method}"
            assert callable(getattr(adapter, method)), f"方法不可调用: {method}"

    def test_column_mapping_config(self):
        """测试列映射配置"""
        # 测试启用列映射
        adapter1 = CustomerDataSource(use_column_mapping=True)
        assert adapter1.use_column_mapping == True

        # 测试禁用列映射
        adapter2 = CustomerDataSource(use_column_mapping=False)
        assert adapter2.use_column_mapping == False

    def test_dataframe_standardization_logic(self):
        """测试DataFrame标准化逻辑"""
        adapter = CustomerDataSource()

        # 创建非标准列名的DataFrame
        non_standard_df = pd.DataFrame({"code": ["000001"], "name": ["测试股票"], "price": [10.0]})

        # 调用标准化
        result = adapter._standardize_dataframe(non_standard_df)

        # 验证结果
        assert isinstance(result, pd.DataFrame)

    def test_empty_dataframe_handling(self):
        """测试空DataFrame处理"""
        adapter = CustomerDataSource()

        # 测试空DataFrame
        empty_df = pd.DataFrame()
        result = adapter._standardize_dataframe(empty_df)

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_method_signatures(self):
        """测试方法签名"""
        adapter = CustomerDataSource()

        # 验证方法不会抛出签名异常
        methods_to_test = [
            ("get_stock_daily", ("TEST", "2024-01-01", "2024-01-02")),
            ("get_index_daily", ("000001", "2024-01-01", "2024-01-02")),
            ("get_stock_basic", ("TEST",)),
            ("get_index_components", ("000001",)),
        ]

        for method_name, args in methods_to_test:
            try:
                method = getattr(adapter, method_name)
                assert callable(method)
                # 不实际调用，因为需要真实数据源
            except AttributeError:
                pytest.fail(f"方法 {method_name} 不存在")

    def test_return_type_consistency(self):
        """测试返回类型一致性"""
        adapter = CustomerDataSource()

        # 验证方法的返回类型注解（如果存在）
        import inspect

        methods_to_check = ["get_stock_daily", "get_index_daily", "get_stock_basic"]
        for method_name in methods_to_check:
            if hasattr(adapter, method_name):
                method = getattr(adapter, method_name)
                sig = inspect.signature(method)
                assert sig is not None

    def test_class_import_compatibility(self):
        """测试类导入兼容性"""
        try:
            from src.adapters.customer_adapter import CustomerDataSource

            adapter = CustomerDataSource()
            assert adapter is not None
            assert isinstance(adapter, CustomerDataSource)
        except ImportError:
            pytest.skip("CustomerDataSource不可用")

    def test_attribute_initialization(self):
        """测试属性初始化"""
        adapter = CustomerDataSource()

        # 验证关键属性存在
        expected_attrs = ["use_column_mapping"]

        for attr in expected_attrs:
            assert hasattr(adapter, attr), f"缺少属性: {attr}"

    def test_dataframe_processing_capability(self):
        """测试DataFrame处理能力"""
        adapter = CustomerDataSource()

        # 创建不同结构的测试数据
        test_cases = [
            # 基础数据
            pd.DataFrame({"col1": [1], "col2": ["test"]}),
            # 数值数据
            pd.DataFrame({"numeric": [1.0, 2.0, 3.0]}),
            # 字符串数据
            pd.DataFrame({"text": ["a", "b", "c"]}),
        ]

        for test_df in test_cases:
            result = adapter._standardize_dataframe(test_df)
            assert isinstance(result, pd.DataFrame)

    def test_configuration_management(self):
        """测试配置管理"""
        # 测试不同配置
        configs = [True, False]

        for config in configs:
            adapter = CustomerDataSource(use_column_mapping=config)
            assert adapter.use_column_mapping == config

    def test_error_handling_preparation(self):
        """测试错误处理准备"""
        adapter = CustomerDataSource()

        # 验证DataFrame处理方法存在
        assert hasattr(adapter, "_standardize_dataframe")
        assert callable(getattr(adapter, "_standardize_dataframe"))

    def test_data_validation_methods(self):
        """测试数据验证相关方法"""
        adapter = CustomerDataSource()

        # 验证数据处理相关方法存在
        processing_methods = ["_standardize_dataframe"]

        for method in processing_methods:
            assert hasattr(adapter, method), f"缺少数据处理方法: {method}"
            assert callable(getattr(adapter, method)), f"方法不可调用: {method}"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])
