"""
GPU计算内核层
提供标准化的GPU计算内核接口，封装常用量化交易计算操作

Phase 6.2 GPU加速引擎架构重构
"""

from .standardized_interface import (
    StandardizedKernelInterface,
    MatrixOperationType,
    TransformOperationType,
    InferenceOperationType,
)
from .matrix_kernels import MatrixKernelEngine
from .transform_kernels import TransformKernelEngine
from .inference_kernels import InferenceKernelEngine
from .kernel_registry import KernelRegistry, get_kernel_registry
from .kernel_executor import KernelExecutor


def get_kernel_executor():
    """获取内核执行器实例"""
    return KernelExecutor()


def get_matrix_kernel():
    """获取矩阵内核引擎实例"""
    return MatrixKernelEngine()


def get_transform_kernel():
    """获取变换内核引擎实例"""
    return TransformKernelEngine()


def get_inference_kernel():
    """获取推理内核引擎实例"""
    return InferenceKernelEngine()


# 注册标准内核
def register_standard_kernels():
    """注册标准内核"""
    registry = get_kernel_registry()
    registry.register_kernel(MatrixKernelEngine)
    registry.register_kernel(TransformKernelEngine)
    registry.register_kernel(InferenceKernelEngine)


__all__ = [
    # 核心接口
    "StandardizedKernelInterface",
    "MatrixOperationType",
    "TransformOperationType",
    "InferenceOperationType",
    # 内核引擎
    "MatrixKernelEngine",
    "TransformKernelEngine",
    "InferenceKernelEngine",
    # 注册和执行
    "KernelRegistry",
    "get_kernel_registry",
    "KernelExecutor",
    # 便捷函数
    "get_kernel_executor",
    "get_matrix_kernel",
    "get_transform_kernel",
    "get_inference_kernel",
    "register_standard_kernels",
]
