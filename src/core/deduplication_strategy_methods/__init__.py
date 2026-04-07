"""DeduplicationStrategy 方法级拆分包"""
from .core import DeduplicationStrategyCoreMixin
from .validate_single_table import DeduplicationStrategyValidateSingleTableMixin
from .validation import DeduplicationStrategyValidationMixin


class DeduplicationStrategy(
    DeduplicationStrategyCoreMixin,
    DeduplicationStrategyValidateSingleTableMixin,
    DeduplicationStrategyValidationMixin,
):
    """DeduplicationStrategy - 组合所有方法集"""
    pass


__all__ = ["DeduplicationStrategy"]
