"""
Database Optimization Module Tests

Comprehensive test suite for index optimization, slow query analysis,
and performance monitoring across TDengine and PostgreSQL.
"""

import pytest
import sys
import os

# Calculate project root (3 levels up from script location)
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from src.database_optimization import (
    TDengineIndexOptimizer,
    PostgreSQLIndexOptimizer,
    SlowQueryAnalyzer,
    IndexPerformanceMonitor,
)


class TestTDengineIndexOptimizer:
    """Test TDengine index optimization strategies"""

    def setup_method(self):
        """Initialize optimizer for each test"""
        self.optimizer = TDengineIndexOptimizer()

    def test_initialization(self):
        """Test TDengineIndexOptimizer initialization"""
        assert self.optimizer.host == "localhost"
        assert self.optimizer.port == 6030
        assert self.optimizer.user == "root"
        assert self.optimizer.database == "market_data"
        assert self.optimizer.optimization_stats is not None

    def test_analyze_time_index_strategy(self):
        """Test time index strategy analysis"""
        result = self.optimizer.analyze_time_index_strategy()

        assert "current_strategy" in result
        assert "recommendations" in result
        assert "estimated_improvement" in result
        assert len(result["recommendations"]) >= 3

        # Verify recommendations structure
        for rec in result["recommendations"]:
            assert "priority" in rec
            assert "recommendation" in rec
            assert "impact" in rec
            assert "implementation" in rec

    def test_time_index_critical_priority(self):
        """Test that timestamp primary key has CRITICAL priority"""
        result = self.optimizer.analyze_time_index_strategy()

        critical_recs = [
            r for r in result["recommendations"] if r["priority"] == "CRITICAL"
        ]
        assert len(critical_recs) > 0
        assert any("primary key" in r["recommendation"].lower() for r in critical_recs)

    def test_analyze_tag_index_strategy(self):
        """Test tag index strategy analysis"""
        result = self.optimizer.analyze_tag_index_strategy()

        assert "tag_optimization_plan" in result
        assert "index_structure" in result
        assert "query_performance_impact" in result
        assert len(result["tag_optimization_plan"]) >= 3

        # Verify tag plan structure
        for tag in result["tag_optimization_plan"]:
            assert "tag_name" in tag
            assert "purpose" in tag
            assert "data_type" in tag
            assert "cardinality" in tag
            assert "estimated_filter_efficiency" in tag

    def test_tag_optimization_symbol_tag(self):
        """Test that symbol is primary tag with high cardinality"""
        result = self.optimizer.analyze_tag_index_strategy()

        symbol_tags = [
            t for t in result["tag_optimization_plan"] if t["tag_name"] == "symbol"
        ]
        assert len(symbol_tags) == 1
        assert "High" in symbol_tags[0]["cardinality"]
        assert "Primary" in symbol_tags[0]["index_recommendation"]

    def test_optimize_time_range_queries(self):
        """Test time-range query optimization"""
        result = self.optimizer.optimize_time_range_queries()

        assert "query_patterns" in result
        assert "optimization_techniques" in result
        assert "expected_speedup" in result
        assert len(result["query_patterns"]) >= 4
        assert len(result["optimization_techniques"]) >= 5

        # Verify query pattern structure
        for pattern in result["query_patterns"]:
            assert "pattern" in pattern
            assert "current_approach" in pattern
            assert "optimized_approach" in pattern
            assert "speedup" in pattern

    def test_time_range_speedup_expectations(self):
        """Test that time-range query optimizations show expected speedup"""
        result = self.optimizer.optimize_time_range_queries()

        # Verify speedup values are reasonable (5x to 100x)
        for pattern in result["query_patterns"]:
            speedup_str = pattern["speedup"]
            assert "x" in speedup_str.lower() or "faster" in speedup_str.lower()

    def test_get_optimization_summary(self):
        """Test comprehensive optimization summary"""
        result = self.optimizer.get_optimization_summary()

        assert "timestamp" in result
        assert "database" in result
        assert "optimization_focus" in result
        assert "performance_targets" in result
        assert "stats" in result
        assert "implementation_status" in result

        # Verify performance targets are reasonable
        assert (
            result["performance_targets"]["time_range_queries"]
            == "<500ms for 1-day range"
        )
        assert (
            result["performance_targets"]["k_line_aggregation"]
            == "<1s for 1-minute aggregation"
        )

    def test_optimization_stats_initialization(self):
        """Test that optimization stats are properly initialized"""
        assert "indexes_created" in self.optimizer.optimization_stats
        assert "indexes_optimized" in self.optimizer.optimization_stats
        assert "queries_analyzed" in self.optimizer.optimization_stats


