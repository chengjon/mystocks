import os
from typing import Type
from src.gpu.data_processing_interfaces import IDataProcessor
from src.gpu.accelerated.cpu_data_processor import CPUDataProcessor
from src.gpu.accelerated.data_processor_gpu_fixed import GPUDataProcessorFixed


class DataProcessorFactory:
    """
    数据处理器工厂
    根据是否启用GPU加速来创建并返回相应的数据处理器实例
    """

    @staticmethod
    def get_processor(gpu_enabled: bool = None) -> IDataProcessor:
        """
        获取数据处理器实例。
        Args:
            gpu_enabled: 显式指定是否启用GPU。如果为None，则尝试从环境变量或系统检测。
        Returns:
            IDataProcessor 实例 (CPUDataProcessor 或 GPUDataProcessorImpl)。
        Raises:
            ImportError: 如果指定GPU但无法导入cuDF/cuPy。
        """
        if gpu_enabled is None:
            # 尝试从环境变量判断是否启用GPU
            gpu_enabled = os.getenv("ENABLE_GPU_ACCELERATION", "false").lower() == "true"
            # 也可以在这里添加更复杂的GPU检测逻辑，例如检查CUDA设备

        if gpu_enabled:
            try:
                # 尝试导入cuDF，如果失败则说明GPU环境未就绪
                import cudf  # noqa: F401
                import cupy  # noqa: F401

                return GPUDataProcessorFixed(gpu_enabled=True)
            except ImportError:
                print("GPU加速环境（cuDF/cuPy）未就绪，回退到CPU处理器。")
                return CPUDataProcessor()
        else:
            return CPUDataProcessor()

    @staticmethod
    def get_processor_type(processor_type: str) -> Type[IDataProcessor]:
        """
        根据字符串获取数据处理器类型 (用于依赖注入配置等场景)。
        Args:
            processor_type: "cpu" 或 "gpu"。
        Returns:
            IDataProcessor 的具体实现类。
        Raises:
            ValueError: 如果提供了不支持的处理器类型。
        """
        if processor_type.lower() == "cpu":
            return CPUDataProcessor
        elif processor_type.lower() == "gpu":
            return GPUDataProcessorFixed
        else:
            raise ValueError(f"Unsupported processor type: {processor_type}. Choose 'cpu' or 'gpu'.")
