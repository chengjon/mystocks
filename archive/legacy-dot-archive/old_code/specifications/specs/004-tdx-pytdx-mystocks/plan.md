# Implementation Plan: TDX数据源适配器集成

**Branch**: `004-tdx-pytdx-mystocks` | **Date**: 2025-10-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-tdx-pytdx-mystocks/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integration of pytdx library into MyStocks system to create a TDX (通达信) data source adapter that conforms to the IDataSource interface. The adapter will provide direct access to Chinese A-stock market data (深交所 and 上交所) without API rate limits, supporting 8 core functions: real-time quotes (batch), historical K-lines (9 timeframes), minute/tick data, financial info, dividend info, sector info, and company info.

**Technical Approach**: Wrap pytdx's 3-layer architecture (transport/parser/application) using connection pool pattern, implement IDataSource interface with 8 required methods, reuse existing MyStocks utilities (ColumnMapper, normalize_date, format_stock_code_for_source), and ensure automatic routing compliance with MyStocks 5-tier data classification system.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing MyStocks codebase)
**Primary Dependencies**:
  - pytdx (from temp/pytdx/) - TDX protocol communication layer
  - pandas - DataFrame operations and data standardization
  - typing - Type hints for interface compliance
  - Existing MyStocks utilities: ColumnMapper, normalize_date, format_stock_code_for_source

**Storage**: Multi-database routing via MyStocksUnifiedManager:
  - TDengine: Tick data, minute K-lines (high-frequency time-series)
  - PostgreSQL+TimescaleDB: Daily/weekly/monthly K-lines (historical analysis)
  - MySQL/MariaDB: Financial info, dividend records, sector info (reference data)
  - Redis: Real-time quotes cache (hot data, sub-second access)

**Testing**: pytest with fixtures for TDX connection mocking, contract tests for IDataSource interface compliance

**Target Platform**: Linux server (same as existing adapters: akshare_adapter.py, baostock_adapter.py)

**Project Type**: Single project (monorepo) - adapter added to existing `adapters/` directory

**Performance Goals**:
  - Single stock real-time quote: < 3s response time
  - Batch quotes (50 stocks): < 10s response time
  - 800 daily K-lines query: < 5s response time
  - Success rate: 99%+ under normal TDX server conditions
  - 30% faster than existing adapters during market peak hours

**Constraints**:
  - Network latency to TDX servers (typically 7709 port)
  - TDX single request data limits (800 K-line records max per call)
  - Connection pool size limit (default 5 connections)
  - No authentication required for public market data
  - Must handle GBK/UTF-8 encoding for Chinese text

**Scale/Scope**:
  - Support 5000+ A-stock symbols (深交所 + 上交所)
  - Handle 10+ concurrent users querying simultaneously
  - Process 10,000+ tick records per second during market hours
  - Store 5+ years of historical K-line data
  - Connection pool: 5-10 concurrent connections to TDX servers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. 5层数据分类体系 (COMPLIANT)

**Status**: PASS - All data types properly mapped to constitutional classifications

**Mapping**:
- **Tick数据** (分笔成交) → DataClassification.TICK_DATA → TDengine (超高频,毫秒级)
- **分钟K线** (1min/5min/15min/30min/1hour) → DataClassification.MINUTE_KLINE → TDengine (高频,分钟级)
- **日线/周线/月线/季线/年线** → DataClassification.DAILY_KLINE → PostgreSQL+TimescaleDB (中低频,历史回溯)
- **实时行情** (real-time quotes) → DataClassification.REALTIME_QUOTES → Redis (热数据,高频读写)
- **财务信息** (financial indicators) → DataClassification.REFERENCE_FINANCIAL → MySQL/MariaDB (低频,季度/年度)
- **除权除息** (dividend records) → DataClassification.REFERENCE_DIVIDEND → MySQL/MariaDB (低频,不定期)
- **板块信息** (sector classifications) → DataClassification.REFERENCE_SECTOR → MySQL/MariaDB (半静态)
- **公司信息** (company info) → DataClassification.REFERENCE_STOCK_INFO → MySQL/MariaDB (静态)

**Implementation**: TdxDataSource adapter will not directly handle storage routing - all data will be passed to MyStocksUnifiedManager.save_data_by_classification() which enforces automatic routing based on DataClassification enum.

### ✅ II. 配置驱动设计 (COMPLIANT)

**Status**: PASS - No table structure modifications required

**Rationale**: TdxDataSource is a pure data acquisition adapter. It does not create or modify any database tables. All table structures are already defined in existing table_config.yaml. The adapter simply fetches data and passes it to UnifiedManager for storage using existing table schemas.

**No configuration changes needed**: This feature adds a new data source, not new storage structures.

### ✅ III. 智能自动路由 (COMPLIANT)

**Status**: PASS - Fully leverages automatic routing system

**Implementation**:
- TdxDataSource adapter calls `MyStocksUnifiedManager.save_data_by_classification(data, classification)`
- Does NOT manually specify target databases in application code
- DataStorageStrategy.get_target_database() determines routing based on DataClassification
- Example: Minute K-lines tagged with DataClassification.MINUTE_KLINE automatically route to TDengine

**No manual routing**: Adapter code contains zero direct database connections. All routing handled by core system.

### ✅ IV. 多数据库协同 (COMPLIANT)

**Status**: PASS - Utilizes all 4 database engines optimally

