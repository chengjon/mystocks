# MyStocks Project Structure Analysis

> **设计方案说明**:
> 本文件是架构设计、系统模型、功能结构、映射关系或规格方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、功能清单和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## Executive Summary
- **Total Top-Level Directories**: 95+
- **Total Root-Level Files**: 61
- **Largest Directory**: `logs/` (236GB)
- **Maximum Nesting Depth**: 17 levels (in worktrees/grafana plugins)
- **Primary File Types**: JavaScript (92,523), TypeScript (55,465), JSON (35,415)

---

## 1. ROOT-LEVEL FILES (61 total)

### Configuration Files
- `.pre-commit-config.yaml` - Pre-commit hooks
- `.pre-commit-hooks.yaml` - Hook definitions
- `.gitattributes`, `.gitignore` - Git configuration
- `.env`, `.env.example`, `.env.async_monitoring` - Environment variables
- `.pylintrc`, `.pylint.test.rc` - Python linting
- `pyproject.toml`, `pytest.ini`, `mypy.ini` - Python project config
- `vitest.config.ts` - Vitest configuration
- `.mcp.json` - MCP configuration

### Documentation Files
- `README.md` - Main project readme
- `CLAUDE.md`, `GEMINI.md`, `AGENTS.md` - AI agent documentation
- `IFLOW.md` - Workflow documentation
- `TASK.md`, `TASK-REPORT.md` - Task tracking
- `TASK-T01-REPORT.md` through `TASK-T10-REPORT.md` - Phase reports
- `FRONTEND_OPTIMIZATION_PLAN.md` - Frontend strategy
- `plan_draft.md`, `task_plan.md` - Planning documents

### Package Management
- `package.json`, `package-lock.json` - Node.js dependencies
- `requirements.txt`, `requirements-dev.txt` - Python dependencies
- `requirements-mock.txt`, `requirements-security.txt` - Specialized requirements
- `requirements_freeze.txt` - Frozen dependencies

### Application Files
- `__init__.py` - Python package marker
- `conftest.py` - Pytest configuration
- `core.py`, `data_access.py`, `unified_manager.py` - Core modules
- `monitoring.py` - Monitoring script

### Docker & Deployment
- `docker-compose.prod.yml`, `docker-compose.test.yml` - Docker compose files

### Logs & Reports
- `coverage.xml`, `coverage.json` - Coverage reports
- `data_source_calls.log`, `financial_adapter.log`, `realtime_data_save.log` - Application logs
- `test_timing.csv` - Test metrics
- `.coverage` - Coverage data
- `LICENSE` - License file

---

## 2. TOP-LEVEL DIRECTORY STRUCTURE (95 directories)

### Core Application Directories
```
src/                    - Main source code (25M)
  ├── adapters/
  ├── advanced_analysis/
  ├── algorithms/
  ├── alternative_data/
  ├── api/
  ├── application/
  ├── backtesting/
  ├── components/
  ├── core/
  ├── cron/
  ├── data_access/
  ├── data_governance/
  ├── data_sources/
  ├── database/
  ├── database_optimization/
  ├── db_manager/
  ├── domain/
  ├── factories/
  ├── governance/
  ├── gpu/
  ├── indicators/
  ├── infrastructure/
  ├── interfaces/
  ├── logging/
  ├── ml_strategy/
  ├── mock/
  ├── monitoring/
  ├── portfolio/
  ├── reporting/
  ├── routes/
  ├── services/
  ├── storage/
  ├── styles/
  ├── trading/
  ├── utils/
  └── visualization/

tests/                  - Test suite (28M)
  ├── 001-fix-5-critical/
  ├── 001-readme-md-md/
  ├── 002-arch-optimization/
  ├── acceptance/
  ├── adapters/
  ├── ai/
  ├── analysis/
  ├── api/
  ├── backend/
  ├── changes/
  ├── chaos/
  ├── ci/
  ├── config/
  ├── contract/
  ├── core/
  ├── cron/
  ├── dashboard/
  ├── data/
  ├── data_access/
  ├── data_sources/
  ├── database/
  ├── ddd/
  ├── docs/
  ├── e2e/
  ├── file_level/
  ├── fixtures/
  ├── generated/
  ├── grafana/
  ├── helpers/
  ├── integration/
  ├── logs/
  ├── metrics/
  ├── monitoring/
  ├── orchestration/
  ├── performance/
  ├── pipeline/
  ├── playwright-report/
  ├── prototype/
  ├── reporting/
  ├── reports/
  ├── scripts/
  ├── security/
  ├── setup/
  ├── specs/
  ├── subdir1/
  ├── test-results/
  ├── unit/
  ├── utils/
  └── validation/

web/                    - Web application (1.4G)
  ├── backend/
  ├── frontend/
  └── node_modules/
```

