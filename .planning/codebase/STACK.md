# Technology Stack

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 当前执行口径请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码实现与主线治理文档使用。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码或主线文档冲突，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、当前代码与主线治理文档为准。


**Last mapped**: 2026-04-05

## Languages & Runtimes

| Layer | Language | Runtime | Version |
|-------|----------|---------|---------|
| Backend API | Python | CPython 3.12+ | FastAPI 0.114+ |
| Frontend | TypeScript / Vue 3 | Vite + Node.js | Vue 3.4+ |
| Database TS | SQL (TDengine) | TDengine 3.3+ | High-frequency time-series |
| Database OLTP | SQL (PostgreSQL) | PostgreSQL 17+ TimescaleDB | Relational + time-series |
| GPU (optional) | Python CUDA | gpu_api_system/ | src/gpu/ |

## Backend Dependencies

### Core Framework
- **FastAPI** 0.114+ — async REST API framework
- **Uvicorn** — ASGI server (configured in `web/backend/app/main.py`)
- **SQLAlchemy** — ORM for PostgreSQL
- **Pydantic** — data validation / settings (`web/backend/app/core/config.py`)

### Data & Computation
- **TDengine** client — time-series database connector
- **psycopg2 / asyncpg** — PostgreSQL drivers
- **aiohttp** — async HTTP client (for data source adapters)
- **numpy / pandas** — data manipulation in algorithms

### External Data Sources
- **akshare** — A-share market data (`src/adapters/akshare/`)
- **efinance** — financial data (`src/adapters/efinance_adapter/`)
- **TDX (通达信)** — real-time market protocol (`src/adapters/tdx_adapter/`)

## Frontend Dependencies

### Core Framework
- **Vue 3** + Composition API
- **Pinia** — state management (`web/frontend/src/stores/`)
- **Vue Router** — routing (`web/frontend/src/router/`)
- **Vite** — build tool

### UI & Visualization
- **ECharts** — chart rendering (via `src/components/Charts/`, `src/components/charts/`)
- **ArtDeco** design system — custom theme (`src/views/artdeco-pages/`, `src/components/artdeco/`)

### Additional
- **axios** — HTTP client (`src/api/`)
- **SSE** — server-sent events (`src/components/sse/`)

## Configuration

| Config | Location | Format |
|--------|----------|--------|
| Environment vars | `.env` / `.env.example` | dotenv |
| Backend settings | `web/backend/app/core/config.py` | Pydantic Settings |
| CORS | `web/backend/app/core/config.py` | Python |
| Data sources registry | `config/data_sources_registry.yaml` | YAML |
| Playwright | `config/playwright/` (6 configs) | TypeScript |
| Frontend | `web/frontend/vite.config.js` | JS |
| Linting | Ruff (Python), Stylelint (CSS/SCSS) | TOML / JSON |

## Build & Dev Commands

```bash
# Backend
cd web/backend && uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload

# Frontend
cd web/frontend && npm install && npm run dev -- --port 3020

# Python lint
ruff check src/ web/backend/app/

# CSS lint
cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"

# Type check
cd web/frontend && npx vue-tsc --noEmit
```
