# Feature Specification: Architecture Optimization for Quantitative Trading System

**Feature Branch**: `002-arch-optimization`
**Created**: 2025-10-25
**Status**: Draft
**Input**: Architecture optimization to reduce complexity while maintaining quantitative trading analysis capabilities

## Overview

MyStocks system currently suffers from over-engineering with 7 architecture layers, 34 data classifications, 8 adapters with functional overlaps, and 4 databases. This optimization reduces complexity to manageable levels for a 1-2 person team while enhancing professional quantitative analysis capabilities including industry classification, sector analysis, concept tracking, capital flow monitoring, and chip distribution analysis.

**Core Problem (Revised)**: Provide individual/small team quantitative traders with capabilities for Chinese A-share market data **acquisition, storage, querying, and professional analysis**.

**Core Data Flow (Enhanced)**: User → Acquire data (daily/minute/realtime/sector/concept/capital flow/indicators) → Store → Query & Analyze → Display/Backtest

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Critical Documentation-Code Alignment (Priority: P1)

As a developer or operations engineer, I need documentation to accurately reflect the actual code implementation so that I can confidently deploy and maintain the system without confusion.

**Why this priority**: This is blocking deployment decisions. Documentation says "Week 3: simplified to 1 PostgreSQL database" but code still implements 4 databases (TDengine, PostgreSQL, MySQL, Redis). This creates deployment confusion and maintenance uncertainty.

**Independent Test**: Review all documentation files (CLAUDE.md, DATASOURCE_AND_DATABASE_ARCHITECTURE.md, README.md, .env.example) and verify they match actual code implementation in core.py, unified_manager.py, and data_access.py. Test that following deployment instructions results in a working system.

**Acceptance Scenarios**:

1. **Given** current codebase, **When** developer reads CLAUDE.md database section, **Then** it accurately describes the 2-database architecture (TDengine + PostgreSQL) with no mention of MySQL or Redis
2. **Given** .env.example file, **When** operations engineer configures environment, **Then** only TDengine and PostgreSQL configuration variables are present and required
3. **Given** DATASOURCE_AND_DATABASE_ARCHITECTURE.md, **When** architect reviews system design, **Then** all architecture diagrams show only 2 databases and 3 layers (not 4 databases and 7 layers)
4. **Given** deployment documentation, **When** new team member follows setup instructions, **Then** system deploys successfully without requiring MySQL or Redis

---

### User Story 2 - Simplified Database Architecture (Priority: P1)

As a system administrator, I need to maintain only 2 databases (TDengine for high-frequency time-series data + PostgreSQL for everything else) instead of 4 databases to reduce operational complexity and infrastructure costs.

**Why this priority**: Reduces infrastructure complexity by 50%, lowers monthly cloud costs, simplifies backup/recovery procedures, and matches team capacity (1-2 people cannot effectively manage 4 databases).

**Independent Test**: Deploy system with only TDengine and PostgreSQL. Verify all data types (market data, reference data, derived data, trading data, metadata) can be stored and retrieved successfully. Confirm MySQL and Redis are completely removed from codebase.

**Acceptance Scenarios**:

1. **Given** high-frequency tick data and minute bars, **When** system stores data, **Then** it automatically routes to TDengine for optimal time-series performance
2. **Given** daily K-line, reference data, derived indicators, and trading records, **When** system stores data, **Then** it automatically routes to PostgreSQL with appropriate table structures
3. **Given** system startup, **When** UnifiedManager initializes, **Then** only TDengine and PostgreSQL connections are created (no MySQL or Redis initialization)
4. **Given** configuration file, **When** environment variables are loaded, **Then** only TDENGINE_* and POSTGRESQL_* variables are required (MYSQL_* and REDIS_* removed)
5. **Given** monitoring requirements, **When** system operates, **Then** monitoring database uses PostgreSQL (no separate MySQL monitoring database)

---

### User Story 3 - Streamlined Architecture Layers (Priority: P1)

As a developer, I need a simplified 3-layer architecture (Adapter Layer → Data Manager Layer → Database Layer) instead of 7 layers to improve code maintainability, reduce onboarding time from 2-3 weeks to 2-3 days, and increase development velocity by 80%.

