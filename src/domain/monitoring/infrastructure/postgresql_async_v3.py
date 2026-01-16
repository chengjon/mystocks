#!/usr/bin/env python3
"""
监控模块 - PostgreSQL异步数据库访问层 (v3.0)

职责:
- 封装 asyncpg 连接池管理
- 提供类型安全的数据库操作方法
- 支持批量操作（性能优化）
- 支持健康度评分和高级风险指标

作者: Claude Code (Main CLI)
创建日期: 2026-01-07
版本: v3.0
依赖: asyncpg >= 0.27.0
版权: MyStocks Project © 2026
"""

import asyncio
import json
import logging
import os
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from dataclasses import dataclass

try:
    import asyncpg

    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    logging.warning("⚠️ asyncpg 不可用，异步数据库功能将不可用")

logger = logging.getLogger(__name__)


@dataclass
class WatchlistCreate:
    """创建清单参数"""

    user_id: int
    name: str
    watchlist_type: str = "manual"
    risk_profile: Optional[Dict] = None


@dataclass
class StockToAdd:
    """添加股票参数"""

    watchlist_id: int
    stock_code: str
    entry_price: Optional[float] = None
    entry_reason: Optional[str] = None
    stop_loss_price: Optional[float] = None
    target_price: Optional[float] = None
    weight: float = 0.0


@dataclass
class HealthScoreData:
    """健康度评分数据"""

    stock_code: str
    score_date: date
    total_score: float
    radar_scores: Dict[str, float]
    market_regime: str
    sortino_ratio: Optional[float] = None
    calmar_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    max_drawdown_duration: Optional[int] = None
    downside_deviation: Optional[float] = None


class MonitoringPostgreSQLAccess:
    """
    监控模块异步PostgreSQL访问层

    特性:
    - 连接池管理 (min_size=5, max_size=20)
    - 自动重连
    - 批量操作优化
    - 类型安全的查询方法
    - 支持高级风险指标 (Sortino, Calmar等)
    """


def __init__(self):
    self.pool: Optional[asyncpg.Pool] = None
    self._connected = False


async def initialize(self):
    """
    初始化连接池（FastAPI startup事件调用）

    使用环境变量配置：
    POSTGRESQL_HOST=192.168.123.104
    POSTGRESQL_PORT=5438
    POSTGRESQL_USER=postgres
    POSTGRESQL_PASSWORD=c790414J
    POSTGRESQL_DATABASE=mystocks
    """
    if not ASYNCPG_AVAILABLE:
        logger.error("❌ asyncpg 不可用，无法初始化连接池")
        raise RuntimeError("asyncpg module not available")

    try:
        self.pool = await asyncpg.create_pool(
            host=os.getenv("POSTGRESQL_HOST", "192.168.123.104"),
            port=int(os.getenv("POSTGRESQL_PORT", 5438)),
            user=os.getenv("POSTGRESQL_USER", "postgres"),
            password=os.getenv("POSTGRESQL_PASSWORD", "c790414J"),
            database=os.getenv("POSTGRESQL_DATABASE", "mystocks"),
            min_size=5,
            max_size=20,
            command_timeout=60,
            max_inactive_connection_lifetime=300.0,
        )
        self._connected = True
        logger.info("✅ 监控模块数据库连接池已初始化 (v3.0)")
        logger.info(f"   - Host: {os.getenv('POSTGRESQL_HOST')}")
        logger.info(f"   - Port: {os.getenv('POSTGRESQL_PORT')}")
        logger.info(f"   - Database: {os.getenv('POSTGRESQL_DATABASE')}")
        logger.info(f"   - Pool Size: 5-20")

    except Exception as e:
        logger.error(f"❌ 数据库连接池初始化失败: {e}")
        raise


async def close(self):
    """关闭连接池"""
    if self.pool:
        await self.pool.close()
        self._connected = False
        logger.info("✅ 监控模块数据库连接池已关闭")


def is_connected(self) -> bool:
    """检查连接状态"""
    return self._connected and self.pool is not None

    # =====================================================
    # 监控清单相关操作
    # =====================================================


async def create_watchlist(self, params: WatchlistCreate) -> int:
    """
    创建监控清单

    Args:
        params: 清单创建参数

    Returns:
        新创建的清单ID
    """
    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    async with self.pool.acquire() as conn:
        watchlist_id = await conn.fetchval(
            """
                INSERT INTO monitoring_watchlists
                (user_id, name, type, risk_profile, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id
                """,
            params.user_id,
            params.name,
            params.watchlist_type,
            json.dumps(params.risk_profile) if params.risk_profile else None,
        )

    logger.info(f"✅ 创建监控清单: {params.name} (ID: {watchlist_id})")
    return watchlist_id


