# Backend Service Lifecycle Candidate Refresh After Integrated Facade Retirement

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-26

Current HEAD: `090c0c30a7ac64c75e30febce1b3f6e4d20eee1c`

Parent closeout: G2.137 / PR `#290`

Boundary note: this is a governance-only candidate refresh. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, or GitHub issue labels. It does not authorize implementation.

## Purpose

Refresh the service lifecycle DI candidate pool after the unused IntegratedServices service-facade getter lane was closed.

The parent lane retired these six unused facade getters from `web/backend/app/services/__init__.py`:

- `get_trading_data_service`
- `get_analysis_data_service`
- `get_data_api_service`
- `get_database_service`
- `get_websocket_service`
- `get_cache_service`

This report confirms the post-closeout state and selects only the next authorization candidate. The actual source edit must be separately authorized.

## Scan Snapshot

| Metric | Value |
|---|---:|
| Service Python files | 152 |
| Backend app Python files | 575 |
| Backend API Python files | 219 |
| Backend test Python files | 205 |
| `def get_*` definitions under `web/backend/app/services` | 54 |
| Root facade getters in `web/backend/app/services/__init__.py` | 7 |
| FastAPI dependency/provider getters | 9 |
| Zero-external-reference getter definitions | 9 |

IntegratedServices facade verification:

| Group | Expected | Current |
|---|---:|---:|
| Retired facade getter definitions | 0 each | 0 each |
| Locked facade getter definitions | 1 each | 1 each |

Locked facade getters remain:

- `get_integrated_services`
- `get_market_data_service`
- `get_risk_calculator`
- `get_risk_monitoring`
- `get_risk_alerts`
- `get_risk_settings`
- `get_risk_dashboard`

## Candidate Decision

Selected next authorization candidate:

| Candidate | File | Reason | Current gate |
|---|---|---|---|
| `get_backtest_engine` / `_backtest_engine` | `web/backend/app/services/backtest_engine.py` | GitNexus reports LOW risk, impacted `0`, direct `0`, processes `0`; exact text scan finds only the defining service file in backend code | Future authorization-only lane |

This selection does not authorize deleting `get_backtest_engine` or `_backtest_engine`. It only identifies the next small authorization package to prepare.

## Holds And Exclusions

| Symbol or group | Disposition | Reason |
|---|---|---|
| `get_tdx_service` | Hold | GitNexus reports CRITICAL risk, impacted `6`, direct `2`, processes `5`; API dashboard flows still depend on it |
| `get_data_service` | Hold | Existing high-risk design lane; not selected by this refresh |
| `get_strategy_service` | Hold | Existing high-risk design lane; not selected by this refresh |
| `get_streaming_service` | Hold | Broad caller surface; not selected by this refresh |
| `get_market_data_service` root facade | Retain | Locked IntegratedServices composition/root facade |
| Risk helper facades in `web/backend/app/services/__init__.py` | Retain | Locked compatibility facades from the IntegratedServices ownership decision |
| `get_indicator_registry_dependency` | Exclude from service getter retirement queue | Active FastAPI route provider seam with API/test references |
| `get_tradingview_service_dependency` | Exclude from service getter retirement queue | Active FastAPI route provider seam with API/test references |
| `get_company_news` | Exclude | Stock-search helper callable, not a service singleton lifecycle getter |

## Evidence

Local evidence collected in this lane:

- Current file-count scan at HEAD `090c0c30a7`.
- Current `def get_*` scan under `web/backend/app/services`.
- Current exact definition-count scan for retired and locked IntegratedServices facades.
- GitNexus impact for `get_backtest_engine`: LOW, impacted `0`.
- GitNexus impact for `get_tdx_service`: CRITICAL, impacted `6`, direct `2`, processes `5`.
- Exact text reference checks for selected low-risk and excluded candidates.

Generated artifact:

- `.planning/codebase/generated/service-lifecycle-candidate-refresh-after-integrated-facade-retirement-2026-05-26.json`

## Next Gate

Recommended next lane:

G2.139 BacktestEngine singleton/getter retirement authorization.

Expected mode:

- Authorization-only.
- Define exact allowed paths, tests, rollback, and pre-edit GitNexus impact requirements.
- Do not edit `web/backend/app/services/backtest_engine.py` until that authorization lane is accepted.

## Non-Goals

- No backend source or test edit.
- No getter deletion.
- No route/API behavior change.
- No OpenAPI exposure change.
- No frontend, PM2, OpenSpec, or issue-label change.
- No authorization for `get_tdx_service`, `get_data_service`, `get_strategy_service`, `get_streaming_service`, route provider seams, or root/risk compatibility facades.
