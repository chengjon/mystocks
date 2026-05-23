# Backend TDX Route Provider Migration Closeout - 2026-05-24

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Workline: G2.41 TDX route provider migration closeout
- Base branch: `wip/root-dirty-20260403`
- Current HEAD: `86b0ec43c037729b28df51c40484196175c96c6e`
- Closed implementation PR: `#180`
- PR state: `MERGED`
- Merge timestamp: `2026-05-23T17:08:53Z`
- Merge commit: `86b0ec43c037729b28df51c40484196175c96c6e`
- Scope: governance-only closeout for the already-merged G2.40 implementation

## Closeout Scope

This packet records the already-merged G2.40 implementation result. It does not
edit backend source, tests, route contracts, OpenAPI schema exposure, frontend,
PM2/runtime configuration, OpenSpec artifacts, issue labels, or docs/API files.

The implementation branch completed the approved TDX route provider migration:

- `tdx_service.py` exposes `TDX_SERVICE_STATE_KEY = "tdx_service"`.
- `tdx_service.py` exposes `get_tdx_service_dependency(request)`.
- `get_tdx_service()` remains public and active as the compatibility fallback.
- `install_tdx_service(app, service=None)` reads and writes the named app-state
  key.
- exactly five `/api/v1/tdx` route dependencies now use
  `Depends(get_tdx_service_dependency)`.
- `/api/ml/tdx` remains unrelated local `TdxDataService()` usage.

## Post-Merge Verification

All commands below were run from the G2.41 closeout worktree at HEAD
`86b0ec43c037729b28df51c40484196175c96c6e`.

| Check | Result |
|---|---|
| PR state | PR `#180` is `MERGED` |
| Merge commit | `86b0ec43c037729b28df51c40484196175c96c6e` |
| Focused TDX lifecycle DI pytest | `4 passed in 1.09s` |
| Ruff touched files | `All checks passed!` |
| Black touched files | `3 files would be left unchanged` |
| `tdx.py` `Depends(get_tdx_service)` sites | `0` |
| `tdx.py` `Depends(get_tdx_service_dependency)` sites | `5` |
| `tdx_service.py` `get_tdx_service_dependency()` definitions | `1` |
| `tdx_service.py` `get_tdx_service()` definitions | `1` |
| `tdx_service.py` `install_tdx_service()` definitions | `1` |
| `tdx_service.py` `TDX_SERVICE_STATE_KEY` mentions | `4` |
| `app.main` import / OpenAPI smoke | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`, TDX paths=`7` |

The `app.main` and OpenAPI smoke emitted existing import-time service logs and
the known optional GPU dependency warning:
`Numba needs NumPy 2.2 or less. Got NumPy 2.4.` The smoke command still exited
successfully and produced the expected route/OpenAPI results.

## Current State After Merge

- The public `/api/v1/tdx` route handlers are provider-fed through FastAPI
  dependency injection.
- The TDX route dependency seam now matches the app-state installer pattern used
  by the earlier dashboard helper migration.
- `get_tdx_service()` remains intentionally active as compatibility fallback.
- There is no current authorization to retire `get_tdx_service()`.
- OpenAPI remains stable at `500` paths with `0` duplicate operation IDs.
- Issue `#79` remains the parent service lifecycle DI issue and should not be
  moved to implementation-ready state by this closeout.
- No next service lifecycle DI candidate is selected by this closeout.

## Next Gate

Human review of this closeout packet. If accepted and merged, create a separate
G2.42 current-head service lifecycle DI candidate refresh before selecting the
next implementation lane.
