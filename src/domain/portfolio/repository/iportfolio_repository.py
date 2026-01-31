"""
Portfolio Repository Interface
投资组合仓储接口

定义投资组合持久化的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..model.portfolio import Portfolio
from ..model.transaction import Transaction


class IPortfolioRepository(ABC):
    """
    投资组合仓储接口

    职责：
    - 定义投资组合持久化的抽象接口
    - 提供投资组合查询方法
    - 支持按名称、创建时间查询

    实现方式：
    - PostgreSQL实现（Infrastructure层）
    """

    @abstractmethod
    def save(self, portfolio: Portfolio) -> None:
        """
        保存投资组合

        Args:
            portfolio: 投资组合聚合根
        """

    @abstractmethod
    def find_by_id(self, portfolio_id: str) -> Optional[Portfolio]:
        """
        根据ID查找投资组合

        Args:
            portfolio_id: 投资组合ID

        Returns:
            投资组合聚合根，如果不存在返回None
        """

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Portfolio]:
        """
        根据名称查找投资组合

        Args:
            name: 投资组合名称

        Returns:
            投资组合聚合根，如果不存在返回None
        """

    @abstractmethod
    def find_all(self, limit: int = 100) -> List[Portfolio]:
        """
        查找所有投资组合

        Args:
            limit: 返回数量限制

        Returns:
            投资组合列表
        """

    @abstractmethod
    def delete(self, portfolio_id: str) -> None:
        """
        删除投资组合

        Args:
            portfolio_id: 投资组合ID
        """

    @abstractmethod
    def exists(self, portfolio_id: str) -> bool:
        """
        检查投资组合是否存在

        Args:
            portfolio_id: 投资组合ID

        Returns:
            如果存在返回True，否则返回False
        """

    @abstractmethod
    def count(self) -> int:
        """
        统计投资组合数量

        Returns:
            投资组合数量
        """


class ITransactionRepository(ABC):
    """
    交易流水仓储接口

    职责：
    - 定义交易流水持久化的抽象接口
    - 提供交易流水查询方法
    - 支持按投资组合、标的查询

    实现方式：
    - PostgreSQL实现（Infrastructure层）
    """

    @abstractmethod
    def save(self, transaction: Transaction) -> None:
        """
        保存交易流水

        Args:
            transaction: 交易流水实体
        """

    @abstractmethod
    def find_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        根据ID查找交易流水

        Args:
            transaction_id: 交易流水ID

        Returns:
            交易流水实体，如果不存在返回None
        """

    @abstractmethod
    def find_by_portfolio(self, portfolio_id: str, limit: int = 100) -> List[Transaction]:
        """
        查找投资组合的所有交易流水

        Args:
            portfolio_id: 投资组合ID
            limit: 返回数量限制

        Returns:
            交易流水列表，按时间倒序
        """

    @abstractmethod
    def find_by_portfolio_and_symbol(self, portfolio_id: str, symbol: str, limit: int = 100) -> List[Transaction]:
        """
        查找投资组合中特定标的的交易流水

        Args:
            portfolio_id: 投资组合ID
            symbol: 标的代码
            limit: 返回数量限制

        Returns:
            交易流水列表，按时间倒序
        """

    @abstractmethod
    def delete(self, transaction_id: str) -> None:
        """
        删除交易流水

        Args:
            transaction_id: 交易流水ID
        """
