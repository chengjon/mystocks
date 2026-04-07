"""GPURiskCalculator 方法级拆分包"""
from .core import GPURiskCalculatorCoreMixin
from .get_concentration_level import GPURiskCalculatorGetConcentrationLevelMixin
from .portfolio_events import GPURiskCalculatorPortfolioEventsMixin


class GPURiskCalculator(
    GPURiskCalculatorCoreMixin,
    GPURiskCalculatorGetConcentrationLevelMixin,
    GPURiskCalculatorPortfolioEventsMixin,
):
    """GPURiskCalculator - 组合所有方法集"""
    pass


__all__ = ["GPURiskCalculator"]