### Documentation & Specifications
```
docs/                   - Documentation (241M)
  ├── 04-测试/
  ├── ai_tools/
  ├── api/
  ├── architecture/
  ├── archive/
  ├── ci-cd/
  ├── cli_reports/
  ├── code_quality/
  ├── completion_reports/
  ├── deployment/
  ├── design/
  ├── design-references/
  ├── docs/
  ├── e2e/
  ├── examples/
  ├── features/
  ├── frontend/
  ├── function-classification-manual/
  ├── guides/
  ├── legacy/
  ├── media/
  ├── monitoring/
  ├── monitoring_reports/
  ├── openspec_cmd/
  ├── operations/
  ├── overview/
  ├── performance/
  ├── phase_reports/
  ├── plans/
  ├── quality/
  ├── reports/
  ├── reviews/
  ├── security/
  ├── standards/
  ├── tasks/
  ├── tdx_integration/
  ├── technical_debt/
  ├── test_reports/
  ├── testing/
  ├── ui-ux-pro-max/
  ├── web/
  └── web-dev/

specs/                  - Specifications (980K)
  ├── 001-fix-5-critical/
  ├── 001-readme-md-md/
  └── 002-arch-optimization/
```

### Infrastructure & Deployment
```
docker/                 - Docker configuration
  └── scripts/

deployment/             - Deployment configs
deployments/            - Deployment artifacts
ci-cd/                  - CI/CD pipeline
config/                 - Configuration files (17M)
  ├── alerts/
  ├── calendars/
  ├── data_sources/
  ├── docker/
  ├── grafana/
  ├── indicators/
  ├── lnav/
  ├── monitoring/
  ├── playwright/
  └── pm2/

monitoring-stack/       - Monitoring infrastructure (73M)
  ├── config/
  ├── data/
  ├── grafana-dashboards/
  └── provisioning/

monitoring/             - Monitoring configs
monitoring_data/        - Monitoring data
monitoring_reports/     - Monitoring reports
```

### Data & Storage
```
data/                   - Data storage (43M)
  ├── cache/
  ├── grafana/
  ├── models/
  └── prometheus/

mock_data_storage/      - Mock data
logs/                   - Application logs (236GB) ⚠️ LARGEST
  ├── app/
  ├── archive/
  ├── data_sync/
  └── security/

backups/                - Backup data
  └── data_source_registry/

bak/                    - Backup directory (554M)
  └── del/
      └── scripts_development_20260201/
```

### Services & APIs
```
services/               - Microservices (114M)
  ├── a-stock-backtest/
  ├── a-stock-financial/
  ├── a-stock-realtime/
  ├── a-stock-risk-management/
  ├── backtest-api/
  ├── risk-control-api/
  └── websocket-server/

api/                    - API definitions
```

### Development & Tools
```
scripts/                - Utility scripts (454M)
  ├── archive/
  ├── async_monitoring/
  ├── cli/
  ├── database/
  ├── db/
  ├── deployment/
  ├── dev/
  ├── file_analysis/
  ├── hooks/
  ├── logs/
  ├── maintenance/
  ├── migrations/
  ├── runtime/
  ├── security/
  ├── tests/
  └── utils/

utils/                  - Utility modules
ai_tools/               - AI tooling
ai_test_optimizer_toolkit/ - Test optimization
ai_generated_tests/     - Generated tests
smart_ai_tests/         - Smart test suite
```

### Quality & Analysis
```
reports/                - Test/analysis reports (115M)
  ├── analysis/
  ├── bugs/
  ├── calculator_coverage/
  ├── cli/
  ├── completion/
  ├── compliance/
  ├── config_loader_coverage/
  ├── coverage/
  ├── data_classification_coverage/
  ├── data_cleaning/
  ├── database_cov/
  ├── debug/
  ├── integration/
  ├── logs/
  ├── performance/
  ├── phase7_monitoring/
  ├── quant/
  ├── simple_calculator_full_coverage/
  ├── structure-baseline/
  ├── type_check/
  └── unit/

code_quality/           - Code quality configs
completion_reports/     - Completion tracking
performance-tests/      - Performance testing
performance/            - Performance data
htmlcov/                - HTML coverage reports (90M)
ts-quality-guard/       - TypeScript quality (120M)
```

