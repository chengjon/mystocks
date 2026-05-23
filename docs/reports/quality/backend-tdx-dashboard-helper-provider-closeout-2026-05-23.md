# Backend TDX Dashboard Helper Provider Closeout - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: closeout-prepared-for-review
- Workline: G2.36 TDX dashboard helper provider closeout
- Parent issue: `#79`
- Implementation PR: https://github.com/chengjon/mystocks/pull/175
- Implementation merge commit: `efbc02db5100a4927476a4c8eb2c4cd4533a352f`
- Implementation PR merged at: `2026-05-23T13:26:49Z`
- Closeout branch: `g2-36-tdx-dashboard-helper-provider-closeout`
- Closeout HEAD: `efbc02db5100a4927476a4c8eb2c4cd4533a352f`
- Recorded at: `2026-05-23T21:37:00+08:00`

## Closeout Scope

This packet records the already-merged G2.35 implementation result. It does not
edit backend source, tests, route contracts, OpenAPI schema exposure, frontend,
PM2/runtime configuration, OpenSpec artifacts, issue labels, or docs/API files.

The implementation branch added the TDX dashboard helper provider seam:

- `tdx_service.py` exposes `install_tdx_service(app, service=None)`.
- `get_tdx_service()` remains public and active as the compatibility fallback.
- `RealBusinessDataSource` accepts injected/provider `TdxService` instances.
- `_get_major_index_quotes()` and `_get_tdx_live_market_snapshot()` use
  provider-fed service access.
- startup dashboard prewarm passes the installed app-state TDX service.
- `web/backend/app/api/tdx.py` remains unchanged.

## Preserved Compatibility Boundary

The implementation intentionally preserves `get_tdx_service()` because
`web/backend/app/api/tdx.py` still has five `Depends(get_tdx_service)` sites and
the installer uses the getter as fallback behavior.

Any future cleanup of the compatibility getter, `/api/tdx` route dependency
wiring, adapter/protocol behavior, or broader TDX service lifecycle work must be
routed through a separate packet with impact evidence, exact write scope, tests,
rollback plan, and review gate.

## Post-Merge Verification

All commands below were run from the G2.36 closeout worktree at HEAD
`efbc02db5100a4927476a4c8eb2c4cd4533a352f`.

| Check | Result |
|---|---|
| PR state | PR `#175` is `MERGED` |
| Merge commit | `efbc02db5100a4927476a4c8eb2c4cd4533a352f` |
| Focused authorized pytest | `133 passed in 65.37s` |
| Ruff touched files | `All checks passed!` |
| Black touched files | `All checks passed!` |
| `app.main` import smoke | `app.main import ok`, routes=`548` |
| OpenAPI smoke | paths=`500`, duplicate operation IDs=`0`, warnings=`0` |
| `dashboard_data_source.py` direct `get_tdx_service()` calls | `0` |
| `dashboard_data_source.py` private `_get_tdx_service()` calls | `3` |
| `tdx_service.py` `get_tdx_service()` definitions | `1` |
| `tdx_service.py` `install_tdx_service()` definitions | `1` |
| `tdx.py` `Depends(get_tdx_service)` sites | `5` |

The `app.main` and OpenAPI smoke emitted an existing GPU dependency warning:
`Numba needs NumPy 2.2 or less. Got NumPy 2.4.` The smoke commands still exited
successfully and produced the expected route/OpenAPI results.

## Current State After Merge

- TDX dashboard helper direct compatibility getter calls are now `0`.
- The dashboard helper path is provider-fed for both major index quotes and TDX
  live market snapshot helpers.
- Startup prewarm uses the installed app-state TDX service.
- `/api/tdx` remains on the existing public compatibility getter dependency.
- The OpenAPI schema remains stable at `500` paths with `0` duplicate operation
  IDs.
- Issue `#79` remains the parent service lifecycle DI issue and should not be
  moved to implementation-ready state by this closeout.
- No next service lifecycle DI candidate is selected by this closeout.

## Next Gate

Human review of this closeout packet.

If accepted, the next step should be a fresh current-head service lifecycle DI
candidate refresh before selecting another source implementation lane.
