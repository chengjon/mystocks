# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MyStocks is a professional quantitative trading data management system that implements a scientific 5-tier data classification framework with intelligent routing strategies for multi-database coordination. The system is built on adapter and factory patterns to provide unified data access layers with configuration-driven automation.

## Common Development Commands

### Environment Setup
```bash
# Install dependencies
pip install pandas numpy pyyaml pymysql psycopg2-binary redis taospy akshare

# Create .env file with database configurations
# Required environment variables:
# - MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_DATABASE
# - POSTGRESQL_HOST, POSTGRESQL_USER, POSTGRESQL_PASSWORD, POSTGRESQL_PORT, POSTGRESQL_DATABASE
# - TDENGINE_HOST, TDENGINE_USER, TDENGINE_PASSWORD, TDENGINE_PORT, TDENGINE_DATABASE
# - REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB
# - MONITOR_DB_URL (for monitoring database)
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

# Check database table status
python check_mysql_tables.py
python check_tdengine_tables.py
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

1. **5-Tier Data Classification System**: Scientific categorization based on data characteristics and access patterns
   - **Market Data** (时序数据): High-frequency tick/minute data → TDengine
   - **Reference Data** (参考数据): Relatively static descriptive data → MySQL/MariaDB
   - **Derived Data** (衍生数据): Computed analytical results → PostgreSQL+TimescaleDB
   - **Transaction Data** (交易数据): Hot/cold separation strategy → Redis (hot) + PostgreSQL (cold)
   - **Meta Data** (元数据): System configuration and metadata → MySQL/MariaDB

2. **Intelligent Auto-Routing**: Data automatically routed to optimal database based on classification
   - `DataStorageStrategy.get_target_database()` determines best database for each data type
   - `DataClassification` enum defines all supported data categories

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
- `DatabaseTarget`: Supported database types (TDengine, PostgreSQL, MySQL, Redis)
- `DataStorageStrategy`: Auto-routing logic mapping data types to databases
- `ConfigDrivenTableManager`: YAML-driven table management

#### Unified Access Layer (`unified_manager.py`)
- `MyStocksUnifiedManager`: Single entry point for all data operations
- `AutomatedMaintenanceManager`: Scheduled maintenance and health checks
- Auto-routing: `save_data_by_classification()` and `load_data_by_classification()` methods

#### Database Access Layer (`data_access.py`)
- `TDengineDataAccess`: High-frequency time-series data (tick, minute bars)
- `PostgreSQLDataAccess`: Historical analysis data (daily bars, indicators)
- `MySQLDataAccess`: Reference and metadata (symbols, calendars, config)
- `RedisDataAccess`: Real-time caching and hot data

#### Data Source Adapters (`adapters/`)
- Unified interface `IDataSource` for all external data providers
- `AkshareDataSource`: Chinese market data via Akshare
- `BaostockDataSource`: Alternative Chinese market data
- `FinancialDataSource`: Financial statements and fundamental data

#### Database Infrastructure (`db_manager/`)
- `DatabaseTableManager`: Multi-database connection and table management
- Supports TDengine (WebSocket/REST), PostgreSQL (TimescaleDB), MySQL, Redis
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

- **TDengine**: Extreme compression (20:1 ratio), ultra-high write performance for market data
- **PostgreSQL+TimescaleDB**: Complex time-series queries, automatic partitioning
- **MySQL/MariaDB**: ACID compliance for reference data, complex JOINs
- **Redis**: Sub-millisecond access for real-time positions and hot data

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

### Multi-Database Support
- System designed for heterogeneous database environments
- Each database type optimized for specific data characteristics
- Seamless failover and connection management built-in

This architecture enables efficient handling of quantitative trading data with automatic optimization, comprehensive monitoring, and simplified management through configuration-driven automation.
