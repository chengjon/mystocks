# Task Management Legacy Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/TaskManagement.vue`
- Synthetic route key: `/secondary/task-management-static-shell`
- Family: `secondary wrapper / honest static shell`

## Problem
- `TaskManagement.vue` still rendered local task stats, task tables, import/export controls, and history dialogs even though no routed or otherwise active canonical task-management owner existed to verify that truth.
- Keeping those shell semantics in place would preserve pseudo-live task-management truth in a legacy page.

## Repair
- Replace `web/frontend/src/views/TaskManagement.vue` with an honest static shell.
- Keep only handoff guidance to nearby canonical `/strategy/*`, `/trade/*`, and `/system/*` routes instead of preserving local task stats, list chrome, or history surfaces.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/__tests__/TaskManagement.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `TaskManagement.vue` now renders an honest static shell.
- The legacy task-management page no longer preserves pseudo task-management stats, list, import-export, or history truth.
