# MyStocks Database Architecture Overview

## Executive Summary

MyStocks implements a **dual-database architecture** optimized for quantitative trading data management:
- **TDengine**: High-frequency time-series data (tick, minute-level K-lines)
- **PostgreSQL + TimescaleDB**: Historical analysis data, reference data, and transaction records

The system uses a classification-driven routing strategy to automatically select the optimal database for each data type, with comprehensive monitoring and performance tracking.

---

## Database Architecture Overview

### 1. Dual-Database Strategy

#### **TDengine (High-Frequency Time-Series Data)**

**Purpose**: Store high-frequency market data with extreme compression and ultra-fast writes

**Key Characteristics**:
- Native time-series database optimized for IoT and financial data
- Compression ratio: ~20:1 (extremely space-efficient)
- Ultra-high write performance (millions of events per second)
- Automatic data retention policies
- Tag-based data organization (time-series optimized)

**Data Classes Stored**:
- `tick_data`: Stock tick-level execution data (price, volume, bid/ask)
- `minute_kline`: Minute-level OHLCV data 
- `depth_data`: Order book depth snapshots

**Database Configuration**:
```yaml
database: market_data
tables:
  - tick_data (SuperTable with symbol/exchange tags)
  - minute_kline (SuperTable with symbol/frequency tags)
  - depth_data (SuperTable with symbol/exchange tags)
```

**Sample Queries**:
```sql
-- Aggregate tick data to 5-minute K-lines
SELECT
    _wstart as ts,
    FIRST(price) as open,
    MAX(price) as high,
    MIN(price) as low,
    LAST(price) as close,
    SUM(volume) as volume
FROM tick_data
WHERE ts >= '2025-01-01 09:30:00'
  AND ts < '2025-01-01 15:00:00'
INTERVAL(5m)

-- Query latest tick data for a symbol
SELECT * FROM tick_data_600000
ORDER BY ts DESC LIMIT 100
```

---

#### **PostgreSQL + TimescaleDB (Historical & Analysis Data)**

**Purpose**: Store historical market data, reference data, derived indicators, and transaction records with ACID compliance

**Key Characteristics**:
- Full ACID compliance for all transactional data
- TimescaleDB extension for hypertables (time-series optimization)
- Complex JOINs with reference tables
- Full-text search and advanced indexing
- Automatic partitioning by time (via TimescaleDB)

**Data Classes Stored**:

1. **Market Data (Historical)**
   - `daily_kline`: Daily OHLCV data with adjustment factors
   - Indexes: symbol+date (unique), date, symbol

2. **Reference Data**
   - `symbols`: Stock symbol information with sectors, industries, market types
   - `constituents`: Index constituent stocks with weightings
   - `trade_calendar`: Trading days and holidays

3. **Derived Data**
   - `technical_indicators`: MA, RSI, MACD, etc. (TimescaleDB hypertable)
   - `quantitative_factors`: Factor analysis results (quality, growth, value, momentum)
   - `model_outputs`: ML model predictions and confidence scores
   - `trading_signals`: Buy/sell signals with target prices

4. **Transaction Data**
   - `order_records`: Order placement history (TimescaleDB hypertable)
   - `transaction_records`: Execution history with fees
   - `position_records`: Position snapshots by date
   - `account_funds`: Daily account equity and cash balances

5. **Metadata**
   - `data_sources`: Data source status, API keys, rate limits
   - `task_schedules`: Scheduled task definitions
   - `strategy_parameters`: Strategy configuration versions
   - `system_config`: System configuration key-value pairs

**Database Configuration**:
```yaml
database: quant_research

# Market Data Tables
daily_kline:
  type: TimescaleDB Hypertable
  time_column: trade_date
  indexes: (symbol, trade_date), (trade_date), (symbol)
  partitioning: Automatic via TimescaleDB

# Reference Data (Standard Tables)
symbols:
  type: Standard Table
  indexes: (symbol), (exchange), (sector), (is_active)

# Derived Data (TimescaleDB Hypertables)
technical_indicators:
  type: TimescaleDB Hypertable
  time_column: calc_date
  indexes: (symbol, calc_date, indicator_name), (calc_date), (indicator_name)

# Transaction Data (TimescaleDB Hypertables)
order_records:
  type: TimescaleDB Hypertable
  time_column: order_time
  indexes: (account_id, order_time), (symbol, order_time), (strategy_id)
```

