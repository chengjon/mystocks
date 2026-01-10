"""
Portfolio Context Repository Interface
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..model.portfolio import Portfolio

class IPortfolioRepository(ABC):
    """投资组合仓储接口"""
    
    @abstractmethod
    def save(self, portfolio: Portfolio) -> None:
        """保存投资组合"""
        pass
    
    @abstractmethod
    def get_by_id(self, portfolio_id: str) -> Optional[Portfolio]:
        """根据ID获取"""
        pass
        
    @abstractmethod
    def get_all(self) -> List[Portfolio]:
        """获取所有投资组合"""
        pass
