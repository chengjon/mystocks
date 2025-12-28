"""
矩阵运算GPU内核引擎
实现高效的矩阵乘法、转置、求逆等基础矩阵运算
"""

import logging
import time
from typing import Optional, Dict, Any, List
import numpy as np

try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False
    cp = None
    print("Warning: CuPy not available, falling back to NumPy")

from .standardized_interface import (
    StandardizedKernelInterface,
    MatrixOperationType,
    MatrixOperationConfig,
    TransformConfig,
    InferenceConfig,
    KernelExecutionResult,
    KernelConfig,
    MatrixConfig,  # 别名
)

logger = logging.getLogger(__name__)


class MatrixKernelEngine(StandardizedKernelInterface):
    """矩阵运算GPU内核引擎"""

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

        # 缓存编译的内核
        self.compiled_kernels = {}

    async def initialize(self) -> bool:
        """初始化矩阵内核引擎"""
        try:
            if CUPY_AVAILABLE:
                # 初始化CuPy环境
                cp.cuda.Device(self.config.device_id).use()

                # 预热GPU
                await self._warmup_gpu()

                self.is_initialized = True
                logger.info("MatrixKernelEngine initialized on device %s", self.config.device_id)
                return True
            else:
                logger.warning("CuPy not available, falling back to NumPy")
                self.is_initialized = True
                return True

        except Exception as e:
            logger.error("Failed to initialize MatrixKernelEngine: %s", e)
            return False

    async def _warmup_gpu(self):
        """预热GPU"""
        if not CUPY_AVAILABLE:
            return

        try:
            # 创建小的测试矩阵进行预热
            test_matrix = cp.random.random((100, 100), dtype=cp.float32)
            result = cp.dot(test_matrix, test_matrix.T)
            del test_matrix, result

            # 等待GPU完成
            cp.cuda.Stream.null.synchronize()
            logger.debug("GPU warmup completed")
        except Exception as e:
            logger.warning("GPU warmup failed: %s", e)

    async def execute_matrix_operation(
        self,
        left_data: np.ndarray,
        right_data: Optional[np.ndarray] = None,
        config: Optional[MatrixOperationConfig] = None,
    ) -> KernelExecutionResult:
        """执行矩阵运算"""
        if not self.is_initialized:
            await self.initialize()

        start_time = time.time()
        operation_config = config or MatrixOperationConfig(operation_type=MatrixOperationType.MULTIPLY)

        try:
            # 验证输入
            if not self.validate_matrix_input(left_data, operation_config.operation_type):
                return KernelExecutionResult(
                    success=False,
                    execution_time_ms=0.0,
                    error_message="Invalid matrix input",
                )

            # 检查维度兼容性
            if not self._check_matrix_dimensions(left_data, right_data, operation_config):
                return KernelExecutionResult(
                    success=False,
                    execution_time_ms=0.0,
                    error_message="Matrix dimensions are not compatible",
                )

            # 执行矩阵运算
            result = await self._execute_matrix_kernel(left_data, right_data, operation_config)

            execution_time = (time.time() - start_time) * 1000
            self.stats["total_operations"] += 1
            self.stats["total_execution_time"] += execution_time

            if result.success:
                logger.debug(
                    "Matrix operation {operation_config.operation_type.value} " f"completed in {execution_time:.2f}ms"
                )
            else:
                self.stats["fallback_to_cpu"] += 1

            return result

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error("Error executing matrix operation: %s", e)
            return KernelExecutionResult(success=False, execution_time_ms=execution_time, error_message=str(e))

    def _check_matrix_dimensions(
        self,
        left_data: np.ndarray,
        right_data: Optional[np.ndarray],
        config: MatrixOperationConfig,
    ) -> bool:
        """检查矩阵维度兼容性"""
        if config.operation_type in [
            MatrixOperationType.MULTIPLY,
            MatrixOperationType.MULTIPLY_TRANSPOSE,
            MatrixOperationType.TRANSPOSE_MULTIPLY,
        ]:
            if right_data is None:
                return False

            m, n = left_data.shape
            p, q = right_data.shape

            if config.operation_type == MatrixOperationType.MULTIPLY:
                return n == p  # (m,n) * (p,q) -> (m,q)
            elif config.operation_type == MatrixOperationType.MULTIPLY_TRANSPOSE:
                return n == q  # (m,n) * (p,q)^T -> (m,p)
            elif config.operation_type == MatrixOperationType.TRANSPOSE_MULTIPLY:
                return m == p  # (m,n)^T * (p,q) -> (n,q)

        return True

    async def _execute_matrix_kernel(
        self,
        left_data: np.ndarray,
        right_data: Optional[np.ndarray],
        config: MatrixOperationConfig,
    ) -> KernelExecutionResult:
        """执行矩阵内核运算"""
        try:
            if CUPY_AVAILABLE and not self._should_use_cpu_fallback(left_data, config):
                # 使用GPU加速
                return await self._execute_gpu_matrix_kernel(left_data, right_data, config)
            else:
                # 使用CPU
                return await self._execute_cpu_matrix_kernel(left_data, right_data, config)

        except Exception as e:
            logger.error("Matrix kernel execution failed: %s", e)
            return KernelExecutionResult(success=False, execution_time_ms=0.0, error_message=str(e))

    def _should_use_cpu_fallback(self, data: np.ndarray, config: MatrixOperationConfig) -> bool:
        """判断是否应该使用CPU回退"""
        # 小矩阵使用CPU可能更快
        if data.size < 10000:  # 小于10k元素
            return True

        # 特定操作可能更适合CPU
        if config.operation_type in [
            MatrixOperationType.INVERSE,
            MatrixOperationType.EIGENVALUES,
        ]:
            return True

        return False

    async def _execute_gpu_matrix_kernel(
        self,
        left_data: np.ndarray,
        right_data: Optional[np.ndarray],
        config: MatrixOperationConfig,
    ) -> KernelExecutionResult:
        """使用GPU执行矩阵运算"""
        start_time = time.time()

        try:
            # 转换数据到GPU
            gpu_left = cp.asarray(left_data, dtype=cp.float32)
            gpu_right = cp.asarray(right_data, dtype=cp.float32) if right_data is not None else None

            memory_used = gpu_left.nbytes
            if gpu_right is not None:
                memory_used += gpu_right.nbytes

            # 根据操作类型执行计算
            if config.operation_type == MatrixOperationType.MULTIPLY:
                result_gpu = self._gpu_matrix_multiply(gpu_left, gpu_right, config)
            elif config.operation_type == MatrixOperationType.MULTIPLY_TRANSPOSE:
                result_gpu = self._gpu_matrix_multiply_transpose(gpu_left, gpu_right, config)
            elif config.operation_type == MatrixOperationType.TRANSPOSE_MULTIPLY:
                result_gpu = self._gpu_matrix_transpose_multiply(gpu_left, gpu_right, config)
            elif config.operation_type == MatrixOperationType.ELEMENT_WISE:
                result_gpu = self._gpu_element_wise_operation(gpu_left, gpu_right, config)
            elif config.operation_type == MatrixOperationType.TRANSPOSE:
                result_gpu = cp.transpose(gpu_left)
            elif config.operation_type == MatrixOperationType.DOT_PRODUCT:
                result_gpu = cp.dot(
                    gpu_left.flatten(),
                    gpu_right.flatten() if gpu_right is not None else gpu_left.flatten(),
                )
            elif config.operation_type == MatrixOperationType.NORM:
                result_gpu = cp.linalg.norm(gpu_left)
            else:
                raise ValueError(f"Unsupported matrix operation: {config.operation_type}")

            # 等待GPU完成
            cp.cuda.Stream.null.synchronize()

            # 转换结果回CPU
            result = cp.asnumpy(result_gpu) if isinstance(result_gpu, cp.ndarray) else np.array([result_gpu])

            # 清理GPU内存
            del gpu_left
            if gpu_right is not None:
                del gpu_right
            if isinstance(result_gpu, cp.ndarray):
                del result_gpu

            execution_time = (time.time() - start_time) * 1000
            self.stats["cache_hits"] += 1

            return KernelExecutionResult(
                success=True,
                execution_time_ms=execution_time,
                result_data=result,
                memory_used_bytes=memory_used,
                performance_metrics={
                    "operation": config.operation_type.value,
                    "input_shape": left_data.shape,
                    "output_shape": result.shape if hasattr(result, "shape") else None,
                },
            )

        except Exception as e:
            logger.error("GPU matrix kernel execution failed: %s", e)
            # 回退到CPU
            return await self._execute_cpu_matrix_kernel(left_data, right_data, config)

    async def _execute_cpu_matrix_kernel(
        self,
        left_data: np.ndarray,
        right_data: Optional[np.ndarray],
        config: MatrixOperationConfig,
    ) -> KernelExecutionResult:
        """使用CPU执行矩阵运算"""
        start_time = time.time()

        try:
            # 根据操作类型执行计算
            if config.operation_type == MatrixOperationType.MULTIPLY:
                result = np.dot(left_data, right_data)
            elif config.operation_type == MatrixOperationType.MULTIPLY_TRANSPOSE:
                result = np.dot(left_data, right_data.T)
            elif config.operation_type == MatrixOperationType.TRANSPOSE_MULTIPLY:
                result = np.dot(left_data.T, right_data)
            elif config.operation_type == MatrixOperationType.ELEMENT_WISE:
                if config.alpha != 1.0:
                    left_data = left_data * config.alpha
                if right_data is not None:
                    if config.beta != 0.0:
                        result = left_data + right_data * config.beta
                    else:
                        result = left_data * right_data
                else:
                    result = left_data
            elif config.operation_type == MatrixOperationType.TRANSPOSE:
                result = left_data.T
            elif config.operation_type == MatrixOperationType.DOT_PRODUCT:
                result = np.dot(
                    left_data.flatten(),
                    right_data.flatten() if right_data is not None else left_data.flatten(),
                )
            elif config.operation_type == MatrixOperationType.NORM:
                result = np.linalg.norm(left_data)
            else:
                raise ValueError(f"Unsupported matrix operation: {config.operation_type}")

            execution_time = (time.time() - start_time) * 1000

            return KernelExecutionResult(
                success=True,
                execution_time_ms=execution_time,
                result_data=result,
                memory_used_bytes=left_data.nbytes + (right_data.nbytes if right_data is not None else 0),
                performance_metrics={
                    "operation": config.operation_type.value,
                    "execution_backend": "CPU",
                    "input_shape": left_data.shape,
                    "output_shape": result.shape if hasattr(result, "shape") else None,
                },
            )

        except Exception as e:
            logger.error("CPU matrix kernel execution failed: %s", e)
            return KernelExecutionResult(success=False, execution_time_ms=0.0, error_message=str(e))

    def _gpu_matrix_multiply(self, left: np.ndarray, right: np.ndarray, config: MatrixOperationConfig) -> np.ndarray:
        """GPU矩阵乘法"""
        if config.alpha != 1.0:
            left = left * config.alpha
        result = cp.dot(left, right)
        if config.beta != 0.0:
            result = result + config.beta
        return result

    def _gpu_matrix_multiply_transpose(
        self, left: np.ndarray, right: np.ndarray, config: MatrixOperationConfig
    ) -> np.ndarray:
        """GPU矩阵乘法转置"""
        if config.alpha != 1.0:
            left = left * config.alpha
        result = cp.dot(left, right.T)
        if config.beta != 0.0:
            result = result + config.beta
        return result

    def _gpu_matrix_transpose_multiply(
        self, left: np.ndarray, right: np.ndarray, config: MatrixOperationConfig
    ) -> np.ndarray:
        """GPU转置矩阵乘法"""
        if config.alpha != 1.0:
            left = left * config.alpha
        result = cp.dot(left.T, right)
        if config.beta != 0.0:
            result = result + config.beta
        return result

    def _gpu_element_wise_operation(
        self,
        left: np.ndarray,
        right: Optional[np.ndarray],
        config: MatrixOperationConfig,
    ) -> np.ndarray:
        """GPU元素级运算"""
        if right is None:
            return left

        if config.alpha != 1.0:
            left = left * config.alpha
            right = right * config.alpha

        result = left * right

        if config.beta != 0.0:
            result = result + config.beta

        return result

    async def execute_transform_operation(self, data: np.ndarray, config: TransformConfig) -> KernelExecutionResult:
        """矩阵内核不支持数据变换操作"""
        return KernelExecutionResult(
            success=False,
            execution_time_ms=0.0,
            error_message="Matrix kernels do not support transform operations",
        )

    async def execute_inference_operation(self, data: np.ndarray, config: InferenceConfig) -> KernelExecutionResult:
        """矩阵内核不支持推理操作"""
        return KernelExecutionResult(
            success=False,
            execution_time_ms=0.0,
            error_message="Matrix kernels do not support inference operations",
        )

    async def batch_execute(self, operations: list, config: Optional[KernelConfig] = None) -> list:
        """批量执行矩阵运算"""
        results = []
        for op_data in operations:
            operation_type, left_data, right_data, op_config = op_data[:4]
            if isinstance(op_config, MatrixOperationConfig):
                result = await self.execute_matrix_operation(left_data, right_data, op_config)
            else:
                result = await self.execute_matrix_operation(left_data, right_data)
            results.append(result)
        return results

    def get_supported_operations(self) -> Dict[str, List[str]]:
        """获取支持的矩阵操作"""
        return {
            "matrix": [op.value for op in MatrixOperationType],
            "supported_backends": ["GPU", "CPU"],
            "optimized_operations": [
                MatrixOperationType.MULTIPLY.value,
                MatrixOperationType.MULTIPLY_TRANSPOSE.value,
                MatrixOperationType.TRANSPOSE_MULTIPLY.value,
            ],
        }

    def get_kernel_info(self, operation_name: str) -> Dict[str, Any]:
        """获取矩阵内核信息"""
        try:
            op_type = MatrixOperationType(operation_name)
        except ValueError:
            op_type = None

        return {
            "operation_type": operation_name,
            "category": "matrix",
            "gpu_accelerated": CUPY_AVAILABLE,
            "supported": op_type is not None,
            "performance_characteristics": self._get_operation_characteristics(op_type),
        }

    def _get_operation_characteristics(self, operation_type: Optional[MatrixOperationType]) -> Dict[str, Any]:
        """获取操作性能特征"""
        if operation_type is None:
            return {}

        characteristics = {
            MatrixOperationType.MULTIPLY: {
                "complexity": "O(n³)",
                "memory_efficiency": "high",
                "parallelizable": True,
                "cache_friendly": True,
            },
            MatrixOperationType.ELEMENT_WISE: {
                "complexity": "O(n)",
                "memory_efficiency": "very_high",
                "parallelizable": True,
                "cache_friendly": True,
            },
            MatrixOperationType.TRANSPOSE: {
                "complexity": "O(n)",
                "memory_efficiency": "very_high",
                "parallelizable": True,
                "cache_friendly": True,
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
        """根据数据大小优化矩阵内核配置"""
        data_size = np.prod(data_shape)

        # 根据数据大小优化配置
        if data_size < 1000:
            block_size = 32
            grid_size = 256
        elif data_size < 10000:
            block_size = 64
            grid_size = 512
        elif data_size < 100000:
            block_size = 128
            grid_size = 1024
        else:
            block_size = 256
            grid_size = 2048

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

    def _gpu_multiply_optimized(self, a: cp.ndarray, b: cp.ndarray, config: MatrixConfig) -> cp.ndarray:
        """优化的GPU矩阵乘法实现"""
        m, k = a.shape
        k2, n = b.shape

        if k != k2:
            raise ValueError(f"Matrix dimensions incompatible: {a.shape} x {b.shape}")

        # 根据矩阵大小选择最优算法
        total_elements = m * n * k

        if total_elements < 1000 * 1000:  # 小矩阵使用标准乘法
            return cp.matmul(a, b)

        elif m == n and k == n and n >= 512:  # 大方阵使用分块乘法
            return self._gpu_blocked_multiply(a, b, block_size=128)

        else:  # 一般情况使用优化的矩阵乘法
            return cp.matmul(a, b)

    def _gpu_blocked_multiply(self, a: cp.ndarray, b: cp.ndarray, block_size: int = 128) -> cp.ndarray:
        """GPU分块矩阵乘法"""
        m, k = a.shape
        k2, n = b.shape

        if k != k2:
            raise ValueError("Matrix dimensions incompatible")

        # 创建结果矩阵
        result = cp.zeros((m, n), dtype=a.dtype)

        # 分块计算
        for i in range(0, m, block_size):
            for j in range(0, n, block_size):
                for kk in range(0, k, block_size):
                    # 获取块
                    a_block = a[i : min(i + block_size, m), kk : min(kk + block_size, k)]
                    b_block = b[kk : min(kk + block_size, k), j : min(j + block_size, n)]

                    # 块乘法
                    result_block = result[i : min(i + block_size, m), j : min(j + block_size, n)]
                    result_block += cp.matmul(a_block, b_block)
                    result[i : min(i + block_size, m), j : min(j + block_size, n)] = result_block

        return result

    def _gpu_multiply_strassen(self, a: cp.ndarray, b: cp.ndarray, config: MatrixConfig) -> cp.ndarray:
        """Strassen算法实现（仅适用于2的幂次方矩阵）"""
        m, k = a.shape
        k2, n = b.shape

        if k != k2 or m != k or k != n:
            # 不满足Strassen算法条件，回退到标准乘法
            return cp.matmul(a, b)

        # 检查是否为2的幂次
        if (m & (m - 1)) != 0:  # 不是2的幂
            return cp.matmul(a, b)

        if m <= 64:  # 小矩阵不使用Strassen
            return cp.matmul(a, b)

        # Strassen算法实现
        return self._strassen_recursive(a, b)

    def _strassen_recursive(self, a: cp.ndarray, b: cp.ndarray) -> cp.ndarray:
        """递归Strassen算法"""
        n = a.shape[0]

        if n <= 64:  # 基础情况
            return cp.matmul(a, b)

        # 分割矩阵
        mid = n // 2
        a11, a12, a21, a22 = a[:mid, :mid], a[:mid, mid:], a[mid:, :mid], a[mid:, mid:]
        b11, b12, b21, b22 = b[:mid, :mid], b[:mid, mid:], b[mid:, :mid], b[mid:, mid:]

        # 7次乘法（而不是8次）
        p1 = self._strassen_recursive(a11 + a22, b11 + b22)
        p2 = self._strassen_recursive(a21 + a22, b11)
        p3 = self._strassen_recursive(a11, b12 - b22)
        p4 = self._strassen_recursive(a22, b21 - b11)
        p5 = self._strassen_recursive(a11 + a12, b22)
        p6 = self._strassen_recursive(a21 - a11, b11 + b12)
        p7 = self._strassen_recursive(a12 - a22, b21 + b22)

        # 组合结果
        c11 = p1 + p4 - p5 + p7
        c12 = p3 + p5
        c21 = p2 + p4
        c22 = p1 - p2 + p3 + p6

        # 合并结果
        c = cp.zeros((n, n), dtype=a.dtype)
        c[:mid, :mid], c[:mid, mid:], c[mid:, :mid], c[mid:, mid:] = c11, c12, c21, c22

        return c

    def _gpu_multiply_parallel(self, a: cp.ndarray, b: cp.ndarray, config: MatrixConfig) -> cp.ndarray:
        """并行矩阵乘法优化"""
        m, k = a.shape
        k2, n = b.shape

        if k != k2:
            raise ValueError(f"Matrix dimensions incompatible: {a.shape} x {b.shape}")

        # 对于大型矩阵，使用多个流并行计算
        if m * k * n > 1000 * 1000 * 1000:  # 超过10亿个元素
            streams = []
            num_streams = min(4, (m * k * n) // (256 * 256 * 256))  # 最多4个流

            try:
                # 创建多个CUDA流
                for i in range(num_streams):
                    streams.append(cp.cuda.Stream())

                # 分配结果矩阵
                result = cp.zeros((m, n), dtype=a.dtype)

                # 并行计算矩阵块
                block_rows = (m + num_streams - 1) // num_streams

                for i, stream in enumerate(streams):
                    start_row = i * block_rows
                    end_row = min((i + 1) * block_rows, m)

                    if start_row < end_row:
                        with stream:
                            a_block = a[start_row:end_row, :]
                            result_block = cp.matmul(a_block, b)
                            result[start_row:end_row, :] = result_block

                # 同步所有流
                for stream in streams:
                    stream.synchronize()

                return result

            except Exception as e:
                # 并行计算失败，回退到标准方法
                logger.warning("Parallel multiplication failed, falling back: %s", e)
                return cp.matmul(a, b)

        else:
            # 小矩阵使用标准方法
            return cp.matmul(a, b)

    def _optimize_memory_access(self, data: cp.ndarray) -> cp.ndarray:
        """优化内存访问模式"""
        # 确保数据在GPU上是连续的
        if not data.flags["C_CONTIGUOUS"] and not data.flags["F_CONTIGUOUS"]:
            return cp.ascontiguousarray(data)

        # 对于大型矩阵，考虑内存对齐
        if data.size > 1000 * 1000:
            # 使用内存池分配对齐的内存
            return cp.zeros_like(data, dtype=data.dtype, order="C")

        return data

    def _gpu_transpose_optimized(self, data: cp.ndarray, config: MatrixConfig) -> cp.ndarray:
        """优化的矩阵转置"""
        # 优化内存访问
        data = self._optimize_memory_access(data)

        # 对于大型矩阵，使用分块转置
        if data.size > 1000 * 1000:
            return self._gpu_blocked_transpose(data)
        else:
            return cp.transpose(data)

    def _gpu_blocked_transpose(self, data: cp.ndarray, block_size: int = 1024) -> cp.ndarray:
        """分块矩阵转置"""
        m, n = data.shape
        result = cp.zeros((n, m), dtype=data.dtype)

        for i in range(0, m, block_size):
            for j in range(0, n, block_size):
                # 获取块
                block = data[i : min(i + block_size, m), j : min(j + block_size, n)]
                # 转置块
                result_block = cp.transpose(block)
                # 放置到结果矩阵
                result[j : min(j + block_size, n), i : min(i + block_size, m)] = result_block

        return result