**Sample Queries**:
```sql
-- Get daily returns with technical indicators
SELECT
    dk.symbol,
    dk.trade_date,
    dk.close,
    dk.pct_chg,
    ti.indicator_name,
    ti.indicator_value
FROM daily_kline dk
LEFT JOIN technical_indicators ti 
    ON dk.symbol = ti.symbol 
    AND dk.trade_date = ti.calc_date
WHERE dk.symbol = '600000.SH'
  AND dk.trade_date >= '2025-01-01'
ORDER BY dk.trade_date DESC;

-- Get recent trading signals with model confidence
SELECT
    ts.signal_id,
    ts.symbol,
    ts.signal_type,
    ts.signal_strength,
    mo.output_value as predicted_return,
    mo.confidence
FROM trading_signals ts
LEFT JOIN model_outputs mo
    ON ts.symbol = mo.symbol
    AND DATE(ts.signal_time) = mo.calc_date
WHERE ts.signal_time >= NOW() - INTERVAL '7 days'
  AND ts.is_executed = FALSE
ORDER BY ts.signal_time DESC;

-- Account performance analysis
SELECT
    af.record_date,
    af.total_assets,
    af.cash_balance,
    af.market_value,
    af.total_pnl,
    (af.total_pnl / af.total_assets * 100)::numeric(5,2) as return_pct
FROM account_funds af
WHERE af.account_id = 'ACC_001'
  AND af.record_date >= '2025-01-01'
ORDER BY af.record_date DESC;
```

---

### 2. Data Classification System

The system defines 5 data classes with automatic routing:

| Classification | Storage | Use Case | Characteristics |
|---|---|---|---|
| **Tick Data** | TDengine | High-frequency trading | Real-time, massive writes, compression critical |
| **Minute K-Line** | TDengine | Intraday analysis | Time-series, aggregation queries, sub-second latency |
| **Daily K-Line** | PostgreSQL | Historical analysis | Time-series, JOIN-heavy, long history |
| **Reference Data** | PostgreSQL | Static lookups | Rarely updated, multiple indexes, text search |
| **Derived Data** | PostgreSQL | Analytical results | Computed values, various periods, archive-friendly |
| **Transaction Data** | PostgreSQL | Account audit | ACID critical, JOIN heavy, compliance audit |
| **Meta Data** | PostgreSQL | Configuration | System state, versioning, audit trail |

---

### 3. Connection Management

**DatabaseConnectionManager** (`src/storage/database/connection_manager.py`):
- Manages connections for TDengine, PostgreSQL, MySQL, and Redis
- Connection validation from environment variables
- Error handling and connection pooling
- Lazy initialization

**Key Configuration** (from `.env`):
```
# TDengine (High-Frequency Data)
TDENGINE_HOST=
TDENGINE_PORT=6041
TDENGINE_USER=
TDENGINE_PASSWORD=
TDENGINE_DATABASE=market_data
TDENGINE_REST_PORT=6041

# PostgreSQL (Historical & Analysis Data)
POSTGRESQL_HOST=
POSTGRESQL_PORT=5432
POSTGRESQL_USER=
POSTGRESQL_PASSWORD=
POSTGRESQL_DATABASE=quant_research

# MySQL (Metadata) - Optional
MYSQL_HOST=
MYSQL_PORT=3306
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DATABASE=quant_research

# Monitoring
MONITOR_DB_URL=postgresql://...
```

---

## Query Pattern Analysis

### High-Frequency Data Queries (TDengine)

**1. Time-Range Queries**
```python
def query_by_time_range(
    table_name: str,
    start_time: datetime,
    end_time: datetime,
    columns: Optional[List[str]] = None,
    limit: Optional[int] = None
) -> pd.DataFrame:
    """Query tick data within time range"""
    # Optimized for time-based range queries
    # Returns millions of rows efficiently
```

**2. K-Line Aggregation**
```python
def aggregate_to_kline(
    table_name: str,
    start_time: datetime,
    end_time: datetime,
    interval: str = "1m",  # "1m", "5m", "15m", "1h"
    price_col: str = "price",
    volume_col: str = "volume"
) -> pd.DataFrame:
    """Aggregate tick data to OHLC K-lines"""
    # Uses TDengine INTERVAL() for fast aggregation
```

**3. Latest Data Queries**
```python
def query_latest(table_name: str, limit: int = 100) -> pd.DataFrame:
    """Get latest N records"""
    # ORDER BY ts DESC LIMIT N
    # Used for real-time monitoring
```

