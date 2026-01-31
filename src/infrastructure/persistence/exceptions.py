"""
Infrastructure Persistence Exceptions
基础设施层持久化异常

定义持久化层相关的异常类。
"""


class ConcurrencyException(Exception):
    """
    并发冲突异常

    当检测到并发修改冲突时抛出此异常。
    通常由乐观锁（版本号）或分布式锁检测触发。
    """

    def __init__(self, message: str, entity_type: str = None, entity_id: str = None):
        """
        初始化并发异常

        Args:
            message: 错误消息
            entity_type: 实体类型（可选）
            entity_id: 实体ID（可选）
        """
        self.entity_type = entity_type
        self.entity_id = entity_id

        if entity_type and entity_id:
            full_message = f"Concurrency conflict for {entity_type} {entity_id}: {message}"
        else:
            full_message = message

        super().__init__(full_message)


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
