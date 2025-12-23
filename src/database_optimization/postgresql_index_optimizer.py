"""
PostgreSQL 索引优化器

优化PostgreSQL的单列索引、复合索引、部分索引和BRIN索引
"""

import logging
import os
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)


class PostgreSQLIndexOptimizer:
    """PostgreSQL索引优化管理器"""

    def __init__(self):
        """初始化PostgreSQL索引优化器"""
        self.host = os.getenv("POSTGRESQL_HOST", "localhost")
        self.port = int(os.getenv("POSTGRESQL_PORT", "5432"))
        self.user = os.getenv("POSTGRESQL_USER", "postgres")
        self.password = os.getenv("POSTGRESQL_PASSWORD")
        if not self.password:
            raise ValueError("POSTGRESQL_PASSWORD environment variable is required")
        self.database = os.getenv("POSTGRESQL_DATABASE", "mystocks")

        self.optimization_stats = {
            "indexes_created": 0,
            "indexes_analyzed": 0,
            "estimated_size_reduction": "0MB",
            "query_time_improvements": [],
        }

    def design_single_column_indexes(self) -> Dict:
        """
        设计单列索引

        Returns:
            {
                "indexes": [
                    {"column": "...", "table": "...", "reason": "...", "type": "BTREE/HASH"}
                ],
                "implementation": "..."
            }
        """
        logger.info("Designing single-column indexes for PostgreSQL...")

        indexes = [
            {
                "table": "daily_kline",
                "column": "symbol",
                "reason": "Frequent filtering by stock symbol",
                "type": "BTREE",
                "selectivity": "High (3000+ unique values)",
                "sql": "CREATE INDEX idx_daily_kline_symbol ON daily_kline(symbol);",
                "estimated_improvement": "10-20x faster symbol lookups",
            },
            {
                "table": "daily_kline",
                "column": "trade_date",
                "reason": "Frequent filtering by date range",
                "type": "BTREE",
                "selectivity": "Medium (250+ unique dates)",
                "sql": "CREATE INDEX idx_daily_kline_date ON daily_kline(trade_date);",
                "estimated_improvement": "15-30x faster date range queries",
            },
            {
                "table": "technical_indicators",
                "column": "symbol",
                "reason": "Lookup by symbol before calculating indicators",
                "type": "BTREE",
                "selectivity": "High",
                "sql": "CREATE INDEX idx_tech_indicators_symbol ON technical_indicators(symbol);",
                "estimated_improvement": "5-15x faster indicator lookups",
            },
            {
                "table": "technical_indicators",
                "column": "created_at",
                "reason": "Filter recent indicators for real-time analysis",
                "type": "BRIN",
                "selectivity": "High (sorted by time)",
                "sql": "CREATE INDEX idx_tech_indicators_created ON technical_indicators USING BRIN(created_at);",
                "estimated_improvement": "2-5x faster with minimal storage overhead",
            },
            {
                "table": "order_records",
                "column": "user_id",
                "reason": "Lookup orders by user",
                "type": "BTREE",
                "selectivity": "Medium-High",
                "sql": "CREATE INDEX idx_order_records_user ON order_records(user_id);",
                "estimated_improvement": "8-20x faster user order lookups",
            },
            {
                "table": "order_records",
                "column": "symbol",
                "reason": "Filter orders by trading symbol",
                "type": "BTREE",
                "selectivity": "High",
                "sql": "CREATE INDEX idx_order_records_symbol ON order_records(symbol);",
                "estimated_improvement": "5-15x faster symbol-based filtering",
            },
            {
                "table": "transaction_records",
                "column": "user_id",
                "reason": "Lookup user transactions for portfolio",
                "type": "BTREE",
                "selectivity": "Medium-High",
                "sql": "CREATE INDEX idx_transaction_records_user ON transaction_records(user_id);",
                "estimated_improvement": "10-25x faster transaction lookups",
            },
        ]

        return {
            "indexes": indexes,
            "total_indexes": len(indexes),
            "estimated_total_size": "50-100MB (indexes)",
            "estimated_table_size": "2-5GB (tables)",
            "index_to_data_ratio": "2-5%",
        }

    def design_composite_indexes(self) -> Dict:
        """
        设计复合索引

        Returns:
            {
                "composite_indexes": [
                    {"columns": [...], "reason": "...", "selectivity": "..."}
                ]
            }
        """
        logger.info("Designing composite indexes for PostgreSQL...")

        composite_indexes = [
            {
                "table": "daily_kline",
                "columns": ["symbol", "trade_date"],
                "column_order": "symbol ASC, trade_date DESC",
                "reason": "Most common query: find daily candle for specific stock on specific date",
                "selectivity": "Very High (symbol + date combination)",
                "sql": "CREATE INDEX idx_daily_kline_symbol_date ON daily_kline(symbol, trade_date DESC);",
                "estimated_improvement": "20-40x faster stock-date lookups",
                "use_case": "Retrieve day's OHLCV data for charting",
            },
            {
                "table": "technical_indicators",
                "columns": ["symbol", "created_at"],
                "column_order": "symbol ASC, created_at DESC",
                "reason": "Retrieve latest indicators for symbol",
                "selectivity": "Very High",
                "sql": "CREATE INDEX idx_tech_indicators_symbol_created ON technical_indicators(symbol, created_at DESC);",
                "estimated_improvement": "15-35x faster indicator lookups",
                "use_case": "Get latest MA/MACD/RSI for real-time analysis",
            },
            {
                "table": "order_records",
                "columns": ["user_id", "symbol", "created_at"],
                "column_order": "user_id ASC, symbol ASC, created_at DESC",
                "reason": "Find user's orders for specific symbol, sorted by recency",
                "selectivity": "Very High",
                "sql": "CREATE INDEX idx_order_records_user_symbol_date ON order_records(user_id, symbol, created_at DESC);",
                "estimated_improvement": "25-50x faster order history lookups",
                "use_case": "Portfolio page showing order history by symbol",
            },
            {
                "table": "transaction_records",
                "columns": ["user_id", "created_at"],
                "column_order": "user_id ASC, created_at DESC",
                "reason": "Retrieve user's transaction history",
                "selectivity": "High",
                "sql": "CREATE INDEX idx_transaction_records_user_date ON transaction_records(user_id, created_at DESC);",
                "estimated_improvement": "15-30x faster transaction history",
                "use_case": "Trading history/account statement",
            },
        ]

        return {
            "composite_indexes": composite_indexes,
            "total_indexes": len(composite_indexes),
            "key_benefit": "Reduces disk I/O by avoiding table scans",
            "implementation_priority": "HIGH",
        }

    def design_partial_indexes(self) -> Dict:
        """
        设计部分索引（有条件的索引）

        Returns:
            {
                "partial_indexes": [...]
            }
        """
        logger.info("Designing partial indexes for PostgreSQL...")

        partial_indexes = [
            {
                "table": "order_records",
                "columns": ["user_id", "symbol"],
                "where_clause": "status = 'ACTIVE' OR status = 'PENDING'",
                "reason": "Only index active orders (most frequently queried)",
                "space_savings": "40-60% smaller than full index",
                "sql": "CREATE INDEX idx_order_records_active ON order_records(user_id, symbol) WHERE status IN ('ACTIVE', 'PENDING');",
                "estimated_improvement": "30-60% faster active order lookups",
                "use_case": "Real-time portfolio monitoring",
            },
            {
                "table": "daily_kline",
                "columns": ["symbol"],
                "where_clause": "trade_date >= CURRENT_DATE - INTERVAL '1 year'",
                "reason": "Index only recent 1-year data (most frequently queried)",
                "space_savings": "80% smaller than full index",
                "sql": "CREATE INDEX idx_daily_kline_recent ON daily_kline(symbol) WHERE trade_date >= CURRENT_DATE - INTERVAL '1 year';",
                "estimated_improvement": "40-70% faster recent data queries",
                "use_case": "Charting, technical analysis",
            },
            {
                "table": "technical_indicators",
                "columns": ["symbol"],
                "where_clause": "indicator_type IN ('MA', 'MACD', 'RSI')",
                "reason": "Index only popular technical indicators",
                "space_savings": "50-70% smaller",
                "sql": "CREATE INDEX idx_tech_indicators_popular ON technical_indicators(symbol) WHERE indicator_type IN ('MA', 'MACD', 'RSI');",
                "estimated_improvement": "25-50% faster popular indicator lookups",
                "use_case": "Real-time indicator calculation",
            },
        ]

        return {
            "partial_indexes": partial_indexes,
            "total_indexes": len(partial_indexes),
            "key_benefit": "Reduced index size + faster queries on filtered data",
            "implementation_priority": "HIGH",
        }

    def design_brin_indexes(self) -> Dict:
        """
        设计BRIN索引（块范围索引，适合大型有序表）

        Returns:
            {
                "brin_indexes": [...]
            }
        """
        logger.info("Designing BRIN indexes for PostgreSQL...")

        brin_indexes = [
            {
                "table": "daily_kline",
                "column": "trade_date",
                "reason": "TimescaleDB hypertable with time-ordered data",
                "selectivity": "Very high (data pre-sorted by date)",
                "sql": "CREATE INDEX idx_daily_kline_date_brin ON daily_kline USING BRIN(trade_date);",
                "index_size": "1-2MB (vs 50-100MB for BTREE)",
                "estimated_improvement": "80% smaller index + 2-5x faster range scans",
                "use_case": "Date range queries (e.g., last 30 days)",
            },
            {
                "table": "technical_indicators",
                "column": "created_at",
                "reason": "TimescaleDB hypertable with time-ordered data",
                "selectivity": "Very high",
                "sql": "CREATE INDEX idx_tech_indicators_created_brin ON technical_indicators USING BRIN(created_at);",
                "index_size": "0.5-1MB",
                "estimated_improvement": "90% smaller index + minimal maintenance overhead",
                "use_case": "Time-range indicator lookups",
            },
            {
                "table": "order_records",
                "column": "created_at",
                "reason": "Time-ordered trading orders",
                "selectivity": "Very high",
                "sql": "CREATE INDEX idx_order_records_created_brin ON order_records USING BRIN(created_at);",
                "index_size": "0.5-1MB",
                "estimated_improvement": "90% smaller + minimal INSERT/UPDATE overhead",
                "use_case": "Recent order lookups",
            },
            {
                "table": "transaction_records",
                "column": "created_at",
                "reason": "Time-ordered transactions",
                "selectivity": "Very high",
                "sql": "CREATE INDEX idx_transaction_records_created_brin ON transaction_records USING BRIN(created_at);",
                "index_size": "0.5-1MB",
                "estimated_improvement": "90% smaller + efficient for time-series data",
                "use_case": "Transaction history lookups",
            },
        ]

        return {
            "brin_indexes": brin_indexes,
            "total_indexes": len(brin_indexes),
            "total_index_size": "3-5MB (all BRIN indexes combined)",
            "key_benefit": "Minimal storage overhead for large time-series tables",
            "maintenance_cost": "Very low (only updated on page changes)",
            "implementation_priority": "HIGH",
        }

    def get_optimization_summary(self) -> Dict:
        """获取索引优化总结"""
        logger.info("Generating PostgreSQL optimization summary...")

        single_col = self.design_single_column_indexes()
        composite = self.design_composite_indexes()
        partial = self.design_partial_indexes()
        brin = self.design_brin_indexes()

        total_indexes = (
            single_col["total_indexes"]
            + composite["total_indexes"]
            + partial["total_indexes"]
            + brin["total_indexes"]
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "database": self.database,
            "total_indexes_to_create": total_indexes,
            "index_breakdown": {
                "single_column": single_col["total_indexes"],
                "composite": composite["total_indexes"],
                "partial": partial["total_indexes"],
                "brin": brin["total_indexes"],
            },
            "estimated_total_index_size": "60-110MB",
            "estimated_improvement": {
                "symbol_lookups": "10-40x faster",
                "date_range_queries": "15-40x faster",
                "composite_queries": "20-50x faster",
                "time_range_queries": "80-90% smaller index + fast scans",
            },
            "implementation_phases": [
                "Phase 1: Create single-column indexes (8 indexes)",
                "Phase 2: Create composite indexes (4 indexes)",
                "Phase 3: Create BRIN indexes (4 indexes)",
                "Phase 4: Create partial indexes (3 indexes)",
            ],
            "stats": self.optimization_stats,
            "implementation_status": "PENDING",
        }
