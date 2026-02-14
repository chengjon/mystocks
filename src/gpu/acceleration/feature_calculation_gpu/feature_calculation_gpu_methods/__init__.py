"""FeatureCalculationGPU 方法级拆分包"""
from .part1 import FeatureCalculationGPUCoreMixin
from .part2 import FeatureCalculationGPUCalculatePriceVolumeMixin


class FeatureCalculationGPU(
    FeatureCalculationGPUCoreMixin,
    FeatureCalculationGPUCalculatePriceVolumeMixin,
):
    """FeatureCalculationGPU - 组合所有方法集"""
    pass


__all__ = ["FeatureCalculationGPU"]
