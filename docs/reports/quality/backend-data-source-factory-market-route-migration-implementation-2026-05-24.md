# Backend DataSourceFactory Market Route Migration Implementation - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Workline: G2.65 path-limited implementation

Base branch: `wip/root-dirty-20260403`

Current HEAD before commit: `20a7b67f1898506586e7858840d0ae058461fe93`

## Scope Boundary

This implementation follows the G2.64 authorization packet. It changes only the
selected route file, the focused route-contract test, this evidence report, the
generated JSON artifact, the steward tree, and the mainline task card.

It does not change route paths, response contracts, OpenAPI exposure, generated
clients, OpenSpec files, issue labels, runtime process state, PM2 state,
frontend code, or any non-`market.py` DataSourceFactory route consumer.

## Implementation

Modified source:

- `web/backend/app/api/data/market.py`
- `web/backend/tests/test_health_route_conflicts.py`

Runtime change:

- `get_market_overview` now injects `DataSourceFactory` through
  `Depends(get_data_source_factory_dependency)`.
- The inline `from app.services.data_source_factory import get_data_source_factory`
  and `await get_data_source_factory()` call were removed from the handler.
- `get_data_source_factory()` and `_global_factory` compatibility surfaces remain
  intact.

Same-file style debt resolved inside the authorized `market.py` scope:

- line `123` previous `if cached_data: return cached_data`
- line `154` previous `if cached_data: return cached_data`
- line `179` previous `if cached_data: return cached_data`

Those lines were expanded so touched-file ruff and black gates pass. No broad
formatting cleanup outside `market.py` was performed.

## TDD Evidence

RED:

| Check | Result |
|---|---|
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_market_overview_route_uses_data_source_factory_dependency -q --no-cov --tb=short` | `1 failed`: `KeyError: 'factory'` |

GREEN:

| Check | Result |
|---|---|
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_market_overview_route_uses_data_source_factory_dependency -q --no-cov --tb=short` | `1 passed` |

## Route Guard

Post-implementation static scan reports:

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

Executed after implementation:

| Check | Result |
|---|---|
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `114 passed` |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | `4 passed` |
| `ruff check` on touched source/test files | passed |
| `black --check` on touched source/test files | `3 files would be left unchanged` |
| app import / OpenAPI smoke with non-secret test env | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |

The app/OpenAPI smoke still reports `warning_count=121`, including the existing
local GPU fallback warning for the NumPy/Numba mismatch.

## GitNexus Pre-Edit Evidence

GitNexus was refreshed from a non-linked checkout before source edits:

- Repo: `g2-65-gitnexus-index-checkout`
- HEAD: `20a7b67f1`
- `.git` kind: `directory`
- `gitnexus analyze` exit: `0`
- Nodes: `62665`
- Edges: `145822`
- Flows: `300`

Pre-edit upstream impact:

| Target | Risk | Impacted count | Direct | Processes affected |
|---|---|---:|---:|---:|
| `web/backend/app/api/data/market.py` | LOW | 1 | 1 | 0 |
| `get_data_source_factory_dependency` | LOW | 0 | 0 | 0 |

## Decision

G2.65 is ready for review as the `market.py` DataSourceFactory route consumer
migration.

This implementation completes the authorized migration:

- `market.py`: `1` direct call -> `0`
- API total: `14` direct calls -> `13`
- route/OpenAPI contract unchanged
- existing `market.py` same-file style debt cleared enough for touched-file gates

## Next Gate

Human review of this implementation PR.

If accepted and merged, run a separate G2.65 closeout/current-head refresh
before selecting another DataSourceFactory route consumer packet.
