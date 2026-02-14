"""ResourceScheduler 方法级拆分包"""
from .part1 import ResourceSchedulerCoreMixin
from .part2 import ResourceSchedulerCalculateQueueEfficiencyMixin


class ResourceScheduler(
    ResourceSchedulerCoreMixin,
    ResourceSchedulerCalculateQueueEfficiencyMixin,
):
    """ResourceScheduler - 组合所有方法集"""
    pass


__all__ = ["ResourceScheduler"]
