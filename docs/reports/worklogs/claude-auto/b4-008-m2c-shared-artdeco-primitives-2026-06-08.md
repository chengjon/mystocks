# B4.008-M2c shared ArtDeco primitives

Date: 2026-06-08
Status: source package landed
Source commit: `04f4a5fc151bc5066a93b36c515af8674110ea80`

## Authorization

User granted source-authorized approval for `B4.008-M2c UI-2 shared ArtDeco primitives`.

Authorized source paths:

- `web/frontend/src/components/artdeco/base/ArtDecoDialog.vue`
- `web/frontend/src/components/artdeco/base/ArtDecoLanguageSwitcher.vue`
- `web/frontend/src/components/artdeco/core/ArtDecoSkeleton.vue`

Explicitly held outside this package:

- B4.007 route truth and root legacy archive work.
- B4.008-M2a and B4.008-M2b already-closed source packages.
- `web/frontend/src/components.d.ts`
- `web/frontend/src/layouts/archive/BaseLayout.vue`
- `ST-HOLD`
- `marketKlineData`
- Backend/API contracts, route pages, generated files, and unrelated dirty files.

## Change Summary

- `ArtDecoDialog.vue`: normalized internal TODO ownership markers for trading settings and pause-trading placeholders. Runtime behavior was not changed.
- `ArtDecoLanguageSwitcher.vue`: preserved the existing language switcher behavior, made flag glyphs presentation-only for assistive technology, and migrated the token stylesheet load from deprecated Sass `@import` to `@use`.
- `ArtDecoSkeleton.vue`: preserved skeleton rendering behavior while aligning radius and spacing values to ArtDeco token expressions and migrating the token stylesheet load from deprecated Sass `@import` to `@use`.

No router, menu, store, API client, backend contract, route page, or generated component registry change was included.

## Risk And Impact

- GitNexus symbol-name impact lookup for SFC-level names was not available for these component filenames, so the hard gate used staged path analysis.
- GitNexus staged detect before the source commit reported:
  - 3 changed source files.
  - 6 touched symbols.
  - 0 affected processes.
  - Risk level: low.
  - Index status: up to date and fresh for staged diff.
- `node .gitnexus/run.cjs verify-staged --repo mystocks` reported 3 files, 6 symbols, 0 affected processes, low risk.
- Post-source GitNexus analyze completed successfully after commit `04f4a5fc151bc5066a93b36c515af8674110ea80`.

## Validation

- PM2 status:
  - `mystocks-backend`: online, `http://localhost:8020`
  - `mystocks-frontend`: online, `http://localhost:3020`
- Type check:
  - Command: `cd web/frontend && npm run type-check`
  - Result: passed, structural syntax errors 0.
  - OPENDOG run id: 102, status passed.
- Focused unit tests:
  - Command: `cd web/frontend && npm run test -- tests/unit/components/ArtDecoLanguageSwitcher.accessibility.spec.ts src/views/artdeco-pages/_templates/__tests__/ArtDecoPageTemplate.spec.ts src/views/risk/__tests__/Center.spec.ts`
  - Result: 3 files passed, 18 tests passed.
  - OPENDOG run id: 103, status passed.
- Stable frontend unit suite:
  - Command: `cd web/frontend && npm run test:unit:stable`
  - Result: 33 files passed, 415 tests passed.
- PM2 business smoke E2E:
  - Command: `cd web/frontend && PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 npm run test:e2e:business-smoke`
  - Project: chromium.
  - Result: 55 tests passed.
  - OPENDOG run id: 104, status passed, 55 passed.

## Next Gate

Next package remains authorization-gated:

- `B4.008-M2d UI-4 shared market/data composables`

Candidate paths from the M1 grouping:

- `web/frontend/src/composables/market/dataAnalysisData.ts`
- `web/frontend/src/composables/market/__node_tests__/dataAnalysisData.test.ts`
- `web/frontend/src/composables/market/useDataAnalysis.ts`