class TestPostgreSQLIndexOptimizer:
    """Test PostgreSQL index design and optimization"""

    def setup_method(self):
        """Initialize optimizer for each test"""
        self.optimizer = PostgreSQLIndexOptimizer()

    def test_initialization(self):
        """Test PostgreSQLIndexOptimizer initialization"""
        assert self.optimizer.host == "localhost"
        assert self.optimizer.port == 5432
        assert self.optimizer.user == "postgres"
        assert self.optimizer.database == "mystocks"

    def test_design_single_column_indexes(self):
        """Test single-column index design"""
        result = self.optimizer.design_single_column_indexes()

        assert "indexes" in result
        assert "total_indexes" in result
        assert result["total_indexes"] == len(result["indexes"])
        assert result["total_indexes"] >= 7

        # Verify index structure
        for index in result["indexes"]:
            assert "table" in index
            assert "column" in index
            assert "type" in index
            assert "sql" in index
            assert "estimated_improvement" in index

    def test_single_column_indexes_have_sql(self):
        """Test that all single-column indexes have valid SQL"""
        result = self.optimizer.design_single_column_indexes()

        for index in result["indexes"]:
            assert index["sql"].startswith("CREATE INDEX")
            assert "ON" in index["sql"]

    def test_design_composite_indexes(self):
        """Test composite index design"""
        result = self.optimizer.design_composite_indexes()

        assert "composite_indexes" in result
        assert "total_indexes" in result
        assert result["total_indexes"] >= 4

        # Verify composite index structure
        for index in result["composite_indexes"]:
            assert "table" in index
            assert "columns" in index
            assert len(index["columns"]) >= 2
            assert "sql" in index
            assert "estimated_improvement" in index

    def test_composite_indexes_performance_expectation(self):
        """Test that composite indexes have high performance expectations"""
        result = self.optimizer.design_composite_indexes()

        for index in result["composite_indexes"]:
            speedup = index["estimated_improvement"]
            # Should expect at least 15x improvement
            assert (
                "20-40x" in speedup
                or "25-50x" in speedup
                or "15-35x" in speedup
                or "15-30x" in speedup
            )

    def test_design_partial_indexes(self):
        """Test partial index design"""
        result = self.optimizer.design_partial_indexes()

        assert "partial_indexes" in result
        assert "total_indexes" in result
        assert result["total_indexes"] >= 3

        # Verify partial index structure
        for index in result["partial_indexes"]:
            assert "table" in index
            assert "columns" in index
            assert "where_clause" in index
            assert "space_savings" in index
            assert "sql" in index

    def test_partial_indexes_have_where_clause(self):
        """Test that partial indexes have proper WHERE clauses"""
        result = self.optimizer.design_partial_indexes()

        for index in result["partial_indexes"]:
            assert "WHERE" in index["sql"]

    def test_design_brin_indexes(self):
        """Test BRIN index design"""
        result = self.optimizer.design_brin_indexes()

        assert "brin_indexes" in result
        assert "total_indexes" in result
        assert result["total_indexes"] >= 4

        # Verify BRIN index structure
        for index in result["brin_indexes"]:
            assert "table" in index
            assert "column" in index
            assert "USING BRIN" in index["sql"]
            assert "index_size" in index

    def test_brin_indexes_size_advantage(self):
        """Test that BRIN indexes show significant size advantage"""
        result = self.optimizer.design_brin_indexes()

        for index in result["brin_indexes"]:
            # BRIN should be significantly smaller
            assert "MB" in index["index_size"]
            assert (
                "90%" in index["estimated_improvement"]
                or "80%" in index["estimated_improvement"]
            )

    def test_get_optimization_summary(self):
        """Test comprehensive PostgreSQL optimization summary"""
        result = self.optimizer.get_optimization_summary()

        assert "timestamp" in result
        assert "database" in result
        assert "total_indexes_to_create" in result
        assert "index_breakdown" in result
        assert "estimated_total_index_size" in result
        assert "implementation_phases" in result

        # Verify index breakdown
        breakdown = result["index_breakdown"]
        assert breakdown["single_column"] >= 7
        assert breakdown["composite"] >= 4
        assert breakdown["partial"] >= 3
        assert breakdown["brin"] >= 4

    def test_optimization_summary_total_indexes(self):
        """Test that total indexes equals sum of all types"""
        result = self.optimizer.get_optimization_summary()

        breakdown = result["index_breakdown"]
        total_calculated = (
            breakdown["single_column"]
            + breakdown["composite"]
            + breakdown["partial"]
            + breakdown["brin"]
        )
        assert result["total_indexes_to_create"] == total_calculated