**Why this priority**: 80% of current 11,000 lines of code are abstraction overhead. Reducing to 3 layers eliminates 4 unnecessary abstraction layers, improves performance by 35% (removing 50-70ms routing overhead), and drastically reduces cognitive load for developers.

**Independent Test**: Implement sample data flow (acquire stock data → save → query) using new 3-layer architecture. Measure code lines, performance, and developer understanding time. Verify no functionality is lost compared to 7-layer architecture.

**Acceptance Scenarios**:

1. **Given** stock daily data acquisition request, **When** data flows through system, **Then** it passes through exactly 3 layers: Adapter (acquire) → DataManager (route & validate) → Database (persist), with no intermediate routing/strategy/factory layers
2. **Given** new developer onboarding, **When** they study architecture documentation, **Then** they can understand complete data flow in under 6 hours (down from 24-38 hours)
3. **Given** 1000 records batch save operation, **When** performance is measured, **Then** total execution time is ≤80ms (vs current 120ms), with abstraction overhead ≤30% (vs current 58%)
4. **Given** need to modify data save logic, **When** developer locates code, **Then** changes are confined to 1-2 files (vs current 5-8 files)
5. **Given** complete system, **When** core architecture code is counted, **Then** total lines ≤4,000 (vs current 11,000), with ≥70% being business logic (vs current 20%)

---

### User Story 4 - Optimized Data Classification System (Priority: P2)

As a quantitative analyst, I need a practical 8-10 data classification system that covers essential market data types including industry sectors, concept plates, capital flow, and chip distribution, replacing the over-engineered 34-classification system.

**Why this priority**: Current 34 classifications are 70% unused and create unnecessary complexity. New system balances simplicity with professional analysis needs. Enables sector rotation analysis, capital flow tracking, and chip distribution studies critical for quantitative strategies.

**Independent Test**: Map all real-world data acquisition scenarios to the new 8-10 classifications. Verify no actual use case is lost. Confirm new classifications support professional quantitative analysis workflows (sector analysis, capital tracking, chip monitoring).

**Acceptance Scenarios**:

1. **Given** stock market data needs, **When** analyst reviews classification system, **Then** 8-10 core classifications cover: (1) High-frequency data (tick/minute), (2) Historical K-line (daily/weekly/monthly), (3) Real-time quotes, (4) Industry & Sector data, (5) Concept plates, (6) Financial statements, (7) Capital flow & money tracking, (8) Chip distribution & holder analysis, (9) News & announcements, (10) Derived indicators & signals
2. **Given** data routing requirements, **When** system determines storage location, **Then** decision is made in <5ms using simple classification-to-database mapping (no complex strategy classes)
3. **Given** professional analysis scenario, **When** analyst queries industry sector performance, **Then** system provides sector classification, constituent stocks, sector indices, and capital flow data
4. **Given** capital flow analysis need, **When** analyst queries fund movements, **Then** system provides main fund flow, retail flow, institutional flow by stock/sector/market
5. **Given** chip distribution analysis, **When** analyst studies shareholder structure, **Then** system provides holder concentration, chip distribution by price level, and shareholder changes

---

### User Story 5 - Consolidated Core Adapters (Priority: P2)

As a developer, I need 2-3 core data adapters (TDX, AkShare, Byapi) with flexible interface that doesn't force implementation of unsupported methods, eliminating 90% functional overlap between current 8 adapters.

**Why this priority**: Reduces adapter maintenance from 8,000 lines to ~2,500 lines (-69%). Eliminates confusion from overlapping adapters (financial + customer both use efinance/easyquotation). Flexible interface prevents forcing TDX to implement financial methods it doesn't support.

**Independent Test**: Implement all current data acquisition scenarios using only 3 core adapters. Verify no data source is lost. Confirm adapter interface allows partial implementation without violating type contracts.

**Acceptance Scenarios**:

