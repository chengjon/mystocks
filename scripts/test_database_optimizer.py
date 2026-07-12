"""测试数据库优化器
Test Database Optimizer

验证数据库优化、索引优化、查询分析等功能的正确性。
Validates database optimization, index optimization, query analysis functions.
"""

import asyncio
import logging
import os
import sys
from unittest.mock import patch


# Setup project path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from scripts.database.database_optimizer import DatabaseOptimizer


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockDatabaseConnection:
    """模拟数据库连接"""

    def __init__(self):
        self.queries_executed = []
        self.fetch_results = {
            "table_stats": [
                {
                    "schemaname": "public",
                    "tablename": "test_table",
                    "n_tup_ins": 1000,
                    "n_tup_upd": 500,
                    "n_tup_del": 100,
                    "n_live_tup": 1400,
                    "n_dead_tup": 200,
                    "last_vacuum": None,
                    "last_autovacuum": None,
                    "last_analyze": None,
                    "last_autoanalyze": None,
                },
            ],
            "index_stats": [
                {
                    "schemaname": "public",
                    "tablename": "test_table",
                    "indexname": "idx_test_column",
                    "idx_scan": 100,
                    "idx_tup_read": 1000,
                    "idx_tup_fetch": 800,
                },
                {
                    "schemaname": "public",
                    "tablename": "test_table",
                    "indexname": "idx_unused",
                    "idx_scan": 0,
                    "idx_tup_read": 0,
                    "idx_tup_fetch": 0,
                },
            ],
            "index_candidates": [
                {
                    "schemaname": "public",
                    "tablename": "test_table",
                    "attname": "high_cardinality_column",
                    "n_distinct": 10000,
                    "correlation": 0.8,
                },
            ],
            "vacuum_candidates": [{"tablename": "test_table"}],
            "slow_queries": [
                {
                    "query": "SELECT * FROM large_table WHERE slow_column = ?",
                    "calls": 100,
                    "total_time": 50000,
                    "mean_time": 500,
                    "rows": 1000,
                },
            ],
            "frequent_queries": [
                {"query": "SELECT COUNT(*) FROM frequent_table", "calls": 5000, "total_time": 2500, "mean_time": 0.5},
            ],
        }

    async def fetch(self, query: str):
        """模拟查询结果"""
        if "pg_stat_user_tables" in query:
            return self.fetch_results["table_stats"]
        if "pg_stat_user_indexes" in query:
            return self.fetch_results["index_stats"]
        if "pg_stats" in query:
            return self.fetch_results["index_candidates"]
        if "n_dead_tup > 1000" in query:
            return self.fetch_results["vacuum_candidates"]
        if "pg_stat_statements" in query and "mean_time > 1000" in query:
            return self.fetch_results["slow_queries"]
        if "pg_stat_statements" in query and "calls > 1000" in query:
            return self.fetch_results["frequent_queries"]
        return []

    async def fetchval(self, query: str):
        """模拟单个值查询"""
        return

    async def execute(self, query: str, *args):
        """模拟执行查询"""
        self.queries_executed.append((query, args))
        return "1"  # 模拟影响行数

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


