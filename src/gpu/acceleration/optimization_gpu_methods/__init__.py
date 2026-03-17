"""OptimizationGPU 方法级拆分包"""
from .part1 import OptimizationGPUCoreMixin
from .part2 import OptimizationGPURiskParityOptimizationMixin
from .part3 import OptimizationGPUPortfolioMixin


class OptimizationGPU(
    OptimizationGPUCoreMixin,
    OptimizationGPURiskParityOptimizationMixin,
    OptimizationGPUPortfolioMixin,
):
    """OptimizationGPU - 组合所有方法集"""
    pass


__all__ = ["OptimizationGPU"]
