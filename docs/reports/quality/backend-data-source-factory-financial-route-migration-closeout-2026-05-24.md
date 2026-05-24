# Backend DataSourceFactory Financial Route Migration Closeout - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Workline: G2.63 closeout / current-head refresh

Base branch: `wip/root-dirty-20260403`

Current HEAD: `229cd7fe0a21cb9bf7b9079d07e9551baaf0a4c7`

## Scope Boundary

This closeout records the merged G2.63 result. It does not change backend
source code, tests, route paths, response contracts, OpenAPI exposure, generated
clients, OpenSpec files, issue labels, runtime process state, or PM2 state.

## Merge Evidence

PR `#208` was merged at
`229cd7fe0a21cb9bf7b9079d07e9551baaf0a4c7`.

Merged implementation summary:

- Migrated `web/backend/app/api/data/financial.py` route handler
  `get_financial_data` to `Depends(get_data_source_factory_dependency)`.
- Removed the inline `await get_data_source_factory()` call from
  `financial.py`.
- Preserved `get_data_source_factory()` and `_global_factory` compatibility
  surfaces.
- Kept route paths, response models, OpenAPI exposure, and response shape
  unchanged.

## Current-Head Route Guard

Post-merge static scan reports:

- API files scanned: `219`
- Direct `get_data_source_factory()` API calls: `14`
- `get_data_source_factory_dependency` API refs: `5`
- `financial.py` direct refs: `0`

Remaining direct-call files:

| File | Calls |
|---|---:|
| `web/backend/app/api/data/futures.py` | 2 |
| `web/backend/app/api/data/kline.py` | 2 |
| `web/backend/app/api/data/lhb.py` | 2 |
| `web/backend/app/api/data/market.py` | 1 |
| `web/backend/app/api/data/margin.py` | 3 |
| `web/backend/app/api/data/stocks.py` | 2 |
| `web/backend/app/api/market/market_data_request.py` | 2 |

The remaining `14` route/API consumers stay locked until a separate
authorization packet selects the next batch.

## Verification

Executed at current HEAD:

| Check | Result |
|---|---|
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `113 passed` |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | `4 passed` |
| `ruff check` on touched source/test files | passed |
| `black --check` on touched source/test files | `3 files would be left unchanged` |
| app import / OpenAPI smoke with non-secret test env | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |

The app/OpenAPI smoke still reports `warning_count=121`, including the existing
local GPU fallback warning for the NumPy/Numba mismatch.

## GitNexus Refresh

GitNexus was refreshed from a non-linked checkout:

- Repo: `g2-63-closeout-gitnexus-index-checkout`
- HEAD: `229cd7fe0`
- `.git` kind: `directory`
- `gitnexus analyze` exit: `0`
- Nodes: `62659`
- Edges: `145822`
- Flows: `300`

Current-head upstream impact:

| Target | Risk | Impacted count | Direct | Processes affected |
|---|---|---:|---:|---:|
| `web/backend/app/api/data/financial.py` | LOW | 1 | 1 | 0 |
| `get_data_source_factory_dependency` | LOW | 0 | 0 | 0 |

## Decision

G2.63 is closed as merged and stable at current HEAD.

The second DataSourceFactory route consumer migration is now complete:

- `financial.py`: `1` direct call -> `0`;
- API total: `15` direct calls -> `14`;
- route/OpenAPI contract unchanged.

## Next Gate

Prepare a separate G2.64 authorization-only packet before any further route
edits.

Recommended G2.64 candidate:

- `web/backend/app/api/data/market.py`

Reason: `market.py` is the remaining one-call route consumer, but it has a
broader four-route file surface than `financial.py`; it needs its own TDD,
rollback, and guard scope before source edits.
