# Backend MarketDataServiceV2 Route-Provider Closeout - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: closeout-prepared-for-review
- Workline: G2.28 `MarketDataServiceV2` route-provider closeout
- Parent issue: `#79`
- Implementation PR: https://github.com/chengjon/mystocks/pull/167
- Implementation merge commit: `8120f01a7022472b604f525ac9af2a517150c39b`
- Implementation PR merged at: `2026-05-23T07:26:57Z`
- Authorization PR: https://github.com/chengjon/mystocks/pull/166
- Authorization merge commit: `76a1e271fa602e692553acf2760f100ca88030aa`
- Closeout branch: `g2-28-market-data-v2-route-provider-closeout`
- Closeout HEAD: `8120f01a7022472b604f525ac9af2a517150c39b`
- Recorded at: `2026-05-23T15:38:42+08:00`

## Governance Boundary

This closeout is governance bookkeeping only. It records the merged G2.27
`MarketDataServiceV2` route-provider implementation and reruns post-merge
verification from the clean closeout worktree.

It does not authorize another service lifecycle DI candidate, dashboard helper
migration, market-data adapter migration, service consolidation, route/OpenAPI
contract changes, OpenSpec changes, issue label movement, PM2/runtime work,
frontend work, docs/API changes, or additional source edits.

## Completed Scope

PR `#167` implemented the G2.26-authorized route-provider scope:

- `web/backend/app/services/market_data_service_v2.py`
  - added `MARKET_DATA_SERVICE_V2_STATE_KEY`
  - added `install_market_data_service_v2(app, service=None)`
  - added `get_market_data_service_v2_dependency(request)`
  - retained `get_market_data_service_v2()` as the compatibility getter
- `web/backend/app/api/market_v2.py`
  - injected `MarketDataServiceV2` into all 13 route handlers
  - removed route-body direct `get_market_data_service_v2()` calls from those
    13 handlers
- `web/backend/tests/test_market_data_service_v2_lifecycle_di.py`
  - covers provider installation, request-state fallback, route signature
    injection, and compatibility fallback
- `docs/reports/quality/backend-market-data-service-v2-route-provider-implementation-2026-05-23.md`
  - records implementation evidence and rollback boundaries
- `governance/mainline/task-cards/pr-167.yaml`
  - records implementation scope and gates
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
  - records G2.27 as implementation prepared for review

## Preserved Compatibility Boundary

The implementation preserved `get_market_data_service_v2()` as the legacy
compatibility getter. This is intentional because `dashboard_data_source.py`
still has two non-route helper callers that were explicitly excluded from the
route-provider implementation scope.

Any dashboard helper migration, adapter migration, market-data package provider
work, service consolidation, or compatibility getter cleanup must be routed
through a separate packet with impact evidence, exact write scope, tests,
rollback plan, and review gate.

## Post-Merge Verification

All commands below were run from the G2.28 closeout worktree at HEAD
`8120f01a7022472b604f525ac9af2a517150c39b`.

| Check | Result |
|---|---|
| Focused lifecycle DI test | `4 passed in 1.23s` |
| `ruff check` on touched Python files | passed |
| `black --check` on touched Python files | passed |
| `app.main` import smoke | status `0`, `app-main-import-ok` |
| OpenAPI smoke | paths=`500`, `/api/v2/market` paths=`13`, duplicate operationIds=`0` |
| PR `#167` GitHub state | `MERGED` |

GitHub PR `#167` checks:

| Check | Result |
|---|---|
| `Validate API Contracts` | pass |
| `Generate TypeScript Types` | pass |
| `Detect Breaking Changes` | pass/skipped according to workflow matrix |
| `Generate Contract Validation Report` | pass |
| `Mainline Governance Gate` | pass |
| `check-compliance` | pass |
| weekly/notify jobs | skipped as expected |

Post-merge route-surface scan:

| File | Direct `get_market_data_service_v2()` calls | Injected route params | Notes |
|---|---:|---:|---|
| `web/backend/app/api/market_v2.py` | 0 | 13 | Approved route surface migrated |
| `web/backend/app/api/dashboard_data_source.py` | 2 | 0 | Non-route helper compatibility callers intentionally unchanged |

Provider seam scan:

| Symbol or field | Present |
|---|---|
| `MARKET_DATA_SERVICE_V2_STATE_KEY` | yes |
| `install_market_data_service_v2` | yes |
| `get_market_data_service_v2_dependency` | yes |
| `get_market_data_service_v2` compatibility getter | yes |

## Current State After Merge

- `MarketDataServiceV2` now has a merged route-provider lifecycle DI seam for
  the `market_v2.py` route surface.
- All 13 `market_v2.py` routes receive `MarketDataServiceV2` through the
  provider dependency.
- Direct route-body calls to `get_market_data_service_v2()` in `market_v2.py`
  are now `0`.
- `dashboard_data_source.py` retains its two compatibility helper calls by
  design.
- The OpenAPI schema remains stable at `500` paths with `13` `/api/v2/market`
  paths and `0` duplicate operationIds.
- Issue `#79` remains the parent service lifecycle DI issue and should not be
  moved to implementation-ready state by this closeout.
- No next service lifecycle DI candidate is selected by this closeout.

## Next Gate

Human review of this closeout packet.

If accepted, select the next service lifecycle DI lane only through a separate
evidence or authorization packet. That packet must define the exact target,
impact evidence, write scope, tests, rollback plan, and forbidden scope before
any source edit.
