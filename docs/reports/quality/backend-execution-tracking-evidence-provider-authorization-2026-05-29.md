# Backend Execution Tracking Evidence Provider Authorization - 2026-05-29

> **历史文档说明**: 本文件是 G2.220 执行证据快照，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Branch: `g2-220-execution-tracking-evidence-provider-authorization`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `b51256b775f7b4c6e5baad8c82a7f86446c0151b`
- Prepared at: `2026-05-29T02:01:47+08:00`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`
- Source authority in this package: none

## Parent Merge

| Item | State |
|---|---|
| Parent decision | G2.219 `get_execution_tracking_evidence_service` ownership decision |
| GitHub PR | `#372` |
| PR state | `MERGED` |
| Merge commit | `b51256b775f7b4c6e5baad8c82a7f86446c0151b` |

G2.220 starts from the accepted G2.219 classification. It authorizes a future implementation lane only after this package is reviewed and accepted.

## Current Shape

| Item | Value |
|---|---|
| Provider helper | `get_execution_tracking_evidence_service` |
| Provider definition | `web/backend/app/api/trade/execution_tracking_routes.py:289` |
| Provider factory | line 290 |
| Direct provider call lines | 364, 542 |
| List route | `get_execution_tracking` |
| Detail route | `get_execution_tracking_detail` |
| Trigger route | out of scope |
| Current dependency style | direct helper calls, no FastAPI `Depends` for this provider |

GitNexus impact remains a stop sign for broad edits:

| Metric | Value |
|---|---:|
| Risk | `HIGH` |
| Direct callers | 2 |
| Affected processes | 3 |
| Affected modules | 1 |

Direct callers:

- `_load_execution_records`
- `get_execution_tracking_detail`

## Authorization

If G2.220 is accepted, G2.221 may proceed as a path-limited source implementation lane.

Authorized future source paths:

| Path | Scope |
|---|---|
| `web/backend/app/api/trade/execution_tracking_routes.py` | convert the execution tracking evidence provider access to route dependency/provider injection |
| `web/backend/tests/test_trade_execution_tracking_routes.py` | update or add focused tests for the injection seam |

Authorized future implementation pattern:

- Preserve `get_execution_tracking_evidence_service` as the default provider factory.
- Add route dependency/provider injection for the list and detail execution tracking flows.
- Pass the injected evidence service into `_load_execution_records` instead of calling the provider helper inside that helper.
- Inject the evidence service into `get_execution_tracking_detail` instead of calling the provider helper in the route body.
- Leave `trigger_external_execution` out of scope.
- Update focused tests to use FastAPI dependency override or an equivalent explicit injection seam.

Contract invariants for any future implementation:

- No path changes.
- No `response_model` changes.
- No `UnifiedResponse` shape changes.
- No request schema changes.
- No miniQMT evidence semantic changes.
- No `broker_state` or bridge evidence interpretation changes.

## Pre-Implementation Gate For G2.221

Before editing source in G2.221:

- Run GitNexus impact on `get_execution_tracking_evidence_service`.
- Rerun app.main/OpenAPI smoke before claiming the later source implementation complete.
- Run `web/backend/tests/test_trade_execution_tracking_routes.py` as the focused baseline.
- Run ruff on the route and test files.
- Keep staged scope limited to the authorized source/test paths plus governance evidence.

## Verification

| Check | Result |
|---|---|
| `web/backend/tests/test_trade_execution_tracking_routes.py` | `4 passed in 2.13s` |
| Ruff on route and test files | `All checks passed!` |
| OpenSpec strict validate | `Change 'migrate-backend-singletons-to-lifecycle-di' is valid` |
| app.main/OpenAPI smoke | passed with transient runtime environment; `route_count=548`, `openapi_paths=500` |

The G2.220 app.main/OpenAPI smoke used transient environment values only. Secret
values were not persisted in repository files or recorded in this report. G2.221
must rerun this smoke after the future source implementation before claiming the
implementation complete.

## Not Changed

- No backend source edits.
- No tests changed.
- No route/OpenAPI contracts changed.
- No OpenSpec proposal or spec files changed.
- No GitHub issue or PR labels changed.
- No DataService, Strategy, data-quality monitor, realtime/socket, cache prewarming, root facade, `adapter_split`, or `market_data_adapter.py` work opened.

## Next Gate

If this authorization package is accepted, start G2.221 as the path-limited trade execution tracking evidence provider route injection implementation lane.

G2.221 should not expand beyond the two authorized implementation paths and the governance evidence required for the PR.

## Evidence Artifacts

| Artifact | Purpose |
|---|---|
| `.planning/codebase/generated/execution-tracking-evidence-provider-authorization-2026-05-29.json` | Machine-readable G2.220 authorization evidence |
| `docs/reports/quality/backend-execution-tracking-evidence-provider-authorization-2026-05-29.md` | Human-readable G2.220 authorization report |
| `governance/mainline/task-cards/pr-373.yaml` | Mainline governance task card |
