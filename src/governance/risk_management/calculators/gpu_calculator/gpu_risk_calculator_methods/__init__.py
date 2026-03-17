"""GPURiskCalculator 方法级拆分包"""
from .part1 import GPURiskCalculatorCoreMixin
from .part2 import GPURiskCalculatorGetConcentrationLevelMixin
from .part3 import GPURiskCalculatorPortfolioEventsMixin


class GPURiskCalculator(
    GPURiskCalculatorCoreMixin,
    GPURiskCalculatorGetConcentrationLevelMixin,
    GPURiskCalculatorPortfolioEventsMixin,
):
    """GPURiskCalculator - 组合所有方法集"""
    pass


__all__ = ["GPURiskCalculator"]