### Historical Data Queries (PostgreSQL)

**1. Time-Series Range Queries**
```python
def query_by_time_range(
    table_name: str,
    time_column: str,
    start_time: datetime,
    end_time: datetime,
    columns: Optional[List[str]] = None,
    filters: Optional[str] = None
) -> pd.DataFrame:
    """Query historical data with complex filters"""
    # Supports TimescaleDB hypertable optimization
```

**2. Complex Joins with Reference Data**
```sql
SELECT
    dk.symbol, dk.trade_date, dk.close,
    s.sector, s.industry,
    ti.indicator_value
FROM daily_kline dk
JOIN symbols s ON dk.symbol = s.symbol
JOIN technical_indicators ti 
    ON dk.symbol = ti.symbol 
    AND dk.trade_date = ti.calc_date
WHERE s.sector = 'Finance'
```

**3. Aggregate Queries**
```python
def get_table_stats(table_name: str) -> Dict[str, Any]:
    """Get row count and size statistics"""
    sql = """
    SELECT
        COUNT(*) as row_count,
        pg_size_pretty(pg_total_relation_size('table_name')) as total_size
    FROM table_name
    """
```

**4. Upsert Operations**
```python
def upsert_dataframe(
    table_name: str,
    df: pd.DataFrame,
    conflict_columns: List[str],
    update_columns: Optional[List[str]] = None
) -> int:
    """INSERT ... ON CONFLICT UPDATE"""
    # Used for updating daily data that may have corrections
```

---

## Database Infrastructure (src/storage/database/)

### DatabaseTableManager
**File**: `database_manager.py`

Core responsibilities:
- DDL operations: CREATE TABLE, ALTER TABLE, DROP TABLE
- Batch table creation from YAML configuration
- Table structure validation
- Multi-database support (TDengine, PostgreSQL, MySQL, Redis)

**Key Methods**:
```python
# Connection Management
def get_connection(db_type: DatabaseType, db_name: str, **kwargs)
def close_all_connections()

# DDL Operations
def create_table(db_type, db_name, table_name, columns)
def alter_table(db_type, db_name, table_name, alterations)
def drop_table(db_type, db_name, table_name)

# Batch Operations
def batch_create_tables(config_file: str)  # From table_config.yaml

# Validation
def validate_table_structure(db_type, db_name, table_name, expected_columns)
def get_table_info(db_type, db_name, table_name)

# Logging
def _log_operation(table_name, db_type, db_name, operation_type, ...)
```

### Data Access Layer

#### TDengineDataAccess (`tdengine_access.py`)

High-frequency time-series data operations:

```python
class TDengineDataAccess:
    # SuperTable Management
    def create_stable(stable_name, schema, tags)
    def create_table(table_name, stable_name, tag_values)
    
    # Data Operations
    def insert_dataframe(table_name, df, timestamp_col)
    def query_by_time_range(table_name, start_time, end_time, ...)
    def query_latest(table_name, limit)
    def aggregate_to_kline(table_name, start_time, end_time, interval)
    
    # Management
    def delete_by_time_range(table_name, start_time, end_time)
    def get_table_info(table_name)
```

**Performance Characteristics**:
- Batch inserts: 10,000 rows per batch
- Time-range queries: O(log N) via timestamp indexing
- K-line aggregation: Fast via INTERVAL() operator
- Compression: ~20:1 ratio saves storage

#### PostgreSQLDataAccess (`postgresql_access.py`)

Historical and analytical data operations:

```python
class PostgreSQLDataAccess:
    # Table Management
    def create_table(table_name, schema, primary_key)
    def create_hypertable(table_name, time_column, chunk_interval)
    
    # Data Operations
    def insert_dataframe(table_name, df)
    def upsert_dataframe(table_name, df, conflict_columns, update_columns)
    def query(table_name, columns, where, order_by, limit)
    def query_by_time_range(table_name, time_column, start_time, end_time, ...)
    
    # Advanced Queries
    def execute_sql(sql, params)  # Custom SQL with parameters
    def get_table_stats(table_name)
    
    # Data Management
    def delete(table_name, where)
    def close_all()
```

**Performance Characteristics**:
- Batch inserts using `execute_values()`: 50,000+ rows per batch
- TimescaleDB hypertable automatic partitioning
- Index-accelerated queries on (symbol, date) pairs
- Connection pooling: 1-20 connections per pool

---

## Monitoring & Performance Tracking

### MonitoringDatabase (`src/monitoring/monitoring_database.py`)

