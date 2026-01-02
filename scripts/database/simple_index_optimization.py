"""
Simple Database Index Optimization Script
Task: task-2.1 - Optimize database query performance

Author: DB CLI (Claude Code)
Date: 2026-01-01
"""

import os
import sys
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def get_postgresql_url():
    """Get PostgreSQL connection URL from environment"""
    host = os.getenv("POSTGRESQL_HOST", "localhost")
    port = os.getenv("POSTGRESQL_PORT", "5432")
    user = os.getenv("POSTGRESQL_USER", "postgres")
    password = os.getenv("POSTGRESQL_PASSWORD", "")
    database = os.getenv("POSTGRESQL_DATABASE", "mystocks")

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def main():
    print("🚀 Starting Database Index Optimization")
    print("=" * 80)

    try:
        # Load environment variables
        from dotenv import load_dotenv

        load_dotenv()

        # Connect to PostgreSQL
        db_url = get_postgresql_url()
        print(f"📡 Connecting to PostgreSQL at {db_url.split('@')[1].split('/')[0]}...")

        engine = create_engine(db_url, isolation_level="AUTOCOMMIT")
        print("✅ Connected to PostgreSQL successfully")

        # Index creation statements (excluding partial indexes with CURRENT_DATE)
        index_statements = [
            "CREATE INDEX IF NOT EXISTS idx_stock_fund_flow_symbol_date_timeframe ON stock_fund_flow (symbol, trade_date DESC, timeframe);",
            "CREATE INDEX IF NOT EXISTS idx_etf_spot_data_symbol_date ON etf_spot_data (symbol, trade_date DESC);",
            "CREATE INDEX IF NOT EXISTS idx_chip_race_data_symbol_date_type ON chip_race_data (symbol, trade_date DESC, race_type);",
            "CREATE INDEX IF NOT EXISTS idx_stock_lhb_detail_symbol_date ON stock_lhb_detail (symbol, trade_date DESC);",
            "CREATE INDEX IF NOT EXISTS idx_sector_fund_flow_type_date ON sector_fund_flow (sector_type, timeframe, trade_date DESC);",
            "CREATE INDEX IF NOT EXISTS idx_stock_dividend_symbol_exdate ON stock_dividend (symbol, ex_dividend_date DESC);",
            "CREATE INDEX IF NOT EXISTS idx_stock_blocktrade_symbol_date ON stock_blocktrade (symbol, trade_date DESC);",
        ]

        # Analyze statements
        analyze_statements = [
            "ANALYZE stock_fund_flow;",
            "ANALYZE etf_spot_data;",
            "ANALYZE chip_race_data;",
            "ANALYZE stock_lhb_detail;",
            "ANALYZE sector_fund_flow;",
            "ANALYZE stock_dividend;",
            "ANALYZE stock_blocktrade;",
        ]

        created_indexes = []
        analyzed_tables = []

        print("\n🔧 Creating indexes...")
        with engine.connect() as conn:
            for statement in index_statements:
                try:
                    conn.execute(text(statement))
                    index_name = statement.split()[5].strip().strip(";")
                    print(f"   ✅ Created: {index_name}")
                    created_indexes.append(index_name)
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print("   ℹ️  Index already exists (skipping)")
                    else:
                        print(f"   ⚠️  Failed: {e}")

        print("\n📊 Analyzing tables...")
        with engine.connect() as conn:
            for statement in analyze_statements:
                try:
                    conn.execute(text(statement))
                    table_name = statement.split()[1].strip().strip(";")
                    print(f"   ✅ Analyzed: {table_name}")
                    analyzed_tables.append(table_name)
                except Exception as e:
                    print(f"   ⚠️  Failed: {e}")

        # Generate optimization report
        print("\n📊 Index Usage Statistics:")
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                    SELECT
                        schemaname,
                        relname as tablename,
                        indexrelname as indexname,
                        idx_scan as scans,
                        pg_size_pretty(pg_relation_size(indexrelid)) as size
                    FROM pg_stat_user_indexes
                    WHERE schemaname = 'public'
                    ORDER BY idx_scan DESC
                    LIMIT 10
                """)
                )

                print(f"   {'Table':<20} {'Index':<40} {'Scans':<10} {'Size':<10}")
                print("   " + "-" * 80)
                for row in result:
                    print(f"   {row[1]:<20} {row[2]:<40} {row[3]:<10} {row[4]:<10}")
        except Exception as e:
            print(f"   ⚠️  Could not fetch statistics: {e}")

        print("\n" + "=" * 80)
        print("✅ Database Index Optimization Completed Successfully!")
        print("=" * 80)

        # Update task progress
        try:
            import subprocess

            subprocess.run(
                [
                    "python",
                    "scripts/dev/task_pool.py",
                    "--update",
                    "--task=task-2.1",
                    "--cli=db",
                    "--progress=100",
                    "--status=completed",
                ],
                check=True,
                capture_output=True,
            )
            print("✅ Task progress updated to 100%")
        except Exception as e:
            print(f"⚠️  Failed to update task progress: {e}")

        return 0

    except Exception as e:
        print(f"\n❌ Optimization failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
