"""AlgorithmModelRepository 方法级拆分包"""
from .part1 import AlgorithmModelRepositoryCoreMixin
from .part2 import AlgorithmModelRepositoryValidateDataIntegrityMixin
from .part3 import AlgorithmModelRepositoryMaintenanceMixin


class AlgorithmModelRepository(
    AlgorithmModelRepositoryCoreMixin,
    AlgorithmModelRepositoryValidateDataIntegrityMixin,
    AlgorithmModelRepositoryMaintenanceMixin,
):
    """AlgorithmModelRepository - 组合所有方法集"""
    pass


__all__ = ["AlgorithmModelRepository"]
