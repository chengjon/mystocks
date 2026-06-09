# Frontend View Governance A4 Root Demo Parent Shells Defer Decision

> **Scope**: `openspec/changes/update-frontend-view-governance`
> **Decision date**: 2026-05-12

## Decision

Select `A4-root-demo-parent-shells-defer`.

Do not execute archive moves for the root demo parent shells in the current repo-local micro-batch:

- `web/frontend/src/views/FreqtradeDemo.vue`
- `web/frontend/src/views/TdxpyDemo.vue`
- `web/frontend/src/views/PyprofilingDemo.vue`

## Reason

These pages are not active routed business pages, but they still own child or support assets and guards. They are not safe standalone archive candidates.

Current ownership and guard evidence:

- `FreqtradeDemo.vue` imports all files under `web/frontend/src/views/freqtrade-demo/*`.
- `TdxpyDemo.vue` imports all files under `web/frontend/src/views/tdxpy-demo/*`.
- `PyprofilingDemo.vue` imports `web/frontend/src/views/composables/usePyprofilingDemo.ts` and `web/frontend/src/views/styles/PyprofilingDemo.css`.
- `web/frontend/package.json` still includes changed-scope coverage for `src/views/freqtrade-demo`, `src/views/tdxpy-demo`, `src/views/demo`, and a file-level target for `src/views/PyprofilingDemo.vue`.
- `web/frontend/tests/unit/config/freqtrade-demo-mainline-gate.spec.ts`, `tdxpy-demo-mainline-gate.spec.ts`, `pyprofiling-mainline-gate.spec.ts`, and `root-demo-style-entrypoints.spec.ts` still guard those scopes or entrypoints.

Existing evidence already classifies these assets as demo inventory rather than active route truth:

- `docs/reports/quality/myweb-audit/frontend-view-checklist-demo-examples-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-demo-directory-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-root-demo-sidecars-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-demo-openstock-root-sidecars-inventory-2026-05-11.md`

Those records do not approve archive execution. They require parent and child/support decisions together.

## Boundary

This decision does not move files, edit runtime code, retire package/test guards, or change demo behavior.

The current classifications remain:

- `FreqtradeDemo.vue`: `candidate-review/demo-parent-shell`, retain with `freqtrade-demo/*` until parent-child disposition is approved.
- `TdxpyDemo.vue`: `candidate-review/demo-parent-shell`, retain with `tdxpy-demo/*` until parent-child disposition is approved.
- `PyprofilingDemo.vue`: `candidate-review/demo-research-shell`, retain with root composable/style support until AI/strategy successor or no-successor rationale is approved.

This decision does not claim global frontend lint is clean.

## Next Valid Step

Prepare a separate approval package if the team wants to retire or relocate these demo parents. That package must decide each parent shell with its coupled assets:

- parent Vue file
- child tab directory or support composable/style
- package `lint:artdeco:changed` guard
- mainline/style-source specs
- successor or explicit `no-successor-needed` rationale

Until then, no archive execution is approved for these root demo parent shells.
