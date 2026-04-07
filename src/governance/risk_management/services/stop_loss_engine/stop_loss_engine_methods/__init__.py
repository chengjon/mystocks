"""StopLossEngine 方法级拆分包"""
from .core import StopLossEngineCoreMixin
from .calculate_trigger_confidence import StopLossEngineCalculateTriggerConfidenceMixin
from .risk_assessment import StopLossEngineRiskAssessmentMixin


class StopLossEngine(
    StopLossEngineCoreMixin,
    StopLossEngineCalculateTriggerConfidenceMixin,
    StopLossEngineRiskAssessmentMixin,
):
    """StopLossEngine - 组合所有方法集"""
    pass


__all__ = ["StopLossEngine"]
