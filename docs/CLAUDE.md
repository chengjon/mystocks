<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Note**: This file works in conjunction with the project constitution (`.specify/memory/constitution.md`) and the highest guidance document (`项目开发规范与指导文档.md`) to ensure consistent development practices.

## 🗂️ 重大更新 (2025-11-09): 项目目录重组完成

**目录结构优化**: 从42个杂乱的根目录精简到13个科学组织的目录

**重组成果**:
- ✅ 所有源代码整合到 `src/` 目录
- ✅ 所有文档整合到 `docs/` 目录
- ✅ 所有脚本整合到 `scripts/` 目录
- ✅ 统一导入路径为 `from src.*` 格式
- ✅ 创建 `src/db_manager/` 兼容层确保平滑过渡
- ✅ Git历史完整保留 (使用 `git mv` 移动所有文件)
- ✅ 目录混乱度降低 **69%**

**新的导入路径标准**:
```python
# ✅ 推荐: 新的标准导入路径
from src.core import ConfigDrivenTableManager, DataClassification
from src.adapters.akshare_adapter import AkshareDataSource
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess
from src.db_manager import DatabaseTableManager  # 兼容层
from src.monitoring import MonitoringDatabase, AlertManager
from src.interfaces import IDataSource

# ⚠️ 仍然有效: 旧的导入路径 (通过兼容层)
from core import ConfigDrivenTableManager
from db_manager.database_manager import DatabaseTableManager

# ❌ 已废弃: 直接从根目录导入模块目录
from adapters.akshare_adapter import AkshareDataSource
```

**脚本路径更新**:
```bash
# ✅ 新路径
python scripts/runtime/system_demo.py
python scripts/tests/test_config_driven_table_manager.py
python scripts/database/check_tdengine_tables.py

# ❌ 旧路径
python system_demo.py
python test_config_driven_table_manager.py
```

**详细报告**: 参见 [`REORGANIZATION_COMPLETION_REPORT.md`](./REORGANIZATION_COMPLETION_REPORT.md)

**核心原则**: 清晰的目录结构 + 科学的文件分类 + 完整的Git历史保留

---

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
python scripts/runtime/system_demo.py

# Validate database connections and table structures
python -c "from core import ConfigDrivenTableManager; mgr = ConfigDrivenTableManager(); mgr.validate_all_table_structures()"

# Run realtime market data saver
python scripts/runtime/run_realtime_market_saver.py

# Check database connections (TDengine + PostgreSQL)
python scripts/database/check_tdengine_tables.py
python scripts/database/verify_tdengine_deployment.py
```

### Testing
```bash
# Test unified manager functionality
python scripts/tests/test_config_driven_table_manager.py

# Test financial adapter
python scripts/tests/test_financial_adapter.py

# Test dual database architecture
python scripts/tests/test_dual_database_architecture.py

# Test realtime data functionality
python scripts/tests/test_save_realtime_data.py

# Test TDX adapter
python scripts/tests/test_tdx_mvp.py
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

### Key Components (重组后的模块路径)

#### Core Management Layer (`src/core/`)
**位置**: `src/core/` 目录
- `DataClassification`: 5大数据分类枚举定义
- `DatabaseTarget`: 支持的数据库类型 (**TDengine**, **PostgreSQL**)
- `DataStorageStrategy`: 智能路由逻辑,自动映射数据类型到最优数据库
- `ConfigDrivenTableManager`: YAML配置驱动的表管理器

**导入**:
```python
from src.core import ConfigDrivenTableManager, DataClassification
from src.core.data_storage_strategy import DataStorageStrategy
```

#### Unified Access Layer (`src/core/` - unified_manager)
**位置**: `src/core/unified_manager.py` + 根目录 `unified_manager.py` (入口点)
- `MyStocksUnifiedManager`: 所有数据操作的统一入口点
- `AutomatedMaintenanceManager`: 定时维护和健康检查
- 自动路由方法: `save_data_by_classification()` 和 `load_data_by_classification()`

**导入**:
```python
from unified_manager import MyStocksUnifiedManager  # 通过根目录入口点
# 或
from src.core.unified_manager import MyStocksUnifiedManager  # 直接导入
```

#### Database Access Layer (`src/data_access/`)
**位置**: `src/data_access/` 目录
- `TDengineDataAccess`: 高频时序数据访问 (tick, 分钟K线)
- `PostgreSQLDataAccess`: 所有其他数据访问 (日线、指标、参考数据、元数据)

**导入**:
```python
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess
```

