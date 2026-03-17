"""FeatureCalculationGPU 方法级拆分包"""
from .part1 import FeatureCalculationGPUCoreMixin
from .part2 import FeatureCalculationGPUCalculatePriceVolumeMixin
from .part3 import FeatureCalculationGPUPostVolumeMixin


class FeatureCalculationGPU(
    FeatureCalculationGPUCoreMixin,
    FeatureCalculationGPUCalculatePriceVolumeMixin,
    FeatureCalculationGPUPostVolumeMixin,
):
    """FeatureCalculationGPU - 组合所有方法集"""
    pass


__all__ = ["FeatureCalculationGPU"]
