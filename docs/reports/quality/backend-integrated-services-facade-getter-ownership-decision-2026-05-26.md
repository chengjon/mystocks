# Backend IntegratedServices Facade Getter Ownership Decision - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Decision prepared for review.

This packet resolves the G2.133 question about LOW graph-risk getters in `web/backend/app/services/__init__.py`. It is decision-only and does not authorize source edits, tests edits, OpenSpec changes, PM2 execution, route changes, OpenAPI exposure changes, or issue-label movement.

## Decision

Treat the `web/backend/app/services/__init__.py` getter group as a shared IntegratedServices compatibility facade owned by the IntegratedServices composition root.

These functions are not equivalent to the already completed route-surface singleton getter retirements. Each delegates through `get_integrated_services()` and belongs to the same composition-root facade. The group must be handled as an ownership decision and future narrow authorization, not as isolated opportunistic deletion.

## Parent State

| Field | Value |
|---|---|
| Parent PR | `#286` |
| Parent state | `MERGED` |
| Parent merged at | `2026-05-26T04:02:08Z` |
| Parent merge commit | `bc2d2a891787484b7fc65dd8fec61e19d66345bf` |
| Parent title | `G2.133 Refresh service lifecycle candidates after WatchlistService` |
| Parent URL | `https://github.com/chengjon/mystocks/pull/286` |

## Facade Ownership

| Symbol | Definition | Ownership decision |
|---|---|---|
| `get_integrated_services` | `web/backend/app/services/__init__.py:227` | Retain as the composition-root accessor |
| `get_market_data_service` | `web/backend/app/services/__init__.py:260` | Retain for now; same-name package provider and test consumers require separate disambiguation |
| `get_trading_data_service` | `web/backend/app/services/__init__.py:266` | Eligible for a future unused-facade retirement authorization packet |
| `get_analysis_data_service` | `web/backend/app/services/__init__.py:272` | Eligible for a future unused-facade retirement authorization packet |
| `get_data_api_service` | `web/backend/app/services/__init__.py:278` | Eligible for a future unused-facade retirement authorization packet |
| `get_database_service` | `web/backend/app/services/__init__.py:284` | Eligible for a future unused-facade retirement authorization packet |
| `get_websocket_service` | `web/backend/app/services/__init__.py:290` | Eligible for a future unused-facade retirement authorization packet |
| `get_cache_service` | `web/backend/app/services/__init__.py:296` | Eligible for a future unused-facade retirement authorization packet |

The risk helper facade functions in the same file are out of this service-getter queue:

- `get_risk_calculator`
- `get_risk_monitoring`
- `get_risk_alerts`
- `get_risk_settings`
- `get_risk_dashboard`

## Evidence

| Evidence | Result |
|---|---|
| Current HEAD | `bc2d2a891787484b7fc65dd8fec61e19d66345bf` |
| `get_integrated_services` impact | GitNexus MEDIUM, impacted `13`, direct `13`, processes `0` |
| Six eligible service facades | Active app calls excluding definitions `0`; test calls `0`; prior GitNexus impact LOW / impacted `0` |
| `get_market_data_service` | Active app calls excluding definition `0`, but package token exists in `web/backend/app/services/market_data_service/__init__.py` and tests still reference market-data getter/provider names |
| G2.133 source queue | `get_tdx_service`, `get_data_service`, `get_strategy_service`, and `get_streaming_service` remain HIGH/CRITICAL holds |

## Next Gate

Prepare a narrow unused IntegratedServices service-facade getter retirement authorization packet.

The future authorization packet may consider only:

- `get_trading_data_service`
- `get_analysis_data_service`
- `get_data_api_service`
- `get_database_service`
- `get_websocket_service`
- `get_cache_service`

The future authorization packet must explicitly exclude:

- `get_integrated_services`
- `get_market_data_service`
- Risk helper facades
- `get_tdx_service`
- `get_data_service`
- `get_strategy_service`
- `get_streaming_service`

## Future Implementation Requirements

Future source work is not authorized by this packet. If a later authorization packet is accepted, implementation must include:

- Exact allowed path list before edits.
- Pre-edit GitNexus impact for every edited symbol.
- TDD red proof for the selected removable facade names.
- Import smoke for `app.services`.
- Focused tests covering the selected facade names and excluded names.
- Staged GitNexus scope check.
- Mainline scope gate.
- PR review.

## Boundary

No runtime source, tests, route paths, response contracts, OpenAPI exposure, PM2 workflow, OpenSpec changes, GitHub issue labels, or product behavior are changed by this decision packet.
