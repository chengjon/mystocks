# Technical Debt & Concerns

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 当前执行口径请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码实现与主线治理文档使用。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码或主线文档冲突，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、当前代码与主线治理文档为准。


**Last mapped**: 2026-04-05
**Based on**: Actual codebase exploration (not document summaries)

---

## Critical Issues

### 1. Adapter Layer Fully Duplicated (P0)

`src/interfaces/adapters/` is a complete copy of `src/adapters/` but missing all import statements. This single issue causes **500+ of the 1,173 F821 ruff errors**.

**Evidence**:
- `src/interfaces/adapters/akshare/misc_data/get_ths_industry_names.py` — 635 lines, identical to `src/adapters/akshare/misc_data/get_ths_industry_names.py` — 635 lines
- Same pattern for `get_futures_index_daily.py` (54 errors each), `financial/stock_daily.py` (50 errors each), `financial/realtime_data.py` (45 errors each)
- Interface files lack `import pandas`, `import akshare`, `import logging`, etc.

**Root cause**: Original design intended interface/impl separation, but interface layer became a full copy without imports.

**Fix**: Decide if `src/interfaces/` should be pure Protocol/ABC (only signatures) or be deleted entirely.

### 2. Frontend Case-Conflict Directories (P0)

Case-sensitive directories that will merge on macOS but are separate on Linux (deployment target):

| Upper case | Lower case |
|-----------|-----------|
| `components/Charts/` | `components/charts/` |
| `components/Common/` | `components/common/` |
| `components/Market/` | `components/market/` |

**Risk**: Module resolution failures on Linux deployment.

**Fix**: Merge into lowercase directories (Vue community convention).

---

## High-Priority Issues

### 3. Three Overlapping Data Access Layers (P1)

Four directories doing similar work:
- `src/data_access/` — 14 files (TDengine, PostgreSQL, factory, interfaces)
- `src/data_access_pkg/` — 5 files (duplicate `postgresql_access.py`, `tdengine_access.py`)
- `src/database/` — 11 files (contains both `database_service.py` shim and `database_service_new.py`)
- `src/db_manager/` — only `__init__.py` (empty shell)

Plus shim files: `src/data_access.py` uses bare `from data_access_pkg import *` (F403 violation).

### 4. Routes in Wrong Layer (P1)

Route definitions spread across three locations:
- `src/routes/` — 19 files (with mock-era `check_use_mock_data.py` in each sub-route)
- `src/api/` — 5 files
- `web/backend/app/api/` — 205 files (the actual FastAPI routes)

`src/routes/` and `src/api/` appear to be dead code from before the web/backend/ consolidation.

### 5. Test Quality vs Quantity Mismatch (P1)

908 test files but quality issues:
- `tests/test_api_endpoints.py` — manual script with `print()`, no `assert`, no pytest
- `tests/contract/` — framework code (`contract_engine.py`, `report_generator.py`) mixed with tests
- Actual coverage last measured at **0.16%** (2026-01-03)
- File count inflated by non-test files and infrastructure code

---

## Medium-Priority Issues

### 6. Frontend Structural Mess (P2)

- **8 main entry files**: `main.js` (actual) + 7 variants (debug, enhanced, minimal, original, simplified, standard, test)
- **artdeco-pages monolith**: 143 files in single directory, includes `.backup` files and empty subdirs
- **Dead code in source tree**: `views/converted.archive/` (9 old pages), `views/demo/` (33 demo files)
- **Misplaced composables**: `views/composables/` (17 files) should be in `src/composables/`

### 7. Backend API Directory Explosion (P2)

- 205 Python files in `web/backend/app/api/`
- Top files: `monitoring.py` (1,270 lines), `strategy_management/get_monitoring_db.py` (1,242 lines)
- `main.py` (885 lines) mixes CSRF management, Socket.IO setup with app configuration
- Route registration requires manual updates to both `router_modules` dict and `VERSION_MAPPING`

### 8. Root-Level Shim Chain (P2)

```
core.py         → from core import *         # bare name, no src. prefix
src/core.py     → from core import *         # circular risk
data_access.py  → from data_access_pkg import *  # wildcard
```

Potential circular imports depending on `sys.path` ordering.

### 9. Naming & Split Quality (P2)

- `src/calcu/` — truncated, should be `calculator` or merged
- `part1.py/part2.py/part3.py` — mechanical splits in `storage/database/`, `gpu/acceleration/` (no semantic meaning)
- `database_service_new.py` — "new" suffix = incomplete migration
- `src/database_optimization/` overlaps `src/database/`

---

## Low-Priority Issues

### 10. Mock Infrastructure in Source Tree

66 mock files (55 in `src/`, 11 in `web/backend/`) coexist with production code. Current mode is REAL (`USE_MOCK_DATA=False`). Mocks are reasonable for dev/test but need periodic interface consistency checks.

### 11. Store Domain Confusion

`web/frontend/src/stores/`:
- `market.ts` vs `marketData.ts` — unclear boundary
- `trading.ts` vs `tradingData.ts` — same issue
- `dataAdapters.ts` — data transformation logic, not state management
- `baseStore.ts.bak` — backup file in source

### 12. Ruff Issues Breakdown

Total ~1,456 issues across `src/` and `web/backend/app/`:

| Rule | Count | Fixable |
|------|-------|---------|
| F821 undefined-name | 1,173 | Root cause: duplicate adapter layer (#1) |
| W293 blank-line-whitespace | 95 | Auto-fixable |
| F841 unused-variable | 78 | Auto-fixable |
| W291 trailing-whitespace | 28 | Auto-fixable |
| F401 unused-import | 21 | Auto-fixable |
| F811 redefined-while-unused | 17 | Needs review |
| E701 multiple-statements | 15 | Auto-fixable |
| E722 bare-except | 13 | Manual fix |
| Others | 16 | Mixed |

~46% are auto-fixable via `ruff check --fix`.

---

## Metrics Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Ruff F821 | 1,173 | 0 | Fix duplicate adapters → eliminates ~500+ |
| Ruff total | ~1,456 | <500 | Fix adapters + auto-fix → ~200 |
| Test files | 908 | Quality > quantity | Verify with pytest --cov |
| TS tech debt | 0 | 0 | Clear |
| Files >800 lines | 0 | 0 | Clear |
| TODO/FIXME files | 63 | <50 | Improving |
| Mock files | 66 | As needed | OK, check consistency |
| Case conflicts | 3 pairs | 0 | Deploy risk on Linux |