async def get_watchlist(self, watchlist_id: int) -> Optional[Dict]:
    """获取监控清单详情"""
    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    async with self.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
                SELECT * FROM monitoring_watchlists
                WHERE id = $1
                """,
            watchlist_id,
        )

    if row:
        result = dict(row)
        if result.get("risk_profile"):
            result["risk_profile"] = json.loads(result["risk_profile"])
        return result
    return None


async def get_user_watchlists(self, user_id: int) -> List[Dict]:
    """获取用户所有监控清单"""
    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    async with self.pool.acquire() as conn:
        rows = await conn.fetch(
            """
                SELECT * FROM monitoring_watchlists
                WHERE user_id = $1 AND is_active = true
                ORDER BY created_at DESC
                """,
            user_id,
        )

    results = []
    for row in rows:
        result = dict(row)
        if result.get("risk_profile"):
            result["risk_profile"] = json.loads(result["risk_profile"])
        results.append(result)

    logger.info(f"✅ 获取用户 {user_id} 的 {len(results)} 个清单")
    return results


async def add_stock_to_watchlist(self, params: StockToAdd) -> int:
    """
    添加股票到监控清单（增强版）

    Args:
        params: 添加股票参数

    Returns:
        记录ID
    """
    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    async with self.pool.acquire() as conn:
        record_id = await conn.fetchval(
            """
                INSERT INTO monitoring_watchlist_stocks
                (watchlist_id, stock_code, entry_price, entry_at, entry_reason,
                 stop_loss_price, target_price, weight, is_active)
                VALUES ($1, $2, $3, CURRENT_TIMESTAMP, $4, $5, $6, $7, true)
                ON CONFLICT (watchlist_id, stock_code)
                DO UPDATE SET
                    entry_price = EXCLUDED.entry_price,
                    entry_reason = EXCLUDED.entry_reason,
                    stop_loss_price = EXCLUDED.stop_loss_price,
                    target_price = EXCLUDED.target_price,
                    weight = EXCLUDED.weight
                RETURNING id
                """,
            params.watchlist_id,
            params.stock_code,
            params.entry_price,
            params.entry_reason,
            params.stop_loss_price,
            params.target_price,
            params.weight,
        )

    logger.info(f"✅ 添加股票到清单 {params.watchlist_id}: {params.stock_code}")
    return record_id


async def batch_add_stocks(self, watchlist_id: int, stocks: List[StockToAdd]) -> Dict[str, int]:
    """
    批量添加股票到清单

    Returns:
        {'success': 成功数量, 'skipped': 跳过数量}
    """
    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    success_count = 0
    skipped_count = 0

    async with self.pool.acquire() as conn:
        for stock in stocks:
            try:
                await conn.fetchval(
                    """
                        INSERT INTO monitoring_watchlist_stocks
                        (watchlist_id, stock_code, entry_price, entry_at, entry_reason,
                         stop_loss_price, target_price, weight, is_active)
                        VALUES ($1, $2, $3, CURRENT_TIMESTAMP, $4, $5, $6, $7, true)
                        ON CONFLICT (watchlist_id, stock_code) DO NOTHING
                        """,
                    watchlist_id,
                    stock.stock_code,
                    stock.entry_price,
                    stock.entry_reason,
                    stock.stop_loss_price,
                    stock.target_price,
                    stock.weight,
                )
                success_count += 1
            except Exception:
                skipped_count += 1

    logger.info(f"✅ 批量添加股票: 成功 {success_count}, 跳过 {skipped_count}")
    return {"success": success_count, "skipped": skipped_count}


async def get_watchlist_with_stocks(self, watchlist_id: int) -> Optional[Dict]:
    """
    获取清单及成员（API调用）

    Returns:
        清单详情 + 股票列表
    """
    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    async with self.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
                SELECT
                    w.*,
                    json_agg(
                        json_build_object(
                            'stock_code', ws.stock_code,
                            'entry_price', ws.entry_price,
                            'entry_at', ws.entry_at,
                            'entry_reason', ws.entry_reason,
                            'stop_loss_price', ws.stop_loss_price,
                            'target_price', ws.target_price,
                            'weight', ws.weight,
                            'is_active', ws.is_active
                        )
                    ) as stocks
                FROM monitoring_watchlists w
                LEFT JOIN monitoring_watchlist_stocks ws
                    ON w.id = ws.watchlist_id AND ws.is_active = true
                WHERE w.id = $1
                GROUP BY w.id
                """,
            watchlist_id,
        )

    if row:
        result = dict(row)
        if result.get("risk_profile"):
            result["risk_profile"] = json.loads(result["risk_profile"])
        result["stocks"] = result.get("stocks", [])
        return result
    return None


