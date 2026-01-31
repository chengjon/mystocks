"""
Watchlist Repository Interface
自选股仓储接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..model import Watchlist, WatchlistStock


class IWatchlistRepository(ABC):
    """自选股仓储接口"""

    @abstractmethod
    def save(self, watchlist: Watchlist) -> None:
        """保存自选股"""

    @abstractmethod
    def find_by_id(self, watchlist_id: str) -> Optional[Watchlist]:
        """根据ID查找自选股"""

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Watchlist]:
        """根据名称查找自选股"""

    @abstractmethod
    def find_all(self, limit: int = 100) -> List[Watchlist]:
        """查找所有自选股"""

    @abstractmethod
    def find_by_type(self, watchlist_type: str) -> List[Watchlist]:
        """根据类型查找自选股"""

    @abstractmethod
    def delete(self, watchlist_id: str) -> None:
        """删除自选股"""

    @abstractmethod
    def exists(self, watchlist_id: str) -> bool:
        """检查自选股是否存在"""

    @abstractmethod
    def count(self) -> int:
        """统计自选股数量"""


class IWatchlistStockRepository(ABC):
    """自选股内股票仓储接口"""

    @abstractmethod
    def save(self, stock: WatchlistStock) -> None:
        """保存股票"""

    @abstractmethod
    def find_by_id(self, stock_id: str) -> Optional[WatchlistStock]:
        """根据ID查找股票"""

    @abstractmethod
    def find_by_watchlist(self, watchlist_id: str) -> List[WatchlistStock]:
        """查找自选股内的所有股票"""

    @abstractmethod
    def find_by_code(self, watchlist_id: str, stock_code: str) -> Optional[WatchlistStock]:
        """根据股票代码查找"""

    @abstractmethod
    def delete(self, stock_id: str) -> None:
        """删除股票"""

    @abstractmethod
    def find_all_by_codes(self, stock_codes: List[str]) -> List[WatchlistStock]:
        """根据多个股票代码查找"""
