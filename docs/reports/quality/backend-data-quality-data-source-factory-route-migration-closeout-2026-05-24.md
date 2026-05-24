# Backend Data Quality DataSourceFactory Route Migration Closeout - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Workline: G2.61c closeout / current-head refresh

Base branch: `wip/root-dirty-20260403`

Current HEAD: `b9d0bb31a72d362dc67a38dcd719578de56af739`

## Scope Boundary

This closeout records the merged G2.61c result. It does not change backend
source code, tests, route paths, response contracts, OpenAPI exposure, generated
clients, OpenSpec files, issue labels, runtime process state, or PM2 state.

## Merge Evidence

PR `#205` was merged at
`b9d0bb31a72d362dc67a38dcd719578de56af739`.

Merged implementation summary:

- Re-exported `get_data_source_factory_dependency` from
  `app.services.data_source_factory`.
- Migrated `get_sources_health` and `get_system_status_overview` to
  `Depends(get_data_source_factory_dependency)`.
- Removed both `data_quality.py` direct `await get_data_source_factory()` calls.
- Preserved `get_data_source_factory()` and `_global_factory`.
- Kept route paths, response models, OpenAPI exposure, and response shape
  unchanged.

## Current-Head Route Guard

Post-merge static scan reports:

- API files scanned: `219`
- Direct `get_data_source_factory()` API calls: `15`
- `get_data_source_factory_dependency` API refs: `3`
- `data_quality.py` direct refs: `0`
- `data_quality.py` dependency refs: `3`
- Direct handler call refs to the migrated functions: `0`

Remaining direct-call files:

| File | Calls |
|---|---:|
| `web/backend/app/api/data/financial.py` | 1 |
| `web/backend/app/api/data/futures.py` | 2 |
| `web/backend/app/api/data/kline.py` | 2 |
| `web/backend/app/api/data/lhb.py` | 2 |
| `web/backend/app/api/data/margin.py` | 3 |
| `web/backend/app/api/data/market.py` | 1 |
| `web/backend/app/api/data/stocks.py` | 2 |
| `web/backend/app/api/market/market_data_request.py` | 2 |

The remaining `15` route/API consumers stay locked until a separate
authorization packet selects the next batch.

## Verification

Executed at current HEAD:

| Check | Result |
|---|---|
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_mock_configuration.py -q --no-cov --tb=short` | `4 passed` |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | `4 passed` |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory.py -q --no-cov --tb=short` | `38 passed` |
| `ruff check` + `black --check` on touched source/test files | passed; `4 files would be left unchanged` |
| app import / OpenAPI smoke with non-secret test env | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |

The app/OpenAPI smoke still reports `warning_count=121`, including the existing
local GPU fallback warning for the NumPy/Numba mismatch.

## GitNexus Refresh

GitNexus was refreshed from a non-linked checkout:

- Repo: `g2-61c-closeout-gitnexus-index-checkout`
- HEAD: `b9d0bb31a`
- `.git` kind: `directory`
- `gitnexus analyze` exit: `0`
- Nodes: `62656`
- Edges: `145815`
- Flows: `300`

Current-head upstream impact:

| Symbol | Risk | Impacted count |
|---|---|---:|
| `get_sources_health` | LOW | 0 |
| `get_system_status_overview` | LOW | 0 |
| `get_data_source_factory_dependency` | LOW | 0 |

## Decision

G2.61c is closed as merged and stable at current HEAD.

The first DataSourceFactory route consumer migration is now complete:

- `data_quality.py`: `2` direct calls -> `0`;
- API total: `17` direct calls -> `15`;
- route/OpenAPI contract unchanged.

## Next Gate

Prepare a separate G2.62 authorization-only packet before any further route
edits.

Recommended G2.62 candidates are the remaining one-call route consumers:

- `web/backend/app/api/data/financial.py`
- `web/backend/app/api/data/market.py`

The G2.62 packet should choose one candidate, define TDD and rollback scope, and
keep all other remaining direct consumers locked.
