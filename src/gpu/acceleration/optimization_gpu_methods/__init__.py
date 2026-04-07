"""OptimizationGPU 方法级拆分包"""
from .core import OptimizationGPUCoreMixin
from .risk_parity_optimization import OptimizationGPURiskParityOptimizationMixin
from .portfolio import OptimizationGPUPortfolioMixin


class OptimizationGPU(
    OptimizationGPUCoreMixin,
    OptimizationGPURiskParityOptimizationMixin,
    OptimizationGPUPortfolioMixin,
):
    """OptimizationGPU - 组合所有方法集"""
    pass


__all__ = ["OptimizationGPU"]
