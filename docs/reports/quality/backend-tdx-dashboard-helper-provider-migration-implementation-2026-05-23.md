# Backend TDX Dashboard Helper Provider Migration Implementation - 2026-05-23

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Workline: G2.35 TDX dashboard helper provider migration
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `a8bd0c158ff9db1e8446bc17d9322a4e84b0c45e`
- Parent approval: G2.34 authorization packet, PR `#174`
- Scope: approved source implementation plus focused tests and evidence

Boundary note: this packet implements only the G2.34-approved TDX dashboard
helper provider migration. It does not authorize broader backend refactors,
`web/backend/app/api/tdx.py` edits, route path changes, OpenAPI contract
changes, OpenSpec changes, issue label movement, PM2/frontend/docs/API changes,
adapter/protocol refactors, or deletion/privatization of `get_tdx_service()`.

## What Changed

`web/backend/app/services/tdx_service.py`

- Added `install_tdx_service(app, service=None)`.
- The installer stores the selected `TdxService` on `app.state.tdx_service`.
- Public `get_tdx_service()` remains defined and active as the compatibility
  fallback.

`web/backend/app/api/dashboard_data_source.py`

- `RealBusinessDataSource` now accepts an optional `TdxService` instance and a
  narrow fallback provider callable.
- `_get_major_index_quotes()` now gets the TDX service from the instance-level
  provider path instead of directly calling `get_tdx_service()`.
- `_get_tdx_live_market_snapshot()` now uses the same provider-fed service for
  adapter host/port access.
- `prewarm_dashboard_market_overview_cache()` can receive an explicit
  `TdxService` instance.
- `get_data_source(market_service=None, tdx_service=None)` preserves direct-call
  compatibility.

`web/backend/app/main.py`

- Startup dashboard market-overview prewarm now installs/gets the app-state
  `TdxService` instance and passes it into
  `prewarm_dashboard_market_overview_cache()`.

`web/backend/tests/test_dashboard_data_source.py`

- Adds regression coverage proving injected `TdxService` is used by
  `_get_major_index_quotes()`.
- Adds regression coverage proving injected `TdxService` host/port data is used
  by `_get_tdx_live_market_snapshot()`.
- Adds prewarm coverage proving the same injected `TdxService` instance reaches
  both dashboard helper paths.
- Adds an AST static guard that `dashboard_data_source.py` no longer directly
  calls `get_tdx_service()`.

## What Did Not Change

- `web/backend/app/api/tdx.py` was not edited.
- `get_tdx_service()` remains public and defined in `tdx_service.py`.
- `/api/tdx` route paths, HTTP methods, response models, OpenAPI examples, and
  operation IDs are unchanged.
- No adapter protocol, external TDX client behavior, frontend files, PM2
  scripts, docs/API files, generated clients, OpenSpec files, or issue labels
  were changed.

## TDD Evidence

RED command:

`env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_dashboard_data_source.py -q --no-cov --tb=short`

Observed failures before implementation:

- `RealBusinessDataSource.__init__()` did not accept `tdx_service`
- `_get_tdx_live_market_snapshot()` could not receive an injected TDX service
- `prewarm_dashboard_market_overview_cache()` did not accept an injected TDX
  service
- `dashboard_data_source.py` still contained direct `get_tdx_service()` helper
  calls

RED result: `4 failed, 7 passed`.

GREEN command:

`env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_dashboard_data_source.py -q --no-cov --tb=short`

GREEN result: `11 passed in 3.52s`.

## Verification Evidence

| Check | Result |
|---|---|
| Authorized focused pytest | `133 passed in 65.69s` |
| Ruff touched files | `All checks passed!` |
| Black touched files | `All checks passed!` |
| `app.main` import smoke | `app.main import ok`, routes=`548` |
| OpenAPI smoke | paths=`500`, duplicate operation IDs=`0`, warnings=`0` |
| `dashboard_data_source.py` direct `get_tdx_service()` calls | `0` |
| `tdx_service.py` getter definitions | `1` |
| `web/backend/app/api/tdx.py` edits | `0` |
| Staged GitNexus detect changes | `risk_level=high`, `changed_files=7`, affected dashboard/prewarm processes=`9` |

The `app.main` and OpenAPI smoke emitted an existing GPU dependency warning:
`Numba needs NumPy 2.2 or less. Got NumPy 2.4.` The smoke commands still exited
successfully and produced the expected route/OpenAPI results.

## GitNexus Pre-Edit Evidence

| Target | Risk | Interpretation |
|---|---:|---|
| `get_tdx_service` | CRITICAL | Expected known compatibility surface; retained, not renamed, not privatized |
| `_get_major_index_quotes` | CRITICAL | Expected dashboard helper path; moved to provider-fed service access with focused test coverage |
| `_get_tdx_live_market_snapshot` | CRITICAL | Expected dashboard helper path; moved to provider-fed service access with focused test coverage |
| `prewarm_dashboard_market_overview_cache` | LOW | Narrow helper change covered by focused test |
| `lifespan` | LOW | Startup change limited to installing/passing app-state TDX service into prewarm |
| `dashboard_data_source.py` | MEDIUM | Direct import consumers include dashboard, main, focused tests, and dashboard integration tests |

`get_data_source` is ambiguous in the GitNexus index because another repository
symbol shares the same name. The dashboard module file-level impact was used to
cover the actual `web/backend/app/api/dashboard_data_source.py` modification.

The staged GitNexus result is `high` because the authorized TDX helper seam feeds
dashboard summary, market overview, and prewarm execution flows. That matches the
G2.34 pre-edit CRITICAL risk classification and is covered by focused dashboard
helper tests plus app/OpenAPI smoke.

## Rollback

Revert this PR as a unit. The rollback restores:

- dashboard helper direct compatibility getter calls
- dashboard prewarm without an explicit TDX service argument
- startup prewarm without app-state TDX service passing
- the focused TDX dashboard provider tests and evidence added by this batch

Earlier G2 service lifecycle DI PRs remain valid unless separately reverted.

## Decision

G2.35 is ready for human review.

If accepted, the steward tree should record the TDX dashboard helper provider
migration as implemented. The next service lifecycle DI movement should be a
fresh candidate refresh or closeout packet, not deletion of `get_tdx_service()`,
because the compatibility getter remains the public fallback for `tdx.py` and
for installer fallback behavior.
