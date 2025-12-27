"""
Data Processor Factory Simple Test Suite
数据处理器工厂简单测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.gpu.data_processor_factory (58行)
测试重点: 基础功能，避免复杂依赖Mocking
"""

import pytest
from unittest.mock import patch
import sys
import os

# 添加src路径到导入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))


class TestDataProcessorFactorySimple:
    """数据处理器工厂简单测试"""

    def test_factory_class_exists(self):
        """测试工厂类存在"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 验证类存在
        assert DataProcessorFactory is not None

        # 验证方法存在
        assert hasattr(DataProcessorFactory, "get_processor")
        assert hasattr(DataProcessorFactory, "get_processor_type")

    def test_get_processor_method_signature(self):
        """测试get_processor方法签名"""
        from gpu.data_processor_factory import DataProcessorFactory
        import inspect

        # 获取方法签名
        sig = inspect.signature(DataProcessorFactory.get_processor)

        # 验证参数
        assert "gpu_enabled" in sig.parameters
        assert sig.parameters["gpu_enabled"].default is None

    def test_get_processor_type_method_signature(self):
        """测试get_processor_type方法签名"""
        from gpu.data_processor_factory import DataProcessorFactory
        import inspect

        # 获取方法签名
        sig = inspect.signature(DataProcessorFactory.get_processor_type)

        # 验证参数
        assert "processor_type" in sig.parameters

    def test_get_processor_returns_something(self):
        """测试get_processor返回值类型"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 调用方法（不关心具体类型）
        processor = DataProcessorFactory.get_processor()

        # 验证返回了某个对象
        assert processor is not None

    @patch.dict(os.environ, {"ENABLE_GPU_ACCELERATION": "true"})
    def test_get_processor_with_gpu_env(self):
        """测试有GPU环境变量时的行为"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 调用方法
        processor = DataProcessorFactory.get_processor()

        # 验证返回了某个对象
        assert processor is not None

    def test_get_processor_explicit_false(self):
        """测试显式指定gpu_enabled=False"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 调用方法
        processor = DataProcessorFactory.get_processor(gpu_enabled=False)

        # 验证返回了某个对象
        assert processor is not None

    def test_get_processor_explicit_true(self):
        """测试显式指定gpu_enabled=True"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 调用方法
        processor = DataProcessorFactory.get_processor(gpu_enabled=True)

        # 验证返回了某个对象
        assert processor is not None

    def test_get_processor_type_cpu_string(self):
        """测试通过'cpu'字符串获取处理器类型"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 调用方法
        processor_type = DataProcessorFactory.get_processor_type("cpu")

        # 验证返回了某个类型
        assert processor_type is not None
        assert callable(processor_type)

    def test_get_processor_type_gpu_string(self):
        """测试通过'gpu'字符串获取处理器类型"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 调用方法
        processor_type = DataProcessorFactory.get_processor_type("gpu")

        # 验证返回了某个类型
        assert processor_type is not None
        assert callable(processor_type)

    def test_get_processor_type_uppercase_cpu(self):
        """测试大写'CPU'字符串"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 调用方法
        processor_type = DataProcessorFactory.get_processor_type("CPU")

        # 验证返回了某个类型
        assert processor_type is not None
        assert callable(processor_type)

    def test_get_processor_type_uppercase_gpu(self):
        """测试大写'GPU'字符串"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 调用方法
        processor_type = DataProcessorFactory.get_processor_type("GPU")

        # 验证返回了某个类型
        assert processor_type is not None
        assert callable(processor_type)

    def test_get_processor_type_invalid_string(self):
        """测试无效处理器类型异常"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 验证抛出异常
        with pytest.raises(ValueError):
            DataProcessorFactory.get_processor_type("invalid")

    def test_get_processor_type_empty_string(self):
        """测试空字符串异常"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 验证抛出异常
        with pytest.raises(ValueError):
            DataProcessorFactory.get_processor_type("")

    def test_get_processor_type_none_value(self):
        """测试None值异常"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 验证抛出异常
        with pytest.raises((ValueError, AttributeError)):
            DataProcessorFactory.get_processor_type(None)

    def test_factory_static_methods(self):
        """测试工厂方法是静态方法"""
        from gpu.data_processor_factory import DataProcessorFactory
        import inspect

        # 验证是静态方法
        assert isinstance(inspect.getattr_static(DataProcessorFactory, "get_processor"), staticmethod)
        assert isinstance(
            inspect.getattr_static(DataProcessorFactory, "get_processor_type"),
            staticmethod,
        )

    def test_factory_module_import(self):
        """测试工厂模块可以正常导入"""
        import gpu.data_processor_factory

        # 验证模块导入成功
        assert gpu.data_processor_factory is not None

        # 验证类存在
        assert hasattr(gpu.data_processor_factory, "DataProcessorFactory")

    def test_processor_types_are_different(self):
        """测试CPU和GPU处理器类型不同"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 获取两种处理器类型
        cpu_type = DataProcessorFactory.get_processor_type("cpu")
        gpu_type = DataProcessorFactory.get_processor_type("gpu")

        # 验证类型不同
        assert cpu_type != gpu_type

    def test_processor_types_same_string(self):
        """测试相同字符串返回相同类型"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 获取两次相同类型
        cpu_type1 = DataProcessorFactory.get_processor_type("cpu")
        cpu_type2 = DataProcessorFactory.get_processor_type("cpu")

        # 验证类型相同
        assert cpu_type1 == cpu_type2

    def test_case_insensitive_processor_type(self):
        """测试处理器类型大小写不敏感"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 获取不同大小写的相同类型
        cpu_lower = DataProcessorFactory.get_processor_type("cpu")
        cpu_upper = DataProcessorFactory.get_processor_type("CPU")

        # 验证类型相同
        assert cpu_lower == cpu_upper

    def test_processor_creation_flow(self):
        """测试处理器创建流程"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 1. 获取处理器类型
        cpu_type = DataProcessorFactory.get_processor_type("cpu")

        # 2. 创建处理器实例
        processor1 = DataProcessorFactory.get_processor(gpu_enabled=False)
        processor2 = cpu_type()

        # 3. 验证都是有效对象
        assert processor1 is not None
        assert processor2 is not None

    def test_factory_consistency(self):
        """测试工厂方法的一致性"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 通过不同方式获取CPU处理器
        processor1 = DataProcessorFactory.get_processor(gpu_enabled=False)
        cpu_type = DataProcessorFactory.get_processor_type("cpu")
        processor2 = cpu_type()

        # 验证都是有效实例
        assert processor1 is not None
        assert processor2 is not None
        assert type(processor1).__name__ == type(processor2).__name__


class TestDataProcessorFactoryIntegrationSimple:
    """数据处理器工厂集成测试 - 简化版"""

    def test_full_workflow_simulation(self):
        """模拟完整工作流程"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 1. 检查可用的处理器类型
        cpu_type = DataProcessorFactory.get_processor_type("cpu")
        gpu_type = DataProcessorFactory.get_processor_type("gpu")

        # 2. 验证类型有效
        assert cpu_type is not None
        assert gpu_type is not None

        # 3. 创建处理器实例
        processor_cpu = DataProcessorFactory.get_processor(gpu_enabled=False)

        # 4. 验证实例创建成功
        assert processor_cpu is not None

    def test_environment_variable_handling(self):
        """测试环境变量处理"""
        import os
        from gpu.data_processor_factory import DataProcessorFactory

        # 备份原始环境变量
        original_value = os.environ.get("ENABLE_GPU_ACCELERATION")

        try:
            # 测试不同环境变量值
            test_values = ["true", "false", "invalid", ""]

            for value in test_values:
                os.environ["ENABLE_GPU_ACCELERATION"] = value

                # 获取处理器（应该不抛出异常）
                processor = DataProcessorFactory.get_processor()
                assert processor is not None

        finally:
            # 恢复原始环境变量
            if original_value is not None:
                os.environ["ENABLE_GPU_ACCELERATION"] = original_value
            else:
                os.environ.pop("ENABLE_GPU_ACCELERATION", None)

    def test_error_handling_robustness(self):
        """测试错误处理的健壮性"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 测试各种无效输入不会导致崩溃
        invalid_types = ["invalid", "123", "cpu_gpu", "GPU_CPU", None, ""]

        for invalid_type in invalid_types:
            try:
                DataProcessorFactory.get_processor_type(invalid_type)
                # 如果没有抛出异常，说明输入被接受了
                pass
            except (ValueError, AttributeError, TypeError):
                # 预期的异常类型
                pass
            except Exception as e:
                # 不应该有其他异常
                pytest.fail(f"Unexpected exception for input {invalid_type}: {e}")

    def test_factory_design_patterns(self):
        """测试工厂设计模式"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 验证工厂模式特征
        assert hasattr(DataProcessorFactory, "get_processor")  # 工厂方法
        assert hasattr(DataProcessorFactory, "get_processor_type")  # 类型方法

        # 验证方法可调用
        assert callable(getattr(DataProcessorFactory, "get_processor"))
        assert callable(getattr(DataProcessorFactory, "get_processor_type"))

    def test_method_call_count(self):
        """测试方法调用计数"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 多次调用相同方法，确保行为一致
        processors = [DataProcessorFactory.get_processor() for _ in range(5)]

        # 验证所有调用都成功
        for processor in processors:
            assert processor is not None

    def test_type_return_consistency(self):
        """测试类型返回的一致性"""
        from gpu.data_processor_factory import DataProcessorFactory

        # 多次获取相同类型
        cpu_types = [DataProcessorFactory.get_processor_type("cpu") for _ in range(3)]
        gpu_types = [DataProcessorFactory.get_processor_type("gpu") for _ in range(3)]

        # 验证一致性
        for cpu_type in cpu_types:
            assert cpu_type == cpu_types[0]

        for gpu_type in gpu_types:
            assert gpu_type == gpu_types[0]


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--no-cov"])