#### Data Source Adapters (`src/adapters/`)
**位置**: `src/adapters/` 目录 (7个核心适配器)
- 统一接口 `IDataSource` 定义于 `src/interfaces/data_source.py`
- `AkshareDataSource`: Akshare中国市场数据
- `BaostockDataSource`: Baostock历史数据
- `FinancialDataSource`: 财务报表和基本面数据
- `TdxDataSource`: 通达信直连数据源
- `ByapiDataSource`: REST API数据源
- `CustomerDataSource`: 实时行情数据源
- `TushareDataSource`: Tushare专业数据源

**导入**:
```python
from src.adapters.akshare_adapter import AkshareDataSource
from src.adapters.tdx_adapter import TdxDataSource
from src.interfaces import IDataSource
```

#### Database Infrastructure (`src/storage/database/` + 兼容层 `src/db_manager/`)
**实际位置**: `src/storage/database/` 目录
**兼容层**: `src/db_manager/` (重导出 `src.storage.database` 的所有类)

- `DatabaseTableManager`: 双数据库连接和表管理
- `DatabaseConnectionManager`: 数据库连接池管理
- 支持 **TDengine** (WebSocket/Native) 和 **PostgreSQL** (TimescaleDB扩展)
- 环境变量驱动配置,确保安全性

**导入** (两种方式均可):
```python
# 方式1: 通过兼容层 (旧代码可继续使用)
from src.db_manager import DatabaseTableManager, DatabaseConnectionManager

# 方式2: 直接导入 (推荐)
from src.storage.database import DatabaseTableManager, DatabaseConnectionManager
```

#### Monitoring and Quality (`src/monitoring/`)
**位置**: `src/monitoring/` 目录
- `MonitoringDatabase`: 独立监控数据库
- `DataQualityMonitor`: 数据完整性、准确性、新鲜度检查
- `PerformanceMonitor`: 查询性能跟踪和慢查询检测
- `AlertManager`: 多渠道告警 (邮件、Webhook、日志)

**导入**:
```python
from src.monitoring import MonitoringDatabase, DataQualityMonitor
from src.monitoring import PerformanceMonitor, AlertManager
```

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

## File Organization Rules

**Philosophy**: Maintain a clean, minimal root directory with logical categorization by functionality. Every file should have a clear, rule-based location.

### Root Directory Standards

**ONLY these 5 core files belong in root**:
- `README.md` - Project overview and main documentation
- `CLAUDE.md` - Claude Code integration guide (this file)
- `CHANGELOG.md` - Version history and changes
- `requirements.txt` - Python dependencies
- `.mcp.json` - MCP server configuration

**All other files MUST be organized into subdirectories**.

### Directory Structure and Rules

#### 1. **scripts/** - All Executable Scripts

Organized by functionality into 4 categories:

