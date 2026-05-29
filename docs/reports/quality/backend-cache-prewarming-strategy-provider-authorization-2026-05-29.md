# Backend Cache Prewarming Strategy Provider Authorization

> **历史决策说明**: 本文件是 G2.228 缓存预热策略 provider 授权决策记录，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: for review

Date: 2026-05-29

Base branch: `wip/root-dirty-20260403`

Base HEAD: `f2b528e5feaf7fd89f19a857e75a3c3442ba9c6b`

Related lane: G/#79 service lifecycle DI

Parent: G2.227 / PR `#380`

## Governance Boundary

This authorization package is governance bookkeeping only. It records the
accepted G2.227 ownership decision and defines the review boundary for a future
path-limited G2.229 implementation lane.

It does not authorize source edits in this PR, route/OpenAPI contract changes,
PM2 execution, frontend changes, OpenSpec spec creation, or product behavior
changes.

## Boundary

G2.228 is a no-source authorization package. It does not modify backend source,
tests, route definitions, OpenAPI schema, runtime configuration, frontend code,
or OpenSpec specs.

The purpose is to decide whether a future source lane may convert
`get_prewarming_strategy` route-body calls into an explicit route dependency
provider pattern.

## Parent Decision

PR `#380` merged G2.227 at
`f2b528e5feaf7fd89f19a857e75a3c3442ba9c6b`.

G2.227 classified `get_prewarming_strategy` as a cache prewarming route/provider
ownership surface, not a deletion candidate and not generic singleton cleanup.

## Current Evidence

| Evidence | Value |
|---|---:|
| Candidate symbol | `get_prewarming_strategy` |
| Definition | `web/backend/app/core/cache_prewarming.py:306` |
| Text hits | 9 |
| Hit files | 3 |
| Direct route-body calls | 3 |
| GitNexus risk | LOW |
| Direct callers | 3 |
| Processes affected | 0 |
| Affected module | `Api` |
| Focused cache tests | `54 passed` |
| app.main / OpenAPI smoke | `routes=548`, `paths=500` |

Direct route callers:

| Route function | Current call |
|---|---|
| `trigger_cache_prewarming` | `get_prewarming_strategy().prewarm_cache()` |
| `get_prewarming_status` | `get_prewarming_strategy().get_prewarming_status()` |
| `get_cache_health_status` | `get_prewarming_strategy().get_health_status()` |

Current route surface:

- `/api/cache/prewarming/trigger`
- `/api/cache/prewarming/status`
- `/api/cache/monitoring/health`

Non-target route:

- `/api/cache/monitoring/metrics` uses `get_cache_monitor`, not
  `get_prewarming_strategy`.

## Authorization Decision

Authorize a future path-limited implementation lane only after this package is
accepted.

Future lane:

- G2.229 cache prewarming route dependency injection implementation

Future source scope if G2.228 is accepted:

- `web/backend/app/api/_cache_prewarming_routes.py`

Future test scope if G2.228 is accepted:

- `web/backend/tests/test_cache_api.py`
- `web/backend/tests/test_cache_prewarming.py`

Expected implementation shape:

- Preserve `get_prewarming_strategy` as the default provider.
- Inject `CachePrewarmingStrategy` into the three target route handlers via
  FastAPI `Depends(get_prewarming_strategy)` or an equivalent route-local
  provider parameter.
- Replace route-body direct `get_prewarming_strategy()` calls with the injected
  strategy object.
- Preserve route paths, auth dependencies, response shapes, OpenAPI exposure,
  and `CachePrewarmingStrategy` behavior.

## Explicit Non-Goals

- Do not edit source in G2.228.
- Do not edit `web/backend/app/core/cache_prewarming.py` in the future source
  lane unless a separate review approves core-provider changes.
- Do not delete or rename `get_prewarming_strategy`.
- Do not change `CachePrewarmingStrategy` behavior.
- Do not change `get_cache_monitor` or cache monitor behavior.
- Do not change route paths, OpenAPI exposure, response models, auth, SQL, PM2,
  frontend code, or `docs/api`.

## Required Future Gates

Before any G2.229 source edit:

- Run GitNexus context and impact for `get_prewarming_strategy` and the target
  route handlers.
- Add a TDD red guard proving route-body direct `get_prewarming_strategy()`
  calls in the target route handlers are not acceptable.
- Run focused cache API and cache prewarming tests.
- Run ruff for target files.
- Run app.main/OpenAPI smoke and preserve the `548 routes / 500 paths` snapshot
  unless current HEAD has explicitly documented drift.
- Run OpenSpec strict validate.
- Run mainline scope gate and GitNexus detect_changes before commit.

## Review Questions

- Does the package correctly keep G2.228 no-source?
- Is the future implementation scope limited to route dependency/provider
  wiring, not core prewarming behavior?
- Are route paths, response shape, auth, and OpenAPI exposure preserved as
  invariants?
- Is G2.229 correctly separated as the source implementation lane?
