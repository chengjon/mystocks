# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Note**: This file works in conjunction with the project constitution (`.specify/memory/constitution.md`) and the highest guidance document (`项目开发规范与指导文档.md`) to ensure consistent development practices.

## ⚡ Week 3 Update (2025-10-19): Database Simplification

**Major Change**: System simplified from 4 databases to 2 (TDengine + PostgreSQL)

**Migration Completed**:
- ✅ MySQL data migrated to PostgreSQL (18 tables, 299 rows)
- ✅ Redis removed (configured db1 was empty)
- ✅ Architecture complexity reduced by 50%
- ✅ **TDengine retained**: Specialized for high-frequency time-series market data
- ✅ **PostgreSQL**: Handles all other data types with TimescaleDB extension

**New Configuration**: See `.env` for 2-database setup (TDengine + PostgreSQL).

**Philosophy**: Right Tool for Right Job, Simplicity > Unnecessary Complexity

---

## Project Overview

MyStocks is a professional quantitative trading data management system that uses a **dual-database architecture** optimized for different data characteristics. The system is built on adapter and factory patterns to provide unified data access layers with configuration-driven automation.

**Current Architecture** (Post-Week 3):
- **TDengine**: High-frequency time-series market data (tick/minute data) with extreme compression
- **PostgreSQL + TimescaleDB**: All other data types (daily bars, reference data, derived data, metadata)
- **Optimized Operations**: Right database for right workload, reduced unnecessary complexity

## Common Development Commands

### Environment Setup
```bash
# Install dependencies (dual-database setup)
pip install pandas numpy pyyaml psycopg2-binary taospy akshare

# Create .env file with database configuration
# Required environment variables for 2-database architecture:
# TDengine (high-frequency time-series data):
# - TDENGINE_HOST, TDENGINE_PORT, TDENGINE_USER, TDENGINE_PASSWORD, TDENGINE_DATABASE
# PostgreSQL (all other data):
# - POSTGRESQL_HOST, POSTGRESQL_USER, POSTGRESQL_PASSWORD, POSTGRESQL_PORT, POSTGRESQL_DATABASE
# - MONITOR_DB_URL (uses PostgreSQL for monitoring database)

# Note: MySQL (pymysql) and Redis removed after Week 3 simplification
```

### System Initialization and Management
```bash
# Initialize the complete system
python -c "from unified_manager import MyStocksUnifiedManager; manager = MyStocksUnifiedManager(); manager.initialize_system()"

# Run system demonstration
python system_demo.py

# Validate database connections and table structures
python -c "from core import ConfigDrivenTableManager; mgr = ConfigDrivenTableManager(); mgr.validate_all_table_structures()"

# Run realtime market data saver
python run_realtime_market_saver.py

# Check database connections (TDengine + PostgreSQL)
python -c "import taos; taos.connect(host='192.168.123.104', port=6030); print('TDengine OK')"
python -c "import psycopg2; print('PostgreSQL connection OK')"
```

### Testing
```bash
# Test unified manager functionality
python test_unified_manager.py

# Test financial adapter
python test_financial_adapter.py

# Test comprehensive system
python test_comprehensive.py

# Test realtime data functionality
python test_save_realtime_data.py
```

### Configuration Management
```bash
# View current table configuration
python -c "
import yaml
with open('table_config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
print(f'Configuration version: {config.get(\"version\", \"unknown\")}')
print(f'Tables configured: {len(config.get(\"tables\", []))}')
"

# Create tables from configuration
python -c "from db_manager.database_manager import DatabaseTableManager; mgr = DatabaseTableManager(); mgr.batch_create_tables('table_config.yaml')"
```

## High-Level Architecture

### Core Design Principles

1. **Dual-Database Data Storage** (Week 3+): Right database for right workload
   - **High-Frequency Market Data** (高频时序数据): Tick/minute data → **TDengine** (extreme compression, ultra-high write performance)
   - **Daily Market Data** (日线数据): Daily bars, historical data → **PostgreSQL TimescaleDB** hypertables
   - **Reference Data** (参考数据): Relatively static descriptive data → **PostgreSQL** standard tables
   - **Derived Data** (衍生数据): Computed analytical results → **PostgreSQL** standard tables
   - **Transaction Data** (交易数据): Orders, positions, portfolios → **PostgreSQL** standard tables
   - **Meta Data** (元数据): System configuration and metadata → **PostgreSQL** standard tables

