# Backend Data Quality Route Provider Closeout Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: governance closeout / remaining candidate refresh review candidate
- Prepared at: `2026-05-28T01:52:33+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `2b0c3ce373fba38bacd62eff5436822527dccda1`
- Worktree branch: `g2-193-data-quality-route-provider-closeout-refresh`
- Scope: governance-only closeout and remaining surface refresh
- Source edit authority: none

Boundary note: this package records the G2.192 closeout and selects the next
governance gate. It does not authorize adapter constructor implementation,
legacy adapter edits, singleton wrapper deletion, `DataQualityMonitor` internals,
frontend edits, `src` edits, `docs/api` edits, or OpenSpec change/spec edits.

## Parent State

| Item | State | Evidence |
|---|---|---|
| G2.192 data-quality route provider implementation | Merged | PR `#345`, merge commit `2b0c3ce373fba38bacd62eff5436822527dccda1` |
| G2.193 closeout / remaining candidate refresh | For review | This report plus `.planning/codebase/generated/data-quality-route-provider-closeout-refresh-2026-05-28.json` |

## Closeout Result

The data-quality route-body provider migration is closed.

| Metric | Count |
|---|---:|
| `get_data_quality_monitor_provider` definitions | 1 |
| `_resolve_direct_call_dependency` definitions | 1 |
| `get_data_quality_monitor()` calls inside affected route bodies | 0 |
| `monitor_data_quality()` calls inside affected route bodies | 0 |
| `Depends(get_data_quality_monitor_provider)` route parameters | 7 |
| `_resolve_direct_call_dependency(...)` route fallbacks | 7 |

The route file still has one `get_data_quality_monitor()` call in
`get_data_quality_monitor_provider`. That is the retained provider backing
getter, not a route-body singleton call.

## Verification

| Check | Result |
|---|---|
| PR `#345` state | `MERGED` |
| PR `#345` merge commit | `2b0c3ce373fba38bacd62eff5436822527dccda1` |
| Focused pytest | `7 passed` |
| OpenAPI smoke | `openapi_paths=500`, `data_quality_paths=9`, `dependency_params_leaked=0` |

The OpenAPI smoke used local dummy environment variables only for required
settings, with repository root and `web/backend` on `PYTHONPATH`. It did not
write `.env`, start PM2, or modify runtime configuration.

## Remaining Surface Refresh

Current scan scope: `web/backend/app/api` and `web/backend/app/services`.

| Bucket | Files | `get_data_quality_monitor()` | `monitor_data_quality()` | Classification |
|---|---:|---:|---:|---|
| route | 1 | 1 | 0 | provider backing getter retained; route-body migration closed |
| adapter_split | 8 | 8 | 0 | remaining adapter constructor seam |
| service_adapter | 2 | 2 | 0 | remaining adapter compatibility seam |
| legacy_adapter | 2 | 2 | 0 | remaining legacy adapter compatibility seam |
| other | 1 | 1 | 0 | `market_data_adapter.py` compatibility surface |
| service_wrapper | 1 | 2 | 1 | retained singleton wrapper / backing API |

Remaining adapter-surface files:

- `web/backend/app/services/adapters_split/base_adapter.py`
- `web/backend/app/services/adapters_split/baostock_adapter.py`
- `web/backend/app/services/adapters_split/tushare_adapter.py`
- `web/backend/app/services/adapters_split/customer_adapter.py`
- `web/backend/app/services/adapters_split/byapi_adapter.py`
- `web/backend/app/services/adapters_split/akshare_adapter.py`
- `web/backend/app/services/adapters_split/efinance_adapter.py`
- `web/backend/app/services/adapters_split/tdx_adapter.py`
- `web/backend/app/services/adapters/dashboard_adapter.py`
- `web/backend/app/services/adapters/data_adapter.py`
- `web/backend/app/services/data_adapters/data_source.py`
- `web/backend/app/services/data_adapters/dashboard.py`
- `web/backend/app/services/market_data_adapter.py`
- `web/backend/app/services/_data_quality_monitor_singleton.py`

## Decision

G2.193 marks the route provider migration closed and does not start source
implementation. The next governance gate should be:

`G2.194 data-quality adapter constructor seam design / test-double decision package`

This next package should decide interface shape, test-double strategy, adapter
grouping, compatibility handling, and rollback boundaries before any adapter
constructor source edit is allowed.

## Explicit Non-Goals

- No adapter constructor implementation.
- No legacy adapter compatibility edits.
- No singleton wrapper deletion.
- No `DataQualityMonitor` implementation rewrite.
- No frontend edits.
- No `src` edits.
- No `docs/api` edits.
- No OpenSpec change/spec edits.

## Evidence Artifacts

| Artifact | Role |
|---|---|
| `.planning/codebase/generated/data-quality-route-provider-implementation-2026-05-28.json` | G2.192 implementation evidence |
| `docs/reports/quality/backend-data-quality-route-provider-implementation-2026-05-28.md` | G2.192 implementation report |
| `.planning/codebase/generated/data-quality-route-provider-closeout-refresh-2026-05-28.json` | G2.193 machine-readable closeout / refresh evidence |
| `docs/reports/quality/backend-data-quality-route-provider-closeout-refresh-2026-05-28.md` | G2.193 closeout / refresh report |
| `governance/mainline/task-cards/pr-346.yaml` | G2.193 governance PR scope card |
