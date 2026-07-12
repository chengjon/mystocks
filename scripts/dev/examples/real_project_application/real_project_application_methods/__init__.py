"""RealProjectApplication 方法级拆分包"""

from .part1 import RealProjectApplicationCoreMixin
from .part2 import RealProjectApplicationGenerateTeamQualityMixin


class RealProjectApplication(
    RealProjectApplicationCoreMixin,
    RealProjectApplicationGenerateTeamQualityMixin,
):
    """RealProjectApplication - 组合所有方法集"""


__all__ = ["RealProjectApplication"]
