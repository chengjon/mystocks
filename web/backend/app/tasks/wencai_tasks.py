#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
问财数据后台任务

使用Celery实现的后台任务：
  1. 单个查询刷新任务
  2. 定时刷新所有查询
  3. 清理旧数据任务

作者: MyStocks Backend Team
创建日期: 2025-10-17
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from celery import shared_task
from sqlalchemy import create_engine, text

from app.services.wencai_service import WencaiService, ALLOWED_QUERY_TABLES
from app.core.database import SessionLocal
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)


def _get_safe_table_name(query_name: str) -> str:
    """
    从白名单获取安全的表名，防止 SQL 注入

    Args:
        query_name: 查询名称（如 'qs_1'）

    Returns:
        安全的表名

    Raises:
        ValueError: 如果 query_name 不在白名单中
    """
    table_name = ALLOWED_QUERY_TABLES.get(query_name)
    if not table_name:
        raise ValueError(
            f"Invalid query_name: {query_name}. Must be one of {list(ALLOWED_QUERY_TABLES.keys())}"
        )
    return table_name


@shared_task(
    name="wencai.refresh_query", bind=True, max_retries=3, default_retry_delay=60
)
def refresh_wencai_query(self, query_name: str, pages: int = 1) -> Dict[str, Any]:
    """
    刷新单个问财查询（后台任务）

    Args:
        query_name: 查询名称（如qs_1）
        pages: 获取页数

    Returns:
        执行结果统计
    """
    logger.info(f"[Celery Task] Starting refresh for {query_name}, pages={pages}")

    db = SessionLocal()

    try:
        service = WencaiService(db=db)
        result = service.fetch_and_save(query_name=query_name, pages=pages)

        logger.info(
            f"[Celery Task] Refresh completed for {query_name}: "
            f"total={result['total_records']}, "
            f"new={result['new_records']}, "
            f"dup={result['duplicate_records']}"
        )

        return {
            "success": True,
            "query_name": query_name,
            "total_records": result["total_records"],
            "new_records": result["new_records"],
            "duplicate_records": result["duplicate_records"],
            "completed_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(
            f"[Celery Task] Refresh failed for {query_name}: {str(e)}", exc_info=True
        )

        # 重试机制
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task (attempt {self.request.retries + 1})")
            raise self.retry(exc=e)

        return {
            "success": False,
            "query_name": query_name,
            "error": str(e),
            "completed_at": datetime.now().isoformat(),
        }

    finally:
        db.close()


@shared_task(name="wencai.scheduled_refresh_all")
def scheduled_refresh_all_queries(
    pages: int = 1, active_only: bool = True
) -> Dict[str, Any]:
    """
    定时刷新所有查询（每日任务）

    Args:
        pages: 每个查询获取的页数
        active_only: 是否只刷新启用的查询

    Returns:
        批量执行结果统计
    """
    logger.info(
        f"[Celery Task] Starting scheduled refresh all queries, "
        f"pages={pages}, active_only={active_only}"
    )

    db = SessionLocal()
    results = {
        "started_at": datetime.now().isoformat(),
        "total_queries": 0,
        "successful": 0,
        "failed": 0,
        "details": [],
    }

    try:
        service = WencaiService(db=db)
        queries = service.get_all_queries()

        # 过滤启用的查询
        if active_only:
            queries = [q for q in queries if q.get("is_active", False)]

        results["total_queries"] = len(queries)
        logger.info(f"Found {len(queries)} queries to refresh")

        # 逐个刷新
        for query_info in queries:
            query_name = query_info["query_name"]
            logger.info(f"Refreshing {query_name}...")

            try:
                result = service.fetch_and_save(query_name=query_name, pages=pages)

                results["successful"] += 1
                results["details"].append(
                    {
                        "query_name": query_name,
                        "success": True,
                        "new_records": result["new_records"],
                    }
                )

                logger.info(f"✅ {query_name}: {result['new_records']} new records")

            except Exception as e:
                results["failed"] += 1
                results["details"].append(
                    {"query_name": query_name, "success": False, "error": str(e)}
                )

                logger.error(f"❌ {query_name}: {str(e)}")

        results["completed_at"] = datetime.now().isoformat()
        logger.info(
            f"[Celery Task] Scheduled refresh completed: "
            f"{results['successful']}/{results['total_queries']} successful"
        )

        return results

    except Exception as e:
        logger.error(f"[Celery Task] Scheduled refresh failed: {str(e)}", exc_info=True)
        results["error"] = str(e)
        results["completed_at"] = datetime.now().isoformat()
        return results

    finally:
        db.close()


