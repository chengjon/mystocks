# Backend Data Quality DataSourceFactory Route Migration Implementation - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Workline: G2.61c data-quality DataSourceFactory route migration implementation

Base branch: `wip/root-dirty-20260403`

Base HEAD: `52a2aaa57150db834bcef3a526a4b78e37ac438a`

## Scope Boundary

This implementation follows the G2.61b authorization packet.

Modified source/test paths:

- `web/backend/app/services/data_source_factory/__init__.py`
- `web/backend/app/api/data_quality.py`
- `web/backend/tests/test_data_quality_mock_configuration.py`

Modified governance paths:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/data-quality-data-source-factory-route-migration-implementation-2026-05-24.json`
- `docs/reports/quality/backend-data-quality-data-source-factory-route-migration-implementation-2026-05-24.md`
- `governance/mainline/task-cards/pr-205.yaml`

This implementation does not change route paths, response models, response
shape, OpenAPI exposure, generated clients, frontend code, PM2/runtime process
state, OpenSpec files, issue labels, or the remaining DataSourceFactory route
consumers.

## Authorization

G2.61b was merged by PR `#204` at
`52a2aaa57150db834bcef3a526a4b78e37ac438a`.

It authorized only a path-limited implementation for:

- package export of `get_data_source_factory_dependency`;
- the two `web/backend/app/api/data_quality.py` call sites;
- focused tests and implementation evidence.

## GitNexus Evidence

Before source edits, GitNexus was refreshed in a non-linked checkout because the
root `mystocks_spec` index still pointed at an older dirty HEAD.

Refresh details:

- Repo: `g2-61c-gitnexus-index-checkout`
- HEAD: `52a2aaa57`
- `.git` kind: `directory`
- `gitnexus analyze` exit: `0`
- Nodes: `62644`
- Edges: `145830`
- Flows: `300`

Pre-edit upstream impact:

| Symbol | Risk | Impacted count |
|---|---|---:|
| `get_sources_health` | LOW | 0 |
| `get_system_status_overview` | LOW | 0 |
| `get_data_source_factory_dependency` | LOW | 0 |
| `install_data_source_factory` | LOW | 0 |

## TDD

RED:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_mock_configuration.py -q --no-cov --tb=short
```

Result: `2 failed, 2 passed`.

Expected failures:

- package `app.services.data_source_factory` did not export
  `get_data_source_factory_dependency`;
- `get_sources_health` and `get_system_status_overview` did not expose a
  `factory` dependency parameter.

GREEN:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_mock_configuration.py -q --no-cov --tb=short
```

Result: `4 passed`.

## Implementation

Implemented changes:

- Re-exported `get_data_source_factory_dependency` from
  `web/backend/app/services/data_source_factory/__init__.py`.
- Added `Depends(get_data_source_factory_dependency)` to:
  - `get_sources_health`
  - `get_system_status_overview`
- Removed both direct `await get_data_source_factory()` calls from
  `web/backend/app/api/data_quality.py`.
- Preserved `get_data_source_factory()` and `_global_factory`.

## Route Guard

Post-change static scan:

- API files scanned: `219`
- Total direct `get_data_source_factory()` API calls: `15`
- `data_quality.py` direct calls: `0`
- `get_data_source_factory_dependency` API refs: `3`
- Direct handler call references to `get_sources_health(...)` or
  `get_system_status_overview(...)`: `0`

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

The remaining `15` route/API consumers stay locked for later authorization
packets.

## Verification

Executed after implementation:

| Check | Result |
|---|---|
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_mock_configuration.py -q --no-cov --tb=short` | `4 passed` |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | `4 passed` |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory.py -q --no-cov --tb=short` | `38 passed` |
| `ruff check` on touched source/test files | passed |
| `black --check` on touched source/test files | `4 files would be left unchanged` |
| app import / OpenAPI smoke with non-secret test env | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |

The app/OpenAPI smoke still reports `warning_count=121`, including the existing
GPU fallback warning for the local NumPy/Numba mismatch. No duplicate operation
ID warning was emitted.

The root `mystocks_spec` staged detect_changes run still reported `HIGH`
because it used the older project index and over-approximated the modified route
file. The non-linked current-head GitNexus refresh used for the actual edit
authorization remained LOW/0 for the edited route symbols.

## Non-Goals

This implementation does not authorize:

- migrating the remaining `15` DataSourceFactory route/API direct calls;
- deleting `get_data_source_factory()` or `_global_factory`;
- changing data-source factory construction semantics;
- changing route paths, response models, response shape, or OpenAPI exposure;
- touching frontend, generated clients, PM2/runtime process state, OpenSpec
  files, issue labels, docs/API examples, or unrelated service seams.

## Decision

G2.61c completes the first DataSourceFactory route consumer migration:

- `data_quality.py`: `2` direct calls -> `0`;
- API total: `17` direct calls -> `15`;
- route/OpenAPI contract unchanged.

## Next Gate

Human review of this implementation PR.

If accepted and merged, run a separate G2.61c closeout/current-head refresh
before selecting the next DataSourceFactory route consumer packet.
