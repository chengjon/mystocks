"""ComplianceTestEngine 方法级拆分包"""
from .part1 import ComplianceTestEngineCoreMixin
from .part2 import ComplianceTestEngineTestTransactionIntegrityMixin


class ComplianceTestEngine(
    ComplianceTestEngineCoreMixin,
    ComplianceTestEngineTestTransactionIntegrityMixin,
):
    """ComplianceTestEngine - 组合所有方法集"""
    pass


__all__ = ["ComplianceTestEngine"]
