# Backend Cache Prewarming Strategy Ownership Decision - 2026-05-29

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2: `G2.227`
- Status: ownership decision for review
- Prepared at: `2026-05-29T10:56:00+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `854878cd2e09384daddaa8547e8cebc970ec2b74`
- Parent: G2.226 / PR `#379`, merged at `854878cd2e09384daddaa8547e8cebc970ec2b74`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`
- Source edit authority: no

Boundary note: this ownership decision classifies the cache prewarming provider
surface and selects a future authorization gate. It does not edit backend source,
tests, route contracts, OpenAPI specs, frontend code, runtime configuration, PM2
state, or OpenSpec specs.

## Candidate

| Item | Value |
|---|---|
| Symbol | `get_prewarming_strategy` |
| Definition | `web/backend/app/core/cache_prewarming.py:306` |
| Classification | cache prewarming route/provider surface |
| Text hits | 9 |
| App hit files | `web/backend/app/core/cache_prewarming.py`, `web/backend/app/api/_cache_prewarming_routes.py` |
| Test hit file | `web/backend/tests/test_cache_prewarming.py` |

The symbol returns the active `CachePrewarmingStrategy` singleton. The current
route file calls it directly from route bodies.

## Route Surface

| Route handler | Direct use |
|---|---|
| `trigger_cache_prewarming` | `get_prewarming_strategy().prewarm_cache()` |
| `get_prewarming_status` | `get_prewarming_strategy().get_prewarming_status()` |
| `get_cache_health_status` | `get_prewarming_strategy().get_health_status()` |

OpenAPI paths observed at current HEAD:

- `/api/cache/prewarming/trigger`
- `/api/cache/prewarming/status`
- `/api/cache/monitoring/metrics`
- `/api/cache/monitoring/health`

The route handlers already use FastAPI `Depends` for `current_user`, so a future
provider-injection implementation can be scoped to the route dependency seam
without introducing a new route pattern.

## GitNexus Evidence

Exact GitNexus context for `get_prewarming_strategy`:

| Evidence | Value |
|---|---:|
| Risk | LOW |
| Direct callers | 3 |
| Processes affected | 0 |
| Modules affected | 1 |
| Affected module | `Api` |

Direct callers:

- `web/backend/app/api/_cache_prewarming_routes.py:trigger_cache_prewarming`
- `web/backend/app/api/_cache_prewarming_routes.py:get_prewarming_status`
- `web/backend/app/api/_cache_prewarming_routes.py:get_cache_health_status`

File-level impact for `web/backend/app/api/_cache_prewarming_routes.py` is LOW.
The file is imported by `web/backend/app/api/cache.py` and by
`web/backend/tests/test_cache_api.py`.

## Verification

| Check | Result |
|---|---|
| Cache-focused tests | `web/backend/tests/test_cache_prewarming.py` + `web/backend/tests/test_cache_api.py`: `54 passed` |
| Ruff target check | `All checks passed` |
| app.main / OpenAPI smoke | `routes=548`, `paths=500`, cache prewarming paths present |

The app.main / OpenAPI smoke used transient non-secret placeholders for values
that are not required to validate import and schema generation. No environment
configuration or secret values were written to disk.

## Decision

Classify `get_prewarming_strategy` as a cache prewarming route/provider ownership
surface, not as generic singleton deletion.

G2.227 does not authorize source implementation. It selects G2.228 as a future
no-source authorization package for a path-limited implementation candidate.

Potential future authorization shape, if separately approved:

- preserve `get_prewarming_strategy` as the default provider factory
- inject the strategy into the three route handlers with FastAPI `Depends`
- limit source scope to `web/backend/app/api/_cache_prewarming_routes.py`
- use focused tests in `web/backend/tests/test_cache_api.py` and
  `web/backend/tests/test_cache_prewarming.py`

## Non-Goals

G2.227 does not authorize:

- cache prewarming source edits
- route path changes
- response model / response envelope changes
- `CachePrewarmingStrategy` behavior changes
- `get_prewarming_strategy` deletion or rename
- `cache.py` router changes
- frontend changes
- OpenSpec proposal or spec creation

## Artifacts

| Artifact | Purpose |
|---|---|
| `.planning/codebase/generated/cache-prewarming-strategy-ownership-decision-2026-05-29.json` | Machine-readable G2.227 ownership decision evidence |
| `docs/reports/quality/backend-cache-prewarming-strategy-ownership-decision-2026-05-29.md` | Human-readable G2.227 decision package |
| `governance/mainline/task-cards/pr-380.yaml` | Mainline governance task card |

## Next Gate

If accepted, start G2.228 no-source cache prewarming strategy provider
authorization. Do not implement cache prewarming source changes directly from
G2.227.

## Rollback

Revert this decision PR. No runtime source or test changes are present.