@shared_task(name="wencai.cleanup_old_data")
def cleanup_old_wencai_data(days: int = 30, dry_run: bool = False) -> Dict[str, Any]:
    """
    清理旧数据（定期维护任务）

    删除指定天数之前的数据，释放存储空间

    Args:
        days: 保留天数（删除N天前的数据）
        dry_run: 是否只模拟运行（不实际删除）

    Returns:
        清理统计结果
    """
    logger.info(
        f"[Celery Task] Starting cleanup old data, " f"days={days}, dry_run={dry_run}"
    )

    results = {
        "started_at": datetime.now().isoformat(),
        "total_tables": 0,
        "total_deleted": 0,
        "details": [],
        "dry_run": dry_run,
    }

    # 创建数据库引擎
    mysql_url = settings.MYSQL_DATABASE_URL
    engine = create_engine(mysql_url)

    try:
        # 计算截止日期
        cutoff_date = datetime.now() - timedelta(days=days)
        logger.info(f"Cutoff date: {cutoff_date}")

        # 获取所有问财结果表
        with engine.connect() as conn:
            # 查询所有wencai_qs_*表
            tables_query = text("SHOW TABLES LIKE 'wencai_qs_%'")
            tables_result = conn.execute(tables_query)
            tables = [row[0] for row in tables_result]

        results["total_tables"] = len(tables)
        logger.info(f"Found {len(tables)} result tables")

        # 逐表清理
        for table_name in tables:
            try:
                with engine.connect() as conn:
                    # 统计将被删除的记录数
                    count_query = text(
                        f"SELECT COUNT(*) as cnt FROM {table_name} "
                        f"WHERE fetch_time < :cutoff_date"
                    )
                    count_result = conn.execute(
                        count_query, {"cutoff_date": cutoff_date}
                    )
                    delete_count = count_result.scalar()

                    if delete_count > 0:
                        if not dry_run:
                            # 实际删除
                            delete_query = text(
                                f"DELETE FROM {table_name} "
                                f"WHERE fetch_time < :cutoff_date"
                            )
                            conn.execute(delete_query, {"cutoff_date": cutoff_date})
                            conn.commit()

                            logger.info(
                                f"✅ {table_name}: Deleted {delete_count} records"
                            )
                        else:
                            logger.info(
                                f"[DRY RUN] {table_name}: Would delete {delete_count} records"
                            )

                        results["total_deleted"] += delete_count
                        results["details"].append(
                            {"table": table_name, "deleted": delete_count}
                        )

            except Exception as e:
                logger.error(f"Failed to cleanup {table_name}: {str(e)}")
                results["details"].append({"table": table_name, "error": str(e)})

        results["completed_at"] = datetime.now().isoformat()
        logger.info(
            f"[Celery Task] Cleanup completed: "
            f"{results['total_deleted']} records deleted from {results['total_tables']} tables"
        )

        return results

    except Exception as e:
        logger.error(f"[Celery Task] Cleanup failed: {str(e)}", exc_info=True)
        results["error"] = str(e)
        results["completed_at"] = datetime.now().isoformat()
        return results

    finally:
        engine.dispose()


@shared_task(name="wencai.stats")
def get_wencai_stats() -> Dict[str, Any]:
    """
    获取问财统计信息（监控任务）

    统计所有查询的数据情况

    Returns:
        统计信息
    """
    logger.info("[Celery Task] Getting Wencai stats")

    db = SessionLocal()
    stats = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": 0,
        "active_queries": 0,
        "total_records": 0,
        "tables": [],
    }

    try:
        service = WencaiService(db=db)
        queries = service.get_all_queries()

        stats["total_queries"] = len(queries)
        stats["active_queries"] = len([q for q in queries if q.get("is_active", False)])

        # 统计每个表的记录数
        mysql_url = settings.MYSQL_DATABASE_URL
        engine = create_engine(mysql_url)

        with engine.connect() as conn:
            for query_info in queries:
                query_name = query_info["query_name"]
                # 使用白名单获取安全的表名
                table_name = _get_safe_table_name(query_name)

                try:
                    # 检查表是否存在
                    check_query = text(
                        "SELECT COUNT(*) as cnt "
                        f"FROM information_schema.tables "
                        f"WHERE table_schema = DATABASE() "
                        f"AND table_name = :table_name"
                    )
                    exists = (
                        conn.execute(check_query, {"table_name": table_name}).scalar()
                        > 0
                    )

                    if exists:
                        # 统计记录数
                        count_query = text(f"SELECT COUNT(*) as cnt FROM {table_name}")
                        record_count = conn.execute(count_query).scalar()

                        # 获取最新fetch_time
                        latest_query = text(
                            f"SELECT MAX(fetch_time) as latest FROM {table_name}"
                        )
                        latest_fetch = conn.execute(latest_query).scalar()

                        stats["total_records"] += record_count
                        stats["tables"].append(
                            {
                                "query_name": query_name,
                                "table_name": table_name,
                                "record_count": record_count,
                                "latest_fetch": (
                                    latest_fetch.isoformat() if latest_fetch else None
                                ),
                            }
                        )

                except Exception as e:
                    logger.warning(f"Failed to get stats for {table_name}: {str(e)}")

        engine.dispose()

        logger.info(
            f"[Celery Task] Stats completed: " f"{stats['total_records']} total records"
        )

        return stats

    except Exception as e:
        logger.error(f"[Celery Task] Failed to get stats: {str(e)}", exc_info=True)
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

    finally:
        db.close()


# ============================================================================
# 任务工具函数
# ============================================================================


def trigger_refresh_all():
    """
    手动触发刷新所有查询

    Returns:
        Celery AsyncResult
    """
    logger.info("Manually triggering refresh all queries")
    return scheduled_refresh_all_queries.delay()


def trigger_cleanup(days: int = 30, dry_run: bool = False):
    """
    手动触发清理任务

    Args:
        days: 保留天数
        dry_run: 是否模拟运行

    Returns:
        Celery AsyncResult
    """
    logger.info(f"Manually triggering cleanup: days={days}, dry_run={dry_run}")
    return cleanup_old_wencai_data.delay(days=days, dry_run=dry_run)
