# MyStocks Codebase Exploration Report
**Date**: November 11, 2025
**Focus**: Backup, Recovery, and Database Infrastructure

## Executive Summary

The MyStocks quantitative trading system has a **well-structured dual-database architecture** with existing recovery and monitoring capabilities. While formal backup/restore functionality is not yet fully implemented, the foundation is in place with:

1. **Failure Recovery Queue** - SQLite-based queue for handling database failures
2. **Dual Database Architecture** - TDengine (high-frequency) + PostgreSQL (historical)
3. **Comprehensive Monitoring** - Separate monitoring database tracking all operations
4. **Disaster Recovery Configuration** - YAML-based configuration for 16 core tables

---

## 1. Existing Backup/Recovery Code

### 1.1 Failure Recovery Queue System
**Location**: `/opt/claude/mystocks_spec/src/utils/failure_recovery_queue.py`

```python
class FailureRecoveryQueue:
    """故障恢复队列 - SQLite-based Outbox pattern"""
    - Path: /tmp/mystocks_recovery_queue.db
    - Tables: outbox_queue (id, classification, target_database, data_json, created_at, retry_count, status)
    - Methods:
        • enqueue() - Queue failed operations
        • get_pending_items() - Retrieve pending items for retry
        • mark_completed() / mark_failed() - Update queue status
```

**Purpose**: When target database is unavailable, data is persisted to local SQLite queue for automatic retry when database recovers.

**Current Implementation**:
- Automatically integrated into `MyStocksUnifiedManager`
- Supports 34 data classifications
- Handles batch failures gracefully
- Recovery is NOT yet automated (requires manual trigger)

### 1.2 Database Recovery Queue Storage
**Location**: `/opt/claude/mystocks_spec/data/recovery_queue.db`
- Binary SQLite database file (empty/initialized)
- Used at runtime for failure queue persistence
- Location: `/tmp/mystocks_recovery_queue.db` (configurable)

---

## 2. Database Architecture Overview

### 2.1 Dual Database Strategy

| Aspect | TDengine | PostgreSQL |
|--------|----------|-----------|
| **Purpose** | High-frequency time-series data | Historical analysis & derivatives |
| **Data Types** | Tick, minute bars, order book | Daily bars, technical indicators, backtests |
| **Compression** | 20:1 ratio | Standard ACID |
| **Target RTO** | 3 minutes | 3 minutes |
| **Write Speed** | Ultra-high frequency | Moderate |
| **Tables** | 5 supertables + n subtables | 11 standard tables |

### 2.2 Data Access Layer

**TDengine Access** (`/opt/claude/mystocks_spec/src/data_access/tdengine_access.py`)
- Methods: `insert_dataframe()`, `query_by_time_range()`, `aggregate_to_kline()`, `delete_by_time_range()`
- Features: STable management, batch insert (10K rows/batch), time-range queries, OHLC aggregation
- Connection: WebSocket via `taospy` (REST port 6041 or native 6030)

**PostgreSQL Access** (`/opt/claude/mystocks_spec/src/data_access/postgresql_access.py`)
- Methods: `insert_dataframe()`, `upsert_dataframe()`, `query()`, `execute_sql()`
- Features: TimescaleDB hypertables, execute_values optimization, ON CONFLICT handling
- Connection: psycopg2 connection pool (1-20 connections)

---

## 3. Configuration Files

### 3.1 Disaster Recovery Configuration
**Location**: `/opt/claude/mystocks_spec/config/disaster_recovery_config.yaml`

```yaml
disaster_recovery:
  backup_strategy: 'incremental'
  validation_schedule: 'daily'
  recovery_time_objective: '3min'

# 16 core tables defined:
# - 5 TDengine supertables (tick_data, minute_kline, order_book_depth, etc.)
# - 11 PostgreSQL standard tables (daily_kline, technical_indicators, etc.)
```

**Status**: Configuration exists but recovery procedures not yet implemented.

### 3.2 Main Table Configuration
**Location**: `/opt/claude/mystocks_spec/config/table_config.yaml`
- 38KB file with complete schema for 40+ tables
- Version: 2.0
- Includes: Database connections, column definitions, tags, classifications
- Supports: YAML-driven table creation and validation

### 3.3 Database Connection Configuration
**Location**: `/opt/claude/mystocks_spec/config/` (via .env variables)

Environment variables required:
```
# TDengine
TDENGINE_HOST, TDENGINE_PORT, TDENGINE_REST_PORT
TDENGINE_USER, TDENGINE_PASSWORD, TDENGINE_DATABASE

# PostgreSQL
POSTGRESQL_HOST, POSTGRESQL_PORT
POSTGRESQL_USER, POSTGRESQL_PASSWORD, POSTGRESQL_DATABASE

# Monitoring
MONITOR_DB_URL
```

---

## 4. Connection Management Infrastructure

