# Backend Postgres Async Route Consumer Authorization - 2026-05-30

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2 item: `G2.249`
- Status: `for_review`
- Prepared at: `2026-05-30T17:35:00+08:00`
- Base branch: `wip/root-dirty-20260403`
- Current HEAD checked: `89fb66f6ee21ab33d5e1f5c255a8d75af760033b`
- Parent closeout PR: `#401`
- Parent merge commit: `89fb66f6ee21ab33d5e1f5c255a8d75af760033b`

Boundary: this package is no-source authorization planning. It does not
authorize backend source edits, route consumer migration, test edits, OpenAPI
changes, frontend changes, PM2 commands, OpenSpec proposal creation, or issue
label changes.

## Current Evidence

G2.248 recorded 7 active API-adjacent files with 21 `get_postgres_async()` calls.
G2.249 splits that snapshot into route-body candidates and route-adjacent
exclusions.

| Evidence | Value |
|---|---:|
| app routes | 548 |
| OpenAPI paths | 500 |
| G2.248 residual files | 7 |
| G2.248 residual calls | 21 |
| Route-decorated files | 5 |
| Route-decorated calls | 19 |
| Route-adjacent helper / repository files | 2 |
| Route-adjacent helper / repository calls | 2 |

## Route-Decorated Candidates

| File | Calls | Route scope | Decision |
|---|---:|---|---|
| `web/backend/app/api/_monitoring_portfolio_router.py` | 3 | `summary`, `alerts`, `rebalance` portfolio routes | Authorize as future G2.250 pilot |
| `web/backend/app/api/monitoring_analysis.py` | 2 | health history and portfolio analysis routes | Defer until after pilot |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | 3 | signal statistics, active signals, strategy health routes | Defer until after pilot |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | 4 | signal history, quality report, realtime, health routes | Larger batch; defer |
| `web/backend/app/api/monitoring_watchlists.py` | 7 | watchlist CRUD and stock membership routes | Larger batch; defer |

## Route-Adjacent Exclusions

These files are not authorized as route-body provider migration targets by this
package:

| File | Calls | Reason |
|---|---:|---|
| `web/backend/app/api/_data_source_config_responses.py` | 1 | `get_config_manager()` helper/facade function has no route decorator |
| `web/backend/app/api/v1/system/settings.py` | 1 | `PostgresSystemSettingsRepository.__init__` owns the lookup, not the route handler |

If either file is reopened, it needs a separate helper/facade or repository
ownership decision. Do not fold it into the route-body pilot.

## Authorization Decision

Authorize future G2.250 as a path-limited source lane:

- target: `web/backend/app/api/_monitoring_portfolio_router.py`
- test path: `tests/api/file_tests/test_monitoring_analysis_api.py`
- source purpose: move the three portfolio route-body
  `get_postgres_async()` calls behind a route-local provider dependency
- source authority starts only after this G2.249 package is reviewed and
  accepted

The future G2.250 lane must preserve:

- route paths and methods
- `include_in_schema` behavior
- response models and response shapes
- existing `UnifiedResponse` behavior
- existing `calculator_factory=Depends(get_monitoring_calculator_factory)`
  parameters
- OpenAPI path count unless current HEAD changes for an unrelated accepted
  reason

The future G2.250 lane must not touch:

- `monitoring_analysis.py`
- `monitoring_watchlists.py`
- `signal_monitoring/*`
- `_data_source_config_responses.py`
- `v1/system/settings.py`
- `src/monitoring/infrastructure/*`
- `get_monitoring_db`
- frontend, config, scripts, OpenSpec specs/proposals, or PM2 state

## Verification

| Check | Result |
|---|---|
| JSON / YAML parse | passed |
| Markdown governance gate | 6 checked files, 0 errors |
| app/OpenAPI smoke | `routes=548`, `paths=500` |
| OpenSpec strict validation | `migrate-backend-singletons-to-lifecycle-di` valid |
| Mainline scope gate | pass, 9 changed files, 0 violations |
| `git diff --check` | passed |
| GitNexus MCP `detect_changes` | attempted with `repo=mystocks`; timed out after 120 seconds |
| GitNexus CLI fallback | staged/compare fallback attempted; command hung and was terminated |

GitNexus is recorded as unavailable for this no-source package. The blocking
scope guard for G2.249 is the mainline scope gate, which confirms the final
commit changes only the nine authorized governance files.

## Required Future G2.250 Gates

Before any source edit in G2.250:

- read `architecture/STANDARDS.md`
- run GitNexus impact/context on the portfolio route symbols, with CLI fallback
  if MCP is unavailable
- establish a TDD red check
- stage only the authorized source/test/governance paths

After implementation in G2.250:

- focused portfolio route/provider tests pass
- `ruff check` passes on touched source/test files
- app/OpenAPI smoke remains `routes=548`, `paths=500` unless a newer accepted
  baseline changes it
- route table diff confirms no path, method, or `include_in_schema` drift
- mainline scope gate passes
- GitNexus `detect_changes` runs on staged or compare scope, with CLI fallback
  if MCP remains unavailable

## Next Gate

If G2.249 is accepted, start G2.250:

`postgres async monitoring portfolio route provider implementation`

G2.250 is a source lane, but only for the explicitly authorized portfolio route
file and focused tests. It is not a bulk route migration.

## Evidence Files

- `.planning/codebase/generated/postgres-async-route-consumer-authorization-2026-05-30.json`
- `governance/mainline/task-cards/pr-402.yaml`
- `.planning/codebase/steward-tree/current-next-gates.md`
- `.planning/codebase/steward-tree/steward-index.json`
- `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md`
- `.planning/codebase/steward-tree/branch-register.md`
- `.planning/codebase/steward-tree/evidence-index.md`
- `.planning/codebase/steward-tree/completed-ledger.md`

## Forbidden Scope

This authorization package forbids:

- backend source edits
- test source edits
- route consumer migration
- route path or OpenAPI changes
- frontend changes
- PM2 commands
- OpenSpec proposal or spec creation
- `get_monitoring_db` work
- settings repository provider work
- data-source config helper work
- issue label changes