### Architecture & Design
```
architecture/           - Architecture docs
design/                 - Design documents
design-references/      - Design references
standards/              - Coding standards
technical_debt/         - Technical debt tracking
  └── governance/

conductor/              - Orchestration (156K)
  ├── archive/
  ├── code_styleguides/
  └── tracks/
```

### Testing & Validation
```
playwright-tests/       - Playwright E2E tests
  └── grafana/

playwright-report/      - Playwright reports (512K)
test-reports/           - Test reports (128K)
  └── locust/

test_reports/           - Additional test reports
testing/                - Testing utilities
test-directory-org/     - Test directory structure
  └── subdir1/

ai_test_optimizer_toolkit/ - Test optimization
```

### Specialized Modules
```
backtesting/            - Backtesting engine
  └── __pycache__/

calcu/                  - Calculator module
  └── block/

tdx_integration/        - TDX integration
function-classification-manual/ - Function classification

legacy/                 - Legacy code
archived/               - Archived code
archive/                - Archive storage
```

### Frontend & UI
```
frontend/               - Frontend code
ui-ux-pro-max/          - UI/UX components
web-dev/                - Web development
web/                    - Web application (1.4G)
  ├── backend/
  ├── frontend/
  └── node_modules/
```

### Miscellaneous
```
examples/               - Example code (216K)
features/               - Feature modules
guides/                 - User guides
operations/             - Operations docs
overview/               - Project overview
plans/                  - Planning documents
phase_reports/          - Phase reports
reviews/                - Code reviews
security/               - Security configs
share/                  - Shared resources (156K)
tasks/                  - Task definitions
temp/                   - Temporary files (480K)
  ├── backups/
  └── cache/

openspec/               - OpenSpec (3.1M)
  ├── changes/
  ├── changes-frontend-unified-optimization/
  └── specs/

openspec_cmd/           - OpenSpec CLI
CLIS/                   - CLI tools (420K)
  ├── SHARED/
  ├── api/
  ├── db/
  ├── it/
  ├── main/
  ├── templates/
  └── web/

buger/                  - Debugging tools
lnav/                   - Log navigation
grafana/                - Grafana configs (136K)
  └── dashboards/

node_modules/           - Node dependencies (151M)
```

### Hidden/System Directories
```
.git/                   - Git repository
.github/                - GitHub workflows
  └── workflows/

.gitignore, .gitattributes - Git config
.vscode/                - VS Code settings
.cursor/                - Cursor IDE config
  └── rules/

.claude/                - Claude AI config
  ├── agents/
  ├── commands/
  ├── dev/
  ├── hooks/
  ├── skills/
  └── tdd-guard/

.gemini/                - Gemini config
  └── skills/

.specify/               - Specify config
  ├── memory/
  ├── scripts/
  └── templates/

.taskmaster/            - Task management
  ├── docs/
  ├── reports/
  ├── tasks/
  └── templates/

.zencoder/              - Zencoder config
  └── rules/

.zenflow/               - Zenflow config
  └── workflows/

.opencode/              - OpenCode config
  ├── command/
  ├── node_modules/
  └── plugins/

.worktrees/             - Git worktrees (3 branches)
  ├── tech-debt-exec/
  ├── txn-cleaner/
  └── unify-trading-paths/

.amazonq/               - Amazon Q config
  └── prompts/

.archive/               - Archive storage
  ├── old_code/
  ├── old_docs/
  └── sensitive-backups/

.migration/             - Migration scripts
.mypy_cache/            - MyPy cache
.pytest_cache/          - Pytest cache
.ruff_cache/            - Ruff cache
.omc/                   - OMC config
.playwright-mcp/        - Playwright MCP
__pycache__/            - Python cache
```

---

## 3. FILE TYPE DISTRIBUTION

