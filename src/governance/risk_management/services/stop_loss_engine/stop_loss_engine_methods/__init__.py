"""StopLossEngine 方法级拆分包"""
from .part1 import StopLossEngineCoreMixin
from .part2 import StopLossEngineCalculateTriggerConfidenceMixin


class StopLossEngine(
    StopLossEngineCoreMixin,
    StopLossEngineCalculateTriggerConfidenceMixin,
):
    """StopLossEngine - 组合所有方法集"""
    pass


__all__ = ["StopLossEngine"]
