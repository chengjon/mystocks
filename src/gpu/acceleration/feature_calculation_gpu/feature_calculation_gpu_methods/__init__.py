"""FeatureCalculationGPU 方法级拆分包"""
from .core import FeatureCalculationGPUCoreMixin
from .calculate_price_volume import FeatureCalculationGPUCalculatePriceVolumeMixin
from .post_volume import FeatureCalculationGPUPostVolumeMixin


class FeatureCalculationGPU(
    FeatureCalculationGPUCoreMixin,
    FeatureCalculationGPUCalculatePriceVolumeMixin,
    FeatureCalculationGPUPostVolumeMixin,
):
    """FeatureCalculationGPU - 组合所有方法集"""
    pass


__all__ = ["FeatureCalculationGPU"]
