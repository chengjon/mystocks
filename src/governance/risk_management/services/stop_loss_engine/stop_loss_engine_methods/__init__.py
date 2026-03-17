"""StopLossEngine 方法级拆分包"""
from .part1 import StopLossEngineCoreMixin
from .part2 import StopLossEngineCalculateTriggerConfidenceMixin
from .part3 import StopLossEngineRiskAssessmentMixin


class StopLossEngine(
    StopLossEngineCoreMixin,
    StopLossEngineCalculateTriggerConfidenceMixin,
    StopLossEngineRiskAssessmentMixin,
):
    """StopLossEngine - 组合所有方法集"""
    pass


__all__ = ["StopLossEngine"]
