"""数据库优化和维护脚本
Database Optimization and Maintenance Script

提供数据库性能优化、索引维护、查询优化、数据清理等功能。
Provides database performance optimization, index maintenance, query optimization, data cleanup, etc.
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict


# Setup project path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.core.database import DatabaseManager


logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """数据库优化器"""

    def __init__(self):
        self.db_manager = DatabaseManager()

    async def analyze_table_statistics(self) -> Dict[str, Any]:
        """分析表统计信息"""
        logger.info("📊 分析表统计信息...")

        stats = {"tables": {}, "indexes": {}, "performance": {}, "recommendations": []}

        try:
            # 获取所有表信息
            tables_query = """
                SELECT
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_rows,
                    n_dead_tup as dead_rows,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                ORDER BY tablename;
            """

            async with self.db_manager.get_connection() as conn:
                tables = await conn.fetch(tables_query)

                for table in tables:
                    table_name = table["tablename"]
                    stats["tables"][table_name] = {
                        "schema": table["schemaname"],
                        "live_rows": table["live_rows"],
                        "dead_rows": table["dead_rows"],
                        "inserts": table["inserts"],
                        "updates": table["updates"],
                        "deletes": table["deletes"],
                        "last_vacuum": table["last_vacuum"],
                        "last_analyze": table["last_analyze"],
                        "bloat_ratio": (table["dead_rows"] / max(table["live_rows"], 1))
                        if table["live_rows"] > 0
                        else 0,
                    }

                    # 膨胀检查
                    if stats["tables"][table_name]["bloat_ratio"] > 0.2:
                        stats["recommendations"].append(
                            {
                                "type": "vacuum",
                                "table": table_name,
                                "issue": ".2%",
                                "solution": "运行VACUUM或VACUUM FULL",
                            },
                        )

            # 分析索引使用情况
            indexes_query = """
                SELECT
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan as index_scans,
                    idx_tup_read as tuples_read,
                    idx_tup_fetch as tuples_fetched
                FROM pg_stat_user_indexes
                ORDER BY tablename, indexname;
            """

            async with self.db_manager.get_connection() as conn:
                indexes = await conn.fetch(indexes_query)

                for index in indexes:
                    index_name = index["indexname"]
                    table_name = index["tablename"]

                    stats["indexes"][index_name] = {
                        "table": table_name,
                        "scans": index["index_scans"],
                        "tuples_read": index["tuples_read"],
                        "tuples_fetched": index["tuples_fetched"],
                        "efficiency": (index["tuples_fetched"] / max(index["tuples_read"], 1))
                        if index["tuples_read"] > 0
                        else 0,
                    }

                    # 未使用索引检查
                    if index["index_scans"] == 0:
                        stats["recommendations"].append(
                            {
                                "type": "unused_index",
                                "index": index_name,
                                "table": table_name,
                                "issue": "索引未被使用",
                                "solution": "考虑删除未使用的索引",
                            },
                        )

        except Exception as e:
            logger.error(f"分析表统计信息失败: {e}")
            stats["error"] = str(e)

        return stats

    async def optimize_indexes(self) -> Dict[str, Any]:
        """索引优化"""
        logger.info("🔧 优化索引...")

        result = {"created_indexes": [], "dropped_indexes": [], "reindexed_indexes": [], "errors": []}

        try:
            # 分析潜在的索引优化机会
            analyze_query = """
                SELECT
                    schemaname,
                    tablename,
                    attname as column_name,
                    n_distinct,
                    correlation
                FROM pg_stats
                WHERE schemaname = 'public'
                AND n_distinct > 100  -- 高基数列
                ORDER BY n_distinct DESC;
            """

            async with self.db_manager.get_connection() as conn:
                candidates = await conn.fetch(analyze_query)

                for candidate in candidates:
                    table = candidate["tablename"]
                    column = candidate["column_name"]

                    # 检查是否已有索引
                    check_index_query = f"""
                        SELECT 1 FROM pg_indexes
                        WHERE schemaname = 'public'
                        AND tablename = '{table}'
                        AND indexdef LIKE '%{column}%';
                    """

                    existing = await conn.fetchval(check_index_query)

                    if not existing:
                        # 创建索引
                        try:
                            create_index_query = f"""
                                CREATE INDEX CONCURRENTLY idx_{table}_{column}
                                ON {table} ({column});
                            """

                            await conn.execute(create_index_query)
                            result["created_indexes"].append(
                                {"table": table, "column": column, "index_name": f"idx_{table}_{column}"},
                            )

                            logger.info(f"✅ 创建索引: {table}.{column}")

                        except Exception as e:
                            result["errors"].append(
                                {"operation": "create_index", "table": table, "column": column, "error": str(e)},
                            )

        except Exception as e:
            logger.error(f"索引优化失败: {e}")
            result["errors"].append({"operation": "analyze", "error": str(e)})

        return result

    async def vacuum_analyze_tables(self) -> Dict[str, Any]:
        """清理和分析表"""
        logger.info("🧹 清理和分析表...")

        result = {"vacuumed_tables": [], "analyzed_tables": [], "errors": []}

        try:
            # 获取需要清理的表
            tables_query = """
                SELECT tablename
                FROM pg_stat_user_tables
                WHERE n_dead_tup > 1000  -- 死元组超过1000
                OR last_vacuum IS NULL
                OR last_vacuum < NOW() - INTERVAL '7 days';
            """

            async with self.db_manager.get_connection() as conn:
                tables = await conn.fetch(tables_query)

                for table in tables:
                    table_name = table["tablename"]

                    try:
                        # VACUUM ANALYZE
                        await conn.execute(f"VACUUM ANALYZE {table_name}")

                        result["vacuumed_tables"].append(table_name)
                        result["analyzed_tables"].append(table_name)

                        logger.info(f"✅ VACUUM ANALYZE: {table_name}")

                    except Exception as e:
                        result["errors"].append({"operation": "vacuum_analyze", "table": table_name, "error": str(e)})

        except Exception as e:
            logger.error(f"清理和分析表失败: {e}")
            result["errors"].append({"operation": "query_tables", "error": str(e)})

        return result

    async def optimize_queries(self) -> Dict[str, Any]:
        """查询优化分析"""
        logger.info("🔍 分析查询性能...")

        result = {"slow_queries": [], "frequent_queries": [], "recommendations": []}

        try:
            # 分析慢查询
            slow_queries_query = """
                SELECT
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements
                WHERE mean_time > 1000  -- 平均执行时间超过1秒
                ORDER BY mean_time DESC
                LIMIT 10;
            """

            async with self.db_manager.get_connection() as conn:
                slow_queries = await conn.fetch(slow_queries_query)

                for query in slow_queries:
                    result["slow_queries"].append(
                        {
                            "query": query["query"][:200] + "..." if len(query["query"]) > 200 else query["query"],
                            "calls": query["calls"],
                            "total_time_ms": query["total_time"],
                            "mean_time_ms": query["mean_time"],
                            "rows_affected": query["rows"],
                        },
                    )

                    result["recommendations"].append(
                        {
                            "type": "slow_query",
                            "query": query["query"][:100] + "...",
                            "issue": ".2f",
                            "solution": "考虑添加索引或优化查询结构",
                        },
                    )

            # 分析频繁查询
            frequent_queries_query = """
                SELECT
                    query,
                    calls,
                    total_time,
                    mean_time
                FROM pg_stat_statements
                WHERE calls > 1000  -- 调用次数超过1000
                ORDER BY calls DESC
                LIMIT 10;
            """

            async with self.db_manager.get_connection() as conn:
                frequent_queries = await conn.fetch(frequent_queries_query)

                for query in frequent_queries:
                    result["frequent_queries"].append(
                        {
                            "query": query["query"][:200] + "..." if len(query["query"]) > 200 else query["query"],
                            "calls": query["calls"],
                            "total_time_ms": query["total_time"],
                            "mean_time_ms": query["mean_time"],
                        },
                    )

        except Exception as e:
            logger.error(f"查询优化分析失败: {e}")
            result["error"] = str(e)

        return result

    async def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, Any]:
        """清理旧数据"""
        logger.info(f"🗑️ 清理 {days_to_keep} 天前的旧数据...")

        result = {"deleted_records": {}, "errors": []}

        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            # 清理旧的审计日志
            audit_cleanup_query = """
                DELETE FROM audit_logs
                WHERE created_at < $1;
            """

            # 清理旧的性能指标
            metrics_cleanup_query = """
                DELETE FROM performance_metrics
                WHERE timestamp < $1;
            """

            # 清理旧的缓存数据
            cache_cleanup_query = """
                DELETE FROM cache_entries
                WHERE expires_at < NOW() OR (last_accessed < $1 AND expires_at IS NULL);
            """

            async with self.db_manager.get_connection() as conn:
                # 清理审计日志
                try:
                    deleted = await conn.execute(audit_cleanup_query, cutoff_date)
                    result["deleted_records"]["audit_logs"] = deleted
                except Exception as e:
                    result["errors"].append({"table": "audit_logs", "error": str(e)})

                # 清理性能指标
                try:
                    deleted = await conn.execute(metrics_cleanup_query, cutoff_date)
                    result["deleted_records"]["performance_metrics"] = deleted
                except Exception as e:
                    result["errors"].append({"table": "performance_metrics", "error": str(e)})

                # 清理缓存
                try:
                    deleted = await conn.execute(cache_cleanup_query, cutoff_date)
                    result["deleted_records"]["cache_entries"] = deleted
                except Exception as e:
                    result["errors"].append({"table": "cache_entries", "error": str(e)})

            logger.info(f"✅ 数据清理完成: {result['deleted_records']}")

        except Exception as e:
            logger.error(f"数据清理失败: {e}")
            result["errors"].append({"operation": "cleanup", "error": str(e)})

        return result

    async def generate_optimization_report(self) -> Dict[str, Any]:
        """生成优化报告"""
        logger.info("📋 生成数据库优化报告...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "database_stats": {},
            "optimization_results": {},
            "recommendations": [],
        }

        try:
            # 收集统计信息
            report["database_stats"] = await self.analyze_table_statistics()

            # 执行优化
            report["optimization_results"]["index_optimization"] = await self.optimize_indexes()
            report["optimization_results"]["table_maintenance"] = await self.vacuum_analyze_tables()
            report["optimization_results"]["query_analysis"] = await self.optimize_queries()

            # 汇总建议
            all_recommendations = []
            for section in report["database_stats"].get("recommendations", []):
                all_recommendations.append(section)

            for section in report["optimization_results"]["query_analysis"].get("recommendations", []):
                all_recommendations.append(section)

            report["recommendations"] = all_recommendations

        except Exception as e:
            logger.error(f"生成优化报告失败: {e}")
            report["error"] = str(e)

        return report


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="数据库优化和维护工具")
    parser.add_argument(
        "--action",
        choices=["analyze", "optimize_indexes", "vacuum", "query_analysis", "cleanup", "full_report"],
        default="full_report",
        help="要执行的操作",
    )
    parser.add_argument("--days-to-keep", type=int, default=90, help="清理数据时保留的天数")

    args = parser.parse_args()

    # 设置日志
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    optimizer = DatabaseOptimizer()

    try:
        if args.action == "analyze":
            result = await optimizer.analyze_table_statistics()
            print("📊 表统计分析结果:")
            print(f"表数量: {len(result.get('tables', {}))}")
            print(f"索引数量: {len(result.get('indexes', {}))}")
            print(f"优化建议: {len(result.get('recommendations', []))}")

        elif args.action == "optimize_indexes":
            result = await optimizer.optimize_indexes()
            print("🔧 索引优化结果:")
            print(f"创建索引: {len(result.get('created_indexes', []))}")
            print(f"删除索引: {len(result.get('dropped_indexes', []))}")
            print(f"重建索引: {len(result.get('reindexed_indexes', []))}")

        elif args.action == "vacuum":
            result = await optimizer.vacuum_analyze_tables()
            print("🧹 表维护结果:")
            print(f"清理表数: {len(result.get('vacuumed_tables', []))}")
            print(f"分析表数: {len(result.get('analyzed_tables', []))}")

        elif args.action == "query_analysis":
            result = await optimizer.optimize_queries()
            print("🔍 查询分析结果:")
            print(f"慢查询数量: {len(result.get('slow_queries', []))}")
            print(f"频繁查询数量: {len(result.get('frequent_queries', []))}")

        elif args.action == "cleanup":
            result = await optimizer.cleanup_old_data(args.days_to_keep)
            print("🗑️ 数据清理结果:")
            for table, count in result.get("deleted_records", {}).items():
                print(f"{table}: 删除 {count} 条记录")

        elif args.action == "full_report":
            report = await optimizer.generate_optimization_report()
            print("📋 完整数据库优化报告")
            print("=" * 50)
            print(f"生成时间: {report['timestamp']}")
            print(f"表数量: {len(report['database_stats'].get('tables', {}))}")
            print(f"索引数量: {len(report['database_stats'].get('indexes', {}))}")

            print("\n优化结果:")
            opt_results = report.get("optimization_results", {})
            for operation, result in opt_results.items():
                if isinstance(result, dict):
                    success_count = len([k for k in result.keys() if k.endswith("indexes") or k.endswith("tables")])
                    print(f"  {operation}: {success_count} 项成功")

            print(f"\n优化建议数量: {len(report.get('recommendations', []))}")

            # 显示前5个建议
            recommendations = report.get("recommendations", [])[:5]
            if recommendations:
                print("\n前5个优化建议:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec.get('type', 'unknown')}: {rec.get('solution', 'N/A')}")

        print("\n✅ 数据库优化任务完成!")

    except Exception as e:
        logger.error(f"数据库优化任务失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