1. **Given** adapter consolidation, **When** system uses data sources, **Then** exactly 3 core adapters exist: TDX (local high-speed, no API limits), AkShare (comprehensive online data), Byapi (alternative API source with 300 req/min limit)
2. **Given** previous 8 adapters, **When** functionality is mapped, **Then** financial_adapter + customer_adapter → merged into AkShare (both used efinance/easyquotation), baostock_adapter → removed (AkShare covers functionality), akshare_proxy_adapter → removed (proxy parameter added to AkShare instead), tushare_adapter → optional/community (requires paid token)
3. **Given** adapter interface design, **When** TDX adapter is implemented, **Then** it only implements methods it supports (daily/minute/realtime quotes) without being forced to implement financial_data or news methods
4. **Given** external data source, **When** developer needs to integrate new source, **Then** they can register adapter through simple dictionary mapping or DataManager.register_adapter() without complex factory pattern
5. **Given** adapter failure, **When** primary adapter (TDX) is unavailable, **Then** system automatically fails over to secondary adapter (AkShare) based on priority configuration with exponential backoff retry (avoid IP blocking)

---

### User Story 6 - Data Source Capability Matrix (Priority: P2)

As a developer or analyst, I need a comprehensive data source capability matrix showing exactly what data types, formats, and update frequencies each adapter (TDX, AkShare, Byapi, Tushare, web scraping, Sina, EastMoney) provides so I can make informed adapter selection and understand data coverage.

**Why this priority**: Different adapters have different strengths. TDX excels at real-time quotes but lacks financials. AkShare has comprehensive coverage but may have rate limits. Matrix enables intelligent adapter selection and identifies data gaps. Critical for professional analysis requiring specific data types.

**Independent Test**: Create matrix spreadsheet/document. For each adapter, test and document: supported data types, update frequency, API limits, data quality, historical depth. Verify matrix is accurate and complete.

**Acceptance Scenarios**:

1. **Given** data source matrix, **When** developer needs real-time tick data, **Then** matrix clearly shows TDX provides tick data with millisecond latency, no rate limits, while AkShare provides minute-level at best with potential rate limits
2. **Given** financial analysis need, **When** analyst needs balance sheets, **Then** matrix shows AkShare and Tushare provide quarterly financial statements, TDX does not support financials, Byapi provides limited financial data
3. **Given** capital flow analysis, **When** analyst needs main fund flow data, **Then** matrix shows which adapters provide: (a) Stock-level fund flow, (b) Sector-level fund flow, (c) Market-level fund flow, (d) Update frequency (daily/intraday), (e) Historical depth (years available)
4. **Given** industry classification need, **When** analyst needs sector groupings, **Then** matrix documents which adapters provide: (a) CSRC industry classification, (b) SW (Shenwan) industry classification, (c) Concept plate memberships, (d) Custom sector definitions
5. **Given** API limit concerns, **When** developer plans data acquisition, **Then** matrix clearly shows rate limits: TDX (unlimited - local connection), AkShare (unknown - community service), Byapi (300 req/min with license key), Tushare (varies by tier)

---

### User Story 7 - Enhanced Logging and Monitoring (Priority: P3)

As a system administrator, I need modern logging using loguru (replacing standard logging) and professional monitoring using Grafana with independent PostgreSQL monitoring database for comprehensive system observability.

**Why this priority**: Loguru provides better developer experience with simpler syntax and automatic rotation. Grafana provides professional visualization. Independent monitoring database prevents monitoring failures from affecting business operations. Maintains separation of concerns.

**Independent Test**: Configure loguru for application logs, set up Grafana dashboards for PostgreSQL/TDengine metrics, simulate production load and verify all metrics are captured correctly in independent monitoring database.

**Acceptance Scenarios**:

1. **Given** application logging needs, **When** system logs events, **Then** loguru handles all application logs with automatic file rotation, colored console output, and structured logging (JSON format option)
2. **Given** monitoring requirements, **When** system operates, **Then** Grafana dashboards display: (a) Database connection pool status, (b) Query execution times with p50/p95/p99 percentiles, (c) Data ingestion rates (records/second), (d) Adapter success/failure rates, (e) Storage usage trends for TDengine and PostgreSQL
3. **Given** monitoring database design, **When** system stores metrics, **Then** independent PostgreSQL database (separate from business PostgreSQL) stores: operation logs, performance metrics, data quality checks, with separate connection pool and backup schedule
4. **Given** production failure scenario, **When** business database (PostgreSQL) is unavailable, **Then** monitoring database continues to record failures and metrics, enabling root cause analysis without monitoring data loss
5. **Given** log analysis needs, **When** administrator searches logs, **Then** loguru's structured format enables easy grep/search: `grep "ERROR" app.log`, `grep "adapter=tdx" app.log`, with timestamps in ISO format

