# Backend Cache Prewarming Route DI Implementation

> **历史实施说明**: 本文件是 G2.229 缓存预热 route DI 实施记录，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: for review

Date: 2026-05-29

Base branch: `wip/root-dirty-20260403`

Base HEAD: `4d77ee68a1a4a30516134b995c82fa777c3b44d6`

Parent: G2.228 / PR `#381`

## Governance Boundary

This implementation is limited to the source lane authorized by G2.228. It
changes only the cache prewarming route dependency shape and the focused cache
API regression test.

It does not authorize broader cache prewarming behavior changes, route/OpenAPI
contract changes, frontend work, PM2 execution, OpenSpec spec changes, or
additional service lifecycle DI candidates.

## Change Summary

`web/backend/app/api/_cache_prewarming_routes.py` now injects
`CachePrewarmingStrategy` into the three target route handlers with
`Depends(get_prewarming_strategy)`.

Changed handlers:

- `trigger_cache_prewarming`
- `get_prewarming_status`
- `get_cache_health_status`

The route bodies now call the injected `prewarming_strategy` object rather than
calling `get_prewarming_strategy()` directly.

## TDD Evidence

Red:

- `web/backend/tests/test_cache_api.py::test_cache_prewarming_routes_inject_strategy_provider`
  failed before implementation because the target handlers did not expose a
  `prewarming_strategy` dependency parameter.

Green:

- The same test passed after implementation.

Focused verification:

| Gate | Result |
|---|---:|
| Focused cache tests | `55 passed` |
| Ruff target files | passed |
| app.main / OpenAPI smoke | `routes=548`, `paths=500` |
| Git diff whitespace check | clean |

## Preserved Invariants

- Route paths unchanged.
- OpenAPI path count unchanged at `500`.
- Auth dependency preserved.
- Response shapes preserved.
- `get_prewarming_strategy` remains the default provider.
- `CachePrewarmingStrategy` behavior is unchanged.
- `get_cache_monitor` behavior is unchanged.

## Next Gate

If this implementation is accepted, start G2.230 as a no-source closeout /
residual refresh. G2.230 should verify that route-body direct
`get_prewarming_strategy()` calls are closed and then select the next candidate,
if any, from current HEAD evidence.
