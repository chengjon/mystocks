# Backend Domain Router Reconciliation

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> Historical evidence note: this report records the 2026-05-18 local reconciliation
> state for `openspec/changes/consolidate-backend-api-domain-routers/`. Current
> truth remains the code, exported OpenAPI schema, `architecture/STANDARDS.md`,
> and the latest executed verification.

## Purpose

Close the evidence gaps for the backend API domain router consolidation change
without reopening the already-completed P3 implementation batches.

This report is evidence-only except for the targeted test maintenance performed
in this batch:

- `web/backend/tests/test_route_governance_static.py`: stopped treating the
  retired `web/backend/app/api/technical/routes.py` orphan as an active scoped
  router and added an explicit retirement assertion.
- `web/backend/app/api/strategy_management/get_monitoring_db.py`: restored the
  backward-compatible re-export wrapper after the P3 split.
- `web/backend/tests/test_strategy_runtime_fallback.py`: aligned monkeypatch
  targets with the split strategy CRUD router and helper module.

## Source Evidence

| Evidence | Result |
|---|---|
| Orchestration artifact | `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md` exists |
| Route/OpenAPI baseline | `docs/reports/quality/backend-route-table-openapi-baseline-2026-05-18.md` exists |
| Prefix-expanded route table | `docs/reports/quality/generated/backend-fullpath-route-table.md` and `.json` exist |
| OpenAPI baseline | `docs/reports/quality/generated/openapi-before.json` exists |
| P3 implementation evidence | `docs/reports/quality/backend-audit-P3-progress-report.md` |

## Runtime Endpoint Inventory

Generated from the current FastAPI app route table.

| Domain | Runtime routes | Schema exposed | Primary modules |
|---|---:|---:|---|
| announcement | 14 | 14 | `app.api.announcement.routes` |
| strategy | 65 | 64 | `app.api.strategy_mgmt`, `app.api.ml`, `app.api.strategy_management._strategy_crud_router`, `app.api.strategy_management._model_backtest_router` |
| risk | 38 | 37 | `app.api.risk.alerts`, `app.api.risk.stop_loss`, `app.api.risk.metrics`, `app.api.risk.v31` |
| trading | 31 | 31 | `app.api.trade.routes`, `app.api.tradingview`, `app.api.trade.reconciliation_routes`, `app.api.v1.trading.session` |
| backup | 13 | 13 | `app.api.backup_recovery_secure.*` |

Interpretation:

- `announcement` is fully package-owned and schema-exposed.
- `strategy` still intentionally retains concrete legacy routes from
  `app.api.strategy_mgmt` plus one runtime-only compatibility redirect.
- `risk` is package-owned; one WebSocket/update path is runtime-only.
- `trading` and `backup` remain deferred high-risk follow-ups and are not hidden
  inside this OpenSpec change.

## Consumer Matrix

Scanned API path references across backend, frontend, tests, scripts, docs,
OpenSpec, planning, and governance files.

| Domain / prefix group | Backend runtime | Frontend runtime | Backend tests | Frontend tests | Scripts | Docs/governance |
|---|---:|---:|---:|---:|---:|---:|
| announcement | 3 files / 19 hits | 4 / 20 | 11 / 66 | 2 / 44 | 1 / 2 | 77 / 328 |
| strategy | 16 / 43 | 18 / 44 | 46 / 386 | 19 / 72 | 5 / 30 | 210 / 1257 |
| risk | 6 / 6 | 13 / 29 | 17 / 148 | 7 / 31 | 3 / 13 | 100 / 446 |
| trading deferred | 7 / 11 | 16 / 62 | 29 / 141 | 8 / 48 | 3 / 18 | 140 / 478 |
| backup deferred | 3 / 46 | 0 / 0 | 3 / 52 | 0 / 0 | 0 / 0 | 22 / 130 |

Consumer interpretation:

- `announcement`, `strategy`, and `risk` have enough active test and frontend
  references to require route-level smoke before any future deletion.
- `strategy-mgmt` remains active at runtime because concrete legacy endpoints
  are still registered before the catch-all redirect.
- `trading` and `backup` have non-trivial runtime and test consumers; they must
  remain deferred until separate OpenSpec follow-up changes define ownership,
  compatibility, rollback, and verification.

## Shim And Compatibility Status

| Surface | Current status | Exit criteria |
|---|---|---|
| `app.api.strategy_mgmt` | Active legacy concrete router | Migrate remaining runtime caller(s), update fixtures/docs, then remove registration in a later approved batch |
| `app.api._strategy_mgmt_compat` | Runtime compatibility redirect, hidden from OpenAPI schema | Retire only after `/api/strategy-mgmt/*` consumers are proven absent |
| `app.api.strategy_management.get_monitoring_db` | Backward-compatible re-export wrapper | Retain while split-module imports and old references coexist |
| `app.api.auth_compat` | Compatibility surface outside this change | Keep out of C-line scope |
| `app.api.data.market` | Data API module, not the retired root `market.py` shim | Keep out of C-line scope |