---

### User Story 8 - Flexible Adapter Interface Pattern (Priority: P3)

As a developer, I need adapter interface that supports partial method implementation and optional external adapter registration without complex factory patterns, enabling easier integration of new data sources and respecting adapter limitations.

**Why this priority**: Current IDataSource forces all 8 methods even when adapter can't support them (TDX doesn't have financials). Dynamic registration/unregistration needs re-evaluation - likely over-engineered for static adapter set. Embedding adapters in DataManager eliminates factory layer overhead.

**Independent Test**: Implement adapter with only 3 methods (instead of forcing 8). Register external test adapter dynamically. Verify system doesn't fail on unimplemented methods and provides clear capability info.

**Acceptance Scenarios**:

1. **Given** adapter interface design, **When** TDX adapter is created, **Then** it implements base interface with only supported methods: get_realtime_quote(), get_kline_data(), get_transaction_ticks(), without being forced to stub out get_financial_data() or get_news()
2. **Given** adapter capability query, **When** system checks adapter features, **Then** DataManager provides method: adapter.supports('financial_data') → True/False, allowing runtime capability detection without try/catch
3. **Given** external data source, **When** developer integrates custom scraper, **Then** registration uses simple pattern: `DataManager.register_adapter('my_scraper', MyScraperAdapter())` without factory registration, with automatic capability detection
4. **Given** adapter registry, **When** system supports runtime adapter management, **Then** DataManager provides methods: register_adapter(name, instance) and unregister_adapter(name) to add/remove adapters while system is running, enabling hot-plug capability for custom data sources without service restart
5. **Given** adapter polling and retry, **When** adapter request fails, **Then** system implements: (a) Exponential backoff: 1s, 2s, 4s, 8s delays, (b) Circuit breaker: After 3 consecutive failures, pause adapter for 5 minutes, (c) Rate limit respect: Byapi adapter enforces 300 req/min with token bucket algorithm

---

### User Story 9 - Preserved Trading Management Interfaces (Priority: P3)

As a future feature planner, I need to preserve unused trading data classifications and interfaces (order records, transaction records, position tracking, account management) for future trading system integration without implementing functionality now.

**Why this priority**: Follows YAGNI principle - don't implement now, but design interfaces to avoid future breaking changes. Enables future trading system integration without major refactoring. Low cost to maintain interface definitions.

**Independent Test**: Review trading-related data classifications and interfaces. Verify they are defined but not implemented. Confirm they don't add complexity to current system. Validate future trading system could use these interfaces without changes.

**Acceptance Scenarios**:

1. **Given** data classification system, **When** classifications are reviewed, **Then** trading-related types are defined but marked as reserved: TradingOrders (reserved), TradingPositions (reserved), TradingTransactions (reserved), AccountStatus (reserved)
2. **Given** database schema, **When** table_config.yaml is reviewed, **Then** trading-related tables are commented out with note "Reserved for future trading system integration - do not remove"
3. **Given** adapter interface, **When** future trading integration is planned, **Then** interface includes placeholder methods: place_order() (not implemented), get_positions() (not implemented), with clear documentation stating "Reserved for future"
4. **Given** current system operation, **When** system runs, **Then** trading interfaces don't add overhead: no trading-related database connections, no trading API calls, no trading data processing (zero runtime cost)

---

### Edge Cases