async def delete_watchlist(self, watchlist_id: int) -> bool:
    """
    删除清单（级联删除成员）
    """
    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    async with self.pool.acquire() as conn:
        await conn.execute("DELETE FROM monitoring_watchlists WHERE id = $1", watchlist_id)

    logger.info(f"✅ 删除清单: {watchlist_id}")
    return True


async def remove_stock_from_watchlist(self, watchlist_id: int, stock_code: str) -> bool:
    """
    从清单移除股票（软删除）
    """
    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    async with self.pool.acquire() as conn:
        await conn.execute(
            """
                UPDATE monitoring_watchlist_stocks
                SET is_active = false
                WHERE watchlist_id = $1 AND stock_code = $2
                """,
            watchlist_id,
            stock_code,
        )

    logger.info(f"✅ 从清单 {watchlist_id} 移除股票: {stock_code}")
    return True


async def get_watchlist_stocks(self, watchlist_id: int) -> List[Dict]:
    """
    获取清单中的所有股票

    Args:
        watchlist_id: 清单ID

    Returns:
        股票列表
    """
    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

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

    # =====================================================
    # 健康度评分相关操作
    # =====================================================


async def batch_save_health_scores(self, scores: List[HealthScoreData]) -> None:
    """
    批量保存健康度评分（Worker调用）

    Args:
        scores: 健康度评分数据列表，包含高级风险指标
    """
    if not scores:
        return

    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    async with self.pool.acquire() as conn:
        await conn.executemany(
            """
                INSERT INTO monitoring_health_scores
                (stock_code, score_date, total_score, radar_scores,
                 sortino_ratio, calmar_ratio, max_drawdown,
                 max_drawdown_duration, downside_deviation, market_regime)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, CURRENT_TIMESTAMP)
                ON CONFLICT (stock_code, score_date)
                DO UPDATE SET
                    total_score = EXCLUDED.total_score,
                    radar_scores = EXCLUDED.radar_scores,
                    sortino_ratio = EXCLUDED.sortino_ratio,
                    calmar_ratio = EXCLUDED.calmar_ratio,
                    max_drawdown = EXCLUDED.max_drawdown,
                    max_drawdown_duration = EXCLUDED.max_drawdown_duration,
                    downside_deviation = EXCLUDED.downside_deviation,
                    market_regime = EXCLUDED.market_regime
                """,
            [
                (
                    s.stock_code,
                    s.score_date,
                    s.total_score,
                    json.dumps(s.radar_scores),
                    s.sortino_ratio,
                    s.calmar_ratio,
                    s.max_drawdown,
                    s.max_drawdown_duration,
                    s.downside_deviation,
                    s.market_regime,
                )
                for s in scores
            ],
        )

    logger.info(f"✅ 批量保存 {len(scores)} 条健康度评分 (含高级风险指标)")


