# Backend Risk get_monitoring_db Provider Closeout / Residual Refresh - 2026-05-31

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2 item: `G2.276`
- Branch: `g2-276-risk-get-monitoring-db-provider-closeout-refresh`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `daa4f22a557b054ab76042d4990b6e91d9faa7a7`
- Parent PR: `#428`, merged at `daa4f22a557b054ab76042d4990b6e91d9faa7a7`
- Source edit authority: none

Boundary note: this closeout refresh records G2.275 as accepted/merged,
refreshes the remaining `get_monitoring_db` ownership surfaces, and selects the
next no-source gate. It does not authorize backend source edits, tests edits,
route registration, route contract changes, OpenAPI artifact edits, docs/api
edits, frontend, config, scripts, OpenSpec, PM2, or runtime state changes.

## Parent Closeout

G2.275 is closed by PR `#428`.

| Metric | Value |
|---|---:|
| Risk route-body `get_monitoring_db()` calls after G2.275 | 0 |
| Risk `Depends(get_risk_monitoring_db)` parameters | 3 |
| Risk provider backing `get_monitoring_db()` calls | 1 |
| Route contract changes | 0 |
| Generated OpenAPI artifact changes | 0 |

Closed handlers:

- `create_risk_alert`
- `calculate_var_cvar`
- `calculate_beta`

## Residual Refresh

Current `web/backend/app/api` scan after PR `#428`:

| File | Calls | Direct log calls | Classification | Next action |
|---|---:|---:|---|---|
| `web/backend/app/api/risk/_shared.py` | 2 | 0 | retained risk helper definition and provider backing wrapper | closed for route-body migration by G2.275 |
| `web/backend/app/api/strategy_management/_helpers.py` | 3 | 2 | strategy helper ownership surface | feed future no-source strategy authorization |
| `web/backend/app/api/strategy_management/_strategy_crud_router.py` | 4 | 4 | strategy route-body residual candidate | feed future no-source strategy authorization |

The same-name utility helper remains outside the active API route-body surface:

| File | Calls | Active API route-body calls | Classification |
|---|---:|---:|---|
| `web/backend/app/utils/risk_utils.py` | 1 | 0 | deferred utility same-name helper |

Decision: do not create a combined risk/strategy/utility implementation lane.
Risk is closed. Strategy-management should be handled by a separate no-source
authorization gate. Utility remains deferred until there is contradictory
current-HEAD evidence or a separate approved decision package.

## Route / OpenAPI Verification

Runtime/OpenAPI smoke used placeholder import-time environment values and did
not run PM2 or stateful integration gates.

| Metric | Value |
|---|---:|
| FastAPI routes | 548 |
| OpenAPI paths | 500 |
| Duplicate operation IDs | 0 |

Target operations remain stable:

| Operation | Parameters | Request body | Operation ID |
|---|---:|---|---|
| `POST /api/v1/risk/alerts` | 0 | yes | `create_risk_alert_api_v1_risk_alerts_post` |
| `POST /api/v1/risk/var-cvar` | 0 | yes | `calculate_var_cvar_api_v1_risk_var_cvar_post` |
| `POST /api/v1/risk/beta` | 0 | yes | `calculate_beta_api_v1_risk_beta_post` |
| `POST /api/v1/strategy/strategies` | 0 | yes | `create_strategy_api_v1_strategy_strategies_post` |

## Verification

| Check | Result |
|---|---|
| Parent PR state | PR `#428` is `MERGED`; merge commit `daa4f22a557b054ab76042d4990b6e91d9faa7a7` |
| Focused risk provider test | `1 passed` |
| Ruff on G2.275 touched risk source/test paths | `All checks passed` |
| OpenSpec validation | `migrate-backend-singletons-to-lifecycle-di` valid |
| Runtime/OpenAPI smoke | `548` routes, `500` paths, `0` duplicate operation IDs |
| Mainline scope gate | `pass=True` |
| GitNexus staged CLI fallback | exit `0`; status `stale`; `9` changed files; `0` changed symbols; `0` affected processes; risk `low`; indexed `7688380f1e5b` -> current `daa4f22a557b` |

## Non-Goals

G2.276 does not:

- edit backend source or tests
- start strategy-management provider injection
- edit `web/backend/app/utils/risk_utils.py`
- change route registration, route paths, route methods, response models, or
  generated OpenAPI artifacts
- edit docs/api artifacts
- edit frontend, config, scripts, or OpenSpec
- run PM2 or stateful runtime gates

## Next Gate

Start after this PR is accepted:

`G2.277 no-source strategy get_monitoring_db route-provider authorization`

G2.277 should decide whether and how to authorize a path-limited
strategy-management source lane for `_strategy_crud_router.py` and its helper
surface. It must remain no-source unless the maintainer explicitly approves a
later implementation lane.

## Rollback

Revert the future PR carrying this closeout. Rollback only removes governance
evidence and steward-tree state for G2.276; it does not affect the already
merged G2.275 runtime implementation from PR `#428`.