Cleanup rule:

No additional shim, flat module, package, or compatibility prefix should be
deleted in the same batch that records a canonical path unless rollback evidence
and consumer absence are proven for that exact surface.

## OpenAPI Diff

Compared `docs/reports/quality/generated/openapi-before.json` with the current
runtime `app.openapi()` result.

| Metric | Value |
|---|---:|
| Baseline paths | 501 |
| Current paths | 500 |
| Added paths | 0 |
| Removed paths | 1 |
| Duplicate operation IDs | 0 |

Removed path:

- `/api/strategy-mgmt/{path}`

Interpretation:

The removed path is the strategy-mgmt catch-all compatibility redirect that is
intentionally runtime-only and hidden from the OpenAPI schema. No new route
exposure drift was detected.

## Verification

| Check | Result |
|---|---|
| Import smoke for canonical, legacy, compatibility, and retired router paths | 16/16 matched expected import or retirement state |
| `pytest web/backend/tests/test_route_governance_static.py -q -n 0 --tb=short --no-cov` | 7 passed |
| `pytest web/backend/tests/test_announcement_routes_regressions.py -q -n 0 --tb=short --no-cov` | 1 passed |
| `pytest web/backend/tests/test_strategy_runtime_fallback.py -q -n 0 --tb=short --no-cov` | 7 passed |
| Clean HEAD risk verification: `pytest web/backend/tests/test_risk_runtime_bootstrap_regressions.py -q -n 0 --tb=short --no-cov` in a temporary worktree | 8 passed |
| Frontend targeted API smoke: `npx vitest run src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/api/services/__tests__/strategyService.msw.spec.ts tests/unit/config/strategy-route-canonical-paths.spec.ts tests/unit/config/risk-route-canonical-paths.spec.ts src/views/risk/__tests__/Overview.spec.ts` | 5 files passed, 26 tests passed |
| Frontend type generation: `python scripts/generate_frontend_types.py` | Generated strategy/common/trading/common barrel outputs successfully; `NonBlankString` now maps to `string` |
| Frontend type-check: `npm run type-check` | Passed |
| PM2 named equivalent: `bash scripts/run_e2e_pm2.sh` | PM2 startup succeeded, `mystocks-backend` / `mystocks-frontend` reached online state during the run, and 14 Chromium navigation-consistency tests passed |

Current dirty-worktree boundary:

- `web/backend/app/api/risk/stop_loss.py` has an unrelated unstaged change that
  removes the `ENHANCED_RISK_FEATURES_AVAILABLE` import.
- Because of that unrelated dirty file, the current workspace risk test can fail
  even though clean HEAD passes. This report does not revert or include that
  parallel change.
- `web/backend/app/api/signal_monitoring/signal_history_response.py` has an
  unrelated unstaged change that removes the local `router = APIRouter()`
  definition. A manual PM2 restart after the passing named-equivalent run hit
  `NameError: name 'router' is not defined` and produced a backend crash loop.
  The temporary PM2 processes were deleted afterward to avoid leaving a bad
  runtime state.

## Rollback Triggers

| Domain | Rollback trigger | Rollback action |
|---|---|---|
| announcement | Any `/api/announcement/*` route disappears or gains duplicate runtime exposure | Restore `announcement/` package registration from the last passing commit |
| strategy | Canonical `/api/v1/strategy/*` behavior regresses, or legacy `/api/strategy-mgmt/*` concrete routes stop serving active consumers before approved retirement | Restore strategy management router registration and compatibility redirect from the last passing commit |
| risk | `/api/v1/risk/*` package routes fail import/runtime smoke or frontend risk consumers regress | Restore risk package registration and route tests from the last passing commit |
| trading | Any attempt to change ownership without a separate approved proposal | Stop the batch; keep `trading_runtime.py` ownership unchanged |
| backup | Any attempt to collapse secure backup routes into a generic router without security-boundary review | Stop the batch; keep `backup_recovery_secure/` ownership unchanged |

## Closure Position

The C-line can now close evidence tasks for baseline confirmation, endpoint
inventory, consumer matrix, shim identification, trading/backup deferral,
OpenAPI diff, route import smoke, targeted backend tests, frontend API smoke,
PM2 named-equivalent startup, route exposure drift, and compatibility status
documentation.

It is execution-complete for the task checklist. The remaining governance action
is OpenSpec archive, which is separate from checklist completion and should be
handled later because the workspace still contains unrelated dirty changes.