async def get_health_score(self, stock_code: str, score_date: date) -> Optional[Dict]:
    """
    获取单只股票的健康度评分
    """
    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    async with self.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
                SELECT * FROM monitoring_health_scores
                WHERE stock_code = $1 AND score_date = $2
                """,
            stock_code,
            score_date,
        )

    if row:
        result = dict(row)
        result["radar_scores"] = json.loads(result.get("radar_scores", "{}"))
        return result
    return None


async def get_health_score_history(
    self, stock_code: str, start_date: date, end_date: date, limit: int = 100
) -> List[Dict]:
    """
    获取股票健康度历史曲线

    Args:
        stock_code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        limit: 最大返回数量

    Returns:
        健康度历史记录列表
    """
    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    async with self.pool.acquire() as conn:
        rows = await conn.fetch(
            """
                SELECT * FROM monitoring_health_scores
                WHERE stock_code = $1
                  AND score_date >= $2
                  AND score_date <= $3
                ORDER BY score_date DESC
                LIMIT $4
                """,
            stock_code,
            start_date,
            end_date,
            limit,
        )

    results = []
    for row in rows:
        result = dict(row)
        result["radar_scores"] = json.loads(result.get("radar_scores", "{}"))
        results.append(result)

    logger.info(f"✅ 获取股票 {stock_code} 健康度历史: {len(results)} 条记录")
    return results


async def get_latest_health_scores(self, stock_codes: List[str]) -> Dict[str, Dict]:
    """
    批量获取多只股票的最新健康度评分

    Args:
        stock_codes: 股票代码列表

    Returns:
        {stock_code: health_score_dict}
    """
    if not stock_codes:
        return {}

    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    async with self.pool.acquire() as conn:
        rows = await conn.fetch(
            """
                SELECT DISTINCT ON (stock_code)
                    stock_code,
                    score_date,
                    total_score,
                    radar_scores,
                    sortino_ratio,
                    calmar_ratio,
                    max_drawdown,
                    max_drawdown_duration,
                    downside_deviation,
                    market_regime
                FROM monitoring_health_scores
                WHERE stock_code = ANY($1)
                ORDER BY stock_code, score_date DESC
                """,
            stock_codes,
        )

    results = {}
    for row in rows:
        result = dict(row)
        result["radar_scores"] = json.loads(result.get("radar_scores", "{}"))
        results[row["stock_code"]] = result

    logger.info(f"✅ 批量获取 {len(results)} 只股票的最新健康度评分")
    return results

    # =====================================================
    # 统计和查询操作
    # =====================================================


async def get_watchlist_performance_summary(self, watchlist_id: int) -> Optional[Dict]:
    """
    获取清单绩效汇总

    Returns:
        {
            'stock_count': 股票数量,
            'avg_return': 平均收益率,
            'min_return': 最小收益率,
            'max_return': 最大收益率,
            'stop_loss_count': 触发止损数量,
            'target_count': 达到止盈数量
        }
    """
    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    async with self.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
                SELECT
                    COUNT(*) as stock_count,
                    AVG((k.close - ws.entry_price) / NULLIF(ws.entry_price, 0)) as avg_return,
                    MIN((k.close - ws.entry_price) / NULLIF(ws.entry_price, 0)) as min_return,
                    MAX((k.close - ws.entry_price) / NULLIF(ws.entry_price, 0)) as max_return,
                    SUM(CASE WHEN k.close <= ws.stop_loss_price THEN 1 ELSE 0 END) as stop_loss_count,
                    SUM(CASE WHEN k.close >= ws.target_price THEN 1 ELSE 0 END) as target_count
                FROM monitoring_watchlist_stocks ws
                LEFT JOIN LATERAL (
                    SELECT close FROM stock_kline_daily
                    WHERE stock_code = ws.stock_code
                    ORDER BY timestamp DESC
                    LIMIT 1
                ) k ON true
                WHERE ws.watchlist_id = $1 AND ws.is_active = true
                """,
            watchlist_id,
        )

    if row:
        return dict(row)
    return None


async def get_portfolio_risk_distribution(self, watchlist_id: int) -> Optional[Dict]:
    """
    获取组合风险分布

    Returns:
        {
            'high_risk': 高风险股票数,
            'medium_risk': 中风险股票数,
            'low_risk': 低风险股票数
        }
    """
    if not self._connected:
        raise RuntimeError("数据库连接未初始化")

    async with self.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
                SELECT
                    SUM(CASE WHEN hs.total_score < 60 THEN 1 ELSE 0 END) as high_risk,
                    SUM(CASE WHEN hs.total_score >= 60 AND hs.total_score < 80 THEN 1 ELSE 0 END) as medium_risk,
                    SUM(CASE WHEN hs.total_score >= 80 THEN 1 ELSE 0 END) as low_risk
                FROM monitoring_watchlist_stocks ws
                JOIN LATERAL (
                    SELECT stock_code, total_score
                    FROM monitoring_health_scores hs
                    WHERE score_date = (
                        SELECT MAX(score_date)
                        FROM monitoring_health_scores
                        WHERE stock_code = hs.stock_code
                    )
                ) hs ON ws.stock_code = hs.stock_code
                WHERE ws.watchlist_id = $1 AND ws.is_active = true
                """,
            watchlist_id,
        )

    if row:
        return dict(row)
    return None


# =====================================================
# 全局单例
# =====================================================

_postgres_async_instance: Optional[MonitoringPostgreSQLAccess] = None


def get_postgres_async() -> MonitoringPostgreSQLAccess:
    """
    获取全局单例实例

    Returns:
        MonitoringPostgreSQLAccess 实例
    """
    global _postgres_async_instance
    if _postgres_async_instance is None:
        _postgres_async_instance = MonitoringPostgreSQLAccess()
    return _postgres_async_instance


async def initialize_postgres_async() -> bool:
    """
    初始化全局单例

    Returns:
        是否成功
    """
    instance = get_postgres_async()
    try:
        await instance.initialize()
        return True
    except Exception as e:
        logger.error(f"❌ 异步数据库初始化失败: {e}")
        return False


async def close_postgres_async():
    """
    关闭全局单例
    """
    instance = get_postgres_async()
    await instance.close()
    logger.info("✅ 异步数据库连接已关闭")