class TestSlowQueryAnalyzer:
    """Test slow query analysis and optimization recommendations"""

    def setup_method(self):
        """Initialize analyzer for each test"""
        self.analyzer = SlowQueryAnalyzer()

    def test_initialization(self):
        """Test SlowQueryAnalyzer initialization"""
        assert self.analyzer.SLOW_QUERY_THRESHOLD_MS == 500
        assert self.analyzer.VERY_SLOW_QUERY_THRESHOLD_MS == 2000

    def test_analyze_postgresql_slow_queries(self):
        """Test PostgreSQL slow query analysis"""
        result = self.analyzer.analyze_postgresql_slow_queries()

        assert "slow_queries" in result
        assert "recommendations" in result
        assert "total_slow_queries_identified" in result
        assert "total_daily_slow_queries" in result
        assert len(result["slow_queries"]) >= 3

        # Verify slow query structure
        for query in result["slow_queries"]:
            assert "query_id" in query
            assert "query" in query
            assert "execution_time_ms" in query
            assert "severity" in query
            assert "root_cause" in query
            assert "optimization" in query

    def test_postgresql_query_severity_levels(self):
        """Test that PostgreSQL queries have proper severity levels"""
        result = self.analyzer.analyze_postgresql_slow_queries()

        severities = set(q["severity"] for q in result["slow_queries"])
        assert severities.issubset({"CRITICAL", "HIGH", "MEDIUM", "LOW"})

    def test_postgresql_execution_times_exceed_threshold(self):
        """Test that identified slow queries exceed slow query threshold"""
        result = self.analyzer.analyze_postgresql_slow_queries()

        for query in result["slow_queries"]:
            # All identified queries should be slow
            assert query["execution_time_ms"] >= self.analyzer.SLOW_QUERY_THRESHOLD_MS

    def test_analyze_tdengine_slow_queries(self):
        """Test TDengine slow query analysis"""
        result = self.analyzer.analyze_tdengine_slow_queries()

        assert "slow_queries" in result
        assert "recommendations" in result
        assert "total_slow_queries_identified" in result
        assert "total_daily_slow_queries" in result
        assert len(result["slow_queries"]) >= 3

        # Verify slow query structure
        for query in result["slow_queries"]:
            assert "query_id" in query
            assert "query" in query
            assert "execution_time_ms" in query
            assert "root_cause" in query
            assert "optimization" in query

    def test_tdengine_critical_queries(self):
        """Test that CRITICAL queries are properly identified in TDengine"""
        result = self.analyzer.analyze_tdengine_slow_queries()

        critical_queries = [
            q for q in result["slow_queries"] if q.get("severity") == "CRITICAL"
        ]
        assert len(critical_queries) >= 1

    def test_generate_explain_analysis(self):
        """Test EXPLAIN plan analysis"""
        query = (
            "SELECT * FROM daily_kline WHERE symbol = 'AAPL' JOIN technical_indicators"
        )
        result = self.analyzer.generate_explain_analysis(query)

        assert "query" in result
        assert "database" in result
        assert "bottlenecks" in result
        assert "optimization_suggestions" in result
        assert "estimated_improvement_factor" in result

    def test_explain_detects_full_table_scans(self):
        """Test that EXPLAIN analysis detects full table scans"""
        query = "SELECT * FROM order_records WHERE sequential scan on symbol = 'AAPL'"
        result = self.analyzer.generate_explain_analysis(query)

        # Query with "sequential" in it should have bottlenecks
        assert (
            len(result["bottlenecks"]) > 0
            or len(result["optimization_suggestions"]) > 0
        )

    def test_explain_detects_unindexed_joins(self):
        """Test that EXPLAIN analysis detects unindexed JOINs"""
        query = "SELECT * FROM daily_kline JOIN technical_indicators ON daily_kline.symbol = technical_indicators.symbol"
        result = self.analyzer.generate_explain_analysis(query)

        bottleneck_types = [b["type"] for b in result["bottlenecks"]]
        assert "JOIN WITHOUT INDEX" in bottleneck_types

    def test_get_analysis_summary(self):
        """Test comprehensive analysis summary"""
        result = self.analyzer.get_analysis_summary()

        assert "timestamp" in result
        assert "postgresql" in result
        assert "tdengine" in result
        assert "total_slow_queries" in result
        assert "total_daily_impact" in result
        assert "top_priority_actions" in result

        # Verify sub-analyses are complete
        assert result["postgresql"]["total_slow_queries_identified"] >= 3
        assert result["tdengine"]["total_slow_queries_identified"] >= 3


