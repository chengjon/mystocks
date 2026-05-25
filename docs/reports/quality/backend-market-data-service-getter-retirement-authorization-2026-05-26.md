# Backend MarketDataService Getter Retirement Authorization - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.111 MarketDataService getter-retirement authorization
Status: ready for review

## Purpose

Authorize only a future G2.112 implementation branch for retiring the
package-level lazy getter in
`web/backend/app/services/market_data_service/get_market_data_service.py`.

This packet does not edit backend source, tests, routes, OpenAPI, frontend,
PM2, OpenSpec, or issue labels.

## Parent Gate

| Item | Value |
|---|---|
| Parent candidate refresh | G2.110 |
| Parent PR | `#263` |
| Parent merge commit | `c4abd4e8c4705f07a7d86e13c2090d30575e95e9` |
| Current HEAD | `c4abd4e8c4705f07a7d86e13c2090d30575e95e9` |

## Target Evidence

| Evidence | Result |
|---|---|
| Target getter | `web/backend/app/services/market_data_service/get_market_data_service.py:get_market_data_service` at line `28` |
| Target singleton | `_market_data_service` at line `24` |
| Preserved class | `MarketDataService` imported from `.market_data_service` |
| Preserved lifecycle helpers | `install_market_data_service`, `get_market_data_service_dependency` |
| GitNexus context | no incoming graph callers, no outgoing graph calls, no process participation |
| GitNexus impact | LOW / impacted count `0` |
| Direct API refs | `0` |
| App refs | `8` refs across `4` files |
| Backend test refs | `13` refs across `4` files |

## Disambiguation

The low GitNexus impact does not mean the implementation may delete the getter
alone. Exact text scan shows non-API app/package references that must be handled
in the future implementation branch:

- `web/backend/app/services/market_data_adapter.py` imports and calls
  `get_market_data_service`.
- `web/backend/app/services/market_data_service/__init__.py` exports
  `get_market_data_service`.
- `web/backend/app/services/__init__.py` has a separate root-level
  `get_market_data_service` surface and must not be confused with the package
  target.
- Existing tests patch or assert the package getter and must be updated by TDD.

## Authorized Future G2.112 Scope

If this authorization packet is accepted, G2.112 may touch only:

- `web/backend/app/services/market_data_service/get_market_data_service.py`
- `web/backend/app/services/market_data_service/__init__.py`
- `web/backend/app/services/market_data_adapter.py`
- focused market-data service lifecycle tests
- steward tree, generated evidence JSON, implementation report, and PR task card

The future implementation may remove:

- `market_data_service/get_market_data_service.py:_market_data_service`
- `market_data_service/get_market_data_service.py:get_market_data_service`
- package export of the package-level `get_market_data_service`

The future implementation must preserve:

- `MarketDataService`
- `install_market_data_service`
- `get_market_data_service_dependency`
- route/API contracts and OpenAPI exposure
- root-level `web/backend/app/services/__init__.py:get_market_data_service`,
  unless a separate authorization explicitly handles that different surface

## Required Future G2.112 Verification

G2.112 must:

1. Re-read `architecture/STANDARDS.md`.
2. Run GitNexus context/impact for the package-level
   `get_market_data_service`.
3. Write a focused red test proving the package getter and singleton still
   exist before implementation.
4. Retarget `market_data_adapter.py` away from the public package getter.
5. Preserve `install_market_data_service` and
   `get_market_data_service_dependency`.
6. Remove the package-level getter and package export only after tests fail red.
7. Run focused market-data lifecycle tests and relevant adapter tests.
8. Run health route conflicts.
9. Run ruff/black on touched backend files.
10. Stage only authorized paths and run GitNexus `detect_changes` with
    `scope="staged"`.
11. Run mainline scope, markdown, JSON, YAML, and diff checks.

## Boundary

This packet does not:

- edit backend source or tests
- delete any getter
- alter route/API behavior or OpenAPI exposure
- change frontend code
- change PM2 workflows
- create or modify OpenSpec changes/specs
- change GitHub issue labels or readiness state
- authorize broad market-data service refactoring

## Next Gate

Human review / PR merge decision for G2.111.

If accepted, create G2.112 as the MarketDataService getter-retirement
implementation branch before any market-data service source edit.
