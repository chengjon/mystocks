"""
MyStocks Database Index Optimization Script
Task: task-2.1 - Optimize database query performance

Focus areas:
1. Time-series data query optimization
2. Composite indexes for common query patterns
3. Partial indexes for frequent filters
4. Index usage monitoring

Author: DB CLI (Claude Code)
Date: 2026-01-01
"""

import os
import sys
import logging
from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.engine import Engine
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.storage.database.database_manager import DatabaseTableManager

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class DatabaseIndexOptimizer:
    """Database Index Optimization Manager"""

    def __init__(self):
        self.db_manager = DatabaseTableManager()
        self.optimizer_log = []

    def log(self, message: str, level: str = "INFO"):
        """Log optimization actions"""
        timestamp = datetime.now().isoformat()
        log_entry = {"timestamp": timestamp, "level": level, "message": message}
        self.optimizer_log.append(log_entry)
        logger.info(f"[{level}] {message}")

    def get_postgresql_engine(self) -> Engine:
        """Get PostgreSQL engine"""
        return self.db_manager.get_postgresql_engine()

    def check_existing_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Check existing indexes for a table"""
        engine = self.get_postgresql_engine()
        indexes = []

        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                    SELECT
                        indexname,
                        indexdef
                    FROM pg_indexes
                    WHERE tablename = :table_name
                    AND schemaname = 'public'
                """),
                    {"table_name": table_name},
                )

                for row in result:
                    indexes.append({"name": row[0], "definition": row[1]})
        except Exception as e:
            self.log(f"Error checking indexes for {table_name}: {e}", "ERROR")

        return indexes

    def create_composite_indexes(self):
        """Create composite indexes for common query patterns"""
        engine = self.get_postgresql_engine()

        composite_indexes = [
            {
                "name": "idx_stock_fund_flow_symbol_date_timeframe",
                "table": "stock_fund_flow",
                "columns": ["symbol", "trade_date DESC", "timeframe"],
                "description": "Optimize fund flow queries by stock and date",
            },
            {
                "name": "idx_etf_spot_data_symbol_date",
                "table": "etf_spot_data",
                "columns": ["symbol", "trade_date DESC"],
                "description": "Optimize ETF data queries",
            },
            {
                "name": "idx_chip_race_data_symbol_date_type",
                "table": "chip_race_data",
                "columns": ["symbol", "trade_date DESC", "race_type"],
                "description": "Optimize chip race data queries",
            },
            {
                "name": "idx_stock_lhb_detail_symbol_date",
                "table": "stock_lhb_detail",
                "columns": ["symbol", "trade_date DESC"],
                "description": "Optimize dragon-tiger list queries",
            },
            {
                "name": "idx_sector_fund_flow_type_date",
                "table": "sector_fund_flow",
                "columns": ["sector_type", "timeframe", "trade_date DESC"],
                "description": "Optimize sector fund flow queries",
            },
            {
                "name": "idx_stock_dividend_symbol_exdate",
                "table": "stock_dividend",
                "columns": ["symbol", "ex_dividend_date DESC"],
                "description": "Optimize dividend queries",
            },
            {
                "name": "idx_stock_blocktrade_symbol_date",
                "table": "stock_blocktrade",
                "columns": ["symbol", "trade_date DESC"],
                "description": "Optimize block trade queries",
            },
        ]

        created_count = 0
        for idx_def in composite_indexes:
            try:
                existing_indexes = self.check_existing_indexes(idx_def["table"])
                existing_names = [idx["name"] for idx in existing_indexes]

                if idx_def["name"] in existing_names:
                    self.log(f"Index {idx_def['name']} already exists", "INFO")
                    continue

                columns_str = ", ".join(idx_def["columns"])
                sql = f"""
                    CREATE INDEX CONCURRENTLY {idx_def["name"]}
                    ON {idx_def["table"]} ({columns_str})
                """

                with engine.connect() as conn:
                    conn.execute(text(sql))
                    conn.commit()

                self.log(f"✅ Created composite index: {idx_def['name']} on {idx_def['table']}", "SUCCESS")
                self.log(f"   Description: {idx_def['description']}", "INFO")
                created_count += 1

            except Exception as e:
                self.log(f"❌ Failed to create index {idx_def['name']}: {e}", "ERROR")

        return created_count

    def create_partial_indexes(self):
        """Create partial indexes for frequent filter patterns"""
        engine = self.get_postgresql_engine()

        partial_indexes = [
            {
                "name": "idx_stock_fund_flow_recent",
                "table": "stock_fund_flow",
                "columns": ["symbol", "trade_date DESC"],
                "condition": "trade_date >= CURRENT_DATE - INTERVAL '30 days'",
                "description": "Index for recent fund flow data (30 days)",
            },
            {
                "name": "idx_etf_spot_data_today",
                "table": "etf_spot_data",
                "columns": ["symbol", "trade_date DESC"],
                "condition": "trade_date >= CURRENT_DATE",
                "description": "Index for today's ETF data",
            },
            {
                "name": "idx_stock_lhb_recent",
                "table": "stock_lhb_detail",
                "columns": ["trade_date DESC", "net_amount DESC"],
                "condition": "trade_date >= CURRENT_DATE - INTERVAL '7 days'",
                "description": "Index for recent dragon-tiger list data",
            },
            {
                "name": "idx_sector_fund_flow_today",
                "table": "sector_fund_flow",
                "columns": ["sector_type", "main_net_inflow DESC"],
                "condition": "trade_date = CURRENT_DATE",
                "description": "Index for today's sector fund flow",
            },
        ]

        created_count = 0
        for idx_def in partial_indexes:
            try:
                existing_indexes = self.check_existing_indexes(idx_def["table"])
                existing_names = [idx["name"] for idx in existing_indexes]

                if idx_def["name"] in existing_names:
                    self.log(f"Partial index {idx_def['name']} already exists", "INFO")
                    continue

                columns_str = ", ".join(idx_def["columns"])
                sql = f"""
                    CREATE INDEX CONCURRENTLY {idx_def["name"]}
                    ON {idx_def["table"]} ({columns_str})
                    WHERE {idx_def["condition"]}
                """

                with engine.connect() as conn:
                    conn.execute(text(sql))
                    conn.commit()

                self.log(f"✅ Created partial index: {idx_def['name']} on {idx_def['table']}", "SUCCESS")
                self.log(f"   Condition: {idx_def['condition']}", "INFO")
                self.log(f"   Description: {idx_def['description']}", "INFO")
                created_count += 1

            except Exception as e:
                self.log(f"❌ Failed to create partial index {idx_def['name']}: {e}", "ERROR")

        return created_count

    def analyze_tables(self):
        """Analyze tables to update statistics"""
        engine = self.get_postgresql_engine()

        tables = [
            "stock_fund_flow",
            "etf_spot_data",
            "chip_race_data",
            "stock_lhb_detail",
            "sector_fund_flow",
            "stock_dividend",
            "stock_blocktrade",
        ]

        analyzed_count = 0
        for table in tables:
            try:
                with engine.connect() as conn:
                    conn.execute(text(f"ANALYZE {table}"))
                    conn.commit()

                self.log(f"✅ Analyzed table: {table}", "SUCCESS")
                analyzed_count += 1

            except Exception as e:
                self.log(f"❌ Failed to analyze table {table}: {e}", "ERROR")

        return analyzed_count

    def check_index_usage(self):
        """Check index usage statistics"""
        engine = self.get_postgresql_engine()

        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                    SELECT
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan as index_scans,
                        idx_tup_read as tuples_read,
                        idx_tup_fetch as tuples_fetched,
                        pg_size_pretty(pg_relation_size(indexrelid)) as index_size
                    FROM pg_stat_user_indexes
                    WHERE schemaname = 'public'
                    ORDER BY idx_scan ASC
                """)
                )

                usage_stats = []
                for row in result:
                    usage_stats.append(
                        {
                            "schema": row[0],
                            "table": row[1],
                            "index": row[2],
                            "scans": row[3],
                            "tuples_read": row[4],
                            "tuples_fetched": row[5],
                            "size": row[6],
                        }
                    )

                self.log("📊 Index Usage Statistics", "INFO")
                self.log("=" * 80, "INFO")

                for stat in usage_stats[:10]:
                    self.log(f"  {stat['table']}.{stat['index']}: {stat['scans']} scans, size: {stat['size']}", "INFO")

                return usage_stats

        except Exception as e:
            self.log(f"Error checking index usage: {e}", "ERROR")
            return []

    def get_query_performance_baseline(self):
        """Get baseline query performance metrics"""
        engine = self.get_postgresql_engine()

        queries = [
            {
                "name": "Fund Flow Query",
                "sql": """
                    SELECT symbol, trade_date, main_net_inflow
                    FROM stock_fund_flow
                    WHERE symbol = '600000'
                    AND trade_date >= CURRENT_DATE - INTERVAL '7 days'
                    ORDER BY trade_date DESC
                    LIMIT 100
                """,
            },
            {
                "name": "ETF Data Query",
                "sql": """
                    SELECT symbol, latest_price, change_percent
                    FROM etf_spot_data
                    WHERE trade_date = CURRENT_DATE
                    ORDER BY change_percent DESC
                    LIMIT 50
                """,
            },
            {
                "name": "Dragon-Tiger List Query",
                "sql": """
                    SELECT symbol, trade_date, net_amount
                    FROM stock_lhb_detail
                    WHERE trade_date >= CURRENT_DATE - INTERVAL '7 days'
                    ORDER BY net_amount DESC
                    LIMIT 20
                """,
            },
        ]

        performance_results = []

        for query in queries:
            try:
                with engine.connect() as conn:
                    start_time = datetime.now()
                    result = conn.execute(text(query["sql"]))
                    end_time = datetime.now()

                    row_count = len(list(result))
                    execution_time = (end_time - start_time).total_seconds() * 1000

                    performance_results.append(
                        {"query": query["name"], "rows": row_count, "execution_time_ms": execution_time}
                    )

                    self.log(f"📈 {query['name']}: {execution_time:.2f}ms, {row_count} rows", "INFO")

            except Exception as e:
                self.log(f"Error executing {query['name']}: {e}", "ERROR")

        return performance_results

    def run_optimization(self):
        """Run complete index optimization"""
        self.log("🚀 Starting Database Index Optimization", "INFO")
        self.log("=" * 80, "INFO")

        # Step 1: Get baseline performance
        self.log("\n📊 Step 1: Measuring baseline performance...", "INFO")
        baseline = self.get_query_performance_baseline()

        # Step 2: Create composite indexes
        self.log("\n🔧 Step 2: Creating composite indexes...", "INFO")
        composite_count = self.create_composite_indexes()

        # Step 3: Create partial indexes
        self.log("\n🔧 Step 3: Creating partial indexes...", "INFO")
        partial_count = self.create_partial_indexes()

        # Step 4: Analyze tables
        self.log("\n📊 Step 4: Analyzing tables to update statistics...", "INFO")
        analyzed_count = self.analyze_tables()

        # Step 5: Check index usage
        self.log("\n📊 Step 5: Checking index usage statistics...", "INFO")
        usage_stats = self.check_index_usage()

        # Step 6: Measure post-optimization performance
        self.log("\n📊 Step 6: Measuring post-optimization performance...", "INFO")
        post_opt = self.get_query_performance_baseline()

        # Generate report
        self.log("\n" + "=" * 80, "INFO")
        self.log("✅ Database Index Optimization Complete!", "SUCCESS")
        self.log("=" * 80, "INFO")
        self.log("\n📊 Summary:", "INFO")
        self.log(f"  • Composite indexes created: {composite_count}", "INFO")
        self.log(f"  • Partial indexes created: {partial_count}", "INFO")
        self.log(f"  • Tables analyzed: {analyzed_count}", "INFO")
        self.log(f"  • Total optimization actions: {len(self.optimizer_log)}", "INFO")

        self.log("\n📈 Performance Comparison:", "INFO")
        if baseline and post_opt:
            for base, post in zip(baseline, post_opt):
                improvement = (
                    ((base["execution_time_ms"] - post["execution_time_ms"]) / base["execution_time_ms"] * 100)
                    if base["execution_time_ms"] > 0
                    else 0
                )
                self.log(
                    f"  • {base['query']}: {base['execution_time_ms']:.2f}ms → {post['execution_time_ms']:.2f}ms "
                    f"({improvement:+.1f}%)",
                    "INFO",
                )

        # Save optimization log
        log_file = "scripts/database/optimization_log.json"
        with open(log_file, "w") as f:
            json.dump(self.optimizer_log, f, indent=2)

        self.log(f"\n📝 Optimization log saved to: {log_file}", "INFO")

        return {
            "composite_indexes": composite_count,
            "partial_indexes": partial_count,
            "analyzed_tables": analyzed_count,
            "baseline_performance": baseline,
            "post_optimization_performance": post_opt,
            "log_file": log_file,
        }


def main():
    """Main execution function"""
    optimizer = DatabaseIndexOptimizer()

    try:
        results = optimizer.run_optimization()
        print("\n" + "=" * 80)
        print("Database Index Optimization Completed Successfully!")
        print("=" * 80)
        print(f"✅ Created {results['composite_indexes']} composite indexes")
        print(f"✅ Created {results['partial_indexes']} partial indexes")
        print(f"✅ Analyzed {results['analyzed_tables']} tables")
        print(f"📝 Log saved to: {results['log_file']}")

        return 0

    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