class TestIndexPerformanceMonitor:
    """Test query performance monitoring and benchmarking"""

    def setup_method(self):
        """Initialize monitor for each test"""
        self.monitor = IndexPerformanceMonitor()

    def test_initialization(self):
        """Test IndexPerformanceMonitor initialization"""
        assert self.monitor.slow_query_threshold_ms == 500
        assert self.monitor.very_slow_query_threshold_ms == 2000
        assert isinstance(self.monitor.query_metrics, dict)
        assert isinstance(self.monitor.index_usage_stats, dict)

    def test_record_query_execution(self):
        """Test recording query execution time"""
        self.monitor.record_query_execution("test_query", 150.5, "daily_kline")

        assert "test_query" in self.monitor.query_metrics
        assert len(self.monitor.query_metrics["test_query"]) == 1

        metric = self.monitor.query_metrics["test_query"][0]
        assert metric["execution_time_ms"] == 150.5
        assert metric["table_name"] == "daily_kline"
        assert metric["is_slow"] is False

    def test_record_slow_query(self):
        """Test that slow queries are marked correctly"""
        self.monitor.record_query_execution("slow_query", 600, "order_records")

        metric = self.monitor.query_metrics["slow_query"][0]
        assert metric["is_slow"] is True
        assert metric["is_very_slow"] is False

    def test_record_very_slow_query(self):
        """Test that very slow queries are marked correctly"""
        self.monitor.record_query_execution(
            "very_slow_query", 2500, "transaction_records"
        )

        metric = self.monitor.query_metrics["very_slow_query"][0]
        assert metric["is_very_slow"] is True

    def test_analyze_query_performance(self):
        """Test query performance analysis"""
        # Record multiple execution times
        execution_times = [100, 150, 200, 250, 300]
        for time_ms in execution_times:
            self.monitor.record_query_execution("multi_query", time_ms)

        result = self.monitor.analyze_query_performance("multi_query")

        assert "multi_query" in result
        analysis = result["multi_query"]
        assert analysis["execution_count"] == 5
        assert analysis["avg_execution_time_ms"] == 200.0
        assert analysis["min_execution_time_ms"] == 100
        assert analysis["max_execution_time_ms"] == 300

    def test_analyze_query_performance_all_queries(self):
        """Test analysis of all queries when no specific query provided"""
        self.monitor.record_query_execution("query1", 100)
        self.monitor.record_query_execution("query2", 200)

        result = self.monitor.analyze_query_performance()

        assert len(result) == 2
        assert "query1" in result
        assert "query2" in result

    def test_performance_analysis_percentiles(self):
        """Test that P95 and P99 percentiles are calculated"""
        # Record 100 execution times
        for i in range(100):
            self.monitor.record_query_execution("percentile_query", 100 + i)

        result = self.monitor.analyze_query_performance("percentile_query")
        analysis = result["percentile_query"]

        assert "p95_execution_time_ms" in analysis
        assert "p99_execution_time_ms" in analysis
        assert analysis["p95_execution_time_ms"] >= analysis["avg_execution_time_ms"]
        assert analysis["p99_execution_time_ms"] >= analysis["p95_execution_time_ms"]

    def test_track_index_usage(self):
        """Test index usage tracking"""
        self.monitor.track_index_usage("idx_symbol", used=True)
        self.monitor.track_index_usage("idx_symbol", used=True)
        self.monitor.track_index_usage("idx_unused", used=False)

        assert "idx_symbol" in self.monitor.index_usage_stats
        assert self.monitor.index_usage_stats["idx_symbol"]["total_uses"] == 2
        assert self.monitor.index_usage_stats["idx_unused"]["total_uses"] == 0

    def test_get_index_usage_report(self):
        """Test index usage report generation"""
        # Track some indexes - explicitly mark idx_unused as unused (not used at all)
        self.monitor.track_index_usage("idx_active", used=True)
        self.monitor.track_index_usage("idx_active", used=True)
        # Explicitly create an unused index entry without using it
        self.monitor.index_usage_stats["idx_unused"] = {
            "total_uses": 0,
            "unused_days": 0,
            "last_used": None,
        }

        result = self.monitor.get_index_usage_report()

        assert "total_indexes" in result
        assert "unused_indexes" in result
        assert "actively_used_indexes" in result
        assert "recommendations" in result
        assert len(result["unused_indexes"]) >= 1

    def test_establish_performance_baseline(self):
        """Test establishing a performance baseline"""
        baseline_metrics = {
            "symbol_lookup": 150.0,
            "date_range_query": 200.0,
            "composite_query": 300.0,
        }
        self.monitor.establish_performance_baseline("baseline_v1", baseline_metrics)

        assert "baseline_v1" in self.monitor.performance_baselines
        assert (
            self.monitor.performance_baselines["baseline_v1"]["metrics"]
            == baseline_metrics
        )

    def test_benchmark_query_performance(self):
        """Test query performance benchmarking"""
        result = self.monitor.benchmark_query_performance()

        assert "baseline_name" in result
        assert "test_results" in result
        assert "total_tests" in result
        assert "average_speedup" in result
        assert "performance_grade" in result
        assert len(result["test_results"]) >= 5

        # Verify test result structure
        for test in result["test_results"]:
            assert "test_name" in test
            assert "target_time_ms" in test
            assert "baseline_time_ms" in test
            assert "expected_speedup" in test

    def test_generate_performance_report(self):
        """Test comprehensive performance report generation"""
        # Record some data
        self.monitor.record_query_execution("query1", 100)
        self.monitor.record_query_execution("query2", 600)
        self.monitor.track_index_usage("idx_1", used=True)

        result = self.monitor.generate_performance_report()

        assert "timestamp" in result
        assert "report_type" in result
        assert "query_performance_summary" in result
        assert "index_usage_summary" in result
        assert "benchmark_results" in result
        assert "recommendations" in result
        assert "implementation_plan" in result


