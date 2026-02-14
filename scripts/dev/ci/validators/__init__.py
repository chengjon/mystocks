"""
量化策略验证器包

将 QuantStrategyValidator 的各验证维度拆分为独立 Mixin 模块。
"""

from .base import BaseValidatorMixin
from .syntax_validator import SyntaxValidatorMixin
from .correctness_validator import CorrectnessValidatorMixin
from .security_validator import SecurityValidatorMixin
from .quality_validator import QualityValidatorMixin
from .performance_validator import PerformanceValidatorMixin
from .ai_validator import AIValidatorMixin
from .quality_assessment import QualityAssessmentMixin
from .practices_checks import PracticesChecksMixin
from .integration_validators import IntegrationValidatorsMixin
from .orchestration import OrchestrationMixin


class QuantStrategyValidator(
    BaseValidatorMixin,
    SyntaxValidatorMixin,
    CorrectnessValidatorMixin,
    SecurityValidatorMixin,
    QualityValidatorMixin,
    PerformanceValidatorMixin,
    AIValidatorMixin,
    QualityAssessmentMixin,
    PracticesChecksMixin,
    IntegrationValidatorsMixin,
    OrchestrationMixin,
):
    """量化策略验证器 - 组合所有验证维度"""
    pass


__all__ = ["QuantStrategyValidator"]