Centralized monitoring database tracks:

```python
class MonitoringDatabase:
    def log_operation(
        operation_type,  # SAVE/LOAD/DELETE/UPDATE
        classification,  # Data class
        target_database,  # TDengine/PostgreSQL/MySQL
        table_name,
        record_count,
        operation_status,  # SUCCESS/FAILED/PARTIAL
        error_message,
        execution_time_ms,
        user_agent,
        client_ip,
        additional_info
    )
    
    def log_query_performance(
        operation_id,
        query_sql,
        execution_time_ms,
        rows_affected,
        status
    )
    
    def log_data_quality(
        table_name,
        classification,
        completeness_score,
        freshness_hours,
        accuracy_checks
    )
```

**Monitoring Tables** (in PostgreSQL monitoring database):
- `operation_logs`: All data operations with timing and status
- `query_performance_logs`: Query execution metrics
- `data_quality_logs`: Data completeness and freshness checks
- `alert_logs`: Alert events with severity levels

### PerformanceMonitor (`src/monitoring/performance_monitor.py`)

Real-time performance tracking:

```python
class PerformanceMonitor:
    SLOW_QUERY_THRESHOLD_MS = 5000  # 5 seconds
    WARNING_THRESHOLD_MS = 2000      # 2 seconds
    
    @contextmanager
    def track_operation(
        operation_name,
        classification,
        database_type,
        table_name,
        query_sql,
        auto_alert=True
    ):
        """Context manager for automatic operation timing"""
        # Tracks execution time
        # Auto-alerts on slow queries
        # Logs to monitoring database
```

### DataQualityMonitor (`src/monitoring/data_quality_monitor.py`)

Data quality and completeness checks:

```python
class DataQualityMonitor:
    # Completeness Checks
    def check_completeness(
        table_name,
        classification,
        threshold=0.95
    )
    
    # Freshness Checks
    def check_freshness(
        table_name,
        classification,
        max_age_hours=24
    )
    
    # Accuracy Checks
    def check_accuracy(
        table_name,
        classification,
        validation_rules
    )
```

---

## Current Query Performance Baselines

Based on typical configurations:

### TDengine Performance
| Operation | Time | Notes |
|---|---|---|
| Insert 10K rows | ~50-100ms | Batch insert |
| Time-range query (1 day) | ~200-500ms | Millions of rows |
| K-line aggregation (1 month) | ~500-1000ms | INTERVAL() operator |
| Latest 100 records | ~10-50ms | ORDER BY ts DESC LIMIT |

### PostgreSQL Performance
| Operation | Time | Notes |
|---|---|---|
| Insert 10K rows | ~100-200ms | execute_values() |
| Upsert 10K rows | ~200-400ms | ON CONFLICT |
| JOIN with reference data | ~50-200ms | Depends on result size |
| Aggregate query (1 year) | ~100-500ms | With proper indexes |
| Complex analysis query | ~200-1000ms | Multiple JOINs |

---

## Environment Variables Required

```bash
# TDengine Configuration
TDENGINE_HOST=localhost
TDENGINE_PORT=6041
TDENGINE_REST_PORT=6041
TDENGINE_USER=root
TDENGINE_PASSWORD=taosdata
TDENGINE_DATABASE=market_data

# PostgreSQL Configuration
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=password
POSTGRESQL_DATABASE=quant_research

# MySQL Configuration (Optional)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=quant_research

# Redis Configuration (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=1

# Monitoring
MONITOR_DB_URL=postgresql://user:password@localhost:5432/monitoring
```

---

## Configuration Files

### table_config.yaml
**Location**: `/opt/claude/mystocks_spec/config/table_config.yaml`

Defines complete table schemas for both databases:
- 30+ tables organized by data classification
- Column definitions with data types, precision, defaults
- Index definitions for query optimization
- TimescaleDB hypertable configuration
- TDengine SuperTable definitions

---

## Summary

The MyStocks database architecture achieves:

1. **Performance**: Ultra-high writes for tick data, sub-second latency for queries
2. **Scalability**: Handles millions of events/day across multiple symbols
3. **Reliability**: ACID guarantees for transaction data via PostgreSQL
4. **Monitoring**: Comprehensive performance tracking and data quality checks
5. **Maintainability**: Configuration-driven table management, automatic schema validation
6. **Flexibility**: Dual-database strategy allows right tool for right workload

The system is production-ready for quantitative trading with proper monitoring, alerting, and automated maintenance.
