"""
Portfolio Repository Interface
组合管理仓储接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.application.portfolio.model import Portfolio


class IPortfolioRepository(ABC):
    """组合仓储接口"""

    @abstractmethod
    def save(self, portfolio: Portfolio) -> None:
        pass

    @abstractmethod
    def find_by_id(self, portfolio_id: str) -> Optional[Portfolio]:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Portfolio]:
        pass

    @abstractmethod
    def find_all(self, limit: int = 100) -> List[Portfolio]:
        pass

    @abstractmethod
    def delete(self, portfolio_id: str) -> None:
        pass

    @abstractmethod
    def exists(self, portfolio_id: str) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass
