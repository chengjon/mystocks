# Backend Data Lineage Tracker Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for review in future PR `#435`
- Prepared at: `2026-06-01T02:16:40+08:00`
- Base HEAD checked: `b8ba6ca75c573913d7b10553620e5d308c0d13f3`
- Parent: G2.281 accepted/merged by PR `#434` at `b8ba6ca75c573913d7b10553620e5d308c0d13f3`
- Source edit authority: no
- Autopilot status: stop at PR review gate

Boundary note: this package authorizes a possible future source lane only after
human review. G2.282 itself does not edit backend source, tests, route
contracts, OpenAPI artifacts, docs/api, frontend, config, scripts, OpenSpec,
PM2, or runtime state.

## Authorization Decision

G2.282 authorizes a future, path-limited G2.283 implementation package for the
data lineage route-local tracker provider seam.

The only future source path named by this authorization is:

- `web/backend/app/api/data_lineage.py`

The future G2.283 lane must preserve the existing route/API contract and may not
expand into route registration, OpenAPI artifact generation, docs/api examples,
frontend code, config, scripts, OpenSpec specs, PM2 workflows, or broader
database/session infrastructure.

Because `get_lineage_tracker` has GitNexus MEDIUM impact, this PR must not be
auto-merged under the limited-autopilot rule. It must stop for human review.

## Parent Evidence

PR `#434` is merged:

- URL: `https://github.com/chengjon/mystocks/pull/434`
- Base: `wip/root-dirty-20260403`
- Head: `g2-281-data-lineage-tracker-ownership-decision`
- Merge commit: `b8ba6ca75c573913d7b10553620e5d308c0d13f3`
- Merged at: `2026-05-31T18:11:33Z`

G2.281 classified `get_lineage_tracker` as a bounded active API route helper
owned by `web/backend/app/api/data_lineage.py`, not a free deletion candidate and
not a generic service singleton cleanup.

## GitNexus Evidence

GitNexus MCP remained unavailable for this worktree:

- `gitnexus_context`: `Transport closed`
- `gitnexus_impact`: `Transport closed`

CLI fallback was rerun at current HEAD:

- Target: `Function:web/backend/app/api/data_lineage.py:get_lineage_tracker`
- Direction: upstream
- Risk: `MEDIUM`
- Impacted count: `5`
- Direct callers: `5`
- Affected processes: `0`
- Affected modules: `Api`
- Index status: stale warning, `commits_behind=0`, `has_embeddings=false`

Direct callers:

- `record_lineage`
- `get_upstream_lineage`
- `get_downstream_lineage`
- `get_lineage_graph`
- `analyze_impact`

Staged verification:

- `gitnexus_detect_changes(scope=staged)`: MCP `Transport closed`
- CLI fallback: `ok=true`, `status=stale`, risk `low`
- Changed files: `9`
- Changed symbols: `0`
- Affected processes: `0`
- Indexed commit: `f894d77d7cd710a6766921ec8a51256ba4de3428`
- Current commit: `b8ba6ca75c573913d7b10553620e5d308c0d13f3`

## Data Lineage Surface Evidence

Current helper:

- Definition: `web/backend/app/api/data_lineage.py:92`
- Behavior: creates an `asyncpg` raw connection, wraps it in
  `_AsyncpgLineageConnectionAdapter`, and returns it with a `LineageTracker`.
- Current cleanup contract: each active route handler closes the returned
  connection adapter with `await conn.close()`.

Direct call and cleanup sites:

| Handler | Call site | Cleanup site |
|---|---:|---:|
| `record_lineage` | 149 | 181 |
| `get_upstream_lineage` | 226 | 267 |
| `get_downstream_lineage` | 336 | 350 |
| `get_lineage_graph` | 424 | 466 |
| `analyze_impact` | 540 | 545 |

G2.283 must preserve this lifecycle explicitly. If the future implementation
uses a dependency finalizer instead of per-handler `conn.close()`, the focused
tests must prove equivalent cleanup behavior.

## Route / OpenAPI Evidence

Route/OpenAPI smoke used temporary placeholder import-time environment values.
It did not run PM2 or a stateful database workflow.

Current snapshot:

- FastAPI routes: `548`
- OpenAPI paths: `500`
- Duplicate operation IDs: `0`

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

## Focused Test Inventory

Existing data-lineage-related test files:

- `tests/api/file_tests/test_data_lineage_api.py`
- `tests/integration/test_data_lineage_tracker_integration.py`
- `tests/unit/test_governance/test_data_lineage_tracker.py`
- `tests/unit/test_governance/test_lineage.py`
- `web/backend/tests/test_data_lineage_regressions.py`

Future G2.283 must add or update focused regression coverage before changing the
provider seam. The minimum expected proof is:

- route handlers receive the same tracker behavior through the route provider
- connection cleanup is preserved
- `UnifiedResponse` behavior remains stable
- route/OpenAPI smoke remains `548` routes, `500` paths, and `0` duplicate
  operation IDs unless a separately approved route/OpenAPI lane changes that
  policy

## Future G2.283 Authorized Shape

After PR `#435` is human-accepted, a separate implementation lane may be opened
with this narrow scope:

- Allowed source path: `web/backend/app/api/data_lineage.py`
- Allowed focused tests:
  - `tests/api/file_tests/test_data_lineage_api.py`
  - `web/backend/tests/test_data_lineage_regressions.py`
- Allowed governance evidence:
  - generated implementation evidence JSON
  - implementation report
  - steward tree updates
  - implementation task card

The future implementation should stay route-local and should not reclassify the
lineage tracker into a shared infrastructure singleton in the same lane.

## Future G2.283 Forbidden Scope

- non-data-lineage backend source
- `LineageTracker` domain rewrite
- shared database/session infrastructure changes
- route registration changes
- route path, method, response model, response shape, or OpenAPI artifact changes
- docs/api example changes
- frontend, config, scripts, OpenSpec, PM2, or runtime state
- source retirement or compatibility deletion

## Required Future Verification

Future G2.283 must rerun:

- GitNexus impact/context before any source edit
- focused data lineage provider regression tests
- `ruff check` on touched source/test files
- route/OpenAPI smoke for route count, path count, duplicate operation IDs, and
  lineage path presence
- `web/backend/tests/test_health_route_conflicts.py` if app import or route
  collection is touched
- GitNexus staged verification or CLI fallback before commit
- mainline scope gate using the implementation task card
- OpenSpec strict validation for `migrate-backend-singletons-to-lifecycle-di`

Stop rules:

- stop on GitNexus HIGH or CRITICAL risk
- stop on any changed route/OpenAPI contract without a separate route governance
  approval
- stop on any test or gate failure
- stop if the cleanup lifecycle cannot be proven equivalent

## Governance Verification

Fresh verification performed for this no-source package:

- Markdown governance gate: `6` checked files, `0` errors
- OpenSpec strict validate: `migrate-backend-singletons-to-lifecycle-di` valid
- `git diff --check`: passed with no output
- `git diff --cached --check`: passed with no output
- JSON parse: generated evidence and steward index parsed successfully
- GitNexus staged CLI fallback: `9` files, `0` changed symbols, `0` affected
  processes, risk `low`, stale-index warning

## Evidence Artifacts

- `.planning/codebase/generated/data-lineage-tracker-provider-authorization-2026-06-01.json`
- `docs/reports/quality/backend-data-lineage-tracker-provider-authorization-2026-06-01.md`
- `governance/mainline/task-cards/pr-435.yaml`
