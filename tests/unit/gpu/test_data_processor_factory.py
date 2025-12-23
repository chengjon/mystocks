"""
Data Processor Factory Test Suite
数据处理器工厂测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.gpu.data_processor_factory (58行)
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# 添加src路径到导入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))


class MockDataProcessor:
    """模拟数据处理器基类"""

    pass


class MockCPUDataProcessor(MockDataProcessor):
    """模拟CPU数据处理器"""

    def __init__(self):
        self.processor_type = "cpu"


class MockGPUDataProcessorFixed(MockDataProcessor):
    """模拟GPU数据处理器"""

    def __init__(self, gpu_enabled=True):
        self.processor_type = "gpu"
        self.gpu_enabled = gpu_enabled


class TestDataProcessorFactory:
    """数据处理器工厂测试"""

    @patch.dict(os.environ, {"ENABLE_GPU_ACCELERATION": "false"})
    def test_get_processor_default_cpu(self):
        """测试默认获取CPU处理器"""
        # 模拟依赖
        with patch(
            "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
        ):
            from gpu.data_processor_factory import DataProcessorFactory

            processor = DataProcessorFactory.get_processor()

            assert processor.processor_type == "cpu"
            assert hasattr(processor, "processor_type")

    @patch.dict(os.environ, {"ENABLE_GPU_ACCELERATION": "true"})
    def test_get_processor_env_gpu_enabled(self):
        """测试通过环境变量启用GPU处理器"""
        with (
            patch(
                "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
            ),
            patch(
                "src.gpu.data_processor_factory.GPUDataProcessorFixed",
                MockGPUDataProcessorFixed,
            ),
            patch("builtins.__import__") as mock_import,
        ):

            def mock_import_func(name, *args, **kwargs):
                if name in ["cudf", "cupy"]:
                    return Mock()  # 模拟成功导入
                return __builtins__["__import__"](name, *args, **kwargs)

            mock_import.side_effect = mock_import_func

            from gpu.data_processor_factory import DataProcessorFactory

            processor = DataProcessorFactory.get_processor()

            assert processor.processor_type == "gpu"
            assert processor.gpu_enabled is True

    @patch.dict(os.environ, {"ENABLE_GPU_ACCELERATION": "true"})
    def test_get_processor_gpu_fallback_to_cpu(self):
        """测试GPU不可用时回退到CPU"""
        with (
            patch(
                "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
            ),
            patch("builtins.print") as mock_print,
            patch("builtins.__import__") as mock_import,
        ):

            def mock_import_func(name, *args, **kwargs):
                if name in ["cudf", "cupy"]:
                    raise ImportError(f"No module named '{name}'")
                return __builtins__["__import__"](name, *args, **kwargs)

            mock_import.side_effect = mock_import_func

            from gpu.data_processor_factory import DataProcessorFactory

            processor = DataProcessorFactory.get_processor()

            assert processor.processor_type == "cpu"
            mock_print.assert_called_with(
                "GPU加速环境（cuDF/cuPy）未就绪，回退到CPU处理器。"
            )

    def test_get_processor_explicit_cpu(self):
        """测试显式指定CPU处理器"""
        with patch(
            "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
        ):
            from gpu.data_processor_factory import DataProcessorFactory

            processor = DataProcessorFactory.get_processor(gpu_enabled=False)

            assert processor.processor_type == "cpu"

    def test_get_processor_explicit_gpu_success(self):
        """测试显式指定GPU处理器且成功"""
        with (
            patch(
                "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
            ),
            patch(
                "src.gpu.data_processor_factory.GPUDataProcessorFixed",
                MockGPUDataProcessorFixed,
            ),
            patch("builtins.__import__") as mock_import,
        ):

            def mock_import_func(name, *args, **kwargs):
                if name in ["cudf", "cupy"]:
                    return Mock()
                return __builtins__["__import__"](name, *args, **kwargs)

            mock_import.side_effect = mock_import_func

            from gpu.data_processor_factory import DataProcessorFactory

            processor = DataProcessorFactory.get_processor(gpu_enabled=True)

            assert processor.processor_type == "gpu"
            assert processor.gpu_enabled is True

    def test_get_processor_explicit_gpu_fallback(self):
        """测试显式指定GPU处理器但失败回退"""
        with (
            patch(
                "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
            ),
            patch("builtins.print") as mock_print,
            patch("builtins.__import__") as mock_import,
        ):

            def mock_import_func(name, *args, **kwargs):
                if name in ["cudf", "cupy"]:
                    raise ImportError(f"No module named '{name}'")
                return __builtins__["__import__"](name, *args, **kwargs)

            mock_import.side_effect = mock_import_func

            from gpu.data_processor_factory import DataProcessorFactory

            processor = DataProcessorFactory.get_processor(gpu_enabled=True)

            assert processor.processor_type == "cpu"
            mock_print.assert_called_with(
                "GPU加速环境（cuDF/cuPy）未就绪，回退到CPU处理器。"
            )

    def test_get_processor_type_cpu(self):
        """测试通过字符串获取CPU处理器类型"""
        with (
            patch(
                "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
            ),
            patch(
                "src.gpu.data_processor_factory.GPUDataProcessorFixed",
                MockGPUDataProcessorFixed,
            ),
        ):
            from gpu.data_processor_factory import DataProcessorFactory

            processor_type = DataProcessorFactory.get_processor_type("cpu")

            assert processor_type == MockCPUDataProcessor

    def test_get_processor_type_gpu(self):
        """测试通过字符串获取GPU处理器类型"""
        with (
            patch(
                "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
            ),
            patch(
                "src.gpu.data_processor_factory.GPUDataProcessorFixed",
                MockGPUDataProcessorFixed,
            ),
        ):
            from gpu.data_processor_factory import DataProcessorFactory

            processor_type = DataProcessorFactory.get_processor_type("gpu")

            assert processor_type == MockGPUDataProcessorFixed

    def test_get_processor_type_cpu_uppercase(self):
        """测试通过大写字符串获取CPU处理器类型"""
        with (
            patch(
                "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
            ),
            patch(
                "src.gpu.data_processor_factory.GPUDataProcessorFixed",
                MockGPUDataProcessorFixed,
            ),
        ):
            from gpu.data_processor_factory import DataProcessorFactory

            processor_type = DataProcessorFactory.get_processor_type("CPU")

            assert processor_type == MockCPUDataProcessor

    def test_get_processor_type_gpu_uppercase(self):
        """测试通过大写字符串获取GPU处理器类型"""
        with (
            patch(
                "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
            ),
            patch(
                "src.gpu.data_processor_factory.GPUDataProcessorFixed",
                MockGPUDataProcessorFixed,
            ),
        ):
            from gpu.data_processor_factory import DataProcessorFactory

            processor_type = DataProcessorFactory.get_processor_type("GPU")

            assert processor_type == MockGPUDataProcessorFixed

    def test_get_processor_type_invalid(self):
        """测试无效处理器类型异常"""
        from gpu.data_processor_factory import DataProcessorFactory

        with pytest.raises(ValueError, match="Unsupported processor type"):
            DataProcessorFactory.get_processor_type("invalid")

    def test_get_processor_type_empty_string(self):
        """测试空字符串处理器类型异常"""
        from gpu.data_processor_factory import DataProcessorFactory

        with pytest.raises(ValueError, match="Unsupported processor type"):
            DataProcessorFactory.get_processor_type("")

    def test_get_processor_type_none(self):
        """测试None处理器类型异常"""
        from gpu.data_processor_factory import DataProcessorFactory

        with pytest.raises(ValueError, match="Unsupported processor type"):
            DataProcessorFactory.get_processor_type(None)

    @patch.dict(os.environ, {"ENABLE_GPU_ACCELERATION": "invalid_value"})
    def test_get_processor_invalid_env_value(self):
        """测试无效环境变量值"""
        with patch(
            "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
        ):
            from gpu.data_processor_factory import DataProcessorFactory

            processor = DataProcessorFactory.get_processor()

            # 无效值应该被当作false处理
            assert processor.processor_type == "cpu"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_processor_no_env_variable(self):
        """测试没有环境变量时的默认行为"""
        with patch(
            "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
        ):
            from gpu.data_processor_factory import DataProcessorFactory

            processor = DataProcessorFactory.get_processor()

            # 没有环境变量时默认是CPU
            assert processor.processor_type == "cpu"


class TestDataProcessorFactoryIntegration:
    """数据处理器工厂集成测试"""

    @patch.dict(os.environ, {"ENABLE_GPU_ACCELERATION": "true"})
    def test_gpu_detection_and_creation_flow(self):
        """测试GPU检测和创建的完整流程"""
        with (
            patch(
                "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
            ),
            patch(
                "src.gpu.data_processor_factory.GPUDataProcessorFixed",
                MockGPUDataProcessorFixed,
            ),
            patch("builtins.__import__") as mock_import,
        ):
            # 模拟GPU库存在
            mock_import.return_value = Mock()

            from gpu.data_processor_factory import DataProcessorFactory

            # 测试从环境变量检测
            processor = DataProcessorFactory.get_processor()
            assert processor.processor_type == "gpu"

            # 测试显式指定GPU
            processor2 = DataProcessorFactory.get_processor(gpu_enabled=True)
            assert processor2.processor_type == "gpu"

            # 测试显式指定CPU
            processor3 = DataProcessorFactory.get_processor(gpu_enabled=False)
            assert processor3.processor_type == "cpu"

    @patch.dict(os.environ, {"ENABLE_GPU_ACCELERATION": "true"})
    def test_gpu_unavailable_handling(self):
        """测试GPU不可用时的处理流程"""
        with (
            patch(
                "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
            ),
            patch("builtins.print") as mock_print,
            patch("builtins.__import__") as mock_import,
        ):
            # 模拟GPU库不可用
            def mock_import_func(name, *args, **kwargs):
                if name in ["cudf", "cupy"]:
                    raise ImportError(f"No module named '{name}'")
                return __builtins__["__import__"](name, *args, **kwargs)

            mock_import.side_effect = mock_import_func

            from gpu.data_processor_factory import DataProcessorFactory

            # 应该自动回退到CPU
            processor = DataProcessorFactory.get_processor()
            assert processor.processor_type == "cpu"

            # 验证提示消息
            mock_print.assert_called_once()

    def test_processor_type_consistency(self):
        """测试处理器类型的一致性"""
        with (
            patch(
                "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
            ),
            patch(
                "src.gpu.data_processor_factory.GPUDataProcessorFixed",
                MockGPUDataProcessorFixed,
            ),
        ):
            from gpu.data_processor_factory import DataProcessorFactory

            # 获取处理器类型
            cpu_type = DataProcessorFactory.get_processor_type("cpu")
            gpu_type = DataProcessorFactory.get_processor_type("gpu")

            # 创建实例
            cpu_instance = cpu_type()
            gpu_instance = gpu_type()

            # 验证实例类型正确
            assert cpu_instance.processor_type == "cpu"
            assert gpu_instance.processor_type == "gpu"

    def test_factory_method_vs_type_method(self):
        """测试工厂方法和类型方法的一致性"""
        with (
            patch(
                "src.gpu.data_processor_factory.CPUDataProcessor", MockCPUDataProcessor
            ),
            patch(
                "src.gpu.data_processor_factory.GPUDataProcessorFixed",
                MockGPUDataProcessorFixed,
            ),
            patch("builtins.__import__") as mock_import,
        ):
            mock_import.return_value = Mock()

            from gpu.data_processor_factory import DataProcessorFactory

            # 通过工厂方法获取
            factory_cpu = DataProcessorFactory.get_processor(gpu_enabled=False)
            factory_gpu = DataProcessorFactory.get_processor(gpu_enabled=True)

            # 通过类型方法获取并实例化
            type_cpu = DataProcessorFactory.get_processor_type("cpu")()
            type_gpu = DataProcessorFactory.get_processor_type("gpu")()

            # 验证结果一致
            assert factory_cpu.processor_type == type_cpu.processor_type == "cpu"
            assert factory_gpu.processor_type == type_gpu.processor_type == "gpu"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--no-cov"])