async def test_table_statistics_analysis():
    """测试表统计分析"""
    logger.info("🧪 测试表统计分析...")

    optimizer = DatabaseOptimizer()

    # Mock数据库连接
    mock_conn = MockDatabaseConnection()

    with patch.object(optimizer.db_manager, "get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_conn
        mock_get_conn.return_value.__aexit__.return_value = None

        stats = await optimizer.analyze_table_statistics()

        # 验证结果
        assert "tables" in stats
        assert "test_table" in stats["tables"]
        assert "indexes" in stats
        assert "recommendations" in stats

        # 检查膨胀检测
        table_stats = stats["tables"]["test_table"]
        assert "bloat_ratio" in table_stats
        assert table_stats["bloat_ratio"] > 0.1  # 200/1400 = 0.142

        # 检查推荐建议
        recommendations = stats["recommendations"]
        assert len(recommendations) >= 2  # VACUUM + unused index

        logger.info("✅ 表统计分析测试通过")
        return True


async def test_index_optimization():
    """测试索引优化"""
    logger.info("🧪 测试索引优化...")

    optimizer = DatabaseOptimizer()
    mock_conn = MockDatabaseConnection()

    with patch.object(optimizer.db_manager, "get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_conn
        mock_get_conn.return_value.__aexit__.return_value = None

        result = await optimizer.optimize_indexes()

        # 验证结果
        assert "created_indexes" in result
        assert "dropped_indexes" in result
        assert "errors" in result

        # 检查是否创建了索引
        created = result["created_indexes"]
        assert len(created) > 0

        # 验证索引创建参数
        index_info = created[0]
        assert "table" in index_info
        assert "column" in index_info
        assert "index_name" in index_info

        logger.info("✅ 索引优化测试通过")
        return True


async def test_table_maintenance():
    """测试表维护"""
    logger.info("🧪 测试表维护...")

    optimizer = DatabaseOptimizer()
    mock_conn = MockDatabaseConnection()

    with patch.object(optimizer.db_manager, "get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_conn
        mock_get_conn.return_value.__aexit__.return_value = None

        result = await optimizer.vacuum_analyze_tables()

        # 验证结果
        assert "vacuumed_tables" in result
        assert "analyzed_tables" in result
        assert "errors" in result

        # 检查VACUUM ANALYZE执行
        assert len(result["vacuumed_tables"]) > 0
        assert result["vacuumed_tables"][0] == "test_table"

        logger.info("✅ 表维护测试通过")
        return True


async def test_query_analysis():
    """测试查询分析"""
    logger.info("🧪 测试查询分析...")

    optimizer = DatabaseOptimizer()
    mock_conn = MockDatabaseConnection()

    with patch.object(optimizer.db_manager, "get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_conn
        mock_get_conn.return_value.__aexit__.return_value = None

        result = await optimizer.optimize_queries()

        # 验证结果
        assert "slow_queries" in result
        assert "frequent_queries" in result
        assert "recommendations" in result

        # 检查慢查询检测
        slow_queries = result["slow_queries"]
        assert len(slow_queries) > 0

        slow_query = slow_queries[0]
        assert "query" in slow_query
        assert "calls" in slow_query
        assert "mean_time_ms" in slow_query

        # 检查推荐建议
        recommendations = result["recommendations"]
        assert len(recommendations) > 0

        logger.info("✅ 查询分析测试通过")
        return True


async def test_data_cleanup():
    """测试数据清理"""
    logger.info("🧪 测试数据清理...")

    optimizer = DatabaseOptimizer()
    mock_conn = MockDatabaseConnection()

    with patch.object(optimizer.db_manager, "get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_conn
        mock_get_conn.return_value.__aexit__.return_value = None

        result = await optimizer.cleanup_old_data(days_to_keep=90)

        # 验证结果
        assert "deleted_records" in result
        assert "errors" in result

        # 检查删除记录统计
        deleted = result["deleted_records"]
        assert len(deleted) >= 2  # audit_logs and performance_metrics

        logger.info("✅ 数据清理测试通过")
        return True


async def test_full_optimization_report():
    """测试完整优化报告"""
    logger.info("🧪 测试完整优化报告...")

    optimizer = DatabaseOptimizer()
    mock_conn = MockDatabaseConnection()

    with patch.object(optimizer.db_manager, "get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_conn
        mock_get_conn.return_value.__aexit__.return_value = None

        report = await optimizer.generate_optimization_report()

        # 验证报告结构
        assert "timestamp" in report
        assert "database_stats" in report
        assert "optimization_results" in report
        assert "recommendations" in report

        # 验证数据库统计
        db_stats = report["database_stats"]
        assert "tables" in db_stats
        assert "indexes" in db_stats

        # 验证优化结果
        opt_results = report["optimization_results"]
        assert "index_optimization" in opt_results
        assert "table_maintenance" in opt_results
        assert "query_analysis" in opt_results

        logger.info("✅ 完整优化报告测试通过")
        return True


async def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 运行数据库优化器完整测试套件...")

    results = []

    # 测试1: 表统计分析
    logger.info("\n" + "=" * 50)
    logger.info("TEST 1: 表统计分析")
    logger.info("=" * 50)
    result1 = await test_table_statistics_analysis()
    results.append(("Table Statistics Analysis", result1))

    # 测试2: 索引优化
    logger.info("\n" + "=" * 50)
    logger.info("TEST 2: 索引优化")
    logger.info("=" * 50)
    result2 = await test_index_optimization()
    results.append(("Index Optimization", result2))

    # 测试3: 表维护
    logger.info("\n" + "=" * 50)
    logger.info("TEST 3: 表维护")
    logger.info("=" * 50)
    result3 = await test_table_maintenance()
    results.append(("Table Maintenance", result3))

    # 测试4: 查询分析
    logger.info("\n" + "=" * 50)
    logger.info("TEST 4: 查询分析")
    logger.info("=" * 50)
    result4 = await test_query_analysis()
    results.append(("Query Analysis", result4))

    # 测试5: 数据清理
    logger.info("\n" + "=" * 50)
    logger.info("TEST 5: 数据清理")
    logger.info("=" * 50)
    result5 = await test_data_cleanup()
    results.append(("Data Cleanup", result5))

    # 测试6: 完整优化报告
    logger.info("\n" + "=" * 50)
    logger.info("TEST 6: 完整优化报告")
    logger.info("=" * 50)
    result6 = await test_full_optimization_report()
    results.append(("Full Optimization Report", result6))

    # 总结
    logger.info("\n" + "=" * 50)
    logger.info("📊 测试结果汇总")
    logger.info("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info("%s: %s", test_name, status)
        if success:
            passed += 1

    logger.info("总体: %d/%d 测试通过", passed, total)

    if passed == total:
        logger.info("🎉 所有测试通过! 数据库优化器已准备就绪。")
        logger.info("数据库优化功能包括表分析、索引优化、查询分析、数据清理等。")
        return True
    logger.warning("⚠️ 某些测试失败。请检查实现。")
    return False


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
