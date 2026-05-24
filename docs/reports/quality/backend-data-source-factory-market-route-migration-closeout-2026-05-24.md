# Backend DataSourceFactory Market Route Migration Closeout - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Workline: G2.65 closeout / current-head refresh

Base branch: `wip/root-dirty-20260403`

Current HEAD: `277fdd412b2bbf68b64c5186fee943dc50080480`

## Scope Boundary

This closeout records the merged G2.65 result. It does not change backend
source code, tests, route paths, response contracts, OpenAPI exposure, generated
clients, OpenSpec files, issue labels, runtime process state, or PM2 state.

## Merge Evidence

PR `#211` was merged at
`277fdd412b2bbf68b64c5186fee943dc50080480`.

Merged implementation summary:

- Migrated `web/backend/app/api/data/market.py` route handler
  `get_market_overview` to `Depends(get_data_source_factory_dependency)`.
- Removed the inline `await get_data_source_factory()` call from `market.py`.
- Resolved same-file `market.py` E701/black debt authorized by G2.64.
- Preserved `get_data_source_factory()` and `_global_factory` compatibility
  surfaces.
- Kept route paths, response models, OpenAPI exposure, and response shape
  unchanged.

## Current-Head Route Guard

Post-merge static scan reports:

- API files scanned: `219`
- Direct `get_data_source_factory()` API calls: `13`
- `get_data_source_factory_dependency` API refs: `7`
- `market.py` direct refs: `0`
- `market.py` dependency refs: `2`

Remaining direct-call files:

| File | Calls |
|---|---:|
| `web/backend/app/api/data/futures.py` | 2 |
| `web/backend/app/api/data/kline.py` | 2 |
| `web/backend/app/api/data/lhb.py` | 2 |
| `web/backend/app/api/data/margin.py` | 3 |
| `web/backend/app/api/data/stocks.py` | 2 |
| `web/backend/app/api/market/market_data_request.py` | 2 |

The remaining `13` route/API consumers stay locked until a separate
authorization packet selects the next batch.

## Verification

Executed at current HEAD:

| Check | Result |
|---|---|
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `114 passed` |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | `4 passed` |
| `ruff check` on touched source/test files | passed |
| `black --check` on touched source/test files | `3 files would be left unchanged` |
| app import / OpenAPI smoke with non-secret test env | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |

The app/OpenAPI smoke still reports `warning_count=121`, including the existing
local GPU fallback warning for the NumPy/Numba mismatch.

## GitNexus Refresh

GitNexus was refreshed from a non-linked checkout:

- Repo: `g2-65-closeout-gitnexus-index-checkout`
- HEAD: `277fdd412`
- `.git` kind: `directory`
- `gitnexus analyze` exit: `0`
- Nodes: `62667`
- Edges: `145820`
- Flows: `300`

Current-head upstream impact:

| Target | Risk | Impacted count | Direct | Processes affected |
|---|---|---:|---:|---:|
| `web/backend/app/api/data/market.py` | LOW | 1 | 1 | 0 |
| `get_data_source_factory_dependency` | LOW | 0 | 0 | 0 |

## Decision

G2.65 is closed as merged and stable at current HEAD.

The third DataSourceFactory route consumer migration is now complete:

- `market.py`: `1` direct call -> `0`;
- API total: `14` direct calls -> `13`;
- route/OpenAPI contract unchanged.

## Next Gate

Prepare a separate G2.66 authorization-only packet before any further route
edits.

Recommended G2.66 candidate selection should compare the remaining direct-call
files instead of editing one directly:

- `web/backend/app/api/data/kline.py`
- `web/backend/app/api/data/futures.py`
- `web/backend/app/api/data/lhb.py`
- `web/backend/app/api/data/stocks.py`
- `web/backend/app/api/data/margin.py`
- `web/backend/app/api/market/market_data_request.py`
