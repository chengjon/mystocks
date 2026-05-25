# Backend DataSourceFactory Futures Route Migration Implementation Authorization - 2026-05-25

Workline: G2.77 implementation authorization

Current HEAD: `5fab3e8f6b0ebfb660f0cae1010cd59dfb30f039`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This packet authorizes a future path-limited implementation
branch only if reviewed and accepted. It does not itself edit backend source,
tests, route paths, OpenAPI exposure, response shapes, frontend code, PM2/runtime
state, OpenSpec changes, issue labels, or compatibility getter behavior.

## Status

Ready for review.

Parent packet: G2.76, PR `#228`, merged at
`5fab3e8f6b0ebfb660f0cae1010cd59dfb30f039`.

## Authorized Future Implementation

If this authorization is accepted, future G2.78 may edit only:

- `web/backend/app/api/data/futures.py`
- `web/backend/tests/test_health_route_conflicts.py`

The future implementation may also add its implementation report, generated
artifact, steward-tree update, and task-card.

Authorized implementation goal:

1. Add `test_futures_routes_use_data_source_factory_dependency`.
2. Prove the test fails before source edits because `factory` is absent.
3. Add `DataSourceFactory` and `get_data_source_factory_dependency` imports in
   `futures.py`.
4. Add `factory: DataSourceFactory = Depends(get_data_source_factory_dependency)`
   to `get_futures_index_daily` and `get_futures_index_realtime`.
5. Remove both function-local `get_data_source_factory` imports and direct awaits.
6. Normalize same-file `futures.py` black formatting if required by the
   implementation diff.

Expected result:

| Metric | Before G2.78 | After G2.78 |
| --- | ---: | ---: |
| Total direct route/API `get_data_source_factory()` refs | 2 | 0 |
| `web/backend/app/api/data/futures.py` direct refs | 2 | 0 |

## Locked Scope

G2.78 must not change:

- Route paths or HTTP methods.
- OpenAPI exposure policy or operation IDs except changes inherently caused by
  adding a dependency parameter that must remain non-request-visible.
- Response models, response body shape, examples, or error contract.
- Frontend consumers.
- Runtime/PM2 state.
- OpenSpec tasks or issue labels.
- `get_data_source_factory()` compatibility getter.
- Any route/API file other than `futures.py`.
- Formatting outside `futures.py`.

## Required Pre-Edit Gates

Before source edits, G2.78 must run and record:

- GitNexus context for `get_futures_index_daily`.
- GitNexus context for `get_futures_index_realtime`.
- GitNexus impact for `web/backend/app/api/data/futures.py`.
- GitNexus impact or context for `get_data_source_factory_dependency`.

Known accepted risk from G2.76:

| Signal | Value |
| --- | --- |
| File-level `futures.py` impact | HIGH, impactedCount 141, direct 27, processes affected 0 |
| Exact route-handler caller count | 0 |
| Route-handler outgoing calls | both call `get_data_source_factory` |
| Existing style debt | `black --check futures.py` would reformat |

If G2.78 sees a new HIGH/CRITICAL risk outside this known file-level
`futures.py` import fan-out, it must stop and return to review before editing.

## Required TDD And Verification

G2.78 must run:

- TDD red for `test_futures_routes_use_data_source_factory_dependency`.
- Focused TDD green for the same test.
- Full `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short`.
- `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short`.
- `ruff check web/backend/app/api/data/futures.py web/backend/tests/test_health_route_conflicts.py`.
- `black --check web/backend/app/api/data/futures.py web/backend/tests/test_health_route_conflicts.py`.
- OpenAPI smoke with route count, path count, operation ID count, and duplicate
  operation ID warnings.
- Direct route/API factory ref scan, expected `2 -> 0`.
- Staged GitNexus detect_changes.
- Post-commit mainline scope gate.

## Decision

If this packet is accepted, G2.78 may perform the path-limited `futures.py`
DataSourceFactory route migration under the constraints above.

## Next Gate

Human review / PR merge decision for this authorization. If accepted, create the
G2.78 path-limited implementation branch.
