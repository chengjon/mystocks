# Backend Unused IntegratedServices Facade Getter Retirement Authorization - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Authorization prepared for review.

This packet authorizes the shape of a future source lane only. It does not edit source code, tests, OpenSpec content, route paths, OpenAPI exposure, PM2 workflow, GitHub issue labels, or product behavior.

## Parent Decision

| Field | Value |
|---|---|
| Parent PR | `#287` |
| Parent state | `MERGED` |
| Parent merged at | `2026-05-26T04:14:13Z` |
| Parent merge commit | `65498c4565db877ee187f9ceb6dd140b7e4db7fd` |
| Parent title | `G2.134 Decide IntegratedServices facade getter ownership` |
| Parent URL | `https://github.com/chengjon/mystocks/pull/287` |

## Future Source Lane

Future lane name:

`G2.136 unused IntegratedServices service-facade getter retirement implementation`

Future source work is not performed by this packet. If this authorization is accepted, a separate implementation branch may edit only:

- `web/backend/app/services/__init__.py`
- `web/backend/tests/test_integrated_services_facade_getter_retirement.py`
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/unused-integrated-services-facade-getter-retirement-implementation-2026-05-26.json`
- `docs/reports/quality/backend-unused-integrated-services-facade-getter-retirement-implementation-2026-05-26.md`
- `governance/mainline/task-cards/pr-288.yaml`

## Authorized Removable Symbols

Only the following `web/backend/app/services/__init__.py` facade symbols are eligible for future removal:

- `get_trading_data_service`
- `get_analysis_data_service`
- `get_data_api_service`
- `get_database_service`
- `get_websocket_service`
- `get_cache_service`

These were selected because G2.134 classified them as unused service-facade getters with no active app calls excluding their own definitions and no direct test calls in the current scan.

## Locked Symbols

The future implementation must not remove, rename, alter, or migrate:

- `get_integrated_services`
- `get_market_data_service`
- `get_risk_calculator`
- `get_risk_monitoring`
- `get_risk_alerts`
- `get_risk_settings`
- `get_risk_dashboard`
- `get_tdx_service`
- `get_data_service`
- `get_strategy_service`
- `get_streaming_service`

`get_market_data_service` remains locked because same-name package provider and tests require a separate graph/text disambiguation decision.

## Future Forbidden Paths

The future implementation must not edit:

- `web/backend/app/api/**`
- `web/backend/app/services/market_data_service/**`
- `web/backend/app/services/tdx_service.py`
- `web/backend/app/services/data_service.py`
- `web/backend/app/services/strategy_service.py`
- `web/backend/app/services/realtime_streaming_service.py`
- `web/frontend/**`
- `src/**`
- `docs/api/**`
- `docs/guides/**`
- `config/**`
- `scripts/**`
- `openspec/changes/**`
- `openspec/specs/**`

## Future Acceptance Criteria

The future source lane must:

- Run pre-edit GitNexus impact for each removable symbol.
- Use TDD: first add or adjust a focused test that fails because the removable facade symbols still exist.
- Remove only the six authorized removable symbols from `web/backend/app/services/__init__.py`.
- Keep `IntegratedServices` construction unchanged.
- Keep `get_integrated_services`, `get_market_data_service`, and risk helper facades present.
- Keep routes, OpenAPI exposure, PM2 workflow, OpenSpec changes, frontend, issue labels, and high-risk service getters untouched.
- Run an `app.services` import smoke.
- Run Ruff and Black checks on touched files.
- Run focused tests for removed and locked symbols.
- Run staged GitNexus `detect_changes`.
- Run mainline scope gate before PR.

## Boundary

This is an authorization packet only. It defines the future allowed scope and acceptance criteria but does not itself authorize or perform runtime source edits.