- **Database failover**: What happens when TDengine is unavailable? System should log error, queue data for retry (using FailureRecoveryQueue), and continue operating with PostgreSQL-supported features only.
- **Adapter cascading failure**: What if all adapters (TDX, AkShare, Byapi) fail simultaneously? System should implement circuit breaker to prevent request storms, return cached data if available, and alert administrator via Grafana.
- **Data classification ambiguity**: How does system handle data that could fit multiple classifications (e.g., is a dividend announcement "News" or "Financial Statement" classification)? System should use primary classification with cross-reference tags, documented in classification mapping table.
- **Adapter rate limit exceeded**: When Byapi hits 300 req/min limit, how does system respond? System should automatically pause Byapi adapter, fail over to AkShare, and resume Byapi after rate limit window resets (implement token bucket algorithm).
- **Monitoring database failure**: What if independent monitoring PostgreSQL database fails? Application logs continue via loguru to files, metrics queue in memory (with size limit), automatic retry connection to monitoring DB every 60 seconds, alert via separate channel (email/SMS if configured).
- **New data type not in 8-10 classifications**: What if analyst needs data type not covered by optimized classification system? System provides "Custom Data" classification with flexible schema, allows addition of new classification through configuration (not code change), maintains backward compatibility.
- **External adapter compatibility**: What if external adapter doesn't follow interface conventions? DataManager wrapper validates adapter responses, converts to standard format, logs compatibility warnings, provides adapter quality score based on response reliability.

## Requirements *(mandatory)*

### Functional Requirements

**Architecture Simplification**:

- **FR-001**: System MUST reduce architecture layers from current 7 layers to exactly 3 layers: (1) Adapter Layer - external data acquisition, (2) DataManager Layer - routing, validation, orchestration, (3) Database Layer - TDengine and PostgreSQL persistence
- **FR-002**: System MUST eliminate intermediate layers: Factory Pattern layer, DataStorageStrategy routing layer, separate UnifiedManager abstraction layer, complex monitoring infrastructure
- **FR-003**: System MUST reduce core architecture codebase from current ~11,000 lines to ≤4,000 lines, achieving ≥70% business logic ratio (vs current 20%)

**Database Architecture**:

- **FR-004**: System MUST support exactly 2 databases: TDengine (for high-frequency time-series: tick data, minute K-lines) and PostgreSQL (for all other data types: daily K-lines, reference data, derived data, financial data, monitoring data)
- **FR-005**: System MUST completely remove MySQL and Redis from codebase: delete MySQLDataAccess class, delete RedisDataAccess class, remove all MySQL/Redis configuration variables, update all documentation to reflect 2-database architecture
- **FR-006**: System MUST route data automatically: high-frequency time-series (>1000 records/second) → TDengine, all other data → PostgreSQL, with routing decision made in <5ms

**Data Classification**:

- **FR-007**: System MUST implement simplified 8-10 data classification system covering: (1) High-frequency data (tick, minute bars), (2) Historical K-line (daily/weekly/monthly), (3) Real-time quotes & snapshots, (4) Industry & Sector classifications, (5) Concept plates & themes, (6) Financial statements & metrics, (7) Capital flow & fund tracking, (8) Chip distribution & holder analysis, (9) News & announcements, (10) Derived indicators & trading signals
- **FR-008**: System MUST remove unused classifications from current 34-type system: delete classification definitions not mapped to actual use cases, update DataClassification enum to 8-10 types only, remove associated routing logic for deleted classifications
- **FR-009**: System MUST support professional quantitative analysis: sector rotation analysis via industry/concept classifications, capital flow tracking for stocks/sectors/market levels, chip distribution analysis showing holder concentration and price-level distribution

**Adapter Consolidation**:

- **FR-010**: System MUST consolidate to 3 core adapters: (1) TDX Adapter - local data source, unlimited requests, millisecond latency for real-time quotes, (2) AkShare Adapter - comprehensive online data, daily K-lines, financial statements, industry data, (3) Byapi Adapter - alternative API with 300 req/min rate limit, provides capital flow and advanced metrics
- **FR-011**: System MUST eliminate functional overlaps: merge financial_adapter and customer_adapter functionality into AkShare adapter (both use efinance/easyquotation libraries), remove baostock_adapter (fully covered by AkShare), remove akshare_proxy_adapter (add proxy parameter to AkShare instead), move tushare_adapter to optional/community (requires paid token)
- **FR-012**: System MUST implement flexible adapter interface: allow adapters to implement only supported methods (partial implementation), provide capability detection via adapter.supports(method_name) API, prevent type contract violations when methods are unavailable

**Data Source Management**:

