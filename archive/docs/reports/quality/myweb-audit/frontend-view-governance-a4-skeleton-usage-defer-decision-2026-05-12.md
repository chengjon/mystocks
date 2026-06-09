# Frontend View Governance A4 SkeletonUsage Defer Decision

> **Scope**: `openspec/changes/update-frontend-view-governance`
> **Decision date**: 2026-05-12

## Decision

Select `A4-skeleton-usage-defer`.

Do not execute `A4-skeleton-usage-archive` in the current repo-local micro-batch.

## Reason

`web/frontend/src/views/SkeletonUsage.vue` is not an active routed business page, but it is still a direct guard anchor.

Current guard owners:

- `web/frontend/package.json` includes `--target-file src/views/SkeletonUsage.vue` in `lint:artdeco:changed`.
- `.github/workflows/frontend-testing.yml` treats `web/frontend/src/views/SkeletonUsage.vue` as an ArtDeco scope input.
- `web/frontend/tests/unit/config/skeleton-usage-tokenization.spec.ts` reads `src/views/SkeletonUsage.vue` directly.
- `web/frontend/tests/unit/workflows/ci-workflow-gates.spec.ts` asserts the package/workflow guard entries.

Archiving this page safely requires a successor guard for skeleton tokenization and workflow scope. That successor is not approved in the current batch.

## Boundary

This decision does not move files, edit runtime code, retire package/workflow guards, or change skeleton component behavior.

`SkeletonUsage.vue` remains `candidate-review/demo-sandbox` and `retain-as-guard-anchor`.

## Next Valid Step

Prepare a separate approval package if the team wants to migrate skeleton guard ownership. That package must choose one successor path before any archive move:

- component-owned coverage around `web/frontend/src/components/artdeco/core/ArtDecoSkeleton.vue`
- a dedicated non-routed fixture under tests
- continued retention of `SkeletonUsage.vue` as the guard anchor

Until then, no archive execution is approved for `SkeletonUsage.vue`.
