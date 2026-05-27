# Backend Risk Stop-Loss Route Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: authorization package for review
- Prepared at: `2026-05-27T22:30:42+08:00`
- Base HEAD checked: `a63a6cb9a277195905b046cd31777d95160ee2c6`
- Previous gate: G2.186 remaining getter inventory refresh
- Previous PR: `#339`, merged at `a63a6cb9a277195905b046cd31777d95160ee2c6`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`

Boundary note: this PR is governance and authorization documentation only. It
does not edit backend source, tests, OpenSpec specs, route definitions, OpenAPI
schemas, or runtime behavior. If accepted, it authorizes a separate G2.188
source implementation lane with the scope and verification below.

## Why This Candidate

G2.186 classified the remaining getter surfaces after provider governance. The
largest remaining items are high-risk or cross-track surfaces:

- `get_data_quality_monitor`: data-quality and adapter cross-cutting track
- `get_integrated_services` / `get_unified_data_service`: root facade compatibility
- `get_prewarming_strategy`: control-plane cache prewarming
- `get_execution_tracking_evidence_service`: trade evidence route track

The stop-loss route pair is the narrowest low/medium-risk candidate left in the
service lifecycle DI queue. It is route-local, has existing regression tests, and
does not require changing service implementation modules.

## Current Shape

`web/backend/app/api/risk/stop_loss.py` imports the service getters from
`app.api.risk._shared` and wraps them with route-local resolvers:

| Resolver | Direct getter | Route consumers |
|---|---|---|
| `_resolve_history_service` | `get_stop_loss_history_service` | `get_stop_loss_performance`, `get_stop_loss_recommendations` |
| `_resolve_execution_service` | `get_stop_loss_execution_service` | `add_stop_loss_position`, `update_stop_loss_price`, `remove_stop_loss_position`, `get_stop_loss_status`, `get_stop_loss_overview`, `batch_update_stop_loss_prices` |

The source service getters remain canonical compatibility entrypoints and must
not be deleted, renamed, or privatized by this lane.

## GitNexus Evidence

| Target | Risk | Impacted | Direct | Processes | Interpretation |
|---|---|---:|---:|---:|---|
| `get_stop_loss_history_service` | LOW | 3 | 1 | 0 | Two route consumers through `_resolve_history_service` |
| `get_stop_loss_execution_service` | LOW | 0 | 0 | 0 | Graph undercounts the route-local wrapper; static route scan remains required |
| `_resolve_history_service` | LOW | 2 | 2 | 0 | Narrow history route seam |
| `_resolve_execution_service` | MEDIUM | 6 | 6 | 0 | Wider but still single-route-file execution seam |

The medium risk on `_resolve_execution_service` is acceptable for an
authorization package because all direct consumers live in the same route file.
The later implementation lane must rerun GitNexus impact before editing.

## Authorized Next Lane

If this package is accepted, it authorizes opening:

`G2.188 risk stop-loss route service provider implementation`

Allowed implementation scope:

- `web/backend/app/api/risk/stop_loss.py`

Allowed test scope:

- `web/backend/tests/test_risk_runtime_bootstrap_regressions.py`
- `web/backend/tests/test_stop_loss_route_regressions.py`
- `tests/unit/contract/test_risk_router_runtime_import.py`

Forbidden scope:

- `src/**`
- `web/backend/app/api/risk/_shared.py`
- other `web/backend/app/api/risk/*.py` files
- `web/frontend/**`
- `docs/api/**`
- `openspec/changes/**`
- `openspec/specs/**`

## Authorized Design

The implementation lane may:

1. Import FastAPI `Depends` in `web/backend/app/api/risk/stop_loss.py`.
2. Add route-local provider functions:
   - `get_stop_loss_history_service_dependency`
   - `get_stop_loss_execution_service_dependency`
3. Inject those providers into the eight stop-loss route functions.
4. Replace route-body calls to `_resolve_history_service()` and
   `_resolve_execution_service()` with injected service parameters.
5. Keep existing error handling semantics for unavailable services.

The implementation lane must not change:

- route paths
- HTTP methods
- response models
- OpenAPI examples
- request/response shape
- service module behavior
- source-level compatibility getters

## Required G2.188 Verification

Before editing:

- Rerun GitNexus impact on `get_stop_loss_history_service`,
  `get_stop_loss_execution_service`, `_resolve_history_service`, and
  `_resolve_execution_service`.
- Stop and return to review if risk increases to HIGH or CRITICAL.

TDD requirement:

- Add or update a focused red test proving stop-loss endpoint functions can use
  injected fake history/execution services without monkeypatching module-level
  getters.

Required checks:

```bash
pytest -o addopts= \
  web/backend/tests/test_risk_runtime_bootstrap_regressions.py \
  web/backend/tests/test_stop_loss_route_regressions.py \
  tests/unit/contract/test_risk_router_runtime_import.py \
  -q --no-cov

ruff check \
  web/backend/app/api/risk/stop_loss.py \
  web/backend/tests/test_risk_runtime_bootstrap_regressions.py \
  web/backend/tests/test_stop_loss_route_regressions.py \
  tests/unit/contract/test_risk_router_runtime_import.py
```

If route signatures or OpenAPI exposure can drift, the implementation lane must
also run a route/OpenAPI smoke and record the path/operationId result.

## Rollback Plan

For G2.187 itself, rollback is a governance-only revert.

For the future G2.188 source lane, rollback must be path-limited to:

- `web/backend/app/api/risk/stop_loss.py`
- the focused test files changed by the implementation lane

Rollback must restore route-body resolver calls and remove only the newly added
provider injection test expectations.

## Decision

G2.187 recommends accepting this authorization package and then starting G2.188
as a source implementation lane. G2.187 does not itself authorize code changes
inside this PR.
