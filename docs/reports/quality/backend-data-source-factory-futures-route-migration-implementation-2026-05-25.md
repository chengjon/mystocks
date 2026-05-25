# Backend DataSourceFactory Futures Route Migration Implementation - 2026-05-25

Workline: G2.78 path-limited implementation

Current HEAD before commit: `5169da563b883fe0d883b25a09ed0d599952df0d`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This implementation follows G2.77 authorization. It only changes
`web/backend/app/api/data/futures.py`,
`web/backend/tests/test_health_route_conflicts.py`, this implementation report,
the generated evidence artifact, the steward tree, and the mainline task-card.
It does not change route paths, response models, response shapes, OpenAPI
exposure policy, frontend code, PM2/runtime state, OpenSpec tasks, issue labels,
or the `get_data_source_factory()` compatibility getter.

## Status

Ready for review.

Parent authorization: G2.77, PR `#229`, merged at
`5169da563b883fe0d883b25a09ed0d599952df0d`.

## Pre-Edit GitNexus

Known accepted risk from G2.77 was restated before editing:

| Target | Result |
| --- | --- |
| `get_futures_index_daily` context | no incoming callers; outgoing call to `get_data_source_factory` |
| `get_futures_index_realtime` context | no incoming callers; outgoing call to `get_data_source_factory` |
| `web/backend/app/api/data/futures.py` file-level upstream impact | CRITICAL, impactedCount 151, direct 31, processes affected 0 |
| `get_data_source_factory_dependency` impact | not found in current GitNexus index |

The provider dependency symbol is present in code:

- `web/backend/app/services/data_source_factory/data_source_factory.py:315`
- `web/backend/app/services/data_source_factory/__init__.py:13`

No new HIGH/CRITICAL risk outside the accepted `futures.py` file-level import
fan-out was identified before editing.

## TDD

RED:

- Added `test_futures_routes_use_data_source_factory_dependency`.
- Focused test failed as expected with `KeyError: 'factory'`.

GREEN:

- Added `DataSourceFactory` and `get_data_source_factory_dependency` import in
  `futures.py`.
- Added `factory: DataSourceFactory = Depends(get_data_source_factory_dependency)`
  to both futures route handlers.
- Removed both function-local `get_data_source_factory` imports and direct awaits.
- Focused test passed: 1 passed.

## Verification

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_futures_routes_use_data_source_factory_dependency -q --no-cov --tb=short` before implementation | failed with `KeyError: 'factory'` |
| Same focused test after implementation | 1 passed |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | 120 passed |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | 4 passed |
| `ruff check web/backend/app/api/data/futures.py web/backend/tests/test_health_route_conflicts.py` | passed |
| `black --check web/backend/app/api/data/futures.py web/backend/tests/test_health_route_conflicts.py` | passed |
| OpenAPI smoke with root `.env` loaded | 548 routes, 500 paths, 536 operation IDs, duplicate operation IDs 0, duplicate operation ID warnings 0 |
| Staged GitNexus for code/test batch | LOW, changed files 2, changed symbols 0, affected processes 0 |

Route/API direct factory refs:

| Metric | Before | After |
| --- | ---: | ---: |
| Total direct route/API `get_data_source_factory()` refs | 2 | 0 |
| `web/backend/app/api/data/futures.py` direct refs | 2 | 0 |

## Result

The final route/API direct `get_data_source_factory()` calls have been removed.
All active route/API consumers now use `get_data_source_factory_dependency` for
DataSourceFactory access.

The compatibility getter itself remains in place. Its retirement or continued
retention must be handled by a separate decision packet.

## Next Gate

Human review / PR merge decision for this implementation. If accepted, create a
G2.78 closeout/current-head refresh before any compatibility getter retirement
or retained-shim decision.
