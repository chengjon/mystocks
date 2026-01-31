"""
数据变换GPU内核引擎
实现高效的数据预处理、特征工程和技术指标计算
"""

import logging
import time
from typing import Any, Dict, List, Optional

import numpy as np

try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False
    cp = None
    print("Warning: CuPy not available, falling back to NumPy")

from .standardized_interface import (
    KernelConfig,
    KernelExecutionResult,
    StandardizedKernelInterface,
    TransformConfig,
    TransformOperationType,
)

logger = logging.getLogger(__name__)


class TransformKernelEngine(StandardizedKernelInterface):
    """数据变换GPU内核引擎"""

    def __init__(self, config: Optional[KernelConfig] = None):
        self.config = config or KernelConfig()
        self.is_initialized = False

        # 性能统计
        self.stats = {
            "total_operations": 0,
            "total_execution_time": 0.0,
            "cache_hits": 0,
            "fallback_to_cpu": 0,
        }

        # 缓存预计算的窗口值
        self.window_cache = {}

    async def initialize(self) -> bool:
        """初始化数据变换内核引擎"""
        try:
            if CUPY_AVAILABLE:
                # 初始化CuPy环境
                cp.cuda.Device(self.config.device_id).use()

                # 预热GPU
                await self._warmup_gpu()

                self.is_initialized = True
                logger.info("TransformKernelEngine initialized on device %s", self.config.device_id)
                return True
            else:
                logger.warning("CuPy not available, falling back to NumPy")
                self.is_initialized = True
                return True

        except Exception as e:
            logger.error("Failed to initialize TransformKernelEngine: %s", e)
            return False

    async def _warmup_gpu(self):
        """预热GPU"""
        if not CUPY_AVAILABLE:
            return

        try:
            # 创建测试数据进行预热
            test_data = cp.random.random((1000, 20), dtype=cp.float32)
            result = cp.log1p(test_data)
            del test_data, result

            # 等待GPU完成
            cp.cuda.Stream.null.synchronize()
            logger.debug("Transform kernel GPU warmup completed")
        except Exception as e:
            logger.warning("Transform kernel GPU warmup failed: %s", e)

    async def execute_matrix_operation(
        self,
        left_data: np.ndarray,
        right_data: Optional[np.ndarray] = None,
        config: Optional[Any] = None,
    ) -> KernelExecutionResult:
        """数据变换内核不支持矩阵运算"""
        return KernelExecutionResult(
            success=False,
            execution_time_ms=0.0,
            error_message="Transform kernels do not support matrix operations",
        )

    async def execute_transform_operation(self, data: np.ndarray, config: TransformConfig) -> KernelExecutionResult:
        """执行数据变换"""
        if not self.is_initialized:
            await self.initialize()

        start_time = time.time()

        try:
            # 验证输入
            if not self.validate_transform_input(data, config.operation_type):
                return KernelExecutionResult(
                    success=False,
                    execution_time_ms=0.0,
                    error_message="Invalid transform input",
                )

            # 检查窗口大小
            if (
                config.operation_type
                in [
                    TransformOperationType.ROLLING_MEAN,
                    TransformOperationType.ROLLING_STD,
                    TransformOperationType.EXPONENTIAL_MA,
                ]
                and config.window_size is None
            ):
                return KernelExecutionResult(
                    success=False,
                    execution_time_ms=0.0,
                    error_message=f"Window size required for {config.operation_type.value}",
                )

            # 执行数据变换
            result = await self._execute_transform_kernel(data, config)

            execution_time = (time.time() - start_time) * 1000
            self.stats["total_operations"] += 1
            self.stats["total_execution_time"] += execution_time

            if result.success:
                logger.debug(
                    "Transform operation {config.operation_type.value} " f"completed in {execution_time:.2f}ms"
                )
            else:
                self.stats["fallback_to_cpu"] += 1

            return result

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error("Error executing transform operation: %s", e)
            return KernelExecutionResult(success=False, execution_time_ms=execution_time, error_message=str(e))

    async def _execute_transform_kernel(self, data: np.ndarray, config: TransformConfig) -> KernelExecutionResult:
        """执行数据变换内核"""
        try:
            if CUPY_AVAILABLE and not self._should_use_cpu_fallback(data, config):
                # 使用GPU加速
                return await self._execute_gpu_transform_kernel(data, config)
            else:
                # 使用CPU
                return await self._execute_cpu_transform_kernel(data, config)

        except Exception as e:
            logger.error("Transform kernel execution failed: %s", e)
            return KernelExecutionResult(success=False, execution_time_ms=0.0, error_message=str(e))

    def _should_use_cpu_fallback(self, data: np.ndarray, config: TransformConfig) -> bool:
        """判断是否应该使用CPU回退"""
        # 小数据集使用CPU可能更快
        if data.size < 10000:  # 小于10k元素
            return True

        # 某些操作可能CPU更高效
        if (
            config.operation_type in [TransformOperationType.DIFFERENCE, TransformOperationType.RETURN]
            and data.size < 100000
        ):
            return True

        return False

    async def _execute_gpu_transform_kernel(self, data: np.ndarray, config: TransformConfig) -> KernelExecutionResult:
        """使用GPU执行数据变换"""
        start_time = time.time()

        try:
            # 转换数据到GPU
            # 优化内存分配，使用内存池模式
            gpu_data = cp.asarray(data, dtype=cp.float32)
            # 使用内存池减少分配开销
            cp.get_default_memory_pool().free_all_blocks()
            memory_used = gpu_data.nbytes

            # 根据操作类型执行计算
            if config.operation_type == TransformOperationType.NORMALIZE:
                result_gpu = self._gpu_normalize(gpu_data, config)
            elif config.operation_type == TransformOperationType.STANDARDIZE:
                result_gpu = self._gpu_standardize(gpu_data, config)
            elif config.operation_type == TransformOperationType.LOG_TRANSFORM:
                result_gpu = self._gpu_log_transform(gpu_data, config)
            elif config.operation_type == TransformOperationType.DIFFERENCE:
                result_gpu = self._gpu_difference(gpu_data, config)
            elif config.operation_type == TransformOperationType.RETURN:
                result_gpu = self._gpu_return(gpu_data, config)
            elif config.operation_type == TransformOperationType.VOLATILITY:
                result_gpu = self._gpu_volatility(gpu_data, config)
            elif config.operation_type == TransformOperationType.CORRELATION:
                result_gpu = self._gpu_correlation(gpu_data, config)
            elif config.operation_type == TransformOperationType.ROLLING_MEAN:
                result_gpu = self._gpu_rolling_mean(gpu_data, config)
            elif config.operation_type == TransformOperationType.ROLLING_STD:
                result_gpu = self._gpu_rolling_std(gpu_data, config)
            elif config.operation_type == TransformOperationType.EXPONENTIAL_MA:
                result_gpu = self._gpu_exponential_ma(gpu_data, config)
            elif config.operation_type == TransformOperationType.FFT:
                result_gpu = self._gpu_fft(gpu_data, config)
            else:
                raise ValueError(f"Unsupported transform operation: {config.operation_type}")

            # 等待GPU完成
            cp.cuda.Stream.null.synchronize()

            # 转换结果回CPU
            result = cp.asnumpy(result_gpu)

            # 清理GPU内存
            # 改进内存清理逻辑
            try:
                if isinstance(result_gpu, cp.ndarray):
                    result_gpu = None  # 显式释放
            except Exception:
                pass
            finally:
                if isinstance(gpu_data, cp.ndarray):
                    gpu_data = None  # 显式释放

            execution_time = (time.time() - start_time) * 1000
            self.stats["cache_hits"] += 1

            return KernelExecutionResult(
                success=True,
                execution_time_ms=execution_time,
                result_data=result,
                memory_used_bytes=memory_used,
                performance_metrics={
                    "operation": config.operation_type.value,
                    "input_shape": data.shape,
                    "output_shape": result.shape if hasattr(result, "shape") else None,
                    "method": config.method,
                },
            )

        except Exception as e:
            logger.error("GPU transform kernel execution failed: %s", e)
            # 回退到CPU
            return await self._execute_cpu_transform_kernel(data, config)

    async def _execute_cpu_transform_kernel(self, data: np.ndarray, config: TransformConfig) -> KernelExecutionResult:
        """使用CPU执行数据变换"""
        start_time = time.time()

        try:
            # 根据操作类型执行计算
            if config.operation_type == TransformOperationType.NORMALIZE:
                result = self._cpu_normalize(data, config)
            elif config.operation_type == TransformOperationType.STANDARDIZE:
                result = self._cpu_standardize(data, config)
            elif config.operation_type == TransformOperationType.LOG_TRANSFORM:
                result = self._cpu_log_transform(data, config)
            elif config.operation_type == TransformOperationType.DIFFERENCE:
                result = self._cpu_difference(data, config)
            elif config.operation_type == TransformOperationType.RETURN:
                result = self._cpu_return(data, config)
            elif config.operation_type == TransformOperationType.VOLATILITY:
                result = self._cpu_volatility(data, config)
            elif config.operation_type == TransformOperationType.CORRELATION:
                result = self._cpu_correlation(data, config)
            elif config.operation_type == TransformOperationType.ROLLING_MEAN:
                result = self._cpu_rolling_mean(data, config)
            elif config.operation_type == TransformOperationType.ROLLING_STD:
                result = self._cpu_rolling_std(data, config)
            elif config.operation_type == TransformOperationType.EXPONENTIAL_MA:
                result = self._cpu_exponential_ma(data, config)
            elif config.operation_type == TransformOperationType.FFT:
                result = self._cpu_fft(data, config)
            else:
                raise ValueError(f"Unsupported transform operation: {config.operation_type}")

            execution_time = (time.time() - start_time) * 1000

            return KernelExecutionResult(
                success=True,
                execution_time_ms=execution_time,
                result_data=result,
                memory_used_bytes=data.nbytes,
                performance_metrics={
                    "operation": config.operation_type.value,
                    "execution_backend": "CPU",
                    "input_shape": data.shape,
                    "output_shape": result.shape if hasattr(result, "shape") else None,
                    "method": config.method,
                },
            )

        except Exception as e:
            logger.error("CPU transform kernel execution failed: %s", e)
            return KernelExecutionResult(success=False, execution_time_ms=0.0, error_message=str(e))

    def _gpu_normalize(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """GPU数据归一化"""
        mean = cp.mean(data, axis=0, keepdims=True)
        std = cp.std(data, axis=0, keepdims=True)
        return (data - mean) / (std + config.epsilon)

    def _gpu_standardize(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """GPU数据标准化"""
        mean = cp.mean(data, axis=0, keepdims=True)
        std = cp.std(data, axis=0, keepdims=True)
        return (data - mean) / std

    def _gpu_log_transform(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """GPU对数变换"""
        return cp.log1p(cp.abs(data)) * cp.sign(data)

    def _gpu_difference(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """GPU差分运算"""
        return cp.diff(data, axis=0)

    def _gpu_return(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """GPU收益率计算"""
        return data[1:] / data[:-1] - 1.0

    def _gpu_volatility(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """GPU波动率计算"""
        returns = self._gpu_return(data, config)
        return cp.std(returns, axis=0, keepdims=True)

    def _gpu_correlation(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """GPU相关性计算"""
        # 标准化数据
        normalized = self._gpu_standardize(data, config)
        # 计算相关系数矩阵
        return cp.dot(normalized.T, normalized) / (data.shape[0] - 1)

    def _gpu_rolling_mean(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """GPU滚动平均"""
        return self._gpu_rolling_operation(data, config.window_size, cp.mean)

    def _gpu_rolling_std(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """GPU滚动标准差"""
        return self._gpu_rolling_operation(data, config.window_size, cp.std)

    def _gpu_exponential_ma(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """GPU指数移动平均"""
        alpha = 2.0 / (config.window_size + 1) if config.window_size else 0.1
        return self._gpu_exponential_smoothing(data, alpha)

    def _gpu_rolling_operation(self, data: np.ndarray, window_size: int, operation) -> np.ndarray:
        """GPU滚动操作"""
        result = cp.zeros(data.shape, dtype=data.dtype)
        for i in range(window_size, data.shape[0]):
            window_data = data[i - window_size + 1 : i + 1]
            result[i] = operation(window_data, axis=0)
        return result

    def _gpu_exponential_smoothing(self, data: np.ndarray, alpha: float) -> np.ndarray:
        """GPU指数平滑"""
        result = cp.zeros_like(data)
        result[0] = data[0]
        for i in range(1, data.shape[0]):
            result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
        return result

    # CPU版本的方法（用于回退）
    def _cpu_normalize(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """CPU数据归一化"""
        mean = np.mean(data, axis=0, keepdims=True)
        std = np.std(data, axis=0, keepdims=True)
        return (data - mean) / (std + config.epsilon)

    def _cpu_standardize(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """CPU数据标准化"""
        mean = np.mean(data, axis=0, keepdims=True)
        std = np.std(data, axis=0, keepdims=True)
        return (data - mean) / std

    def _cpu_log_transform(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """CPU对数变换"""
        return np.log1p(np.abs(data)) * np.sign(data)

    def _cpu_difference(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """CPU差分运算"""
        return np.diff(data, axis=0)

    def _cpu_return(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """CPU收益率计算"""
        return data[1:] / data[:-1] - 1.0

    def _cpu_volatility(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """CPU波动率计算"""
        returns = self._cpu_return(data, config)
        return np.std(returns, axis=0, keepdims=True)

    def _cpu_correlation(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """CPU相关性计算"""
        # 标准化数据
        normalized = self._cpu_standardize(data, config)
        # 计算相关系数矩阵
        return np.dot(normalized.T, normalized) / (data.shape[0] - 1)

    def _cpu_rolling_mean(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """CPU滚动平均"""
        return self._cpu_rolling_operation(data, config.window_size, np.mean)

    def _cpu_rolling_std(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """CPU滚动标准差"""
        return self._cpu_rolling_operation(data, config.window_size, np.std)

    def _cpu_exponential_ma(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """CPU指数移动平均"""
        alpha = 2.0 / (config.window_size + 1) if config.window_size else 0.1
        return self._cpu_exponential_smoothing(data, alpha)

    def _cpu_rolling_operation(self, data: np.ndarray, window_size: int, operation) -> np.ndarray:
        """CPU滚动操作"""
        result = np.zeros(data.shape, dtype=data.dtype)
        for i in range(window_size, data.shape[0]):
            window_data = data[i - window_size + 1 : i + 1]
            result[i] = operation(window_data, axis=0)
        return result

    def _cpu_exponential_smoothing(self, data: np.ndarray, alpha: float) -> np.ndarray:
        """CPU指数平滑"""
        result = np.zeros_like(data)
        result[0] = data[0]
        for i in range(1, data.shape[0]):
            result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
        return result

    async def execute_inference_operation(self, data: np.ndarray, config: Any) -> KernelExecutionResult:
        """数据变换内核不支持推理操作"""
        return KernelExecutionResult(
            success=False,
            execution_time_ms=0.0,
            error_message="Transform kernels do not support inference operations",
        )

    async def batch_execute(self, operations: list, config: Optional[KernelConfig] = None) -> list:
        """批量执行数据变换"""
        results = []
        for op_data in operations:
            operation_type, data, op_config = op_data[:3]
            if isinstance(op_config, TransformConfig):
                result = await self.execute_transform_operation(data, op_config)
            else:
                # 使用默认配置
                default_config = TransformConfig(operation_type=TransformOperationType.NORMALIZE)
                result = await self.execute_transform_operation(data, default_config)
            results.append(result)
        return results

    def get_supported_operations(self) -> Dict[str, List[str]]:
        """获取支持的数据变换操作"""
        return {
            "transform": [op.value for op in TransformOperationType],
            "supported_backends": ["GPU", "CPU"],
            "optimized_operations": [
                TransformOperationType.NORMALIZE.value,
                TransformOperationType.STANDARDIZE.value,
                TransformOperationType.LOG_TRANSFORM.value,
            ],
        }

    def get_kernel_info(self, operation_name: str) -> Dict[str, Any]:
        """获取数据变换内核信息"""
        try:
            op_type = TransformOperationType(operation_name)
        except ValueError:
            op_type = None

        return {
            "operation_type": operation_name,
            "category": "transform",
            "gpu_accelerated": CUPY_AVAILABLE,
            "supported": op_type is not None,
            "performance_characteristics": self._get_operation_characteristics(op_type),
        }

    def _get_operation_characteristics(self, operation_type: Optional[TransformOperationType]) -> Dict[str, Any]:
        """获取操作性能特征"""
        if operation_type is None:
            return {}

        characteristics = {
            TransformOperationType.NORMALIZE: {
                "complexity": "O(n)",
                "memory_efficiency": "high",
                "parallelizable": True,
                "cache_friendly": True,
            },
            TransformOperationType.ROLLING_MEAN: {
                "complexity": "O(n*w)",
                "memory_efficiency": "medium",
                "parallelizable": True,
                "cache_friendly": True,
            },
            TransformOperationType.CORRELATION: {
                "complexity": "O(n²)",
                "memory_efficiency": "low",
                "parallelizable": False,
                "cache_friendly": False,
            },
        }

        return characteristics.get(
            operation_type,
            {
                "complexity": "varies",
                "memory_efficiency": "medium",
                "parallelizable": True,
                "cache_friendly": "depends",
            },
        )

    def optimize_for_data_size(self, data_shape: tuple) -> KernelConfig:
        """根据数据大小优化数据变换内核配置"""
        data_size = np.prod(data_shape)

        # 根据数据大小优化配置
        if data_size < 10000:
            block_size = 64
            grid_size = 256
        elif data_size < 100000:
            block_size = 128
            grid_size = 512
        else:
            block_size = 256
            grid_size = 1024

        return KernelConfig(
            device_id=self.config.device_id,
            block_size=block_size,
            grid_size=grid_size,
            optimization_level="O3",
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        avg_time = (
            self.stats["total_execution_time"] / self.stats["total_operations"]
            if self.stats["total_operations"] > 0
            else 0
        )

        return {
            "total_operations": self.stats["total_operations"],
            "total_execution_time_ms": self.stats["total_execution_time"],
            "average_execution_time_ms": avg_time,
            "cache_hits": self.stats["cache_hits"],
            "cpu_fallback_rate": self.stats["fallback_to_cpu"] / max(1, self.stats["total_operations"]),
            "gpu_acceleration_available": CUPY_AVAILABLE,
        }

    def _gpu_fft(self, data: cp.ndarray, config: TransformConfig) -> cp.ndarray:
        """GPU FFT实现"""
        if len(data.shape) > 1:
            # 多维FFT
            return cp.fft.fft(data, axis=-1)
        else:
            # 一维FFT
            return cp.fft.fft(data)

    def _cpu_fft(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """CPU FFT实现"""
        if len(data.shape) > 1:
            # 多维FFT
            return np.fft.fft(data, axis=-1)
        else:
            # 一维FFT
            return np.fft.fft(data)
