# ArtDeco BatchAnalysisView Panels/Charts SCSS Split Report

Date: 2026-06-04

## Scope

- Continued the approved ArtDeco SCSS file-size governance work for `ArtDecoBatchAnalysisView`.
- Split the oversized panels and charts slices into smaller semantic partials.
- Kept the Vue component, selectors, CSS rule order, and behavior unchanged.

## Files

- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.panels.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.panels-progress.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.panels-results-summary.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.panels-report-summary.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.panels-report-insights.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.charts.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.charts-breakdown.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.charts-results-table.scss`

## Verification

- Expanded `panels.scss` partial imports and compared against `HEAD`: exact byte-for-byte match.
- Expanded `charts.scss` partial imports and compared against `HEAD`: exact byte-for-byte match.
- Checked all `ArtDecoBatchAnalysisView*.scss` brace balance: passed.
- Ran `git diff --check` on the scoped files: passed.
- Ran `node scripts/check-artdeco-tokens.js --target-dir src/components/artdeco --changed-from-git`: passed.
- Ran `npm run build:no-types`: passed, Vite production build completed successfully.
- Ran `gitnexus.detect_changes(scope=staged)`: low risk, 8 style files, no changed symbols and no affected execution flows. GitNexus reported the index as stale against current commit, so the risk result is used as scoped supporting evidence, not as a fully fresh graph assertion.

## Known Existing Debt

- `npm run lint:artdeco:changed` still fails on pre-existing hardcoded spacing/color literals in `src/views/advanced-analysis/*.vue`.
- Those files were not changed in this batch.
