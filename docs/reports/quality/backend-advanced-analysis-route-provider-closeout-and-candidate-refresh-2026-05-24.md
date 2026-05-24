# Backend AdvancedAnalysis Route Provider Closeout And Candidate Refresh - 2026-05-24

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Status: review-ready.

Boundary note: this packet records closeout and candidate-refresh evidence only.
It does not authorize backend source edits, test edits, route edits, OpenAPI
behavior changes, docs/API changes, generated client updates, frontend changes,
PM2 execution, OpenSpec changes, issue-label changes, compatibility getter
retirement, or selection of a new implementation target.

This report is a governance-only G2.46 closeout and current-head service lifecycle DI refresh after PR `#185` merged the G2.45 `AdvancedAnalysisService` route-provider migration.

It does not authorize source edits, OpenSpec changes, issue-label changes, compatibility getter retirement, PM2 stateful gates, frontend changes, generated client updates, or selection of the next implementation lane.

## Source Snapshot

| Field | Value |
|---|---|
| Worktree | `.worktrees/g2-46-advanced-analysis-closeout-candidate-refresh` |
| Branch | `g2-46-advanced-analysis-closeout-candidate-refresh` |
| Current HEAD | `059638b573c6f2586537973e2a4b396f0ce156d7` |
| HEAD subject | `Merge pull request #185 from chengjon/g2-45-advanced-analysis-route-provider-migration` |
| Review timestamp | `2026-05-24T03:02:17+08:00` |
| Parent PR | `#185` |
| Parent PR state | `MERGED` |
| Parent PR URL | `https://github.com/chengjon/mystocks/pull/185` |
| Issue `#79` state | `OPEN`, labels: `needs-triage` |
| Issue `#92` state | `OPEN`, labels: `enhancement`, `ready-for-human`, `ready-for-downstream` |

## Closeout Evidence

| Check | Result | Interpretation |
|---|---:|---|
| Focused lifecycle DI test | `4 passed in 4.04s` | `AdvancedAnalysisService` route-provider behavior remains covered by the focused test. |
| `advanced_analysis_api.py` class `Depends()` sites | `0` | G2.45 route-level class injection surface is closed. |
| `advanced_analysis_api.py` provider `Depends(get_advanced_analysis_service_dependency)` sites | `14` | All AdvancedAnalysis route dependencies now use the app-state provider seam. |
| Direct route calls to `get_advanced_analysis_service()` | `0` | The route module no longer calls the compatibility getter directly. |
| `ADVANCED_ANALYSIS_SERVICE_STATE_KEY` present | `true` | The service has an app-state lifecycle key. |
| `install_advanced_analysis_service` present | `true` | Startup installation hook is present. |
| `get_advanced_analysis_service_dependency` present | `true` | FastAPI dependency provider is present. |
| `get_advanced_analysis_service()` compatibility getter present | `true` | Compatibility fallback remains intentionally preserved. |

Configured app/OpenAPI smoke was run with the documented local environment overrides and produced:

| Metric | Value |
|---|---:|
| FastAPI routes | `548` |
| OpenAPI paths | `500` |
| Operation IDs | `536` |
| Duplicate operation IDs | `0` |
| AdvancedAnalysis paths | `14` |
| Captured warnings | `0` |

## Current-Head Candidate Refresh

The current-head refresh scanned service and route dependency files after PR `#185` merged. It is a planning/candidate signal refresh only, not deletion evidence and not implementation authorization.

| Metric | Value |
|---|---:|
| Service files scanned | `152` |
| Provider signal files | `8` |
| Getter signal files | `24` |
| Route provider dependency files | `11` |
| Route provider dependency sites | `72` |

Current completed route-provider modules:

| Service module | Provider seam | State key |
|---|---|---|
| `web/backend/app/services/advanced_analysis_service.py` | `install_advanced_analysis_service`, `get_advanced_analysis_service_dependency` | `ADVANCED_ANALYSIS_SERVICE_STATE_KEY` |
| `web/backend/app/services/announcement_service.py` | `install_announcement_service`, `get_announcement_service_dependency` | `ANNOUNCEMENT_SERVICE_STATE_KEY` |
| `web/backend/app/services/email_service.py` | `install_email_service`, `get_email_service_dependency` | `EMAIL_SERVICE_STATE_KEY` |
| `web/backend/app/services/market_data_service_v2.py` | `get_market_data_service_v2_dependency` | none detected |
| `web/backend/app/services/stock_search_service/stock_search_service.py` | `install_stock_search_service`, `get_stock_search_service_dependency` | `STOCK_SEARCH_SERVICE_STATE_KEY` |
| `web/backend/app/services/tdx_service.py` | `install_tdx_service`, `get_tdx_service_dependency` | `TDX_SERVICE_STATE_KEY` |
| `web/backend/app/services/tradingview_widget_service.py` | `install_tradingview_service`, `get_tradingview_service_dependency` | `TRADINGVIEW_SERVICE_STATE_KEY` |
| `web/backend/app/services/watchlist_service.py` | `install_watchlist_service`, `get_watchlist_service_dependency` | `WATCHLIST_SERVICE_STATE_KEY` |

