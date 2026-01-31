"""
异步PostgreSQL访问层 - 专用于监控模块 (v3.0)

功能:
1. 非阻塞: 不阻塞FastAPI事件循环
2. 高性能: 连接池管理，支持并发请求
3. 现代化: 原生async/await语法
4. 读写分离: 支持高频写入的批量操作

创建日期: 2026-01-07
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import asyncpg

logger = logging.getLogger(__name__)


class PostgreSQLAsyncAccess:
    """
    异步PostgreSQL访问层
    """

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._dsn = None

    async def initialize(self):
        """
        初始化连接池
        """
        if self.pool:
            return

        try:
            # 构建DSN
            user = os.getenv("POSTGRESQL_USER", "postgres")
            password = os.getenv("POSTGRESQL_PASSWORD")
            if not password:
                raise ValueError("POSTGRESQL_PASSWORD environment variable must be set")
            host = os.getenv("POSTGRESQL_HOST", "localhost")
            port = os.getenv("POSTGRESQL_PORT", "5432")
            database = os.getenv("POSTGRESQL_DATABASE", "mystocks")

            self._dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"

            self.pool = await asyncpg.create_pool(dsn=self._dsn, min_size=5, max_size=20, command_timeout=60)
            logger.info("✅ 异步PostgreSQL连接池已初始化")
        except Exception as e:
            logger.error("❌ 初始化异步PostgreSQL连接池失败: %(e)s")
            raise

    async def close(self):
        """关闭连接池"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("✅ 异步PostgreSQL连接池已关闭")

    @asynccontextmanager
    async def transaction(self):
        """事务上下文管理器"""
        if not self.pool:
            await self.initialize()

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn

    # ========== 1. 监控清单 (Watchlist) 操作 ==========

    async def create_watchlist(self, user_id: int, name: str, type: str = "manual", risk_profile: Dict = None) -> int:
        """创建监控清单"""
        if not self.pool:
            await self.initialize()

        import json

        risk_profile_json = json.dumps(risk_profile) if risk_profile else None

        async with self.pool.acquire() as conn:
            watchlist_id = await conn.fetchval(
                """
                INSERT INTO monitoring_watchlists
                (user_id, name, type, risk_profile)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                user_id,
                name,
                type,
                risk_profile_json,
            )
        return watchlist_id

    async def get_watchlists_by_user(self, user_id: int) -> List[Dict]:
        """获取用户的所有监控清单"""
        if not self.pool:
            await self.initialize()

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM monitoring_watchlists
                WHERE user_id = $1 AND is_active = true
                ORDER BY created_at DESC
                """,
                user_id,
            )
        return [dict(row) for row in rows]

    async def add_stock_to_watchlist(
        self,
        watchlist_id: int,
        stock_code: str,
        entry_price: Optional[float] = None,
        entry_reason: Optional[str] = None,
        stop_loss_price: Optional[float] = None,
        target_price: Optional[float] = None,
        weight: float = 0.0,
    ) -> int:
        """添加股票到清单 (带入库上下文)"""
        if not self.pool:
            await self.initialize()

        async with self.pool.acquire() as conn:
            stock_id = await conn.fetchval(
                """
                INSERT INTO monitoring_watchlist_stocks
                (watchlist_id, stock_code, entry_price, entry_reason,
                 stop_loss_price, target_price, weight)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (watchlist_id, stock_code)
                DO UPDATE SET
                    weight = EXCLUDED.weight,
                    stop_loss_price = EXCLUDED.stop_loss_price,
                    target_price = EXCLUDED.target_price,
                    is_active = true
                RETURNING id
                """,
                watchlist_id,
                stock_code,
                entry_price,
                entry_reason,
                stop_loss_price,
                target_price,
                weight,
            )
        return stock_id

    async def get_watchlist_stocks(self, watchlist_id: int) -> List[Dict]:
        """获取清单成员"""
        if not self.pool:
            await self.initialize()

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM monitoring_watchlist_stocks
                WHERE watchlist_id = $1 AND is_active = true
                ORDER BY entry_at DESC
                """,
                watchlist_id,
            )
        return [dict(row) for row in rows]

    # ========== 2. 健康度评分 (Analysis Results) 操作 ==========

    async def batch_save_health_scores(self, scores: List[Dict[str, Any]]) -> None:
        """
        批量保存健康度评分

        Args:
            scores: [
                {
                    'stock_code': '600519.SH',
                    'score_date': '2025-01-07',
                    'total_score': 85.5,
                    'radar_scores': {...},
                    'market_regime': 'bull'
                }, ...
            ]
        """
        if not self.pool:
            await self.initialize()

        import json

        # 预处理数据
        data_tuples = []
        for s in scores:
            data_tuples.append(
                (
                    s["stock_code"],
                    s["score_date"],
                    s["total_score"],
                    json.dumps(s.get("radar_scores", {})),
                    s.get("market_regime"),
                )
            )

        async with self.pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO monitoring_health_scores
                (stock_code, score_date, total_score, radar_scores, market_regime)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (stock_code, score_date)
                DO UPDATE SET
                    total_score = EXCLUDED.total_score,
                    radar_scores = EXCLUDED.radar_scores,
                    market_regime = EXCLUDED.market_regime
                """,
                data_tuples,
            )

    async def get_latest_health_score(self, stock_code: str) -> Optional[Dict]:
        """获取最新健康度评分"""
        if not self.pool:
            await self.initialize()

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM monitoring_health_scores
                WHERE stock_code = $1
                ORDER BY score_date DESC
                LIMIT 1
                """,
                stock_code,
            )
        return dict(row) if row else None

    # ========== 3. 指标快照 (Metrics) 操作 ==========

    async def batch_save_metrics(self, metrics: List[Dict[str, Any]]) -> None:
        """批量保存基础指标 (v2.0 兼容)"""
        # 如果表存在，逻辑类似 batch_save_health_scores
        # 暂时预留


# 全局单例
postgres_async = PostgreSQLAsyncAccess()
