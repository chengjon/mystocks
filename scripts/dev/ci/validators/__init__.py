"""量化策略验证器包

将 QuantStrategyValidator 的各验证维度拆分为独立 Mixin 模块。
"""

from .ai_validator import AIValidatorMixin
from .base import BaseValidatorMixin
from .correctness_validator import CorrectnessValidatorMixin
from .integration_validators import IntegrationValidatorsMixin
from .orchestration import OrchestrationMixin
from .performance_validator import PerformanceValidatorMixin
from .practices_checks import PracticesChecksMixin
from .quality_assessment import QualityAssessmentMixin
from .quality_validator import QualityValidatorMixin
from .security_validator import SecurityValidatorMixin
from .syntax_validator import SyntaxValidatorMixin


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


__all__ = ["QuantStrategyValidator"]
