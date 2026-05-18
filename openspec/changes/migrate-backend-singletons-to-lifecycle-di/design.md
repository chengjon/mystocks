## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

The May 2026 audit review measured the backend as having:

- 108 module-level `_xxx = None` singleton-like assignments.
- 200 module-level `def get_xxx(...)` functions.
- 314 `Depends(...)` code hits after removing comments and strings.
- Existing `app.state`, lifespan, shutdown, and `on_event` patterns.

This means the backend already uses DI in places, but lifecycle ownership is inconsistent.

## Goals

- Make backend dependency lifecycle explicit.
- Avoid per-request construction of heavy services.
- Preserve test override seams.
- Preserve adapter/factory behavior where factories are the correct abstraction.
- Introduce teardown requirements for cache, database, client, scheduler, or connection-backed dependencies.

## Non-Goals

- This change does not migrate all singletons in one batch.
- This change does not remove all `global` state automatically.
- This change does not rewrite route handlers except where approved by tasks.
- This change does not split Core modules.
- This change does not move Core files; Core import shape is governed by `split-backend-core-modules-with-compatibility-wrappers`.

## Decisions

### Decision: Lifecycle classification precedes implementation

Every candidate must be classified before code mutation:

| Class | Approved direction |
|-------|--------------------|
| Stateless helper | Pure function or thin `Depends()` wrapper |
| Heavy service | Lifespan/app.state initialization with dependency accessor |
| Adapter factory | Factory-owned instance lifecycle with overrideable provider |
| Cache-backed service | Explicit close/teardown and no request-level connection creation |
| Connection-backed service | Pool/client ownership with shutdown proof |
| Compatibility getter | Thin wrapper retained until call sites migrate |

### Decision: Request-level Depends is not the default

`Depends()` is an injection surface, not a lifecycle decision. A dependency provider may read from `app.state`, return a factory, or delegate to a compatibility wrapper.

### Decision: Test overrides are required

Any migrated dependency used by routes must have a documented `dependency_overrides` or equivalent test override path.

### Decision: Core import compatibility gates shared-module DI

For dependencies implemented in shared Core modules such as database, cache, security, socketio, or logging, DI implementation must wait for the Core split proposal's import compatibility matrix and lifecycle-owned module list. Inventory and classification may run in parallel, but lifecycle mutation must use stable import paths or approved wrappers.

### Decision: First implementation batch is a single low-risk pilot

The first implementation batch may select only one representative low-risk candidate. Broad migration across all lifecycle classes is blocked until that pilot proves startup, override, teardown, and rollback evidence.

2026-05-18 implementation approval was granted for the single pilot. The pilot
implements `get_eastmoney_enhanced_adapter` in
`web/backend/app/adapters/eastmoney_enhanced.py` with a FastAPI provider
(`get_eastmoney_enhanced_adapter_dependency`), app.state install/close helpers,
and lifespan wiring in the compatibility `app_factory`. Canonical `app.main` wiring is deferred until the oversized `main.py` composition root is split or an approved composition hook exists.
The current GH #78 live set contains 6 adapter names and 7 getter definitions
because `get_realtime_mtm_adapter` exists in two API modules. The pilot is
outside the Core database/cache/security/socketio/logger import-compatibility
block and has a smaller consumer surface than the akshare/eastmoney/tqlex
candidates wired through `app.core.adapter_factory`.

### Decision: Teardown evidence is an artifact

Resource-owning lifecycle changes must produce reviewable evidence such as a test fixture, shutdown hook smoke output, log excerpt, or resource close assertion. A prose claim that teardown exists is not sufficient.

## Migration Plan

1. Generate singleton/getter inventory.
2. Classify candidates by lifecycle.
3. Choose one low-risk representative pilot.
4. Confirm F's import compatibility matrix if the pilot touches shared Core modules.
5. Implement the pilot with compatibility getter retained.
6. Run import smoke, dependency override tests, lifecycle startup/shutdown smoke, and teardown artifact capture.
7. Expand by lifecycle class only after pilot verification.

## Rollback

- Keep old `get_xxx` wrappers during coexistence.
- Revert dependency provider to previous getter if smoke tests fail.
- Restore old singleton module state if lifespan migration fails.
- Keep teardown additions reversible per service.

## Risks / Trade-offs

- Keeping compatibility getters temporarily extends old API surface, but reduces blast radius.
- Lifespan migration can expose hidden startup ordering problems.
- Some singletons may be intentional caches; those should be documented rather than removed.
- Implementing DI before Core import compatibility is known can cause repeated provider-path rewrites.

## Resolved Questions

- First pilot candidate: `get_eastmoney_enhanced_adapter`; implemented after explicit approval.
- Pilot teardown strategy: the wrapped `EastMoneyAdapter` owns a `requests.Session`, so `EastMoneyEnhancedAdapter.close()` and `close_eastmoney_enhanced_adapter(app)` close it during app.state teardown.
- Pilot test override strategy: focused FastAPI dependency override tests cover the selected provider while the compatibility getter remains retained.

## Open Questions

- Should later heavy services use only `app.state`, or should some be factory-managed?
- Which existing tests rely on monkeypatching singleton module variables outside the selected pilot?
- Which Core modules are lifecycle-owned and therefore require coordination with the Core split proposal?