| Extension | Count | Purpose |
|-----------|-------|---------|
| `.js` | 92,523 | JavaScript source |
| `.ts` | 55,465 | TypeScript source |
| `.json` | 35,415 | Configuration/data |
| `.map` | 28,543 | Source maps |
| `.md` | 17,827 | Documentation |
| `.cjs` | 10,785 | CommonJS modules |
| `.py` | 10,072 | Python source |
| `.cts` | 9,396 | CommonJS TypeScript |
| `.html` | 7,476 | HTML templates |
| `.mjs` | 3,822 | ES modules |
| `.pyc` | 3,550 | Compiled Python |
| `.svg` | 2,558 | Vector graphics |
| `.tsx` | 1,668 | React TypeScript |
| `.vue` | 1,661 | Vue components |
| `.sh` | 924 | Shell scripts |
| `.txt` | 815 | Text files |
| `.yml` | 781 | YAML config |
| `.yaml` | 332 | YAML config |
| `.css` | 350 | Stylesheets |
| `.scss` | 282 | SCSS stylesheets |
| `.sql` | 136 | SQL queries |
| `.proto` | 8 | Protocol buffers |
| `.wasm` | 48 | WebAssembly |

---

## 4. DISK USAGE BREAKDOWN

| Directory | Size | Notes |
|-----------|------|-------|
| `logs/` | 236GB | ⚠️ CRITICAL - Needs cleanup |
| `web/` | 1.4GB | Frontend + backend |
| `bak/` | 554MB | Old backups |
| `scripts/` | 454MB | Development scripts |
| `docs/` | 241MB | Documentation |
| `node_modules/` | 151MB | Dependencies |
| `ts-quality-guard/` | 120MB | TypeScript tooling |
| `reports/` | 115MB | Test reports |
| `services/` | 114MB | Microservices |
| `htmlcov/` | 90MB | Coverage reports |
| `monitoring-stack/` | 73MB | Monitoring infra |
| `data/` | 43M | Data storage |
| `tests/` | 28M | Test suite |
| `src/` | 25M | Source code |
| `config/` | 17M | Configuration |

---

## 5. STRUCTURAL ISSUES & ANOMALIES

### Critical Issues
1. **Massive logs/ directory (236GB)** - Needs immediate cleanup/archival
2. **Deep nesting (17 levels)** - In worktrees/grafana plugins (acceptable for node_modules)
3. **Duplicate node_modules** - Multiple copies across worktrees and services

### Organizational Issues
1. **Scattered backup directories** - `bak/`, `backups/`, `.archive/`, `archived/`
2. **Multiple test directories** - `tests/`, `testing/`, `test-reports/`, `test_reports/`, `playwright-tests/`
3. **Redundant documentation** - `docs/` mirrors many top-level directories
4. **Orphaned directories** - `buger/`, `calcu/`, `04-测试/` (unclear purpose)
5. **Worktree proliferation** - 3 git worktrees with full copies of dependencies

### Naming Inconsistencies
- `test_reports/` vs `test-reports/` (both exist)
- `monitoring_data/` vs `monitoring_reports/` vs `monitoring/`
- `archived/` vs `archive/` vs `.archive/`
- `deployment/` vs `deployments/`

---

## 6. RECOMMENDED ORGANIZATION STRATEGY

### Immediate Actions
1. **Archive logs/** - Move to external storage, keep only recent 7 days
2. **Consolidate backups** - Merge `bak/`, `backups/`, `.archive/` into single `backups/` with date-based structure
3. **Clean worktrees** - Remove unused worktrees or consolidate node_modules

### Medium-term Refactoring
1. **Standardize naming** - Use consistent separators (hyphens for directories)
2. **Consolidate test directories** - Merge into single `tests/` with clear subdirectories
3. **Centralize documentation** - Keep `docs/` as single source of truth
4. **Remove orphaned directories** - Clarify purpose of `buger/`, `calcu/`, etc.

### Long-term Structure
```
mystocks/
├── src/                    # Source code
├── tests/                  # All tests
├── docs/                   # Documentation
├── config/                 # Configuration
├── scripts/                # Utility scripts
├── services/               # Microservices
├── web/                    # Web application
├── infrastructure/         # Docker, K8s, monitoring
├── backups/                # Archived data (date-based)
├── reports/                # Generated reports
└── tools/                  # Development tools
```

---

## 7. STATISTICS SUMMARY

- **Total Directories**: 95+ top-level + hundreds nested
- **Total Files**: 300,000+ (mostly in node_modules)
- **Largest Single Directory**: `logs/` (236GB)
- **Maximum Nesting Depth**: 17 levels
- **Primary Languages**: JavaScript/TypeScript (147,988 files), Python (10,072 files)
- **Configuration Files**: 50+ at root level
- **Git Worktrees**: 3 active branches
- **Node Modules Copies**: 4+ (main, web/frontend, ts-quality-guard, worktrees)

