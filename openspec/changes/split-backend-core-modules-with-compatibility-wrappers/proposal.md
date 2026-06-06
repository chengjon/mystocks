# Change: Split backend Core modules with compatibility wrappers

## Why

The backend audit found that `web/backend/app/core/` remains broad and mixed: database, cache, security, logging, socketio, validation, exceptions, and service-like modules coexist at the top level while some subpackages already exist.

Moving files without import compatibility would break existing imports such as `app.core.cache_manager`, `app.core.database`, `app.core.security`, `app.core.logger`, and `app.core.socketio_manager`.

## What Changes

- Establish an import compatibility matrix before moving Core modules.
- Distinguish same-name package migrations from old-module wrapper migrations.
- Preserve `app.core.logger` as the canonical logging entrypoint.
- Require import smoke, runtime smoke, and rollback for each Core split batch.
- Retire wrappers only after consumer references are clear and cleanup criteria are met.

## Impact

- Affected specs:
  - `architecture-governance`
  - `directory-governance`
- Affected code, when implementation is later approved:
  - `web/backend/app/core/`
  - Backend imports of `app.core.*`
  - Tests that monkeypatch Core modules
  - PM2 backend startup and health smoke paths

## Source Evidence

- `docs/reports/quality/backend-core-split-plan-2026-05-14.md`
- `docs/reports/quality/backend-audit-documents-review-2026-05-15.md`
- `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md`

## Approval Boundary

This change is a proposal and design package only. It does not approve code implementation. Implementation must not begin until this OpenSpec change is reviewed and approved.