- **FR-013**: System MUST provide data source capability matrix documenting for each adapter: supported data types and methods, update frequency and latency, API rate limits and restrictions, data quality and historical depth, optimal use cases
- **FR-014**: System MUST support external adapter registration: simple registration via DataManager.register_adapter(name, adapter_instance), automatic capability detection for registered adapters, no complex factory pattern required
- **FR-015**: System MUST implement robust retry and failover: exponential backoff retry (1s, 2s, 4s, 8s delays) on adapter failures, automatic failover to secondary adapter based on priority configuration, circuit breaker pattern (pause adapter after 3 consecutive failures for 5 minutes), rate limit enforcement (Byapi token bucket: 300 req/min)

**Logging and Monitoring**:

- **FR-016**: System MUST use loguru for application logging: structured logging with JSON format support, automatic log rotation (daily, max 10 files, 100MB per file), colored console output for development, log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **FR-017**: System MUST use Grafana for system monitoring: dashboards for database metrics (connection pool, query performance, storage usage), adapter performance (success rate, latency, failover events), data ingestion metrics (records/second by data type)
- **FR-018**: System MUST maintain independent monitoring database: separate PostgreSQL database for monitoring data (not business database), separate connection pool preventing monitoring from affecting business operations, automatic connection retry if monitoring database is unavailable (queue metrics in memory with 10MB size limit)

**Documentation Alignment**:

- **FR-019**: System MUST ensure documentation-code consistency: CLAUDE.md must accurately describe 2-database architecture (TDengine + PostgreSQL), DATASOURCE_AND_DATABASE_ARCHITECTURE.md must show 3-layer architecture with 2 databases, .env.example must contain only TDengine and PostgreSQL configuration variables (remove MySQL and Redis), README.md must have updated deployment instructions matching actual implementation

**Future Compatibility**:

- **FR-020**: System MUST preserve trading interfaces for future: define but do not implement trading data classifications (TradingOrders, TradingPositions, TradingTransactions, AccountStatus), comment out trading-related table definitions in table_config.yaml with "Reserved for future" notes, include placeholder adapter methods (place_order, get_positions) with clear "not implemented" documentation
- **FR-021**: System MUST allow new classification addition: support "Custom Data" classification with flexible schema for data types not in core 8-10, enable new classification addition through configuration file (not code changes), maintain backward compatibility when classifications are added

### Key Entities *(data-focused feature)*

- **DataClassification**: Simplified 8-10 enumeration representing core data types (high-frequency, historical K-line, real-time quotes, industry/sector, concept plates, financials, capital flow, chip distribution, news, derived indicators). Each classification maps to target database (TDengine or PostgreSQL) and defines routing rules.

- **DataAdapter**: Abstraction for external data sources (TDX, AkShare, Byapi). Attributes include: adapter name, supported methods/capabilities, rate limits, priority level, health status. Supports partial method implementation and capability detection.

- **DataManager**: Central orchestration layer replacing multiple managers. Responsibilities include: data routing to appropriate database, adapter selection and failover, retry logic with exponential backoff, performance monitoring integration. Embeds adapter registry (eliminates factory layer).

- **DatabaseTarget**: Two-value enumeration (TDengine, PostgreSQL). Used by DataManager for routing decisions. Associated with connection pools, health checks, and failover logic.

- **CapabilityMatrix**: Documentation entity (not code) mapping adapters to supported data types. Includes: data type name, providing adapters, update frequency, rate limits, data quality indicators, historical depth. Used for adapter selection decisions.

- **MonitoringMetrics**: Data captured in independent monitoring database. Includes: operation logs (timestamp, classification, adapter used, success/failure), performance metrics (query times, ingestion rates, storage growth), adapter health (uptime, error rates, circuit breaker status).

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Codebase Simplification**:

- **SC-001**: Core architecture codebase is reduced from current 11,000 lines to ≤4,000 lines (≥64% reduction), measured by counting lines in core.py, unified_manager.py, data_access.py, factory/, and monitoring/ directories
- **SC-002**: Business logic ratio increases from current 20% to ≥70% (actual business code vs abstraction overhead), measured by analyzing code purpose: business logic (data acquisition, storage, query) vs infrastructure (routing, factory, abstract base classes)
- **SC-003**: New developer onboarding time decreases from current 24-38 hours to ≤6 hours, measured by time needed to understand complete data flow and successfully implement first code change

**Performance Improvements**:

