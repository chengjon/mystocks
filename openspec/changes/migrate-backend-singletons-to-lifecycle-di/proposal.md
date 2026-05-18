# Change: Migrate backend singletons to lifecycle-aware DI

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

The backend audit found many module-level lazy singletons and `get_xxx` accessors mixed with FastAPI `Depends`, factories, lifespan hooks, and `app.state`. The issue is not absence of DI; it is unclear lifecycle ownership.

Mechanical conversion of every singleton or getter to request-level `Depends()` can recreate heavy services per request, leak connections, or break tests that rely on override seams.

## What Changes

- Classify backend singleton/getter candidates by lifecycle before implementation.
- Define approved lifecycle patterns for stateless helpers, heavy services, adapter factories, cache-backed services, and connection-backed services.
- Require FastAPI dependency override strategy for testable dependencies.
- Require lifespan/app.state initialization and teardown evidence for heavy or connection-backed objects.
- Block broad singleton deletion or request-scoped conversion until lifecycle classification and verification are complete.

## Impact

- Affected specs:
  - `architecture-governance`
  - `code-quality`
- Affected code, when implementation is later approved:
  - `web/backend/app/**/*.py` singleton/getter modules
  - FastAPI dependency functions and `dependency_overrides`
  - Lifespan/startup/shutdown code in `web/backend/app/main.py` and related app factory modules
  - Tests that monkeypatch singleton accessors or dependency providers

## Source Evidence

- `docs/reports/quality/backend-singleton-to-di-2026-05-14.md`
- `docs/reports/quality/backend-audit-documents-review-2026-05-15.md`
- `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md`

## Approval Boundary

This change is a proposal and design package only. It does not approve code implementation. Implementation must not begin until this OpenSpec change is reviewed and approved.
