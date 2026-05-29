# Backend Service Lifecycle Residual Candidate Refresh After Data-Source Config Manager

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.235
- Status: for review
- Generated at: `2026-05-29T18:05:00+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `659a1dffb1d1306c8fe09ce2bdd9e17ab87dd8a5`
- Parent PR: `#387`
- Source edit authority: No

This package is a no-source residual refresh after G2.234 closed the active
`data_source_config.py` `get_config_manager()` route-body calls. It records the
next service lifecycle candidate decision input only. It does not authorize
backend source edits, test edits, route/OpenAPI changes, issue label movement,
OpenSpec proposal creation, PM2 commands, or frontend work.

## Parent State

PR `#387` merged G2.234 at
`659a1dffb1d1306c8fe09ce2bdd9e17ab87dd8a5`.

Current HEAD evidence preserves the G2.234 closeout:

| Surface | Current HEAD evidence |
|---|---|
| Active `data_source_config.py` route-body `get_config_manager()` calls | 0 |
| Route-local provider wrapper backing call | 1 |
| Active `manager: Depends(get_config_manager_dependency)` parameters | 9 |
| Legacy `data_source_config.old.py` direct call expressions | 8 |
| Legacy `data_source_config.old.py` registered | No |

The legacy `.old.py` calls remain false-positive residuals for the service
lifecycle conveyor. They are not deletion candidates from this package.

## Refresh Scan

| Evidence | Value |
|---|---:|
| Python files scanned | 1500 |
| app/OpenAPI smoke routes | 548 |
| app/OpenAPI smoke paths | 500 |
| `get_config_manager` active route-body calls | 0 |
| `get_calculator_factory` active API call expressions | 8 |
| `get_mock_data_manager` call expressions | 24 |
| `get_monitoring_db` call expressions | 12 |
| `get_postgres_async` call expressions | 30 |

Scan roots:

- `web/backend/app/api`
- `web/backend/app/services`
- `web/backend/app/tasks`
- `src/monitoring`
- `web/backend/app/mock`
- `web/backend/tests`
- `tests`

The GitNexus sample was taken from the existing `mystocks` graph index, which
was stale relative to the current worktree. It is recorded as directional risk
signal only; current-HEAD text scan and app/OpenAPI smoke are the binding facts
for this no-source package.

## Candidate Queue

| Rank | Candidate | Evidence | Disposition |
|---:|---|---|---|
| 1 | `get_calculator_factory` | 8 active API call expressions across `_monitoring_portfolio_router.py` and `monitoring_analysis.py`; GitNexus sample HIGH, 9 direct, 3 affected processes, 2 modules | Select G2.236 no-source monitoring calculator factory ownership / provider seam decision packet |
| 2 | `get_mock_data_manager` | 24 call expressions across API, adapters, mock factory, and tests; GitNexus sample CRITICAL, 27 direct, 4 processes, 8 modules | Defer; broad cross-domain mock/runtime seam |
| 3 | `get_monitoring_db` | 12 call expressions, 2 active definitions, GitNexus ambiguity across multiple matching symbols | Defer; needs ownership classification before authorization |
| 4 | `get_postgres_async` | 30 call expressions across signal monitoring, control-plane, monitoring watchlists, data-source config support, and monitoring internals | Defer; infrastructure data-access singleton, not a service lifecycle pilot |

## Decision

Select G2.236 as a no-source monitoring calculator factory ownership / provider
seam decision packet.

G2.236 should classify:

- active `get_calculator_factory()` API consumers
- route truth in `_monitoring_portfolio_router.py` and `monitoring_analysis.py`
- domain factory internals in `src/monitoring/domain/calculator_factory.py`
- whether a future path-limited provider injection or provider-wrapper lane is
  warranted
- forbidden scope for `get_mock_data_manager`, `get_monitoring_db`,
  `get_postgres_async`, route/OpenAPI changes, frontend, config, scripts, and
  OpenSpec changes

No source implementation is selected by G2.235.

## Retained / Deferred Surfaces

| Surface | Current disposition |
|---|---|
| `get_config_manager` | Closed for active route-body calls by PR `#386` / PR `#387` |
| `get_data_service` | Retained under indicator/data provider governance |
| `get_strategy_service` | Retained Strategy high-risk residual, not a generic next source lane |
| `get_unified_data_service` | Service-internal retained factory/facade residual |
| `get_mock_data_manager` | Deferred broad mock/runtime seam |
| `get_monitoring_db` | Deferred multi-definition monitoring/risk/strategy seam |
| `get_postgres_async` | Deferred infrastructure data-access singleton |

## Verification

| Check | Result |
|---|---|
| Current HEAD scan | Completed at `659a1dffb1d1306c8fe09ce2bdd9e17ab87dd8a5` |
| app/OpenAPI smoke | `routes=548`, `paths=500` |
| Source files changed | None |
| Test files changed | None |
| OpenSpec changes created | None |

Remaining required gates before merge:

- JSON parse for generated artifact and `steward-index.json`
- Markdown governance gate
- OpenSpec strict validate for `migrate-backend-singletons-to-lifecycle-di`
- Mainline scope gate
- GitNexus staged/compare detect for docs-only diff

## Next Gate

Review G2.235. If accepted, start G2.236 as a no-source monitoring calculator
factory ownership / provider seam decision packet. Do not start source work
from G2.235.
