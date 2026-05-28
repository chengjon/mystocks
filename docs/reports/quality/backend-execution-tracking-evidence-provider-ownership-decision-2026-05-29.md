# Backend Execution Tracking Evidence Provider Ownership Decision - 2026-05-29

> **历史文档说明**: 本文件是 G2.219 执行证据快照，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Branch: `g2-219-execution-tracking-evidence-provider-decision`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `d4ee917ad642939c4c60000998b8bea5ca7c9a65`
- Prepared at: `2026-05-29T01:42:47+08:00`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`
- Source authority: none

## Parent Merge

| Item | State |
|---|---|
| Parent closeout | G2.218 `DataService` provider/reset seam closeout / residual refresh |
| GitHub PR | `#371` |
| PR state | `MERGED` |
| Merge commit | `d4ee917ad642939c4c60000998b8bea5ca7c9a65` |

G2.219 starts from the accepted G2.218 decision to inspect `get_execution_tracking_evidence_service` next. This package does not authorize source implementation.

## Target

| Item | Value |
|---|---|
| Symbol | `get_execution_tracking_evidence_service` |
| File | `web/backend/app/api/trade/execution_tracking_routes.py:289` |
| Current shape | route-local factory for `ExecutionTrackingEvidenceService` |
| Current injection style | direct route-module helper calls; no FastAPI `Depends` usage |
| Existing test seam | `test_trade_execution_tracking_routes.py` monkeypatches the helper |

## GitNexus Impact

| Metric | Value |
|---|---:|
| Risk | `HIGH` |
| Direct callers | 2 |
| Impacted symbols | 2 |
| Affected processes | 3 |
| Affected modules | 1 |

Direct callers:

| Caller | File |
|---|---|
| `_load_execution_records` | `web/backend/app/api/trade/execution_tracking_routes.py` |
| `get_execution_tracking_detail` | `web/backend/app/api/trade/execution_tracking_routes.py` |

Affected process names:

- `Get_execution_tracking_detail -> Strip`
- `Get_execution_tracking_detail -> _as_int`
- `Get_execution_tracking_detail -> _broker_state_for`

## Static Inventory

| Evidence | Value |
|---|---|
| Route file line count | 563 |
| Test file line count | 221 |
| Route decorators in file | 3 |
| Provider definition line | 289 |
| Provider call lines | 364, 542 |
| Direct `Depends` usage for provider | 0 |
| Focused route tests | 4 |

Route surfaces in the file:

| Line | Method | Role |
|---:|---|---|
| 435 | `GET` | list execution tracking |
| 469 | `POST` | record external execution trigger |
| 533 | `GET` | get execution tracking detail |

## Verification

| Check | Result |
|---|---|
| `web/backend/tests/test_trade_execution_tracking_routes.py` | `4 passed in 3.30s` |
| Ruff on route and test files | `All checks passed!` |
| OpenSpec strict validate | `Change 'migrate-backend-singletons-to-lifecycle-di' is valid` |

OpenAPI app smoke is currently environment-blocked, not source-blocked. Importing
`app.main` exits with missing required environment variables:

- `POSTGRESQL_HOST`
- `POSTGRESQL_USER`
- `POSTGRESQL_PASSWORD`
- `JWT_SECRET_KEY`
- `BACKEND_PORT`
- `BACKEND_BACKUP_PORT`

Do not treat the blocked OpenAPI smoke as implementation authority. A later source lane should either run the app/OpenAPI smoke with a valid environment or explicitly record the environment blocker disposition.

## Decision

`get_execution_tracking_evidence_service` is not a generic service singleton cleanup candidate. It is a trade execution tracking route/provider ownership surface.

Current disposition:

- Keep the existing route-local provider helper unchanged.
- Do not edit `web/backend/app/api/trade/execution_tracking_routes.py` in G2.219.
- Do not convert direct calls to `Depends` in this decision package.
- Do not change route contracts, response models, miniQMT evidence semantics, or tests from this package.
- Use the existing test monkeypatch seam as evidence that injection is possible, not as permission to start implementation.

## Next Gate

Start G2.220 as a no-source authorization package for the trade execution tracking evidence provider.

G2.220 should decide the exact future implementation boundary before any source edit:

- Whether to convert list/detail direct provider calls to explicit route dependency/provider injection.
- Whether `_load_execution_records` should accept an injected evidence service from the route handler or keep calling the helper.
- Which focused tests must prove behavior stays stable.
- How to handle app.main/OpenAPI smoke when required environment variables are absent.
- The precise allowed source and test paths for any later implementation lane.

## Not Changed

- No backend source edits.
- No tests changed.
- No route/OpenAPI contracts changed.
- No OpenSpec proposal or spec files changed.
- No GitHub issue or PR labels changed.
- No DataService, Strategy, data-quality monitor, realtime/socket, cache prewarming, root facade, `adapter_split`, or `market_data_adapter.py` work opened.

## Evidence Artifacts

| Artifact | Purpose |
|---|---|
| `.planning/codebase/generated/execution-tracking-evidence-provider-ownership-decision-2026-05-29.json` | Machine-readable G2.219 ownership decision evidence |
| `docs/reports/quality/backend-execution-tracking-evidence-provider-ownership-decision-2026-05-29.md` | Human-readable G2.219 decision report |
| `governance/mainline/task-cards/pr-372.yaml` | Mainline governance task card |