**scripts/tests/** - Test Files
- **Pattern**: Files prefixed with `test_`
- **Purpose**: Unit tests, integration tests, acceptance tests
- **Examples**: `test_config_driven_table_manager.py`, `test_financial_adapter.py`
- **Special files**: `test_requirements.txt`, `coverage.xml`

**scripts/runtime/** - Production Runtime Scripts
- **Pattern**: Files prefixed with `run_`, `save_`, `monitor_`, or `*_demo.py`
- **Purpose**: Production data collection, monitoring, demonstrations
- **Examples**: `run_realtime_market_saver.py`, `save_realtime_data.py`, `system_demo.py`

**scripts/database/** - Database Operations
- **Pattern**: Files prefixed with `check_`, `verify_`, `create_`
- **Purpose**: Database initialization, validation, management
- **Examples**: `check_tdengine_tables.py`, `verify_tdengine_deployment.py`

**scripts/dev/** - Development Tools
- **Pattern**: Development utilities not fitting other categories
- **Purpose**: Code validation, testing utilities, development aids
- **Examples**: `gpu_test_examples.py`, `validate_documentation_consistency.py`
- **Special files**: `git_commit_comments.txt`

#### 2. **docs/** - Documentation Files

**docs/guides/** - User and Developer Guides
- **Files**: `QUICKSTART.md`, `IFLOW.md`, tutorial documents
- **Purpose**: Getting started guides, workflow documentation

**docs/archived/** - Deprecated Documentation
- **Files**: `START_HERE.md`, `TASKMASTER_START_HERE.md` (kept for historical reference)
- **Purpose**: Preserve old documentation without cluttering active docs
- **Rule**: Add deprecation notice at top of file when archiving

**docs/architecture/** - Architecture Design Documents
- **Purpose**: System design, technical architecture documentation
- **Examples**: Database design docs, system architecture diagrams

**docs/api/** - API Documentation
- **Purpose**: API reference, endpoint documentation, SDK guides

#### 3. **config/** - Configuration Files

**All configuration files** (regardless of extension):
- **Extensions**: `.yaml`, `.yml`, `.ini`, `.toml`, `docker-compose.*.yml`
- **Examples**:
  - `mystocks_table_config.yaml` - Table structure definitions
  - `docker-compose.tdengine.yml` - Docker setup
  - `pytest.ini` - Test configuration
  - `.readthedocs.yaml` - Documentation build config

#### 4. **reports/** - Generated Reports and Analysis

**Pattern**: Files generated by analysis scripts, timestamped if recurring
- **Extensions**: `.json`, `.txt`, analysis outputs
- **Examples**:
  - `database_assessment_20251019_165817.json`
  - `query_patterns_analysis.txt`
  - `dump_result.txt`
  - `WENCAI_INTEGRATION_FILES.txt`

**Naming Convention**: Use ISO date format for timestamped files: `YYYYMMDD_HHMMSS`

### File Lifecycle Management

#### Pre-Classification (Proactive)

**When creating new files**, place them directly in the correct location:

1. **Determine file purpose**: Test? Runtime? Configuration? Documentation?
2. **Match against rules**: Use the directory structure above
3. **Create in correct location**: Never create in root unless it's one of the 5 core files

**Example Pre-Classification**:
```python
# Creating a new test file
# ✅ CORRECT: Create directly in scripts/tests/
with open('scripts/tests/test_new_feature.py', 'w') as f:
    f.write(test_code)

# ❌ INCORRECT: Creating in root
with open('test_new_feature.py', 'w') as f:
    f.write(test_code)
```

#### Post-Classification (Reactive)

**When organizing existing files**:

1. **Identify misplaced files**: Use `ls` or `find` to list root directory files
2. **Categorize by rules**: Match each file against the directory structure rules
3. **Plan the reorganization**: Create a categorization plan before execution
4. **Use git mv**: Preserve file history when moving tracked files
5. **Update references**: Update all import paths, documentation links
6. **Validate**: Test that moved files work correctly

**Post-Classification Workflow**:
```bash
# 1. List root directory files (exclude core 5)
ls -1 | grep -v -E '^(README\.md|CLAUDE\.md|CHANGELOG\.md|requirements\.txt|\.mcp\.json)$'

# 2. For each file, determine correct location using rules above

# 3. Move files (use git mv for tracked files)
git mv test_something.py scripts/tests/
git mv run_collector.py scripts/runtime/
git mv config.yaml config/
git mv analysis_report.txt reports/

# 4. Update references in affected files

# 5. Commit with descriptive message
git commit -m "refactor: organize files according to directory structure rules"
```

### Import Path Management for Scripts

**Critical Rule**: All scripts in nested directories must calculate project root correctly.

**Standard Pattern for scripts in `scripts/**/`**:
```python
import sys
import os
from pathlib import Path

# Calculate project root (3 levels up from script location)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Now you can import from project root
from core import ConfigDrivenTableManager
from adapters.akshare_adapter import AkshareDataSource
from db_manager.database_manager import DatabaseTableManager
```

**Explanation**:
- Script in `scripts/tests/test_something.py`
- `__file__` → `scripts/tests/test_something.py`
- `os.path.dirname(__file__)` → `scripts/tests/`
- `os.path.dirname(os.path.dirname(__file__))` → `scripts/`
- `os.path.dirname(os.path.dirname(os.path.dirname(__file__)))` → project root `/opt/claude/mystocks_spec/`

### Git Best Practices

**Always use `git mv` for tracked files**:
```bash
# ✅ CORRECT: Preserves file history
git mv old_location/file.py new_location/file.py

# ❌ INCORRECT: Breaks file history
mv old_location/file.py new_location/file.py
git add new_location/file.py
```

**For untracked files**, regular `mv` is fine:
```bash
# For files not in git yet
mv untracked_file.log reports/
```

### Validation Checklist

After any file reorganization:

- [ ] Root directory contains only the 5 core files
- [ ] All scripts properly categorized in scripts/{tests,runtime,database,dev}
- [ ] All documentation in docs/{guides,archived,architecture,api}
- [ ] All configuration files in config/
- [ ] All reports in reports/
- [ ] All moved scripts have updated import paths (3-level dirname)
- [ ] All documentation links updated to new paths
- [ ] `git status` shows moves (not deletions + additions)
- [ ] All tests pass after reorganization
- [ ] `scripts/README.md` is up to date

### Common Mistakes to Avoid

1. **Creating files in root**: Always use subdirectories unless it's one of the 5 core files
2. **Wrong import paths**: Remember to use 3-level dirname for scripts in nested directories
3. **Using `mv` instead of `git mv`**: Always preserve git history
4. **Forgetting to update references**: Check all imports, documentation links
5. **Mixing purposes**: Don't put test files in runtime/, or config files in docs/

### Reference Documentation

For detailed directory contents and file inventory:
- **Complete documentation structure**: See `docs/DOCUMENTATION_STRUCTURE.md`
- **Script organization guide**: See `scripts/README.md`

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md