- **SC-004**: Data save operation latency improves by ≥30%, from current 120ms per 1000 records to ≤80ms, measured by benchmark test saving 1000 stock daily records
- **SC-005**: Abstraction layer overhead decreases from current 58% to ≤30%, measured by ratio: (total operation time - database execution time) / total operation time
- **SC-006**: Data routing decision time is <5ms for any classification, measured by time from classification input to database target determination

**Maintainability Gains**:

- **SC-007**: Code modification scope reduces from current 5-8 files to ≤2 files for typical changes (e.g., add data validation, change save logic), measured by tracking files modified in sample scenarios
- **SC-008**: Test coverage increases from current <50% to ≥80%, measured by pytest --cov for core architecture modules
- **SC-009**: Documentation-code consistency is 100%, verified by spot-checking 10 random documentation claims against actual code implementation with zero mismatches

**Operational Efficiency**:

- **SC-010**: Infrastructure complexity reduces by 50%, from managing 4 databases to 2 databases, measured by count of database services, backup procedures, monitoring dashboards, and configuration files required
- **SC-011**: Adapter maintenance burden decreases by ≥60%, from 8,000 lines across 8 adapters to ≤2,500 lines across 3 adapters, measured by total adapter code line count
- **SC-012**: Monthly infrastructure cost decreases by ≥40% (if deployed to cloud), from running 4 database services to 2, measured by actual cloud service bills or estimated cost for on-premise resources (hardware, electricity, maintenance time)

**Functional Completeness**:

- **SC-013**: Zero functional regression: all current data acquisition scenarios (100+ test cases) continue to work after optimization, measured by passing existing test suite without modification
- **SC-014**: Enhanced data classification coverage: professional analysis scenarios (sector rotation, capital flow tracking, chip distribution analysis) are successfully supported, measured by executing 10 representative quantitative analysis workflows
- **SC-015**: Adapter failover reliability is ≥99%: when primary adapter (TDX) fails, secondary adapter (AkShare) successfully provides data within 3 retry attempts, measured by chaos engineering tests with simulated adapter failures

## Assumptions

1. **Team Size**: System will be maintained by 1-2 developers, not an enterprise team of 5+
2. **Data Scale**: System handles <10 million rows of historical data and <1000 records/second of real-time data, within single-server PostgreSQL and TDengine capacity
3. **Use Case**: Primary use is quantitative strategy research and backtesting, not high-frequency algorithmic trading with microsecond latency requirements
4. **Deployment**: System deploys to single server or small cluster (not distributed multi-datacenter setup), making 2-database architecture sufficient
5. **Adapter Availability**: At least 2 of 3 core adapters (TDX, AkShare, Byapi) are available at any given time for failover redundancy
6. **Rate Limits**: External API rate limits are respected via throttling and token bucket algorithms to prevent IP blocking or account suspension
7. **Monitoring Priority**: System monitoring is important but not mission-critical - brief monitoring database outage is acceptable, business operations continue unaffected
8. **Trading Future**: Trading system integration is planned but not immediate (next 6-12 months), justifying preserved interfaces without full implementation
9. **PostgreSQL Capacity**: PostgreSQL with TimescaleDB extension provides sufficient performance for non-high-frequency time-series data (daily/hourly granularity), eliminating need for separate MySQL
10. **External Adapters**: Custom or third-party adapters are rare (maybe 1-2 over project lifetime), so simple registration mechanism is sufficient without complex plugin architecture

## Dependencies

**External Systems**:
- TDengine database server (open-source time-series database)
- PostgreSQL database server with TimescaleDB extension
- Grafana monitoring platform with PostgreSQL data source
- External data sources: TDX servers (通达信), AkShare API, Byapi service (biyingapi.com)

**Libraries**:
- loguru (logging)
- psycopg2 (PostgreSQL driver)
- taosws/taosrest (TDengine driver)
- pandas (data manipulation)
- pytdx (TDX protocol library)
- akshare (financial data library)

**Internal Dependencies**:
- Existing test suite must pass after changes (regression prevention)
- Current data in MySQL must be migrated to PostgreSQL before removal
- Backup strategy must be updated for 2-database architecture

## Out of Scope

