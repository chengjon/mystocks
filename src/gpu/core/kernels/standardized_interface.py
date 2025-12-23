"""
标准化GPU计算内核接口
定义统一的GPU计算内核接口，支持不同类型的量化交易计算操作
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class MatrixOperationType(Enum):
    """矩阵运算类型"""

    MULTIPLY = "multiply"  # 矩阵乘法 A * B
    MULTIPLY_TRANSPOSE = "multiply_transpose"  # 矩阵乘法转置 A * B^T
    TRANSPOSE_MULTIPLY = "transpose_multiply"  # 转置矩阵乘法 A^T * B
    ELEMENT_WISE = "element_wise"  # 元素级运算
    DOT_PRODUCT = "dot_product"  # 点积
    NORM = "norm"  # 矩阵范数
    INVERSE = "inverse"  # 矩阵求逆
    EIGENVALUES = "eigenvalues"  # 特征值
    CHOLESKY = "cholesky"  # Cholesky分解
    TRANSPOSE = "transpose"  # 矩阵转置


class TransformOperationType(Enum):
    """数据变换类型"""

    NORMALIZE = "normalize"  # 归一化
    STANDARDIZE = "standardize"  # 标准化
    LOG_TRANSFORM = "log_transform"  # 对数变换
    DIFFERENCE = "difference"  # 差分运算
    RETURN = "return"  # 收益率计算
    VOLATILITY = "volatility"  # 波动率计算
    CORRELATION = "correlation"  # 相关性计算
    COVARIANCE = "covariance"  # 协方差计算
    ROLLING_MEAN = "rolling_mean"  # 滚动平均
    ROLLING_STD = "rolling_std"  # 滚动标准差
    EXPONENTIAL_MA = "exponential_ma"  # 指数移动平均
    FFT = "fft"  # 快速傅里叶变换


class InferenceOperationType(Enum):
    """机器学习推理类型"""

    LINEAR_REGRESSION = "linear_regression"  # 线性回归
    LOGISTIC_REGRESSION = "logistic_regression"  # 逻辑回归
    NEURAL_NETWORK = "neural_network"  # 神经网络
    DECISION_TREE = "decision_tree"  # 决策树
    RANDOM_FOREST = "random_forest"  # 随机森林
    SUPPORT_VECTOR_MACHINE = "svm"  # 支持向量机
    CLUSTERING = "clustering"  # 聚类
    PCA = "pca"  # 主成分分析


@dataclass
class KernelConfig:
    """内核配置"""

    device_id: int = 0
    block_size: int = 256
    grid_size: int = 1024
    shared_memory_size: int = 48 * 1024  # 48KB
    stream_id: int = 0
    enable_profiling: bool = False
    optimization_level: str = "O2"  # O0, O1, O2, O3


@dataclass
class MatrixOperationConfig:
    """矩阵运算配置"""

    operation_type: MatrixOperationType
    left_matrix_shape: Optional[Tuple[int, int]] = None
    right_matrix_shape: Optional[Tuple[int, int]] = None
    use_transpose_left: bool = False
    use_transpose_right: bool = False
    alpha: float = 1.0  # 缩放因子
    beta: float = 0.0  # 附加项缩放因子


# 别名：保持向后兼容性
MatrixConfig = MatrixOperationConfig


@dataclass
class TransformConfig:
    """变换操作配置"""

    operation_type: TransformOperationType
    window_size: Optional[int] = None  # 窗口大小
    periods: Optional[int] = None  # 周期数
    method: str = "default"  # 计算方法
    epsilon: float = 1e-8  # 数值稳定性参数


@dataclass
class InferenceConfig:
    """推理操作配置"""

    operation_type: InferenceOperationType
    model_params: Optional[Dict[str, Any]] = None
    input_shape: Optional[Tuple[int, ...]] = None
    output_shape: Optional[Tuple[int, ...]] = None
    batch_size: int = 1
    use_quantization: bool = False


@dataclass
class KernelExecutionResult:
    """内核执行结果"""

    success: bool
    execution_time_ms: float
    result_data: Optional[np.ndarray] = None
    error_message: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    memory_used_bytes: int = 0


class StandardizedKernelInterface(ABC):
    """标准化GPU计算内核接口"""

    @abstractmethod
    async def execute_matrix_operation(
        self,
        left_data: np.ndarray,
        right_data: Optional[np.ndarray] = None,
        config: Optional[MatrixOperationConfig] = None,
    ) -> KernelExecutionResult:
        """执行矩阵运算"""
        pass

    @abstractmethod
    async def execute_transform_operation(
        self, data: np.ndarray, config: TransformConfig
    ) -> KernelExecutionResult:
        """执行数据变换"""
        pass

    @abstractmethod
    async def execute_inference_operation(
        self, data: np.ndarray, config: InferenceConfig
    ) -> KernelExecutionResult:
        """执行机器学习推理"""
        pass

    @abstractmethod
    async def batch_execute(
        self,
        operations: List[Tuple[str, np.ndarray, Any]],
        config: Optional[KernelConfig] = None,
    ) -> List[KernelExecutionResult]:
        """批量执行多个操作"""
        pass

    @abstractmethod
    def get_supported_operations(self) -> Dict[str, List[str]]:
        """获取支持的操作类型"""
        pass

    @abstractmethod
    def get_kernel_info(self, operation_name: str) -> Dict[str, Any]:
        """获取内核信息"""
        pass

    @abstractmethod
    def optimize_for_data_size(self, data_shape: Tuple[int, ...]) -> KernelConfig:
        """根据数据大小优化内核配置"""
        pass

    def validate_matrix_input(
        self, data: np.ndarray, operation: MatrixOperationType
    ) -> bool:
        """验证矩阵输入"""
        if not isinstance(data, np.ndarray):
            return False

        if data.dtype not in [np.float32, np.float64]:
            return False

        if len(data.shape) != 2:
            return False

        return True

    def validate_transform_input(
        self, data: np.ndarray, operation: TransformOperationType
    ) -> bool:
        """验证变换输入"""
        if not isinstance(data, np.ndarray):
            return False

        if data.dtype not in [np.float32, np.float64]:
            return False

        # 检查特定变换的要求
        if operation in [
            TransformOperationType.CORRELATION,
            TransformOperationType.COVARIANCE,
        ]:
            if len(data.shape) < 2:
                return False

        return True

    def estimate_execution_time(
        self, data_shape: Tuple[int, ...], operation: str
    ) -> float:
        """估算执行时间（毫秒）"""
        # 基于数据大小和操作类型的简单估算
        data_size = np.prod(data_shape)

        # 不同操作的时间复杂度系数
        complexity_factors = {
            "multiply": 1e-7,  # O(n^3)
            "normalize": 1e-8,  # O(n)
            "log_transform": 1e-8,  # O(n)
            "correlation": 1e-7,  # O(n^2)
            "neural_network": 1e-6,  # 取决于网络复杂度
            "fft": 1e-7,  # O(n log n)
        }

        factor = complexity_factors.get(operation, 1e-8)
        return data_size * factor

    def optimize_block_size(self, data_size: int, device_memory_mb: int) -> int:
        """优化块大小"""
        # 基于数据大小和设备内存选择最优块大小
        standard_block_sizes = [32, 64, 128, 256, 512, 1024]

        # 根据数据大小选择
        if data_size < 1024:
            return 32
        elif data_size < 10000:
            return 64
        elif data_size < 100000:
            return 128
        elif data_size < 1000000:
            return 256
        else:
            return 512

    def create_execution_profiler(self) -> Dict[str, Any]:
        """创建执行性能分析器"""
        return {
            "start_time": 0.0,
            "end_time": 0.0,
            "memory_allocations": [],
            "kernel_launches": [],
            "data_transfers": [],
        }

    def log_performance_metrics(
        self, result: KernelExecutionResult, profiler: Dict[str, Any]
    ):
        """记录性能指标"""
        if not result.success:
            return

        # 计算吞吐量 (operations/second)
        if hasattr(result, "result_data") and result.result_data is not None:
            data_size = result.result_data.nbytes
            throughput = data_size / (result.execution_time_ms / 1000)  # bytes/second
            result.performance_metrics["throughput_bytes_per_sec"] = throughput

        # 记录内存使用
        result.performance_metrics["memory_used_mb"] = result.memory_used_bytes / (
            1024 * 1024
        )

        # 记录执行时间分解
        if profiler:
            total_time = profiler.get("end_time", 0) - profiler.get("start_time", 0)
            result.performance_metrics["total_wall_time_ms"] = total_time * 1000


class KernelRegistry:
    """内核注册中心"""

    def __init__(self):
        self._kernels: Dict[str, Any] = {}
        self._operation_mappings: Dict[str, str] = {}

    def register_kernel(self, name: str, kernel_class: Any):
        """注册内核"""
        self._kernels[name] = kernel_class
        self._operation_mappings[name] = name

    def get_kernel(self, name: str) -> Optional[Any]:
        """获取内核"""
        return self._kernels.get(name)

    def list_kernels(self) -> List[str]:
        """列出所有已注册的内核"""
        return list(self._kernels.keys())

    def get_kernel_for_operation(
        self, operation_type: str, operation_name: str
    ) -> Optional[str]:
        """根据操作类型获取内核名称"""
        key = f"{operation_type}_{operation_name}"
        return self._operation_mappings.get(key)


# 全局内核注册中心实例
_kernel_registry = KernelRegistry()


def get_kernel_registry() -> KernelRegistry:
    """获取全局内核注册中心"""
    return _kernel_registry


def register_standard_kernels():
    """注册标准内核"""
    # 这里将在内核实现模块中被调用
    pass
