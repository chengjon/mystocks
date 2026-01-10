"""
Portfolio Repository Implementation
组合管理仓储实现
"""

import json
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from src.application.portfolio.model import Portfolio, Holding, Transaction
from src.application.portfolio.repository import IPortfolioRepository

logger = logging.getLogger(__name__)


class PortfolioRepositoryImpl(IPortfolioRepository):
    """组合仓储实现"""

    def __init__(self, session: Session):
        self.session = session
        self._ensure_table()

    def _ensure_table(self) -> None:
        from sqlalchemy import text

        sql = """
        CREATE TABLE IF NOT EXISTS ddd_portfolios_v2 (
            id VARCHAR(64) PRIMARY KEY,
            name VARCHAR(128) NOT NULL,
            portfolio_type VARCHAR(32) NOT NULL,
            description TEXT,
            initial_capital FLOAT,
            current_value FLOAT,
            cash FLOAT,
            benchmark_index VARCHAR(16),
            holdings_json TEXT,
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

    def save(self, portfolio: Portfolio) -> None:
        from sqlalchemy import text

        holdings_json = json.dumps({symbol: h.to_dict() for symbol, h in portfolio.holdings.items()})

        sql = """
        INSERT OR REPLACE INTO ddd_portfolios_v2
        (id, name, portfolio_type, description, initial_capital, current_value,
         cash, benchmark_index, holdings_json, created_at, updated_at)
        VALUES ( :id, :name, :type, :desc, :init_val, :curr_val, :cash, :bench, :holdings, :created, :updated)
        """
        params = {
            "id": portfolio.id,
            "name": portfolio.name,
            "type": portfolio.portfolio_type,
            "desc": portfolio.description,
            "init_val": portfolio.initial_capital,
            "curr_val": portfolio.current_value,
            "cash": portfolio.cash,
            "bench": portfolio.benchmark_index,
            "holdings": holdings_json,
            "created": portfolio.created_at,
            "updated": portfolio.updated_at,
        }
        try:
            self.session.execute(text(sql), params)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise

    def find_by_id(self, portfolio_id: str) -> Optional[Portfolio]:
        from sqlalchemy import text

        sql = "SELECT * FROM ddd_portfolios_v2 WHERE id = :portfolio_id"
        result = self.session.execute(text(sql), {"portfolio_id": portfolio_id}).fetchone()
        if not result:
            return None
        return self._row_to_portfolio(result)

    def find_by_name(self, name: str) -> Optional[Portfolio]:
        from sqlalchemy import text

        sql = "SELECT * FROM ddd_portfolios_v2 WHERE name = :name"
        result = self.session.execute(text(sql), {"name": name}).fetchone()
        if not result:
            return None
        return self._row_to_portfolio(result)

    def find_all(self, limit: int = 100) -> List[Portfolio]:
        from sqlalchemy import text

        sql = f"SELECT * FROM ddd_portfolios_v2 ORDER BY created_at DESC LIMIT {limit}"
        results = self.session.execute(text(sql)).fetchall()
        return [self._row_to_portfolio(row) for row in results]

    def delete(self, portfolio_id: str) -> None:
        from sqlalchemy import text

        sql = "DELETE FROM ddd_portfolios_v2 WHERE id = ?"
        try:
            self.session.execute(text(sql), (portfolio_id,))
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise

    def exists(self, portfolio_id: str) -> bool:
        from sqlalchemy import text

        sql = "SELECT 1 FROM ddd_portfolios_v2 WHERE id = ?"
        result = self.session.execute(text(sql), (portfolio_id,)).fetchone()
        return result is not None

    def count(self) -> int:
        from sqlalchemy import text

        sql = "SELECT COUNT(*) FROM ddd_portfolios_v2"
        result = self.session.execute(text(sql)).fetchone()
        return result[0] if result else 0

    def _row_to_portfolio(self, row) -> Portfolio:
        from datetime import datetime

        portfolio = Portfolio(
            id=row[0],
            name=row[1],
            portfolio_type=row[2],
            description=row[3] or "",
            initial_capital=row[4] or 0,
            current_value=row[5] or 0,
            cash=row[6] or 0,
            benchmark_index=row[7] or "000300",
            created_at=row[9] if isinstance(row[9], datetime) else datetime.now(),
            updated_at=row[10] if isinstance(row[10], datetime) else datetime.now(),
        )
        return portfolio