- **Real-time trading execution**: This optimization focuses on data management and analysis, not live trading with brokers (preserved for future)
- **Distributed architecture**: System remains single-server or small cluster, not refactored for distributed multi-datacenter deployment
- **Complex CEP (Complex Event Processing)**: Advanced real-time pattern matching on streaming data is not included, basic data ingestion only
- **Machine learning model training**: While system stores derived indicators, ML model training infrastructure is separate concern
- **Mobile/web UI changes**: This is backend architecture optimization, frontend/UI is not modified
- **Multi-tenancy**: System serves single trading team/user, not refactored for multi-tenant SaaS deployment
- **Real-time collaboration**: Multiple users working on same analysis simultaneously is not addressed
- **Advanced security hardening**: Focus is on architecture simplification, not adding OAuth2/RBAC/encryption (uses existing security)

## Risks and Mitigation

**Risk 1 - Data Migration Failure (High Impact, Medium Probability)**:
- **Risk**: MySQL data migration to PostgreSQL could fail or cause data loss
- **Mitigation**: Full backup before migration, test migration on copy of production data, verify data integrity with checksums/row counts, maintain MySQL read-only for 2 weeks after migration as safety net, automated rollback plan

**Risk 2 - Performance Regression (Medium Impact, Low Probability)**:
- **Risk**: PostgreSQL might not handle all data types as efficiently as specialized databases (MySQL for reference, Redis for cache)
- **Mitigation**: Load testing before deployment simulating 3x current load, TimescaleDB extension for time-series optimization, PostgreSQL tuning (connection pooling, indexes, vacuuming), keep TDengine for high-frequency data preventing PostgreSQL overload

**Risk 3 - Adapter Consolidation Breaking Changes (High Impact, Low Probability)**:
- **Risk**: Removing 5 adapters might break existing code/scripts depending on them
- **Mitigation**: Comprehensive grep search for adapter references, full test suite execution, deprecation period with warnings before removal, migration guide for any external scripts, Git tags for rollback capability

**Risk 4 - Documentation Lag (Low Impact, Medium Probability)**:
- **Risk**: Documentation updates might not keep pace with code changes during refactoring
- **Mitigation**: Include documentation updates in same commits as code changes, use checklist requiring doc review before merge, automated link checker for documentation cross-references, scheduled documentation audit every 2 weeks

**Risk 5 - Monitoring Gaps During Transition (Medium Impact, Medium Probability)**:
- **Risk**: Moving from complex to simple monitoring might lose visibility into system health temporarily
- **Mitigation**: Deploy Grafana dashboards before removing old monitoring, parallel run old+new monitoring for 1 week, gradual cutover not big-bang switch, keep old monitoring code in separate branch for emergency fallback

## Key Architectural Decisions

1. **Dynamic Adapter Registration Scope**: System supports runtime adapter registration/unregistration without service restart. Core adapters (TDX, AkShare, Byapi, Baostock) are pre-configured at startup, but custom/external adapters can be dynamically added via DataManager.register_adapter(name, instance) API during operation. This enables hot-plug capability for integrating new data sources (web scrapers, custom APIs, third-party feeds) without downtime, trading increased complexity (~300 lines of registration management code) for operational flexibility valuable in research environment where data sources frequently change.

2. **TDengine Data Retention Policy**: System implements tiered storage strategy for high-frequency data: (1) Hot data tier - Recent 3 months of tick/minute data retained in TDengine for high-speed access, (2) Cold data tier - Data older than 3 months automatically archived to PostgreSQL with compression, (3) Automated archival process runs daily to migrate qualifying data from TDengine to PostgreSQL cold storage, balancing storage costs with analytical capabilities for long-term backtesting.

3. **Adapter Priority Configuration**: System implements cache-first, source-type-aware priority strategy: (1) PostgreSQL Cache Layer - Always checked first for all data requests (historical data already stored), (2) Local Data Sources - If cache miss, check TDX for real-time/local data (no API limits, millisecond latency), (3) Network Data Sources - If local unavailable, try network adapters in order: AkShare → Baostock → Byapi, based on reliability and coverage. This strategy minimizes external API calls, respects rate limits, and optimizes for data availability while leveraging PostgreSQL as intelligent cache layer.
