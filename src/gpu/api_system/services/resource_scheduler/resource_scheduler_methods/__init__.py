"""ResourceScheduler 方法级拆分包"""
from .core import ResourceSchedulerCoreMixin
from .calculate_queue_efficiency import ResourceSchedulerCalculateQueueEfficiencyMixin
from .performance import ResourceSchedulerPerformanceMixin


class ResourceScheduler(
    ResourceSchedulerCoreMixin,
    ResourceSchedulerCalculateQueueEfficiencyMixin,
    ResourceSchedulerPerformanceMixin,
):
    """ResourceScheduler - 组合所有方法集"""
    pass


__all__ = ["ResourceScheduler"]