### 4.1 Connection Manager
**Location**: `/opt/claude/mystocks_spec/src/storage/database/connection_manager.py`

Features:
- Manages connections to 4 databases (TDengine, PostgreSQL, MySQL, Redis)
- Environment variable validation
- Connection pooling (PostgreSQL: 1-20 connections)
- WebSocket support for TDengine
- Error handling with detailed diagnostics

**Key Methods**:
- `get_tdengine_connection()` - WebSocket connection
- `get_postgresql_connection()` - Connection pool
- `get_mysql_connection()` - Direct connection (deprecated after Week 3)
- `get_redis_connection()` - Redis client (removed from main flow)

### 4.2 Compatibility Layer
**Location**: `/opt/claude/mystocks_spec/src/db_manager/`
- Re-exports all classes from `src.storage.database`
- Maintains backward compatibility with old import paths
- Enables gradual migration to new structure

---

## 5. Monitoring & Health Check Infrastructure

### 5.1 Monitoring Database System
**Location**: `/opt/claude/mystocks_spec/src/monitoring/`

**Components**:
1. **MonitoringDatabase** - Separate PostgreSQL database for operation tracking
2. **PerformanceMonitor** - Query performance tracking, slow query alerts
3. **DataQualityMonitor** - Data completeness, freshness, accuracy checks
4. **AlertManager** - Multi-channel alerting (email, webhook, log)

**Data Tracked**:
- Operation metrics: duration, status, error_message, data_count
- Alert events: level (info/warning/error/critical), timestamp, resolution
- Performance insights: query patterns, slow operations, bottlenecks

### 5.2 Monitoring Configuration
**File**: `/opt/claude/mystocks_spec/src/monitoring/init_monitoring_db.sql`
- DDL for monitoring database schema
- Tracks all operations independently of business databases

---

## 6. Unified Data Manager with Recovery

### 6.1 MyStocksUnifiedManager
**Location**: `/opt/claude/mystocks_spec/src/core/unified_manager.py`
**Location**: `/opt/claude/mystocks_spec/unified_manager.py` (entry point)

**Capabilities**:
- Automatic routing based on DataClassification (34 categories)
- Transparent failure handling via recovery queue
- Batch operation support (up to 100K rows)
- Monitoring integration (US3)
- Support for 5 data types:
  - High-frequency market data (TDengine)
  - Daily market data (PostgreSQL)
  - Reference data (PostgreSQL)
  - Derived data (PostgreSQL)
  - Transaction data (PostgreSQL)

**Recovery Flow**:
```
save_data_by_classification()
  ↓
Determine target database
  ↓
Attempt save operation
  ↓
[Success] → Log to monitoring DB
  ↓
[Failure] → Enqueue to recovery_queue.db
```

---

## 7. Directory Structure for Database Operations

### 7.1 Scripts Organization

**Database Scripts** (`/opt/claude/mystocks_spec/scripts/database/`)
- `check_tdengine_tables.py` - Validate TDengine table structures
- `verify_tdengine_deployment.py` - Health check deployment
- `create_realtime_quotes_table.py` - Setup realtime data tables
- `test_tdengine_simple.py` - Basic connectivity tests

**Runtime Scripts** (`/opt/claude/mystocks_spec/scripts/runtime/`)
- `system_demo.py` - Complete system demonstration
- `run_realtime_market_saver.py` - Realtime data collection
- `save_realtime_data.py` - Data persistence

**Test Scripts** (`/opt/claude/mystocks_spec/scripts/tests/`)
- `test_config_driven_table_manager.py` - Table creation testing
- `test_dual_database_architecture.py` - Database integration tests
- `test_financial_adapter.py` - Data adapter testing

### 7.2 Configuration Directory Structure
```
/opt/claude/mystocks_spec/config/
├── table_config.yaml                    # Main table schema (40+ tables)
├── table_config.yaml.backup_20251108   # Timestamped backup
├── disaster_recovery_config.yaml        # DR procedures (16 tables)
├── docker-compose.tdengine.yml         # TDengine Docker setup
├── automation_config.yaml               # Automation settings
├── strategy_config.yaml                 # Trading strategy config
├── logging_config.py                    # Logging configuration
└── calendars/                           # Trading calendars
```

### 7.3 Data Directory Structure
```
/opt/claude/mystocks_spec/data/
├── recovery_queue.db                    # Failure queue (SQLite)
├── cache/                               # Cache directory
├── models/                              # Trained models
└── {backups}/                          # Placeholder for backup directory
```

---

## 8. Missing / Not Yet Implemented

### 8.1 What's NOT Yet Implemented
1. **Automated Backup Procedures**
   - No scheduled full/incremental backups
   - No backup verification/validation scripts
   - No backup encryption
   - No backup compression/archival

