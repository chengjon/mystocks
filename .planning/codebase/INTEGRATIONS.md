# External Integrations

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 当前执行口径请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码实现与主线治理文档使用。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码或主线文档冲突，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、当前代码与主线治理文档为准。


**Last mapped**: 2026-04-05

## Databases

### TDengine 3.3+
- **Purpose**: High-frequency time-series data (market quotes, klines, tick data)
- **Access layer**: `src/data_access/tdengine_access.py`, `src/data_access/_tdengine_query_operations.py`, `src/data_access/_tdengine_write_operations.py`
- **Configuration**: via `.env` TDengine connection params

### PostgreSQL 17+ / TimescaleDB
- **Purpose**: Relational data (stocks, strategies, users, alerts) + secondary time-series
- **Access layer**: `src/data_access/postgresql_access.py`, `src/database/database_service_new.py`
- **ORM**: SQLAlchemy (`web/backend/app/core/database.py`)
- **Configuration**: via `.env` `POSTGRES_*` params

## External Data Sources

### akshare
- **Purpose**: A-share market data (quotes, fund flow, industry classification, stock info)
- **Adapter**: `src/adapters/akshare/` (extensive module breakdown)
  - `market_adapter/` — market overview, board sector, forecast, fund flow, stock profile, sentiment
  - `misc_data/` — THS industry names, futures index daily
  - `modules/` — fund flow, market overview, stock info
- **Also duplicated at**: `src/interfaces/adapters/akshare/` (identical files, missing imports)

### efinance
- **Purpose**: Financial data (stock daily, bonds, funds, realtime)
- **Adapter**: `src/adapters/efinance_adapter/`
  - `efinance_data_source_methods/` — part1, part2, part3 (mechanical split)
  - `efinance_bond_helpers.py`, `efinance_fund_helpers.py`

### 通达信 (TDX)
- **Purpose**: Real-time market protocol
- **Adapter**: `src/adapters/tdx_adapter/`

## Real-time & Streaming

### Server-Sent Events (SSE)
- **Implementation**: `web/backend/app/api/sse_endpoints.py`
- **Frontend consumer**: `src/components/sse/`

### WebSocket (Socket.IO)
- **Implementation**: `web/backend/app/core/socketio_manager.py`
- **Backend API**: `web/backend/app/api/websocket.py`

## Authentication
- **JWT-based auth**: `web/backend/app/api/auth.py` (866 lines)
- **CSRF protection**: Built into `web/backend/app/main.py` CSRFTokenManager class
- **Session management**: `web/backend/app/core/config.py` settings

## Monitoring & Observability
- **Prometheus exporter**: `web/backend/app/api/prometheus_exporter.py`
- **Monitoring stack**: `monitoring-stack/` directory
- **Grafana configs**: `config/grafana-auto-setup.js`, `config/package-grafana.json`
- **Performance middleware**: `web/backend/app/core/middleware/performance.py`

## API Documentation
- **Swagger UI**: `/docs` (FastAPI auto-generated)
- **ReDoc**: `/redoc` with custom HTML (`web/backend/app/redoc_custom.html`)
- **OpenAPI config**: `web/backend/app/openapi_config.py` (724 lines)
- **Version mapping**: `web/backend/app/api/VERSION_MAPPING.py`
