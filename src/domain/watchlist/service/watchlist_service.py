"""
Watchlist Domain Service
自选股领域服务

处理跨聚合根的业务逻辑。
"""

import logging
from typing import Any, Dict, List, Optional


from src.domain.watchlist.model import Watchlist, WatchlistStock
from src.domain.watchlist.value_objects import IndicatorSnapshot

from .snapshot_service import SnapshotService

logger = logging.getLogger(__name__)


class WatchlistDomainService:
    """
    自选股领域服务

    职责：
    - 处理跨聚合根的业务逻辑
    - 协调指标计算和快照捕获
    - 提供统计分析方法
    """

    def __init__(self, snapshot_service: SnapshotService):
        self.snapshot_service = snapshot_service

    def add_stock_with_snapshot(
        self,
        watchlist: Watchlist,
        stock_code: str,
        stock_name: str = "",
        capture_indicators: List[str] = None,
        reference_days: int = 20,
        notes: str = "",
        tags: List[str] = None,
    ) -> WatchlistStock:
        """
        添加股票并捕获入选快照

        Args:
            watchlist: 自选股聚合根
            stock_code: 股票代码
            stock_name: 股票名称
            capture_indicators: 需要捕获的指标列表
            reference_days: 参考历史天数
            notes: 备注
            tags: 标签
        """
        stock = watchlist.add_stock(stock_code, stock_name, notes, tags)

        if capture_indicators:
            snapshot = self.snapshot_service.capture_entry_snapshot(
                stock_code=stock_code, indicator_ids=capture_indicators, reference_days=reference_days
            )
            stock.capture_entry_snapshot(snapshot)

        logger.info("Added stock %(stock_code)s to watchlist {watchlist.name")
        return stock

    def capture_observation(
        self, watchlist: Watchlist, stock_code: str, capture_indicators: List[str] = None, notes: str = ""
    ) -> Optional[IndicatorSnapshot]:
        """
        捕获观察点快照

        Args:
            watchlist: 自选股聚合根
            stock_code: 股票代码
            capture_indicators: 需要捕获的指标列表
            notes: 观察备注
        """
        stock = watchlist.get_stock(stock_code)
        if not stock:
            raise ValueError(f"股票 {stock_code} 不在自选股中")

        if capture_indicators:
            snapshot = self.snapshot_service.capture_realtime_snapshot(
                stock_code=stock_code, indicator_ids=capture_indicators
            )
            stock.capture_observation_snapshot(snapshot)
            logger.info("Captured observation snapshot for %(stock_code)s")
            return snapshot
        return None

    def capture_timed_snapshot(
        self, watchlist: Watchlist, stock_code: str, capture_indicators: List[str] = None
    ) -> Optional[IndicatorSnapshot]:
        """捕获定时快照"""
        stock = watchlist.get_stock(stock_code)
        if not stock:
            raise ValueError(f"股票 {stock_code} 不在自选股中")

        if capture_indicators:
            snapshot = self.snapshot_service.capture_realtime_snapshot(
                stock_code=stock_code, indicator_ids=capture_indicators
            )
            stock.capture_timed_snapshot(snapshot)
            return snapshot
        return None

    def compare_stocks(
        self, watchlist: Watchlist, stock_codes: List[str], indicator_id: str = "close"
    ) -> Dict[str, Any]:
        """
        对比多只股票的指标

        Args:
            watchlist: 自选股聚合根
            stock_codes: 要对比的股票代码列表
            indicator_id: 要对比的指标
        """
        comparison = {}
        for code in stock_codes:
            stock = watchlist.get_stock(code)
            if stock:
                history = stock.get_indicator_history(indicator_id)
                if history:
                    values = [h["value"] for h in history]
                    comparison[code] = {
                        "current": values[-1] if values else None,
                        "min": min(values) if values else None,
                        "max": max(values) if values else None,
                        "avg": sum(values) / len(values) if values else None,
                        "history": history,
                    }
        return comparison

    def calculate_correlation(
        self, watchlist: Watchlist, stock_codes: List[str], indicator_id: str = "close", period: int = 20
    ) -> Dict[str, Any]:
        """
        计算股票间的相关性

        Args:
            watchlist: 自选股聚合根
            stock_codes: 股票代码列表
            indicator_id: 指标ID
            period: 计算周期
        """
        import numpy as np

        price_data = {}
        for code in stock_codes:
            stock = watchlist.get_stock(code)
            if stock:
                history = stock.get_indicator_history(indicator_id)
                prices = [h["value"] for h in history[-period:]] if len(history) >= period else []
                if prices:
                    price_data[code] = prices

        if len(price_data) < 2:
            return {"error": "需要至少2只股票的数据"}

        min_len = min(len(p) for p in price_data.values())
        aligned_data = np.array([list(price_data.values())[i][:min_len] for i in range(len(price_data))])

        if len(aligned_data) < 2 or aligned_data.shape[1] < 2:
            return {"error": "数据点不足"}

        correlation_matrix = np.corrcoef(aligned_data)

        result = {}
        codes = list(price_data.keys())
        for i, code1 in enumerate(codes):
            for j, code2 in enumerate(codes):
                result[f"{code1}_{code2}"] = float(correlation_matrix[i][j])

        result["codes"] = codes
        return result

    def get_watchlist_summary(self, watchlist: Watchlist) -> Dict[str, Any]:
        """获取自选股摘要信息"""
        stats = watchlist.get_statistics()

        price_changes = []
        for stock in watchlist.stocks.values():
            if stock.latest_snapshot and stock.entry_snapshot:
                change = stock.get_latest_price_change()
                price_changes.append(change)

        if price_changes:
            stats["avg_price_change"] = sum(price_changes) / len(price_changes)
            stats["up_count"] = sum(1 for c in price_changes if c > 0)
            stats["down_count"] = sum(1 for c in price_changes if c < 0)
        else:
            stats["avg_price_change"] = 0
            stats["up_count"] = 0
            stats["down_count"] = 0

        return stats

    def batch_capture_snapshots(
        self, watchlist: Watchlist, stock_codes: List[str] = None, indicator_ids: List[str] = None
    ) -> Dict[str, Optional[IndicatorSnapshot]]:
        """
        批量捕获快照

        Args:
            watchlist: 自选股聚合根
            stock_codes: 股票代码列表（None表示所有股票）
            indicator_ids: 指标列表
        """
        targets = stock_codes or watchlist.get_all_stock_codes()
        results = {}

        for code in targets:
            try:
                snapshot = self.snapshot_service.capture_realtime_snapshot(
                    stock_code=code, indicator_ids=indicator_ids or ["close", "volume"]
                )
                stock = watchlist.get_stock(code)
                if stock:
                    stock.capture_timed_snapshot(snapshot)
                results[code] = snapshot
            except Exception:
                logger.error("Failed to capture snapshot for %(code)s: %(e)s")
                results[code] = None

        return results
