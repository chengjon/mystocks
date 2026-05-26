# Backend Unused IntegratedServices Facade Getter Retirement Closeout - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Closeout prepared for review.

This packet records the G2.136 source implementation as merged and closes the unused IntegratedServices service-facade getter retirement lane. It is governance-only and does not modify runtime code, tests, API routes, OpenAPI exposure, PM2 workflow, OpenSpec changes, GitHub issue labels, or product behavior.

## Parent Merge

| Field | Value |
|---|---|
| Parent PR | `#289` |
| Parent state | `MERGED` |
| Parent merged at | `2026-05-26T04:51:23Z` |
| Parent merge commit | `541a225b5cbc90807d8cc7af20d0ffd42b07fd2d` |
| Parent title | `G2.136 Retire unused IntegratedServices facade getters` |
| Parent URL | `https://github.com/chengjon/mystocks/pull/289` |

## Current-Head Scan

Current HEAD: `541a225b5cbc90807d8cc7af20d0ffd42b07fd2d`.

| Retired facade getter | Definition count |
|---|---:|
| `get_trading_data_service` | `0` |
| `get_analysis_data_service` | `0` |
| `get_data_api_service` | `0` |
| `get_database_service` | `0` |
| `get_websocket_service` | `0` |
| `get_cache_service` | `0` |

| Locked facade getter | Definition count |
|---|---:|
| `get_integrated_services` | `1` |
| `get_market_data_service` | `1` |
| `get_risk_calculator` | `1` |
| `get_risk_monitoring` | `1` |
| `get_risk_alerts` | `1` |
| `get_risk_settings` | `1` |
| `get_risk_dashboard` | `1` |

## Verification

| Gate | Result |
|---|---|
| Parent PR state | `#289` is `MERGED` at `541a225b5cbc90807d8cc7af20d0ffd42b07fd2d` |
| Focused closeout test | `2 passed in 0.28s` |
| Import smoke | `{'removed_absent': True, 'locked_callable': True}` |
| Exact current-head scan | Retired definitions `0`; locked definitions `1` |

## Closeout Result

The unused IntegratedServices service-facade getter retirement lane is ready to close after this governance PR is reviewed and merged.

The next steward-tree gate is a fresh remaining service lifecycle candidate refresh before selecting another implementation lane.

## Boundary

This closeout does not change runtime source, tests, route paths, response contracts, OpenAPI exposure, PM2 workflow, frontend files, OpenSpec changes, GitHub issue labels, or product behavior.
