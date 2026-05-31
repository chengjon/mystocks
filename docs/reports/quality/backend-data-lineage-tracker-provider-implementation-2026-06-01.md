# Backend Data Lineage Tracker Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for review in future PR `#436`
- Prepared at: `2026-06-01T02:47:10+08:00`
- Base HEAD checked: `891593d2dc4896f909333033a0b454529b9be38c`
- Parent: G2.282 accepted/merged by PR `#435` at `891593d2dc4896f909333033a0b454529b9be38c`
- Source edit authority: yes, path-limited
- Autopilot status: stop at PR review gate

Boundary note: G2.283 is a source implementation package. It must not be
auto-merged under the limited-autopilot rule. It changes only the authorized
data lineage route module, focused regression test, generated evidence, quality
report, steward tree, and task card.

## Implementation Summary

G2.283 moved the five active data lineage route handlers from direct route-body
`get_lineage_tracker()` calls to a route-local FastAPI dependency provider.

Implemented provider:

- `get_lineage_tracker_dependency`
- wraps the existing `get_lineage_tracker()` factory
- yields the existing `(tracker, connection_adapter)` pair
- closes the connection adapter in `finally`

Migrated handlers:

- `record_lineage`
- `get_upstream_lineage`
- `get_downstream_lineage`
- `get_lineage_graph`
- `analyze_impact`

Static result:

- Direct route-body `get_lineage_tracker()` calls: `5 -> 0`
- Manual route-body `await conn.close()` calls: `5 -> 0`
- `Depends(get_lineage_tracker_dependency)` bindings: `5`

The lifecycle stays route-local. This PR does not rewrite `LineageTracker`, move
the seam into shared infrastructure, change route registration, or change
OpenAPI artifacts.

## GitNexus Evidence

Before source edits:

- GitNexus MCP context: `Transport closed`
- GitNexus MCP impact: `Transport closed`
- CLI context target: `Function:web/backend/app/api/data_lineage.py:get_lineage_tracker`
- CLI impact risk: `MEDIUM`
- Impacted count: `5`
- Direct callers: `5`
- Affected processes: `0`
- Affected module: `Api`
- Index status: stale warning, `commits_behind=0`, `has_embeddings=false`

Because the target risk is MEDIUM and this PR changes backend source, PR `#436`
must stop for human review.

Staged verification:

- `gitnexus_detect_changes(scope=staged)`: MCP `Transport closed`
- CLI fallback: `ok=true`, `status=stale`, risk `low`
- Changed files: `11`
- Changed symbols: `8`
- Affected processes: `0`
- Indexed commit: `f894d77d7cd710a6766921ec8a51256ba4de3428`
- Current commit: `891593d2dc4896f909333033a0b454529b9be38c`

Touched symbols reported by GitNexus CLI fallback:

- `record_lineage`
- `get_upstream_lineage`
- `get_downstream_lineage`
- `get_lineage_graph`
- `analyze_impact`
- helper variables from the same route/test files

## TDD Evidence

RED:

```text
pytest -q web/backend/tests/test_data_lineage_regressions.py -q -n 0 --tb=short --no-cov
```

Result: `2 failed, 1 passed`

Expected failures:

- `module 'app.api.data_lineage' has no attribute 'get_lineage_tracker_dependency'`
- `record_lineage` had no `Depends(get_lineage_tracker_dependency)` parameter

GREEN:

```text
pytest -q web/backend/tests/test_data_lineage_regressions.py -q -n 0 --tb=short --no-cov
```

Result: `3 passed in 0.66s`

## Verification

Focused data lineage tests:

```text
pytest -q tests/api/file_tests/test_data_lineage_api.py web/backend/tests/test_data_lineage_regressions.py -q -n 0 --tb=short --no-cov
```

Result: `15 passed in 0.60s`

Health route conflict regression:

```text
pytest -q web/backend/tests/test_health_route_conflicts.py -q -n 0 --tb=short --no-cov
```

Result: `121 passed in 237.08s`

Ruff:

```text
ruff check web/backend/app/api/data_lineage.py web/backend/tests/test_data_lineage_regressions.py
```

Result: `All checks passed`

Route/OpenAPI smoke:

- FastAPI routes: `548`
- OpenAPI paths: `500`
- Duplicate operation IDs: `0`
- Lineage provider parameter leaks: `{}`

Lineage paths present:

- `/api/v1/lineage/record`
- `/api/v1/lineage/{node_id}/upstream`
- `/api/v1/lineage/{node_id}/downstream`
- `/api/v1/lineage/graph`
- `/api/v1/lineage/impact`
- `/api/v1/governance/lineage/stats`

Observed import smoke warnings were existing environment/runtime warnings:

- GPU dependency fallback warning
- FastAPI `example` deprecation warnings

The smoke completed successfully.

## Scope Guard

Changed source/test paths:

- `web/backend/app/api/data_lineage.py`
- `web/backend/tests/test_data_lineage_regressions.py`

Explicitly unchanged:

- route registration
- route path strings
- response model declarations
- generated OpenAPI artifacts
- docs/api examples
- frontend
- config
- scripts
- OpenSpec specs
- PM2/runtime state
- `LineageTracker` domain implementation
- shared database/session infrastructure

## Governance Verification

Fresh governance verification:

- Markdown governance gate: `6` checked files, `0` errors
- OpenSpec strict validate: `migrate-backend-singletons-to-lifecycle-di` valid
- `git diff --check`: passed with no output
- `git diff --cached --check`: passed with no output
- JSON parse: generated evidence and steward index parsed successfully
- Mainline scope gate: pass after task card metadata correction
- GitNexus staged CLI fallback: `11` files, `8` touched symbols, `0` affected
  processes, risk `low`, stale-index warning

## Next Gate

After PR `#436` human acceptance, start:

- G2.284 no-source data_lineage `get_lineage_tracker` provider closeout /
  residual refresh

G2.284 should verify the direct route-body residual remains closed, refresh the
remaining service lifecycle candidate queue, and select the next no-source
decision target. It should not start source work directly.

## Evidence Artifacts

- `.planning/codebase/generated/data-lineage-tracker-provider-implementation-2026-06-01.json`
- `docs/reports/quality/backend-data-lineage-tracker-provider-implementation-2026-06-01.md`
- `governance/mainline/task-cards/pr-436.yaml`