2. **Restore Procedures**
   - No point-in-time recovery (PITR)
   - No table-level restore scripts
   - No data versioning/rollback capability
   - No restore verification

3. **Backup Infrastructure**
   - No backup storage location configured
   - No retention policies defined
   - No backup encryption keys
   - No offsite backup mechanisms

4. **Recovery Automation**
   - Recovery queue exists but retry is manual
   - No automatic failover to replica
   - No automatic recovery procedure execution
   - No recovery time objective automation

5. **Disaster Recovery Testing**
   - No DR drill procedures
   - No recovery scenario testing
   - No RTO/RPO validation
   - No DR documentation/runbooks

---

## 9. What IS Implemented & Ready to Use

### 9.1 Core Infrastructure
✅ Dual-database architecture (TDengine + PostgreSQL)
✅ Connection pooling and management
✅ YAML-driven configuration system
✅ Failure recovery queue (SQLite-based)
✅ Comprehensive monitoring database
✅ Performance tracking and alerts
✅ Data quality monitoring

### 9.2 Data Access Patterns
✅ Time-range queries
✅ Batch insert operations
✅ Aggregation operations (OHLC)
✅ Upsert operations (ON CONFLICT)
✅ Custom SQL execution
✅ Table statistics/metadata

### 9.3 Monitoring Capabilities
✅ All operations logged to monitoring DB
✅ Performance metrics collected
✅ Slow query detection
✅ Data quality metrics
✅ Multi-channel alerting framework

---

## 10. Key File Inventory

| File Path | Purpose | Type | Size |
|-----------|---------|------|------|
| `src/utils/failure_recovery_queue.py` | Outbox pattern implementation | Source | Python |
| `src/data_access/tdengine_access.py` | TDengine data access layer | Source | Python |
| `src/data_access/postgresql_access.py` | PostgreSQL data access layer | Source | Python |
| `src/monitoring/monitoring_service.py` | Monitoring orchestration | Source | Python |
| `src/core/unified_manager.py` | Core data manager | Source | Python |
| `config/disaster_recovery_config.yaml` | DR configuration | Config | YAML |
| `config/table_config.yaml` | Complete table schemas | Config | YAML (38KB) |
| `scripts/database/verify_tdengine_deployment.py` | Health checks | Script | Python |
| `data/recovery_queue.db` | Runtime recovery queue | Database | SQLite |
| `src/storage/database/connection_manager.py` | Connection pooling | Source | Python |

---

## 11. Architecture Insights

### 11.1 Design Patterns
- **Factory Pattern**: Data access factory for TDengine/PostgreSQL
- **Outbox Pattern**: Failure recovery queue for guaranteed delivery
- **Strategy Pattern**: DataStorageStrategy for classification-based routing
- **Adapter Pattern**: Multiple data source adapters (Akshare, Baostock, Tushare, etc.)

### 11.2 Resilience Features
- Automatic routing to optimal database
- Graceful degradation when database unavailable
- Data persistence in local SQLite queue
- Monitoring independent of business databases
- Health check capabilities

### 11.3 Data Flow Architecture
```
External Data Source
    ↓
Data Adapter (AkshareAdapter, BaostockAdapter, etc.)
    ↓
MyStocksUnifiedManager.save_data_by_classification()
    ↓
DataStorageStrategy.determine_target_database()
    ↓
[TDengine] or [PostgreSQL]
    ↓
[Success] → Monitoring DB (operation logged)
    ↓
[Failure] → Recovery Queue (local SQLite)
```

---

## 12. Recommendations

### 12.1 For Implementing Full Backup/Restore
1. Create backup scripts using TDengine export + PostgreSQL pg_dump
2. Implement incremental backup tracking via monitoring DB
3. Create restore procedures with integrity verification
4. Automate recovery queue retry mechanism
5. Implement point-in-time recovery (PITR) capability

### 12.2 For Improving Disaster Recovery
1. Create automated recovery runbooks
2. Implement RTO/RPO monitoring
3. Test DR procedures regularly
4. Document recovery scenarios
5. Implement failover automation

### 12.3 For Production Readiness
1. Configure backup retention policies
2. Implement backup encryption
3. Establish offsite backup storage
4. Automate backup verification
5. Create comprehensive DR documentation

---

## Conclusion

The MyStocks system has a **solid foundation** for backup and recovery with:
- Failure recovery queue for resilience
- Comprehensive monitoring infrastructure
- Well-structured database access layers
- Configuration-driven table management

**The main gap** is the lack of automated backup/restore procedures and recovery automation. The infrastructure supports this well - what remains is implementation of:
1. Backup creation and scheduling
2. Backup verification and archival
3. Restore procedures
4. Automated recovery queue processing

---

**Report Generated**: November 11, 2025
**Scope**: src/, scripts/, config/, web/backend/app directories
**Status**: Exploration Complete - Ready for Implementation Planning
