# Backend Risk Stop-Loss Provider Closeout Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: review candidate
- Prepared at: `2026-05-28T00:19:16+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `0aac0e16f16480bd99eebb8726e21a7db6566b39`
- Worktree branch: `g2-189-risk-stop-loss-provider-closeout-refresh`
- Scope: governance closeout and remaining-candidate refresh only
- Source edit authority: none

Boundary note: this package records the accepted G2.188 outcome and refreshes the
next service-lifecycle DI gate. It does not authorize backend source edits,
frontend edits, test edits, OpenSpec proposal creation, GitHub issue label
changes, PM2 commands, or deletion of retained provider backing getters.

## Parent State

| Item | State | Evidence |
|---|---|---|
| G2.187 risk stop-loss route provider authorization | Merged | PR `#340`, merge commit `2d3b9c7e3ff30c81a19d51e66c32d2c06c1e1c4a` |
| G2.188 risk stop-loss route provider implementation | Merged | PR `#341`, merge commit `0aac0e16f16480bd99eebb8726e21a7db6566b39`, merged at `2026-05-27T15:46:26Z` |
| G2.189 closeout / candidate refresh | For review | This report plus `.planning/codebase/generated/risk-stop-loss-provider-closeout-refresh-2026-05-28.json` |

## Closed Capability

G2.188 is closed as a route-body provider migration for the stop-loss risk route.
The implementation replaced route-body `_resolve_*_service()` calls with
FastAPI dependency-injected service parameters while preserving:

- route paths
- HTTP methods
- response-model declarations
- OpenAPI examples
- direct-test fallback behavior
- src-level `get_stop_loss_history_service` and `get_stop_loss_execution_service`
  provider backing getters

The retained src-level getters are still active provider backing functions. They
are not deletion candidates in this closeout package.

## Post-Merge Verification

| Check | Result |
|---|---|
| `web/backend/tests/test_risk_runtime_bootstrap_regressions.py -k stop_loss` | `5 passed, 5 deselected` |
| `web/backend/tests/test_stop_loss_route_regressions.py` | `2 passed` |
| `tests/unit/contract/test_risk_router_runtime_import.py::test_app_main_registers_canonical_risk_router_without_loading_compat_shim` | `1 passed` |
| touched risk files `ruff check` | passed |
| OpenAPI smoke | `openapi_paths=500`, `stop_loss_paths=10`, `dependency_params_leaked=0` |
| route body resolver scan | `body_resolve_history=0`, `body_resolve_execution=0` |

The endpoint scan covered these stop-loss endpoints:

- `add_stop_loss_position`
- `update_stop_loss_price`
- `remove_stop_loss_position`
- `get_stop_loss_status`
- `get_stop_loss_overview`
- `batch_update_stop_loss_prices`
- `get_stop_loss_performance`
- `get_stop_loss_recommendations`

## Remaining Candidate Refresh

G2.186 classified 10 service-singleton review names with 43 calls. G2.188 closes
the stop-loss pair as a route-body provider migration and leaves the remaining
names in owner-specific tracks.

| Candidate / group | G2.189 disposition | Next handling |
|---|---|---|
| `get_stop_loss_history_service` | Closed for route-body provider migration; retained as provider backing getter | No deletion or source lane from G2.189 |
| `get_stop_loss_execution_service` | Closed for route-body provider migration; retained as provider backing getter | No deletion or source lane from G2.189 |
| `get_data_quality_monitor` | High-risk data-quality / adapter cross-cutting candidate | Recommended next governance target: G2.190 decision / authorization package only |
| `get_execution_tracking_evidence_service` | Trade execution evidence track | Defer to separate trade/evidence authorization package |
| `get_prewarming_strategy` | Control-plane cache prewarming track | Defer to control-plane cache prewarming governance |
| `get_integrated_services` | Root facade compatibility | Retain until root facade compatibility retirement package exists |
| `get_unified_data_service` | Root facade / service self-wrapper | Retain; not a route-body singleton implementation candidate |
| `get_data_service` | Indicator/data provider fallback | Retain under indicator/data provider governance unless later authorization changes it |
| `get_market_data_service_v2` | Constructor install fallback | Retain as constructor install fallback |
| `get_tdx_service` | Constructor install fallback / Dashboard-TDX split | Retain; Dashboard/TDX route work remains separate |

## Recommended Next Gate

If G2.189 is accepted, start `G2.190 data-quality / adapter cross-cutting
decision package` as a design / authorization package only.

G2.190 should not directly edit source. It should first classify the
data-quality monitor surface, adapter ownership, route consumers, OpenAPI /
consumer-contract exposure, test seams, and rollback boundaries. Only after that
authorization is accepted should a new source implementation lane be opened.

## Explicit Non-Goals

- Do not edit backend source from G2.189.
- Do not edit frontend source from G2.189.
- Do not edit tests from G2.189.
- Do not create or change OpenSpec proposals from G2.189.
- Do not change GitHub issue or PR labels from G2.189.
- Do not delete `get_stop_loss_history_service` or
  `get_stop_loss_execution_service`.
- Do not expand into alerts resolver fixes.
- Do not restore or change legacy `app.api.risk_management` compatibility.
- Do not start data-quality implementation before a separate accepted
  authorization package exists.

## Known Out-Of-Scope Baselines

- Alerts route resolver baseline failures remain outside this closeout:
  `_resolve_notification_manager`, `_resolve_rule_engine`, and
  `_resolve_runtime_alert_service`.
- Legacy `app.api.risk_management` compatibility module absence remains a
  separate lane.

## Evidence Artifacts

| Artifact | Role |
|---|---|
| `.planning/codebase/generated/risk-stop-loss-route-provider-implementation-2026-05-27.json` | G2.188 implementation evidence |
| `docs/reports/quality/backend-risk-stop-loss-route-provider-implementation-2026-05-27.md` | G2.188 implementation report |
| `.planning/codebase/generated/risk-stop-loss-provider-closeout-refresh-2026-05-28.json` | G2.189 machine-readable closeout / candidate refresh |
| `docs/reports/quality/backend-risk-stop-loss-provider-closeout-refresh-2026-05-28.md` | G2.189 human-readable closeout / candidate refresh |
| `governance/mainline/task-cards/pr-342.yaml` | G2.189 governance-only PR scope card |
