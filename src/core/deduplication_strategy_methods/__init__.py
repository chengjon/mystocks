"""DeduplicationStrategy 方法级拆分包"""
from .part1 import DeduplicationStrategyCoreMixin
from .part2 import DeduplicationStrategyValidateSingleTableMixin
from .part3 import DeduplicationStrategyValidationMixin


class DeduplicationStrategy(
    DeduplicationStrategyCoreMixin,
    DeduplicationStrategyValidateSingleTableMixin,
    DeduplicationStrategyValidationMixin,
):
    """DeduplicationStrategy - 组合所有方法集"""
    pass


__all__ = ["DeduplicationStrategy"]
