# Backend DataSourceFactory LHB Route Migration Implementation - 2026-05-25

Workline: G2.69 implementation packet

Current HEAD: `a76f6dbdc700738e4d07977ae3808f75b2103fe3`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This document records one path-limited source implementation and
its evidence. It does not authorize route path changes, OpenAPI exposure
changes, response shape changes, frontend edits, PM2/runtime operations,
OpenSpec proposal publication, issue-label changes, or migration of any other
DataSourceFactory route consumer.

## Status

Ready for review.

This is the G2.69 implementation packet authorized by the G2.68 LHB candidate
selection. It is path-limited to `web/backend/app/api/data/lhb.py`, one focused
route-conflict test, and governance evidence. It does not change route paths,
response contracts, OpenAPI exposure policy, frontend code, runtime/PM2 gates,
OpenSpec files, issue labels, or other DataSourceFactory consumers.

## Scope

Changed source/test files:

- `web/backend/app/api/data/lhb.py`
- `web/backend/tests/test_health_route_conflicts.py`

Governance artifacts:

- `.planning/codebase/generated/data-source-factory-lhb-route-migration-implementation-2026-05-25.json`
- `docs/reports/quality/backend-data-source-factory-lhb-route-migration-implementation-2026-05-25.md`
- `governance/mainline/task-cards/pr-217.yaml`
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`

## Pre-Edit Evidence

GitNexus impact before editing:

| Target | Risk | Direct impact | Processes affected |
| --- | --- | ---: | ---: |
| `web/backend/app/api/data/lhb.py` | LOW | 1 | 0 |
| `get_dragon_tiger_detail` | LOW | 0 | 0 |
| `get_dragon_tiger_institution_stats` | LOW | 0 | 0 |

Baseline verification:

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov` | 115 passed |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov` | 4 passed |
| `ruff check web/backend/app/api/data/lhb.py` | passed |
| `black --check web/backend/app/api/data/lhb.py` | would reformat |

The black finding was known from G2.68. Same-file normalization was explicitly
allowed for the future authorized `lhb.py` implementation branch.

## TDD Evidence

Red test:

```text
pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_lhb_routes_use_data_source_factory_dependency -q --no-cov --tb=short
```

Result: failed as expected with `KeyError: 'factory'`.

Green test:

```text
pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_lhb_routes_use_data_source_factory_dependency -q --no-cov --tb=short
```

Result: `1 passed`.

## Implementation

Migrated route handlers:

- `get_dragon_tiger_detail`
- `get_dragon_tiger_institution_stats`

Both handlers now receive:

```python
factory: DataSourceFactory = Depends(get_data_source_factory_dependency)
```

The route-local `from app.services.data_source_factory import get_data_source_factory`
imports and `await get_data_source_factory()` calls were removed from both
handlers. Compatibility surfaces remain intact:

- `get_data_source_factory()`
- `_global_factory`
- `get_data_source_factory_dependency`

## Verification

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov` | 116 passed |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov` | 4 passed |
| `ruff check web/backend/app/api/data/lhb.py web/backend/tests/test_health_route_conflicts.py` | passed |
| `black --check web/backend/app/api/data/lhb.py web/backend/tests/test_health_route_conflicts.py` | passed |
| OpenAPI smoke with `PYTHONPATH=web/backend` and root `.env` loaded | 548 routes, 500 paths, 536 operation IDs, duplicate operation IDs 0 |

Route/API direct factory refs:

| Metric | Before | After |
| --- | ---: | ---: |
| Total direct route/API `get_data_source_factory()` refs | 10 | 8 |
| `web/backend/app/api/data/lhb.py` direct refs | 2 | 0 |

Remaining data route consumers stay locked for future authorization:

- `web/backend/app/api/data/kline.py`
- `web/backend/app/api/data/futures.py`
- `web/backend/app/api/data/stocks.py`

## Boundary

This packet does not authorize:

- route path, response model, response shape, or OpenAPI exposure changes
- frontend edits
- runtime/PM2 stateful gates
- OpenSpec changes
- issue label changes
- `get_data_source_factory()` or `_global_factory` deletion
- migration of `kline.py`, `futures.py`, `stocks.py`, or any market package consumer

## Next Gate

Human review / PR merge decision for G2.69. After merge, create a separate
closeout/current-head refresh and then a new candidate authorization packet
before any additional DataSourceFactory route migration.
