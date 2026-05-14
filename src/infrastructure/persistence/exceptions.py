"""
Infrastructure Persistence Exceptions
基础设施层持久化异常

定义持久化层相关的异常类。
"""

from src.domain.portfolio.exceptions import PortfolioConcurrencyException


class ConcurrencyException(PortfolioConcurrencyException):
    """
    并发冲突异常

    当检测到并发修改冲突时抛出此异常。
    通常由乐观锁（版本号）或分布式锁检测触发。
    """


class RepositoryException(Exception):
    """
    仓储异常基类

    用于所有仓储操作相关的异常。
    """


class EntityNotFoundException(RepositoryException):
    """
    实体未找到异常

    当尝试查询或操作不存在的实体时抛出。
    """

    def __init__(self, entity_type: str, entity_id: str):
        message = f"{entity_type} with ID {entity_id} not found"
        super().__init__(message)
        self.entity_type = entity_type
        self.entity_id = entity_id