Current route provider dependency usage:

| Route module | Sites | Provider dependency |
|---|---:|---|
| `web/backend/app/api/advanced_analysis_api.py` | `14` | `get_advanced_analysis_service_dependency` |
| `web/backend/app/api/announcement/routes.py` | `11` | `get_announcement_service_dependency` |
| `web/backend/app/api/dashboard_data_source.py` | `1` | `get_market_data_service_v2_dependency` |
| `web/backend/app/api/dashboard.py` | `3` | `get_data_source_dependency` |
| `web/backend/app/api/market_v2.py` | `13` | `get_market_data_service_v2_dependency` |
| `web/backend/app/api/market/market_data_request.py` | `1` | `get_stock_search_service_dependency` |
| `web/backend/app/api/notification.py` | `6` | `get_email_service_dependency` |
| `web/backend/app/api/stock_search/stock_search_result.py` | `5` | `get_stock_search_service_dependency` |
| `web/backend/app/api/tdx.py` | `5` | `get_tdx_service_dependency` |
| `web/backend/app/api/tradingview.py` | `6` | `get_tradingview_service_dependency` |
| `web/backend/app/api/watchlist.py` | `7` | `get_watchlist_service_dependency` |

## Candidate Interpretation

G2.45 is closed at the evidence level: the AdvancedAnalysis route module has no remaining class-based route dependency sites and still preserves the compatibility getter. This is the expected endpoint of the G2.44 authorization.

The completed provider seam count is now `8` service modules, with `11` route modules and `72` route dependency sites using provider dependencies. This broadens the service lifecycle DI pattern, but it does not make any remaining getter safe to delete.

The getter scan is intentionally treated as heuristic planning input. It can be polluted by governance artifacts, generated reports, and compatibility re-export modules. A compatibility getter with no active route call should still require a dedicated consumer matrix and retirement/retention decision before any implementation branch removes it.

Broad seams remain excluded from direct pilot selection without a separate design packet:

- `WencaiService`
- `MarketDataService`
- `UnifiedDataService`
- `DataService`
- `StrategyService`
- `TechnicalAnalysisService`

## Decision Boundary

This packet records:

- PR `#185` is merged.
- `AdvancedAnalysisService` route-provider migration is closed at current HEAD `059638b573c6f2586537973e2a4b396f0ce156d7`.
- Issue `#79` remains open and still needs triage for the broader service singleton lifecycle lane.
- Issue `#92` remains open as a governance/downstream decision umbrella.
- No next implementation target is selected.
- No compatibility getter is approved for retirement.

## Recommended Next Gate

Run a separate G2.47 candidate selection and usefulness/ownership triage packet before any new service lifecycle DI source branch.

The G2.47 packet should:

- Regenerate a stricter current-head service getter/provider inventory.
- Filter out governance/report references before interpreting external references.
- Separate active route dependencies, compatibility fallbacks, factory helpers, process-level singletons, DB/session-backed services, and broad data seams.
- Produce one of these outcomes: no next target, a decision-only authorization packet, or a human-reviewed implementation authorization for exactly one narrow target.

## Verification Commands

The focused checks used for this packet were:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_advanced_analysis_service_lifecycle_di.py -q -n 0 --tb=short --no-cov
```

```bash
POSTGRESQL_HOST=localhost POSTGRESQL_USER=mystocks POSTGRESQL_PASSWORD=mystocks JWT_SECRET_KEY=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef BACKEND_PORT=8020 BACKEND_BACKUP_PORT=8021 PYTHONPATH=web/backend:. python - <<'PY'
import warnings
from app.main import app
with warnings.catch_warnings(record=True) as caught:
    schema = app.openapi()
operation_ids = []
for path, methods in schema.get("paths", {}).items():
    for method, operation in methods.items():
        if isinstance(operation, dict) and operation.get("operationId"):
            operation_ids.append(operation["operationId"])
advanced_paths = [path for path in schema.get("paths", {}) if "advanced-analysis" in path]
print({
    "routes": len(app.routes),
    "paths": len(schema.get("paths", {})),
    "operation_ids": len(operation_ids),
    "duplicate_operation_ids": len(operation_ids) - len(set(operation_ids)),
    "advanced_paths": len(advanced_paths),
    "warnings": len(caught),
})
PY
```
