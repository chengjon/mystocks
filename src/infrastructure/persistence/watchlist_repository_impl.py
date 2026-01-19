"""
Watchlist Repository Implementation
自选股仓储实现
"""

import json
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.domain.watchlist.model import Watchlist, WatchlistStock
from src.domain.watchlist.repository import IWatchlistRepository, IWatchlistStockRepository
from src.domain.watchlist.value_objects import WatchlistType, WatchlistConfig, IndicatorSnapshot, AlertCondition

logger = logging.getLogger(__name__)


class WatchlistModel:
    """自选股SQLAlchemy模型"""

    def __init__(self, session: Session):
        self.session = session

    @property
    def table_name(self) -> str:
        return "ddd_watchlists"


class WatchlistRepositoryImpl(IWatchlistRepository):
    """自选股仓储实现"""

    def __init__(self, session: Session):
        self.session = session
        self._ensure_table()

    def _ensure_table(self) -> None:
        """确保表存在"""
        from sqlalchemy import text

        sql = """
        CREATE TABLE IF NOT EXISTS ddd_watchlists (
            id VARCHAR(64) PRIMARY KEY,
            name VARCHAR(128) NOT NULL,
            watchlist_type VARCHAR(32) NOT NULL,
            description TEXT,
            config_json TEXT,
            color_tag VARCHAR(16),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            self.session.execute(text(sql))
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.warning(f"Table creation warning: {e}")

    def save(self, watchlist: Watchlist) -> None:
        from sqlalchemy import text

        config_json = json.dumps(watchlist.config.to_dict())
        alert_conditions = json.dumps([c.to_dict() for c in watchlist.alert_conditions])

        sql = """
        INSERT OR REPLACE INTO ddd_watchlists
        (id, name, watchlist_type, description, config_json, color_tag, created_at, updated_at)
        VALUES ( :id, :name, :type, :desc, :config, :color, :created, :updated)
        """
        params = {
            "id": watchlist.id,
            "name": watchlist.name,
            "type": watchlist.watchlist_type.value,
            "desc": watchlist.description,
            "config": config_json,
            "color": watchlist.color_tag,
            "created": watchlist.created_at,
            "updated": watchlist.updated_at,
        }
        try:
            self.session.execute(text(sql), params)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise

    def find_by_id(self, watchlist_id: str) -> Optional[Watchlist]:
        from sqlalchemy import text

        sql = "SELECT * FROM ddd_watchlists WHERE id = :watchlist_id"
        result = self.session.execute(text(sql), {"watchlist_id": watchlist_id}).fetchone()
        if not result:
            return None

        return self._row_to_watchlist(result)

    def find_by_name(self, name: str) -> Optional[Watchlist]:
        from sqlalchemy import text

        sql = "SELECT * FROM ddd_watchlists WHERE name = :name"
        result = self.session.execute(text(sql), {"name": name}).fetchone()
        if not result:
            return None
        return self._row_to_watchlist(result)

    def find_all(self, limit: int = 100) -> List[Watchlist]:
        from sqlalchemy import text

        sql = f"SELECT * FROM ddd_watchlists ORDER BY created_at DESC LIMIT {limit}"
        results = self.session.execute(text(sql)).fetchall()
        return [self._row_to_watchlist(row) for row in results]

    def find_by_type(self, watchlist_type: str) -> List[Watchlist]:
        from sqlalchemy import text

        sql = "SELECT * FROM ddd_watchlists WHERE watchlist_type = :watchlist_type"
        results = self.session.execute(text(sql), {"watchlist_type": watchlist_type}).fetchall()
        return [self._row_to_watchlist(row) for row in results]

    def delete(self, watchlist_id: str) -> None:
        from sqlalchemy import text

        sql = "DELETE FROM ddd_watchlists WHERE id = :watchlist_id"
        try:
            self.session.execute(text(sql), {"watchlist_id": watchlist_id})
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise

    def exists(self, watchlist_id: str) -> bool:
        from sqlalchemy import text

        sql = "SELECT 1 FROM ddd_watchlists WHERE id = :watchlist_id"
        result = self.session.execute(text(sql), {"watchlist_id": watchlist_id}).fetchone()
        return result is not None

    def count(self) -> int:
        from sqlalchemy import text

        sql = "SELECT COUNT(*) FROM ddd_watchlists"
        result = self.session.execute(text(sql)).fetchone()
        return result[0] if result else 0

    def _row_to_watchlist(self, row) -> Watchlist:
        from datetime import datetime

        config = WatchlistConfig()
        alert_conditions = []

        # 安全访问row字段（按索引）
        # 表结构: id, name, watchlist_type, description, config_json, color_tag, created_at, updated_at
        row_dict = dict(row._mapping) if hasattr(row, "_mapping") else {}

        return Watchlist(
            id=row[0],
            name=row[1],
            watchlist_type=WatchlistType(row[2]),
            description=row[3] if len(row) > 3 else "",
            config=config,
            alert_conditions=alert_conditions,
            color_tag=row[5] if len(row) > 5 else "#3498db",
            created_at=row[6] if len(row) > 6 and isinstance(row[6], datetime) else datetime.now(),
            updated_at=row[7] if len(row) > 7 and isinstance(row[7], datetime) else datetime.now(),
        )


class WatchlistStockRepositoryImpl(IWatchlistStockRepository):
    """自选股内股票仓储实现"""

    def __init__(self, session: Session):
        self.session = session
        self._ensure_table()

    def _ensure_table(self) -> None:
        from sqlalchemy import text

        sql = """
        CREATE TABLE IF NOT EXISTS ddd_watchlist_stocks (
            id VARCHAR(64) PRIMARY KEY,
            watchlist_id VARCHAR(64) NOT NULL,
            stock_code VARCHAR(16) NOT NULL,
            stock_name VARCHAR(64),
            notes TEXT,
            tags TEXT,
            entry_snapshot TEXT,
            observation_snapshots TEXT,
            is_active BOOLEAN DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            self.session.execute(text(sql))
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.warning(f"Table creation warning: {e}")

    def save(self, stock: WatchlistStock) -> None:
        from sqlalchemy import text

        entry_snapshot = json.dumps(stock.entry_snapshot.to_dict()) if stock.entry_snapshot else None
        observation_snapshots = json.dumps([s.to_dict() for s in stock.observation_snapshots])

        sql = """
        INSERT OR REPLACE INTO ddd_watchlist_stocks
        (id, watchlist_id, stock_code, stock_name, notes, tags, entry_snapshot,
         observation_snapshots, is_active, added_at, last_updated)
        VALUES (:id, :watchlist_id, :stock_code, :stock_name, :notes, :tags, :entry_snapshot,
                :observation_snapshots, :is_active, :added_at, :last_updated)
        """
        params = {
            "id": stock.id,
            "watchlist_id": stock.watchlist_id,
            "stock_code": stock.stock_code,
            "stock_name": stock.stock_name,
            "notes": stock.notes,
            "tags": json.dumps(stock.tags),
            "entry_snapshot": entry_snapshot,
            "observation_snapshots": observation_snapshots,
            "is_active": stock.is_active,
            "added_at": stock.added_at,
            "last_updated": stock.last_updated,
        }
        try:
            self.session.execute(text(sql), params)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise

    def find_by_id(self, stock_id: str) -> Optional[WatchlistStock]:
        from sqlalchemy import text

        sql = "SELECT * FROM ddd_watchlist_stocks WHERE id = :stock_id"
        result = self.session.execute(text(sql), {"stock_id": stock_id}).fetchone()
        if not result:
            return None
        return self._row_to_stock(result)

    def find_by_watchlist(self, watchlist_id: str) -> List[WatchlistStock]:
        from sqlalchemy import text

        sql = "SELECT * FROM ddd_watchlist_stocks WHERE watchlist_id = :watchlist_id"
        results = self.session.execute(text(sql), {"watchlist_id": watchlist_id}).fetchall()
        return [self._row_to_stock(row) for row in results]

    def find_by_code(self, watchlist_id: str, stock_code: str) -> Optional[WatchlistStock]:
        from sqlalchemy import text

        sql = "SELECT * FROM ddd_watchlist_stocks WHERE watchlist_id = :watchlist_id AND stock_code = :stock_code"
        result = self.session.execute(text(sql), {"watchlist_id": watchlist_id, "stock_code": stock_code}).fetchone()
        if not result:
            return None
        return self._row_to_stock(result)

    def delete(self, stock_id: str) -> None:
        from sqlalchemy import text

        sql = "DELETE FROM ddd_watchlist_stocks WHERE id = :stock_id"
        try:
            self.session.execute(text(sql), {"stock_id": stock_id})
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise

    def find_all_by_codes(self, stock_codes: List[str]) -> List[WatchlistStock]:
        from sqlalchemy import text

        if not stock_codes:
            return []
        placeholders = ",".join(["?"] * len(stock_codes))
        sql = f"SELECT * FROM ddd_watchlist_stocks WHERE stock_code IN ({placeholders})"
        results = self.session.execute(text(sql), tuple(stock_codes)).fetchall()
        return [self._row_to_stock(row) for row in results]

    def _row_to_stock(self, row) -> WatchlistStock:
        from datetime import datetime

        stock = WatchlistStock(
            id=row[0],
            watchlist_id=row[1],
            stock_code=row[2],
            stock_name=row[3] or "",
            notes=row[4] or "",
            tags=json.loads(row[5]) if row[5] else [],
            is_active=bool(row[8]),
            added_at=row[9] if isinstance(row[9], datetime) else datetime.now(),
            last_updated=row[10] if isinstance(row[10], datetime) else datetime.now(),
        )
        if row[6]:
            try:
                entry_data = json.loads(row[6])
                stock.entry_snapshot = IndicatorSnapshot(
                    snapshot_id=entry_data["snapshot_id"],
                    stock_code=entry_data["stock_code"],
                    captured_at=datetime.fromisoformat(entry_data["captured_at"]),
                    indicators={},
                    price_data=entry_data["price_data"],
                )
            except Exception as e:
                logger.debug(f"Failed to parse entry snapshot: {e}")

        return stock