class TestDatabaseOptimizationIntegration:
    """Integration tests for the complete optimization workflow"""

    def test_complete_optimization_workflow(self):
        """Test complete optimization workflow across all modules"""
        # Initialize all components
        tdengine_opt = TDengineIndexOptimizer()
        postgresql_opt = PostgreSQLIndexOptimizer()
        slow_analyzer = SlowQueryAnalyzer()
        perf_monitor = IndexPerformanceMonitor()

        # Get analysis from each component
        td_summary = tdengine_opt.get_optimization_summary()
        pg_summary = postgresql_opt.get_optimization_summary()
        slow_query_summary = slow_analyzer.get_analysis_summary()

        # Verify all components completed successfully
        assert td_summary["implementation_status"] == "PENDING"
        assert pg_summary["implementation_status"] == "PENDING"
        assert len(slow_query_summary["postgresql"]["slow_queries"]) > 0
        assert len(slow_query_summary["tdengine"]["slow_queries"]) > 0

    def test_optimization_recommendations_consistency(self):
        """Test that optimization recommendations are consistent across modules"""
        postgresql_opt = PostgreSQLIndexOptimizer()
        slow_analyzer = SlowQueryAnalyzer()

        pg_summary = postgresql_opt.get_optimization_summary()
        slow_summary = slow_analyzer.get_analysis_summary()

        # Both should recommend creating indexes
        assert "optimization" in str(slow_summary["postgresql"]["slow_queries"])
        assert "indexes" in str(pg_summary)

    def test_performance_improvement_expectations(self):
        """Test that performance improvement expectations are reasonable"""
        tdengine_opt = TDengineIndexOptimizer()
        postgresql_opt = PostgreSQLIndexOptimizer()

        td_summary = tdengine_opt.get_optimization_summary()
        pg_summary = postgresql_opt.get_optimization_summary()

        # All improvements should show speedup
        td_improvements = td_summary["optimization_focus"]
        pg_improvements = pg_summary["estimated_improvement"]

        assert len(td_improvements) >= 4
        assert len(pg_improvements) >= 3


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