**Database Usage**:
- **TDengine**: High-frequency tick and minute data (20:1 compression, 10k+ writes/sec)
- **PostgreSQL+TimescaleDB**: Historical daily+ K-lines (complex time-series queries, automatic partitioning)
- **MySQL/MariaDB**: Financial statements, dividends, sector mappings (ACID, complex JOINs for reference data)
- **Redis**: Real-time quote cache (sub-millisecond access for hot trading data)

**Justification**: Each data type routed to technically optimal database based on access patterns, not convenience.

### ✅ V. 完整可观测性 (COMPLIANT)

**Status**: PASS - Leverages existing monitoring infrastructure

**Implementation**:
- All adapter operations logged through MyStocksUnifiedManager's monitoring hooks
- Performance metrics automatically tracked by PerformanceMonitor
- Data quality checks run by DataQualityMonitor on all fetched data
- Errors/retries logged to independent MonitoringDatabase
- AlertManager triggers on repeated connection failures

**No custom monitoring needed**: Existing monitoring system covers all adapter operations transparently.

### ✅ VI. 统一访问接口 (COMPLIANT)

**Status**: PASS - Implements IDataSource interface, uses UnifiedManager

**Interface Compliance**:
- TdxDataSource implements all 8 required IDataSource methods
- Application code calls adapter methods (e.g., `get_stock_daily()`)
- Adapter fetches from TDX, then calls `UnifiedManager.save_data_by_classification()`
- No direct database access in adapter code
- Consistent API with AkshareDataSource and BaostockDataSource

**Single entry point**: All data operations flow through UnifiedManager after acquisition.

### ✅ VII. 安全优先 (COMPLIANT)

**Status**: PASS - No credentials required, follows environment variable pattern

**Security Practices**:
- TDX servers are public endpoints (no authentication required for market data)
- TDX server addresses configured via environment variables (TDX_SERVER_HOST, TDX_SERVER_PORT)
- No hardcoded IPs or credentials in source code
- Connection strings loaded from .env file
- .env file excluded from version control via .gitignore

**No credential exposure**: Public market data access, zero authentication secrets.

### 📊 Constitution Compliance Summary

**Overall Status**: ✅ **PASS** - Full compliance with all 7 constitutional principles

| Principle | Status | Notes |
|-----------|--------|-------|
| I. 5层数据分类体系 | ✅ PASS | All 8 data types properly classified and routed |
| II. 配置驱动设计 | ✅ PASS | No table changes, uses existing schemas |
| III. 智能自动路由 | ✅ PASS | Zero manual database selection |
| IV. 多数据库协同 | ✅ PASS | Optimal use of all 4 database engines |
| V. 完整可观测性 | ✅ PASS | Full monitoring integration |
| VI. 统一访问接口 | ✅ PASS | IDataSource + UnifiedManager pattern |
| VII. 安全优先 | ✅ PASS | Environment variables, no credentials |

**Gate Decision**: ✅ **PROCEED TO PHASE 0 RESEARCH**

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
adapters/
├── __init__.py
├── akshare_adapter.py          # Existing - Akshare data source
├── baostock_adapter.py          # Existing - Baostock data source
├── financial_adapter.py         # Existing - Financial data source
└── tdx_adapter.py               # NEW - TDX (pytdx) data source adapter

interfaces/
└── data_source.py               # Existing - IDataSource interface definition

utils/
├── __init__.py
├── column_mapper.py             # Existing - ColumnMapper utility (reused)
├── date_utils.py                # Existing - normalize_date utility (reused)
└── stock_code_formatter.py      # Existing - format_stock_code_for_source (reused)

temp/pytdx/
├── hq.py                        # Reference implementation - TdxHq_API, TdxExHq_API
├── parser/                      # pytdx parsers (imported by adapter)
└── client/                      # pytdx transport layer (imported by adapter)

core.py                          # Existing - DataClassification, DataStorageStrategy
unified_manager.py               # Existing - MyStocksUnifiedManager (routing layer)

tests/
├── test_tdx_adapter.py          # NEW - Unit tests for TdxDataSource
├── test_tdx_integration.py      # NEW - Integration tests with mock TDX server
└── test_tdx_contract.py         # NEW - IDataSource contract compliance tests

config/
└── .env                         # TDX server configuration (TDX_SERVER_HOST, TDX_SERVER_PORT)
```

**Structure Decision**: Single project (monorepo) structure. This feature adds one new adapter file (`tdx_adapter.py`) to the existing `adapters/` directory, following the established pattern of `akshare_adapter.py` and `baostock_adapter.py`. No new directories needed - all infrastructure (interfaces, utilities, core routing, testing framework) already exists.

**Key Files**:
- **Primary Implementation**: `adapters/tdx_adapter.py` (new, ~500-800 lines)
- **Interface Contract**: `interfaces/data_source.py` (existing, defines 8 required methods)
- **pytdx Library**: `temp/pytdx/hq.py` (existing, reference for TDX API calls)
- **Unit Tests**: `tests/test_tdx_adapter.py` (new, ~300-500 lines)
- **Integration Tests**: `tests/test_tdx_integration.py` (new, ~200-300 lines)

**Integration Points**:
- Imports `IDataSource` from `interfaces/data_source.py`
- Imports `ColumnMapper`, `normalize_date`, `format_stock_code_for_source` from `utils/`
- Imports TDX classes from `temp/pytdx/hq.py`
- Called by application code, returns data to `MyStocksUnifiedManager` for routing

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

**No violations detected** - This feature is fully compliant with all constitutional principles. No complexity justification required.
