# Archive ArtDecoBaseLayout Scoped Style Extraction Report

Date: 2026-06-03

## Scope

- Node: `artdeco-web-design-governance/artdeco-base-layout-archive-vue-style-extract`
- Target Vue SFC: `web/frontend/src/layouts/archive/ArtDecoBaseLayout.vue`
- New scoped stylesheet: `web/frontend/src/layouts/archive/styles/ArtDecoBaseLayout.scss`
- Change type: ArtDeco large-file debt reduction through scoped style externalization.

## Result

- `ArtDecoBaseLayout.vue` now uses:
  `<style scoped lang="scss" src="./styles/ArtDecoBaseLayout.scss"></style>`
- The original trailing scoped SCSS block was moved into `styles/ArtDecoBaseLayout.scss`.
- The target is under `layouts/archive`; this task does not reactivate the layout or change current routing/layout registration.
- The extracted archive SCSS exposed pre-existing hardcoded spacing and color literals to the changed-file ArtDeco token gate. Those literals were normalized to equivalent ArtDeco token, `calc(...)`, `rem`, or `color-mix(...)` expressions inside the new SCSS file only.

## Line Count Impact

Measurement scope:
- Root: `web/frontend/src`
- Extensions: `.vue`, `.ts`, `.tsx`
- Threshold: `>500` lines
- Method: LF split count

Measured results:
- `ArtDecoBaseLayout.vue`: `789 -> 236` lines
- `ArtDecoBaseLayout.scss`: `553` lines
- Vue/TS/TSX files over 500 lines: `30 -> 29`
- Vue files over 500 lines: `14 -> 13`
- `ArtDecoBaseLayout.vue` is no longer over the D1.4 threshold.

## Non-Goals Confirmed

- No router route definitions, aliases, or navigation truth changed.
- No backend API contract, OpenAPI/schema, or frontend API client changed.
- No Vue runtime logic, layout registration, archive semantics, template structure, props, emits, slots, or public component API changed.
- No shared component extraction was performed.
- No ArtDeco token definitions or token values were changed.
- No archive layout was reactivated.
- No unrelated dirty files were intentionally modified or staged.

## Validation

Passed:
- Function Tree scope-check: `7 changed file(s) within active authorization`
- Scoped `git diff --check` for authorized paths
- `node scripts/check-artdeco-tokens.js --target-file src/layouts/archive/ArtDecoBaseLayout.vue`
- `node scripts/check-artdeco-tokens.js --target-file src/layouts/archive/styles/ArtDecoBaseLayout.scss`
- `cd web/frontend && npm run build:no-types`
- Local `gitnexus analyze --index-only --max-file-size 64 --worker-timeout 10`
- Local `gitnexus detect-changes --scope staged --repo mystocks`: `6 files`, `8 symbols`, `0 affected processes`, `risk level: low`
- Local `gitnexus verify-staged --repo mystocks --json`: `ok: true`, index up-to-date, no stale staged diff

GitNexus notes:
- MCP impact returned `not_found` for `ArtDecoBaseLayout`.
- Local `gitnexus impact ArtDecoBaseLayout --repo mystocks --direction upstream --depth 2 --summary-only` also returned `not_found`.
- Local `gitnexus query ArtDecoBaseLayout --repo mystocks --limit 3` did not identify the archive file.
- The implementation remained strictly style-only and exact-path bounded.
- The new SCSS path is under `archive/` and is ignored by the repository-level `.gitignore` `archive/` rule, so it must be force-added as an explicitly authorized tracked file. No `.gitignore` policy was changed.

Runtime status:
- `mystocks-backend`: online, `http://localhost:8020`
- `mystocks-frontend`: online, `http://localhost:3020`

Not run:
- `vue-tsc`: not run for this scoped style-only extraction; no TypeScript logic changed.
- E2E: not run for this archive style-only extraction; no route, layout registration, API, or runtime interaction changed. The build and PM2 online checks cover structural runtime readiness for this batch.

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
- `.governance/programs/artdeco-web-design-governance/cards/artdeco-base-layout-archive-vue-style-extract.yaml`
- `web/frontend/src/layouts/archive/ArtDecoBaseLayout.vue`
- `web/frontend/src/layouts/archive/styles/ArtDecoBaseLayout.scss`
- `docs/reports/tasks/2026-06-03-artdeco-base-layout-archive-vue-style-extract-report.md`

Do not stage `.governance/programs/artdeco-web-design-governance/tree.md`, `.planning/*`, active views with existing user changes, or any unrelated worktree changes.
