"""MatrixKernelEngine 转置相关 GPU helper。"""

from __future__ import annotations

try:
    import cupy as cp
except ImportError:
    cp = None

from .standardized_interface import MatrixConfig


class MatrixTransposeKernelMixin:
    """矩阵转置相关方法集。"""

    def _optimize_memory_access(self, data: cp.ndarray) -> cp.ndarray:
        """优化内存访问模式。"""
        if not data.flags["C_CONTIGUOUS"] and not data.flags["F_CONTIGUOUS"]:
            return cp.ascontiguousarray(data)

        if data.size > 1000 * 1000:
            return cp.zeros_like(data, dtype=data.dtype, order="C")

        return data

    def _gpu_transpose_optimized(self, data: cp.ndarray, config: MatrixConfig) -> cp.ndarray:
        """优化的矩阵转置。"""
        data = self._optimize_memory_access(data)

        if data.size > 1000 * 1000:
            return self._gpu_blocked_transpose(data)

        return cp.transpose(data)

    def _gpu_blocked_transpose(self, data: cp.ndarray, block_size: int = 1024) -> cp.ndarray:
        """分块矩阵转置。"""
        m, n = data.shape
        result = cp.zeros((n, m), dtype=data.dtype)

        for i in range(0, m, block_size):
            for j in range(0, n, block_size):
                block = data[i : min(i + block_size, m), j : min(j + block_size, n)]
                result_block = cp.transpose(block)
                result[j : min(j + block_size, n), i : min(i + block_size, m)] = result_block

        return result
