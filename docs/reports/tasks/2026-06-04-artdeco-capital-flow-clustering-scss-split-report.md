# ArtDeco CapitalFlow Clustering SCSS Split Report

Date: 2026-06-04

## Scope

- Continued the approved ArtDeco SCSS file-size governance work.
- Split `ArtDecoCapitalFlow.clustering.scss` into smaller clustering partials.
- Kept the Vue component, route surface, behavior, and selector intent unchanged.

## Files

- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoCapitalFlow.clustering.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoCapitalFlow.clustering-shell.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoCapitalFlow.clustering-overview.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoCapitalFlow.clustering-diagram.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoCapitalFlow.clustering-list.scss`

## Notes

- Unlike the prior `ArtDecoBatchAnalysisView` split, this file was one deeply nested Sass block.
- Each new partial keeps a complete parent selector wrapper so every file remains valid Sass on its own.
- That means the source text is intentionally not byte-for-byte expandable to the old file, while the selector structure and rule order remain equivalent for the component.

## Verification

- Checked all new `ArtDecoCapitalFlow.clustering*.scss` files for balanced braces: passed.
- Checked the `ArtDecoCapitalFlow.scss` import graph: no missing imports.
- Ran `git diff --check` on the scoped files: passed.
- Ran `node scripts/check-artdeco-tokens.js --target-dir src/components/artdeco --changed-from-git`: passed.
- Ran `npm run build:no-types`: passed, Vite production build completed successfully.
- Ran `npm run test:type-ceiling`: passed, `vue-tsc --noEmit` reported 0 TypeScript errors within ceiling 0.

## Existing E2E Context

- The stable E2E subset was previously run in this session against the PM2 frontend with `PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:stable`.
- Result: 10 chromium tests, 6 passed and 4 failed.
- Failures were existing runtime/test-surface issues outside this SCSS split: missing `QUANTIX` H1 expectation and a `vue-i18n` install/use error from `ArtDecoSkipLink.vue`.
