# Backend DataSourceFactory Financial Route Migration Implementation - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Workline: G2.63 financial route DataSourceFactory migration implementation

Base branch: `wip/root-dirty-20260403`

Base HEAD: `7c1b8fce44b3931c44ac5398e12f5715a28833e3`

## Scope Boundary

This implementation follows the G2.62 authorization packet.

Modified source/test paths:

- `web/backend/app/api/data/financial.py`
- `web/backend/tests/test_health_route_conflicts.py`

This implementation does not change route paths, query parameters, response
shape, OpenAPI exposure, generated clients, frontend code, PM2/runtime process
state, OpenSpec files, issue labels, or any remaining DataSourceFactory route
consumer.

## GitNexus Evidence

Before source edits, GitNexus was refreshed in a non-linked checkout:

- Repo: `g2-63-gitnexus-index-checkout`
- HEAD: `7c1b8fce4`
- `gitnexus analyze` exit: `0`
- Nodes: `62644`
- Edges: `145819`
- Flows: `300`

Pre-edit impact:

| Target | Risk | Impacted count | Notes |
|---|---|---:|---|
| `web/backend/app/api/data/financial.py` | LOW | 2 | direct importer `data/__init__.py`; secondary regression test import |
| `get_data_source_factory_dependency` | LOW | 0 | provider dependency symbol |

`get_financial_data` is name-ambiguous in GitNexus, so the file-level impact is
the authoritative pre-edit blast-radius check for this batch.

## TDD

RED:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short
```

Result: `1 failed, 112 passed`.

Expected failure: `get_financial_data` did not expose a `factory` dependency
parameter.

GREEN:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short
```

Result: `113 passed`.

## Implementation

Implemented changes:

- Imported `DataSourceFactory` and `get_data_source_factory_dependency` in
  `web/backend/app/api/data/financial.py`.
- Added `factory: DataSourceFactory =
  Depends(get_data_source_factory_dependency)` to `get_financial_data`.
- Removed the inline `await get_data_source_factory()` call.
- Preserved `get_data_source_factory()` and `_global_factory`.

## Route Guard

Post-change static scan:

- API files scanned: `219`
- Total direct `get_data_source_factory()` API calls: `14`
- `financial.py` direct calls: `0`
- `get_data_source_factory_dependency` API refs: `5`
- `financial.py` dependency refs: `2`

Remaining direct-call files:

| File | Calls |
|---|---:|
| `web/backend/app/api/data/futures.py` | 2 |
| `web/backend/app/api/data/kline.py` | 2 |
| `web/backend/app/api/data/lhb.py` | 2 |
| `web/backend/app/api/data/margin.py` | 3 |
| `web/backend/app/api/data/market.py` | 1 |
| `web/backend/app/api/data/stocks.py` | 2 |
| `web/backend/app/api/market/market_data_request.py` | 2 |

## Verification

Executed after implementation:

| Check | Result |
|---|---|
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `113 passed` |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | `4 passed` |
| `ruff check` on touched files | passed |
| `black --check` on touched files | `2 files would be left unchanged` |
| app import / OpenAPI smoke with non-secret test env | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |

The app/OpenAPI smoke still reports `warning_count=121`, including the existing
local GPU fallback warning for the NumPy/Numba mismatch.

## Decision

G2.63 completes the financial route DataSourceFactory consumer migration:

- `financial.py`: `1` direct call -> `0`;
- API total: `15` direct calls -> `14`;
- route/OpenAPI contract unchanged.

## Next Gate

Human review of this implementation PR.

If accepted and merged, run a separate G2.63 closeout/current-head refresh
before selecting another DataSourceFactory route consumer packet.