2. **Optimized Architecture** (Post-Week 3): 2-database strategy balances performance and simplicity
   - **TDengine database**: `market_data` (超表: tick_data, minute_data)
   - **PostgreSQL database**: `mystocks` (所有其他表 + TimescaleDB混合表)
   - Unified access layer abstracts database differences
   - Monitoring database in PostgreSQL tracks all operations

3. **Configuration-Driven Management**: All table structures managed through YAML configuration
   - `table_config.yaml` defines complete table schemas
   - `ConfigDrivenTableManager` automates table creation and validation

4. **Complete Monitoring Integration**: Separate monitoring database tracks all operations
   - `MonitoringDatabase` logs all operations independent of business databases
   - `PerformanceMonitor` tracks query performance and alerts on slow operations
   - `DataQualityMonitor` ensures data completeness, freshness, and accuracy

### Key Components

#### Core Management Layer (`core.py`)
- `DataClassification`: Enum defining 5-tier data classification
- `DatabaseTarget`: Supported database types (**TDengine**, **PostgreSQL**)
- `DataStorageStrategy`: Auto-routing logic mapping data types to optimal database
- `ConfigDrivenTableManager`: YAML-driven table management

#### Unified Access Layer (`unified_manager.py`)
- `MyStocksUnifiedManager`: Single entry point for all data operations
- `AutomatedMaintenanceManager`: Scheduled maintenance and health checks
- Auto-routing: `save_data_by_classification()` and `load_data_by_classification()` methods

#### Database Access Layer (`data_access.py`)
- `TDengineDataAccess`: High-frequency time-series data (tick, minute bars)
- `PostgreSQLDataAccess`: All other data (daily bars, indicators, reference data, metadata)

#### Data Source Adapters (`adapters/`)
- Unified interface `IDataSource` for all external data providers
- `AkshareDataSource`: Chinese market data via Akshare
- `BaostockDataSource`: Alternative Chinese market data
- `FinancialDataSource`: Financial statements and fundamental data

#### Database Infrastructure (`db_manager/`)
- `DatabaseTableManager`: Dual-database connection and table management
- Supports **TDengine** (WebSocket/Native) and **PostgreSQL** (TimescaleDB extension)
- Environment variable driven configuration for security

#### Monitoring and Quality (`monitoring.py`)
- `MonitoringDatabase`: Independent monitoring database
- `DataQualityMonitor`: Completeness, freshness, accuracy checks
- `PerformanceMonitor`: Query performance tracking
- `AlertManager`: Multi-channel alerting (email, webhook, log)

### Data Flow Architecture

1. **Data Ingestion**: External adapters → Unified Manager → Auto-routing
2. **Storage Strategy**: Classification determines optimal database automatically
3. **Access Pattern**: Unified interface regardless of underlying database
4. **Monitoring**: All operations logged to separate monitoring database
5. **Quality Assurance**: Automated data quality checks and alerts

### Database Specialization Strategy

- **TDengine**: Extreme compression (20:1 ratio), ultra-high write performance for high-frequency market data (tick/minute)
  - Native time-series database optimized for IoT and financial data
  - Automatic data retention policies
  - Superior performance for time-range queries on tick data

- **PostgreSQL + TimescaleDB**: Robust relational database with time-series optimization
  - ACID compliance for all transactional data
  - Complex JOIN operations on reference and derived data
  - TimescaleDB hypertables for daily market data
  - Full-text search and advanced indexing

## Important Implementation Notes

### Configuration Management
- All database connections configured via environment variables (never hardcode credentials)
- `table_config.yaml` contains complete table schemas with support for all database types
- Tables auto-created on system initialization via `ConfigDrivenTableManager`

### Data Operations
- Always use `MyStocksUnifiedManager` as the primary entry point
- Classification-based methods: `save_data_by_classification()`, `load_data_by_classification()`
- System automatically selects optimal database based on data classification

### Error Handling and Monitoring
- All operations automatically logged to monitoring database
- Performance metrics tracked and slow operations flagged
- Data quality checks run automatically with configurable thresholds

### Testing and Validation
- Use `system_demo.py` for comprehensive system testing
- Individual component tests available in `test_*.py` files
- Database validation available via `check_*_tables.py` scripts

### Dual-Database Support
- **TDengine** for high-frequency time-series data (tick, minute bars)
- **PostgreSQL** for all other data types (daily bars, reference, metadata)
- Unified access layer abstracts database differences
- Seamless connection management and automatic routing

This architecture enables efficient handling of quantitative trading data by using the right database for each workload, with comprehensive monitoring and configuration-driven automation.
