#!/usr/bin/env python3
"""
数据迁移脚本
将现有 watchlist.py 数据迁移到 monitoring_watchlists 表

功能:
1. 备份现有数据
2. 读取 SQLite 数据
3. 验证数据完整性
4. 批量写入 PostgreSQL
5. 验证迁移结果

作者: Claude Code
创建日期: 2026-01-07
"""

import os
import sys
import json
import sqlite3
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """迁移错误"""

    pass


class WatchlistDataMigrator:
    """自选股数据迁移器"""

    def __init__(
        self,
        sqlite_path: str = None,
        postgres_dsn: str = None,
        backup_dir: str = "backups",
    ):
        self.sqlite_path = sqlite_path or self._find_sqlite_db()
        self.postgres_dsn = postgres_dsn or self._get_postgres_dsn()
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.stats = {
            "total_watchlists": 0,
            "total_stocks": 0,
            "migrated_watchlists": 0,
            "migrated_stocks": 0,
            "errors": [],
        }

    def _find_sqlite_db(self) -> str:
        """查找 SQLite 数据库"""
        possible_paths = [
            "data/watchlist.db",
            "watchlist.db",
            "data/watchlist.db",
            "/opt/claude/mystocks_spec/data/watchlist.db",
        ]

        for path in possible_paths:
            if Path(path).exists():
                logger.info(f"找到 SQLite 数据库: {path}")
                return path

        logger.warning("未找到 SQLite 数据库，将创建测试数据")
        return "data/watchlist.db"

    def _get_postgres_dsn(self) -> str:
        """获取 PostgreSQL 连接字符串"""
        return os.getenv(
            "POSTGRESQL_DSN",
            "postgresql://postgres:c790414J@192.168.123.104:5438/mystocks",
        )

    def backup_sqlite(self) -> str:
        """备份 SQLite 数据库"""
        if not Path(self.sqlite_path).exists():
            logger.info("SQLite 数据库不存在，跳过备份")
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"watchlist_db_{timestamp}.sqlite"

        import shutil

        shutil.copy2(self.sqlite_path, backup_path)
        logger.info(f"SQLite 数据库已备份到: {backup_path}")

        return str(backup_path)

    def read_sqlite_data(self) -> Tuple[List[Dict], List[Dict]]:
        """读取 SQLite 数据"""
        watchlists = []
        stocks = []

        if not Path(self.sqlite_path).exists():
            logger.warning("SQLite 数据库不存在，返回空数据")
            return watchlists, stocks

        try:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            logger.info(f"SQLite 数据库中的表: {[t[0] for t in tables]}")

            try:
                cursor.execute("SELECT * FROM watchlists")
                rows = cursor.fetchall()
                for row in rows:
                    watchlists.append(dict(row))
                logger.info(f"读取 watchlists: {len(watchlists)} 条")
            except sqlite3.OperationalError as e:
                logger.warning(f"watchlists 表不存在或为空: {e}")

            try:
                cursor.execute("SELECT * FROM watchlist_stocks")
                rows = cursor.fetchall()
                for row in rows:
                    stocks.append(dict(row))
                logger.info(f"读取 watchlist_stocks: {len(stocks)} 条")
            except sqlite3.OperationalError as e:
                logger.warning(f"watchlist_stocks 表不存在或为空: {e}")

            conn.close()

        except Exception as e:
            logger.error(f"读取 SQLite 数据失败: {e}")
            raise MigrationError(f"读取数据失败: {e}")

        return watchlists, stocks

    def validate_data(self, watchlists: List[Dict], stocks: List[Dict]) -> Tuple[bool, List[str]]:
        """验证数据完整性"""
        errors = []

        for i, w in enumerate(watchlists):
            if not w.get("id"):
                errors.append(f"清单 {i}: 缺少 id")
            if not w.get("name"):
                errors.append(f"清单 {i}: 缺少 name")

        stock_watchlist_ids = set(s.get("watchlist_id") for s in stocks)
        watchlist_ids = set(w.get("id") for w in watchlists)

        orphan_stocks = stock_watchlist_ids - watchlist_ids
        if orphan_stocks:
            errors.append(f"发现孤儿股票记录: {orphan_stocks}")

        logger.info(f"数据验证完成: {len(watchlists)} 清单, {len(stocks)} 股票, {len(errors)} 错误")

        return len(errors) == 0, errors

    async def migrate_to_postgres(self, watchlists: List[Dict], stocks: List[Dict], user_id: int = 1) -> Dict[str, Any]:
        """迁移数据到 PostgreSQL"""
        try:
            import asyncpg

            conn = await asyncpg.connect(self.postgres_dsn)

            migrated_watchlists = 0
            migrated_stocks = 0

            watchlist_map = {}

            for w in watchlists:
                try:
                    watchlist_id = await conn.fetchval(
                        """
                        INSERT INTO monitoring_watchlists (user_id, name, type, risk_profile, is_active, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        RETURNING id
                        """,
                        user_id,
                        w.get("name", "未命名"),
                        w.get("type", "manual"),
                        json.dumps(w.get("risk_profile", {})) if w.get("risk_profile") else None,
                        w.get("is_active", True),
                        w.get("created_at", datetime.now()),
                        w.get("updated_at", datetime.now()),
                    )
                    watchlist_map[w["id"]] = watchlist_id
                    migrated_watchlists += 1
                    logger.debug(f"迁移清单: {w['name']} -> {watchlist_id}")
                except Exception as e:
                    self.stats["errors"].append(f"迁移清单失败 {w.get('name')}: {e}")

            for s in stocks:
                try:
                    watchlist_id = watchlist_map.get(s.get("watchlist_id"))
                    if not watchlist_id:
                        continue

                    await conn.execute(
                        """
                        INSERT INTO monitoring_watchlist_stocks
                        (watchlist_id, stock_code, entry_price, entry_at, entry_reason, stop_loss_price, target_price, weight, is_active)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        """,
                        watchlist_id,
                        s.get("stock_code"),
                        s.get("entry_price"),
                        s.get("entry_at", datetime.now()),
                        s.get("entry_reason"),
                        s.get("stop_loss_price"),
                        s.get("target_price"),
                        s.get("weight", 0),
                        s.get("is_active", True),
                    )
                    migrated_stocks += 1
                except Exception as e:
                    self.stats["errors"].append(f"迁移股票失败 {s.get('stock_code')}: {e}")

            await conn.close()

            self.stats["total_watchlists"] = len(watchlists)
            self.stats["total_stocks"] = len(stocks)
            self.stats["migrated_watchlists"] = migrated_watchlists
            self.stats["migrated_stocks"] = migrated_stocks

            return {
                "success": True,
                "watchlists_migrated": migrated_watchlists,
                "stocks_migrated": migrated_stocks,
                "errors": len(self.stats["errors"]),
            }

        except Exception as e:
            logger.error(f"迁移到 PostgreSQL 失败: {e}")
            raise MigrationError(f"迁移失败: {e}")

    def generate_report(self, migration_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成迁移报告"""
        return {
            "migration_time": datetime.now().isoformat(),
            "source": self.sqlite_path,
            "destination": self.postgres_dsn,
            "stats": self.stats,
            "result": migration_result,
            "errors": self.stats["errors"][:10],
        }

    async def run(self, user_id: int = 1, create_test_data: bool = False) -> Dict[str, Any]:
        """执行完整迁移流程"""
        logger.info("=" * 60)
        logger.info("开始数据迁移")
        logger.info("=" * 60)

        logger.info("步骤 1: 备份 SQLite 数据库")
        backup_path = self.backup_sqlite()

        if create_test_data:
            logger.info("创建测试数据...")
            watchlists, stocks = self._create_test_data()
        else:
            logger.info("步骤 2: 读取 SQLite 数据")
            watchlists, stocks = self.read_sqlite_data()

        logger.info(f"读取数据: {len(watchlists)} 清单, {len(stocks)} 股票")

        logger.info("步骤 3: 验证数据完整性")
        valid, errors = self.validate_data(watchlists, stocks)
        if not valid:
            logger.warning(f"数据验证警告: {errors}")

        logger.info("步骤 4: 迁移到 PostgreSQL")
        result = await self.migrate_to_postgres(watchlists, stocks, user_id)

        logger.info("步骤 5: 生成迁移报告")
        report = self.generate_report(result)

        logger.info("=" * 60)
        logger.info("迁移完成")
        logger.info(f"  迁移清单: {result['watchlists_migrated']}")
        logger.info(f"  迁移股票: {result['stocks_migrated']}")
        logger.info(f"  错误数: {result['errors']}")
        logger.info("=" * 60)

        return report

    def _create_test_data(self) -> Tuple[List[Dict], List[Dict]]:
        """创建测试数据"""
        watchlists = [
            {
                "id": 1,
                "name": "核心科技股",
                "type": "manual",
                "risk_profile": {"risk_tolerance": "high", "max_drawdown_limit": 0.2},
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": 2,
                "name": "金融蓝筹",
                "type": "manual",
                "risk_profile": {"risk_tolerance": "medium", "max_drawdown_limit": 0.15},
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]

        stocks = [
            {
                "watchlist_id": 1,
                "stock_code": "600519.SH",
                "entry_price": 1850.00,
                "entry_at": datetime.now(),
                "entry_reason": "macd_gold_cross",
                "stop_loss_price": 1750.00,
                "target_price": 2000.00,
                "weight": 0.30,
                "is_active": True,
            },
            {
                "watchlist_id": 1,
                "stock_code": "000001.SZ",
                "entry_price": 15.00,
                "entry_at": datetime.now(),
                "entry_reason": "manual_pick",
                "stop_loss_price": 14.25,
                "target_price": 16.50,
                "weight": 0.25,
                "is_active": True,
            },
            {
                "watchlist_id": 2,
                "stock_code": "601398.SH",
                "entry_price": 5.50,
                "entry_at": datetime.now(),
                "entry_reason": "value_investment",
                "stop_loss_price": 5.00,
                "target_price": 6.50,
                "weight": 0.40,
                "is_active": True,
            },
        ]

        return watchlists, stocks


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="自选股数据迁移工具")
    parser.add_argument("--sqlite", "-s", help="SQLite 数据库路径")
    parser.add_argument("--postgres", "-p", help="PostgreSQL 连接字符串")
    parser.add_argument("--backup", "-b", default="backups", help="备份目录")
    parser.add_argument("--user-id", "-u", type=int, default=1, help="用户ID")
    parser.add_argument("--test", action="store_true", help="使用测试数据")

    args = parser.parse_args()

    migrator = WatchlistDataMigrator(
        sqlite_path=args.sqlite,
        postgres_dsn=args.postgres,
        backup_dir=args.backup,
    )

    report = await migrator.run(user_id=args.user_id, create_test_data=args.test)

    print("\n" + "=" * 60)
    print("迁移报告")
    print("=" * 60)
    print(json.dumps(report, indent=2, default=str))

    return report


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
