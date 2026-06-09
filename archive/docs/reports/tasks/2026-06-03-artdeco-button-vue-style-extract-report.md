# ArtDecoButton Scoped Style Extraction Report

Date: 2026-06-03

## Scope

- Node: `artdeco-web-design-governance/artdeco-button-vue-style-extract`
- Target Vue SFC: `web/frontend/src/components/artdeco/base/ArtDecoButton.vue`
- New scoped stylesheet: `web/frontend/src/components/artdeco/base/styles/ArtDecoButton.scss`
- Change type: ArtDeco large-file debt reduction through scoped style externalization.

## Result

- `ArtDecoButton.vue` now uses:
  `<style scoped lang="scss" src="./styles/ArtDecoButton.scss"></style>`
- The original trailing scoped SCSS block was moved into `styles/ArtDecoButton.scss`.
- Initial extraction preserved the original style body exactly.
- The extracted SCSS then exposed pre-existing hardcoded spacing literals to the changed-file ArtDeco token gate; those literals were normalized to equivalent ArtDeco token or `calc(token)` expressions inside the new SCSS file only.

## Line Count Impact

Measurement scope:
- Root: `web/frontend/src`
- Extensions: `.vue`, `.ts`, `.tsx`
- Threshold: `>500` lines
- Method: LF split count

Measured results:
- `ArtDecoButton.vue`: `565 -> 146` lines
- `ArtDecoButton.scss`: `419` lines
- Vue/TS/TSX files over 500 lines: `31 -> 30`
- Vue files over 500 lines: `15 -> 14`
- `ArtDecoButton.vue` is no longer over the D1.4 threshold.

## Non-Goals Confirmed

- No router route definitions, aliases, or navigation truth changed.
- No backend API contract, OpenAPI/schema, or frontend API client changed.
- No Vue runtime logic, data fetching, computed state, template structure, props, emits, slots, or public component API changed.
- No shared component extraction was performed.
- No ArtDeco token definitions or token values were changed.
- No unrelated dirty files were intentionally modified or staged.

## Validation

Passed:
- Function Tree scope-check: `7 changed file(s) within active authorization`
- Scoped `git diff --check` for authorized paths
- `node scripts/check-artdeco-tokens.js --target-file src/components/artdeco/base/ArtDecoButton.vue`
- `node scripts/check-artdeco-tokens.js --target-file src/components/artdeco/base/styles/ArtDecoButton.scss`
- `cd web/frontend && npm run build:no-types`
- Local `gitnexus analyze --index-only --max-file-size 64 --worker-timeout 10`
- Local `gitnexus detect-changes --scope staged --repo mystocks`: `6 files`, `0 symbols`, `0 affected processes`, `risk level: low`
- Local `gitnexus verify-staged --repo mystocks --json`: `ok: true`, index up-to-date, no stale staged diff

GitNexus notes:
- MCP impact returned `Transport closed`.
- Local `gitnexus impact ArtDecoButton --repo mystocks --direction upstream --depth 2 --summary-only` returned docs-only ambiguous candidates, so the component was treated as higher blast-radius.
- The implementation remained strictly style-only and exact-path bounded.

Runtime status:
- `mystocks-backend`: online, `http://localhost:8020`
- `mystocks-frontend`: online, `http://localhost:3020`

Not run:
- `vue-tsc`: not run for this scoped style-only extraction; no TypeScript logic changed.
- E2E: not run for this scoped style-only extraction; no route, layout, API, or runtime interaction changed. The build and PM2 online checks cover structural runtime readiness for this batch.

## Quality Status

- Structural syntax errors introduced by this change: `0` based on successful `build:no-types`.
- Type inference errors introduced by this change: not applicable; no TS/Vue script logic changed and `vue-tsc` was not run.
- PM2 services: backend and frontend online at required local addresses.
- E2E status: not executed in this narrow style-only batch; no fixed pass-count wording is claimed.

## Staging Policy

Only the authorized files for this node may be staged:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/cards/artdeco-button-vue-style-extract.yaml`
- `web/frontend/src/components/artdeco/base/ArtDecoButton.vue`
- `web/frontend/src/components/artdeco/base/styles/ArtDecoButton.scss`
- `docs/reports/tasks/2026-06-03-artdeco-button-vue-style-extract-report.md`

Do not stage `.governance/programs/artdeco-web-design-governance/tree.md`, `.planning/*`, or any unrelated user/worktree changes.
