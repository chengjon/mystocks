# Backend get_monitoring_db Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Workline: G2.273
- Type: no-source ownership / route-provider decision
- Prepared at: `2026-05-31T20:12:35+08:00`
- Base HEAD checked: `bcf28e4668391f91ea97ee252b4da4eea64faf74`
- Parent gate: G2.272 service lifecycle residual candidate refresh
- Parent PR: `#425`, merged at `bcf28e4668391f91ea97ee252b4da4eea64faf74`

This package does not authorize backend source edits, provider injection, route
registration, OpenAPI artifact edits, test contract edits, source retirement,
PM2 commands, or runtime state changes.

## Decision

`get_monitoring_db` is a split ownership surface, not one implementation seam.

G2.273 selects `G2.274 no-source risk get_monitoring_db route-provider
authorization` as the next gate. G2.274 should decide whether to authorize a
future risk-only implementation lane for:

- `web/backend/app/api/risk/_shared.py`
- `web/backend/app/api/risk/alerts.py`
- `web/backend/app/api/risk/metrics.py`

Strategy-management and utility same-name helpers remain deferred. They require
separate ownership decisions before any source lane.

## GitNexus Evidence

GitNexus MCP impact failed with `Transport closed`.

The GitNexus CLI fallback returned an ambiguous symbol result:

| Candidate | Path | Line | Interpretation |
|---|---|---:|---|
| `Function:web/backend/app/api/risk/_shared.py:get_monitoring_db` | `web/backend/app/api/risk/_shared.py` | 127 | Risk route helper owner |
| `Function:web/backend/app/utils/risk_utils.py:get_monitoring_db` | `web/backend/app/utils/risk_utils.py` | 22 | Same-name utility helper |
| `Function:web/backend/app/api/strategy_management/_helpers.py:get_monitoring_db` | `web/backend/app/api/strategy_management/_helpers.py` | 419 | Strategy route/helper owner |

Index status from the CLI result:

- `stale: true`
- `commits_behind: 0`
- `has_embeddings: false`

Result: any future source authorization must disambiguate by `target_uid` or
`file_path`. A broad `get_monitoring_db` source lane is not acceptable.

## Static Ownership Evidence

### Risk Surface

Definition:

- `web/backend/app/api/risk/_shared.py:128`

Route-body call sites:

| File | Line | Handler |
|---|---:|---|
| `web/backend/app/api/risk/alerts.py` | 395 | `create_risk_alert` |
| `web/backend/app/api/risk/alerts.py` | 412 | `create_risk_alert` |
| `web/backend/app/api/risk/metrics.py` | 301 | `calculate_var_cvar` |
| `web/backend/app/api/risk/metrics.py` | 327 | `calculate_var_cvar` |
| `web/backend/app/api/risk/metrics.py` | 401 | `calculate_beta` |
| `web/backend/app/api/risk/metrics.py` | 420 | `calculate_beta` |

The risk surface is the only recommended first authorization target because it
has one helper owner and six active route-body calls across three risk
endpoints.

### Strategy Surface

Definition:

- `web/backend/app/api/strategy_management/_helpers.py:420`

Route-body call sites:

| File | Line | Handler |
|---|---:|---|
| `web/backend/app/api/strategy_management/_strategy_crud_router.py` | 157 | `list_strategies` |
| `web/backend/app/api/strategy_management/_strategy_crud_router.py` | 174 | `list_strategies` |
| `web/backend/app/api/strategy_management/_strategy_crud_router.py` | 254 | `create_strategy` |
| `web/backend/app/api/strategy_management/_strategy_crud_router.py` | 271 | `create_strategy` |

Internal helper call sites also exist in
`web/backend/app/api/strategy_management/_helpers.py` at lines `393` and `409`
inside `_handle_strategy_lifecycle_action`.

The strategy surface is deferred because it combines route CRUD behavior with a
helper/lifecycle logging seam. It should not be batched with the risk surface.

### Utility Same-Name Helper

Definition:

- `web/backend/app/utils/risk_utils.py:23`

G2.273 found no active target route calls to this helper in the scoped scan.
Keep it out of any risk-route implementation authorization unless a future
decision package proves active ownership and consumer scope.

## Route / OpenAPI Evidence

The app route/OpenAPI smoke used temporary placeholder environment values only
to satisfy import-time settings validation. It did not run PM2 or a stateful
database workflow.

| Metric | Value |
|---|---:|
| FastAPI route count | 548 |
| OpenAPI path count | 500 |
| Duplicate operation IDs | 0 |

Relevant active documented routes:

| Path | Method | Endpoint | Module | In schema |
|---|---|---|---|---|
| `/api/v1/risk/alerts` | `POST` | `create_risk_alert` | `app.api.risk.alerts` | yes |
| `/api/v1/risk/var-cvar` | `POST` | `calculate_var_cvar` | `app.api.risk.metrics` | yes |
| `/api/v1/risk/beta` | `POST` | `calculate_beta` | `app.api.risk.metrics` | yes |
| `/api/v1/strategy/strategies` | `GET` | `list_strategies` | `app.api.strategy_management._strategy_crud_router` | yes |
| `/api/v1/strategy/strategies` | `POST` | `create_strategy` | `app.api.strategy_management._strategy_crud_router` | yes |

## Future G2.274 Shape

If this decision is accepted, G2.274 should be no-source and should only decide
whether a later risk-only implementation lane is authorized.

Minimum G2.274 acceptance criteria:

- Disambiguated GitNexus impact for
  `web/backend/app/api/risk/_shared.py:get_monitoring_db` using `target_uid` or
  `file_path`.
- Explicit target scope limited to `risk/_shared.py`, `risk/alerts.py`, and
  `risk/metrics.py`.
- Focused risk alerts and risk metrics tests named before any implementation.
- Route/OpenAPI no-contract-change acceptance criteria.
- Rollback rule preserving current `MonitoringDatabase` helper fallback
  behavior.

## Non-Goals

- No backend source edits.
- No provider injection implementation.
- No combined risk and strategy migration.
- No route registration changes.
- No OpenAPI artifact edits.
- No docs/api or test contract edits.
- No source retirement.
- No PM2 or stateful runtime gate.

## Evidence Artifacts

- `.planning/codebase/generated/get-monitoring-db-ownership-decision-2026-05-31.json`
- `docs/reports/quality/backend-get-monitoring-db-ownership-decision-2026-05-31.md`
- `governance/mainline/task-cards/pr-426.yaml`
