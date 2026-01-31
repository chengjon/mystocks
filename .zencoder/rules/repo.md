---
description: Repository Information Overview
alwaysApply: true
---

# MyStocks Repository Information

## Repository Summary
MyStocks is a professional quantitative trading data management system and web platform. It features a dual-database architecture optimized for different data types, a configuration-driven automated management system, and advanced GPU acceleration for backtesting and AI strategies.

## Repository Structure
The repository is organized as a monorepo with core logic, microservices, and a modern web interface.

### Main Repository Components
- **Core Library (`src/`)**: The heart of the system containing data adapters, storage strategies, GPU kernels, and ML strategies.
- **Web Frontend (`web/frontend/`)**: A Vue 3 + Vite management interface using Element Plus and Ant Design Vue.
- **Web Backend (`web/backend/`)**: A FastAPI-based API server serving the frontend and handling real-time data.
- **Microservices (`services/`)**: Specialized components for backtesting, financial data, real-time market simulation, and risk management.
- **Monitoring Stack (`monitoring-stack/`)**: A complete observability suite using the LGTM stack (Loki, Grafana, Tempo, Prometheus).
- **Scripts (`scripts/`)**: Comprehensive toolset for database maintenance, system runtime, and automated testing.

## Projects

### Core Quant System (Python)
**Configuration Files**: `pyproject.toml`, `requirements.txt`, `config/table_config.yaml`

#### Language & Runtime
**Language**: Python  
**Version**: 3.9 - 3.12  
**Build System**: Setuptools  
**Package Manager**: pip

#### Dependencies
**Main Dependencies**:
- **Frameworks**: FastAPI, Uvicorn, Celery, Redis
- **Data Processing**: Pandas 2.0+, NumPy, SQLAlchemy, Pydantic 2.0+
- **Databases**: taospy (TDengine), psycopg2-binary (PostgreSQL), asyncpg
- **GPU Acceleration**: cupy-cuda12x, cudf-cu12, cuml-cu12 (RTX 2080 support)
- **Data Sources**: Akshare, Baostock, Tushare, Efinance

#### Docker
**Configuration**: `monitoring-stack/docker-compose.yml` (Prometheus, Grafana, Loki, Tempo)

#### Testing
**Framework**: Pytest  
**Test Location**: `scripts/tests/`, `tests/`  
**Naming Convention**: `test_*.py`  
**Configuration**: `pyproject.toml` (`[tool.pytest.ini_options]`)
**Run Command**:
```bash
pytest
```

---

### Management Frontend (Vue 3)
**Configuration File**: `web/frontend/package.json`

#### Language & Runtime
**Language**: TypeScript / Vue  
**Version**: Vue 3.4+, Node.js  
**Build System**: Vite  
**Package Manager**: npm

#### Dependencies
**Main Dependencies**:
- **UI**: Element Plus, Ant Design Vue, ECharts
- **State/Routing**: Pinia, Vue Router
- **Utils**: Axios, Zod, Day.js, Lodash-es
- **Trading**: Klinecharts, Technicalindicators

#### Build & Installation
```bash
cd web/frontend
npm install
npm run dev
```

#### Testing
**Framework**: Vitest (Unit), Playwright (E2E)  
**Test Location**: `web/frontend/tests/`, `web/frontend/cypress/` (legacy)  
**Naming Convention**: `*.test.ts`, `*.spec.ts`
**Run Command**:
```bash
npm run test
npm run test:e2e
```

---

### Specialized Microservices
**Type**: Multi-component service layer

#### Key Resources
- **Backtest API**: `services/backtest-api/` (Python/FastAPI)
- **Realtime Market**: `services/a-stock-realtime/` (WebSocket server, Market simulator)
- **Risk Management**: `services/a-stock-risk-management/` (Vue/Frontend component)
- **Financial Service**: `services/a-stock-financial/` (Vue/Frontend component)

#### Usage & Operations
**Key Commands**:
```bash
# Start Realtime Simulator
cd services/a-stock-realtime
./start_server.sh
```

---

### Infrastructure & Operations
**Type**: Configuration and Monitoring Repository

#### Specification & Tools
**Required Tools**: Docker, Docker Compose, PM2 (for frontend/backend process management)

#### Key Resources
- **Monitoring Config**: `monitoring-stack/config/` (Prometheus/Loki/Tempo YAMLs)
- **Database Schema**: `src/core/config_driven_table_manager.py` (Automated table creation from `config/table_config.yaml`)

#### Validation
**Quality Checks**: 
- **Python**: Ruff (Lint/Fix), Black (Formatting), MyPy (Type checking), Pylint (Deep analysis)
- **Frontend**: ESLint, Prettier, Vue-tsc (Type checking)
**Testing Approach**: Comprehensive E2E testing using Playwright across multiple browsers and Bloomberg-style UI validation.
