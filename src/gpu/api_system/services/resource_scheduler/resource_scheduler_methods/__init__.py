"""ResourceScheduler 方法级拆分包"""
from .part1 import ResourceSchedulerCoreMixin
from .part2 import ResourceSchedulerCalculateQueueEfficiencyMixin
from .part3 import ResourceSchedulerPerformanceMixin


class ResourceScheduler(
    ResourceSchedulerCoreMixin,
    ResourceSchedulerCalculateQueueEfficiencyMixin,
    ResourceSchedulerPerformanceMixin,
):
    """ResourceScheduler - 组合所有方法集"""
    pass


__all__ = ["ResourceScheduler"]
