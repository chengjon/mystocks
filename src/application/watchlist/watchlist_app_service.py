"""
Watchlist Application Service
自选股应用服务

提供自选股管理的应用层接口。
"""

import logging
from typing import Any, Dict, List, Optional

from src.domain.watchlist.model import Watchlist
from src.domain.watchlist.repository import IWatchlistRepository, IWatchlistStockRepository
from src.domain.watchlist.service import SnapshotService, WatchlistDomainService
from src.domain.watchlist.value_objects import WatchlistConfig, WatchlistType

logger = logging.getLogger(__name__)


class WatchlistApplicationService:
    """
    自选股应用服务

    职责：
    - 自选股CRUD操作
    - 股票添加/移除
    - 快照捕获
    - 统计分析
    """

    def __init__(
        self,
        watchlist_repo: IWatchlistRepository,
        stock_repo: IWatchlistStockRepository,
        snapshot_service: SnapshotService = None,
    ):
        self.watchlist_repo = watchlist_repo
        self.stock_repo = stock_repo
        self.domain_service = WatchlistDomainService(snapshot_service or SnapshotService())

    def create_watchlist(
        self,
        name: str,
        watchlist_type: str,
        description: str = "",
        color_tag: str = "#3498db",
        config: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """创建自选股"""
        wlt = WatchlistType(watchlist_type)
        watchlist = Watchlist.create(name=name, watchlist_type=wlt, description=description, color_tag=color_tag)
        if config:
            watchlist.update_config(WatchlistConfig(**config))

        self.watchlist_repo.save(watchlist)
        logger.info("Created watchlist: {watchlist.id")
        return watchlist.to_dict()

    def get_watchlist(self, watchlist_id: str) -> Optional[Dict[str, Any]]:
        """获取自选股"""
        watchlist = self.watchlist_repo.find_by_id(watchlist_id)
        if not watchlist:
            return None
        return watchlist.to_dict()

    def list_watchlists(self, watchlist_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """列出自选股"""
        if watchlist_type:
            watchlists = self.watchlist_repo.find_by_type(watchlist_type)
        else:
            watchlists = self.watchlist_repo.find_all(limit)
        return [w.to_dict() for w in watchlists]

    def delete_watchlist(self, watchlist_id: str) -> bool:
        """删除自选股"""
        watchlist = self.watchlist_repo.find_by_id(watchlist_id)
        if not watchlist:
            return False
        self.watchlist_repo.delete(watchlist_id)
        logger.info("Deleted watchlist: %(watchlist_id)s")
        return True

    def add_stock(
        self,
        watchlist_id: str,
        stock_code: str,
        stock_name: str = "",
        notes: str = "",
        tags: List[str] = None,
        capture_indicators: List[str] = None,
        reference_days: int = 20,
    ) -> Dict[str, Any]:
        """添加股票到自选股"""
        watchlist = self.watchlist_repo.find_by_id(watchlist_id)
        if not watchlist:
            raise ValueError(f"自选股不存在: {watchlist_id}")

        stock = self.domain_service.add_stock_with_snapshot(
            watchlist=watchlist,
            stock_code=stock_code,
            stock_name=stock_name,
            capture_indicators=capture_indicators,
            reference_days=reference_days,
            notes=notes,
            tags=tags,
        )

        self.watchlist_repo.save(watchlist)
        self.stock_repo.save(stock)

        logger.info("Added stock %(stock_code)s to watchlist %(watchlist_id)s")
        return stock.to_dict()

    def remove_stock(self, watchlist_id: str, stock_code: str) -> bool:
        """从自选股移除股票"""
        watchlist = self.watchlist_repo.find_by_id(watchlist_id)
        if not watchlist:
            return False

        if watchlist.remove_stock(stock_code):
            self.watchlist_repo.save(watchlist)
            logger.info("Removed stock %(stock_code)s from watchlist %(watchlist_id)s")
            return True
        return False

    def capture_observation(
        self, watchlist_id: str, stock_code: str, capture_indicators: List[str] = None, notes: str = ""
    ) -> Optional[Dict[str, Any]]:
        """捕获观察点快照"""
        watchlist = self.watchlist_repo.find_by_id(watchlist_id)
        if not watchlist:
            raise ValueError(f"自选股不存在: {watchlist_id}")

        snapshot = self.domain_service.capture_observation(
            watchlist=watchlist, stock_code=stock_code, capture_indicators=capture_indicators, notes=notes
        )

        stock = watchlist.get_stock(stock_code)
        if stock:
            self.stock_repo.save(stock)
            self.watchlist_repo.save(watchlist)

        if snapshot:
            return snapshot.to_dict()
        return None

    def get_stock_info(self, watchlist_id: str, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取股票信息"""
        watchlist = self.watchlist_repo.find_by_id(watchlist_id)
        if not watchlist:
            return None

        stock = watchlist.get_stock(stock_code)
        if not stock:
            return None

        return {
            "stock": stock.to_dict(),
            "price_change_pct": stock.get_latest_price_change(),
            "volatility_metrics": stock.get_volatility_metrics(10),
            "indicator_history": stock.get_indicator_history("sma.5")[:10],
        }

    def get_watchlist_summary(self, watchlist_id: str) -> Optional[Dict[str, Any]]:
        """获取自选股摘要"""
        watchlist = self.watchlist_repo.find_by_id(watchlist_id)
        if not watchlist:
            return None
        return self.domain_service.get_watchlist_summary(watchlist)

    def compare_stocks(self, watchlist_id: str, stock_codes: List[str], indicator_id: str = "close") -> Dict[str, Any]:
        """对比股票"""
        watchlist = self.watchlist_repo.find_by_id(watchlist_id)
        if not watchlist:
            raise ValueError(f"自选股不存在: {watchlist_id}")

        return self.domain_service.compare_stocks(watchlist, stock_codes, indicator_id)

    def calculate_correlation(
        self, watchlist_id: str, stock_codes: List[str], indicator_id: str = "close", period: int = 20
    ) -> Dict[str, Any]:
        """计算相关性"""
        watchlist = self.watchlist_repo.find_by_id(watchlist_id)
        if not watchlist:
            raise ValueError(f"自选股不存在: {watchlist_id}")

        return self.domain_service.calculate_correlation(watchlist, stock_codes, indicator_id, period)

    def batch_capture_snapshots(
        self, watchlist_id: str, stock_codes: List[str] = None, indicator_ids: List[str] = None
    ) -> Dict[str, Any]:
        """批量捕获快照"""
        watchlist = self.watchlist_repo.find_by_id(watchlist_id)
        if not watchlist:
            raise ValueError(f"自选股不存在: {watchlist_id}")

        results = self.domain_service.batch_capture_snapshots(
            watchlist=watchlist, stock_codes=stock_codes, indicator_ids=indicator_ids
        )

        for stock in watchlist.stocks.values():
            self.stock_repo.save(stock)
        self.watchlist_repo.save(watchlist)

        return {
            "watchlist_id": watchlist_id,
            "captured_count": sum(1 for v in results.values() if v),
            "results": {k: v.snapshot_id if v else None for k, v in results.items()},
        }


def create_watchlist_service(
    watchlist_repo: IWatchlistRepository, stock_repo: IWatchlistStockRepository, data_source_manager=None
) -> WatchlistApplicationService:
    """工厂方法：创建自选股服务"""
    snapshot_service = SnapshotService(data_source_manager=data_source_manager)
    return WatchlistApplicationService(
        watchlist_repo=watchlist_repo, stock_repo=stock_repo, snapshot_service=snapshot_service
    )
