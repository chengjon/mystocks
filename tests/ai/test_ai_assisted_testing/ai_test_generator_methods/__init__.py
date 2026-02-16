"""AITestGenerator 方法级拆分包"""
from .part1 import AITestGeneratorCoreMixin
from .part2 import AITestGeneratorCreatePatternSpecificMixin


class AITestGenerator(
    AITestGeneratorCoreMixin,
    AITestGeneratorCreatePatternSpecificMixin,
):
    """AITestGenerator - 组合所有方法集"""
    pass


__all__ = ["AITestGenerator"]
