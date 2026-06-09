# BacktestGPU SCSS Style Split Report

Date: 2026-06-03

## Scope

Continued the ArtDeco SCSS file-size remediation by splitting the remaining route-local over-limit style file:

- `web/frontend/src/views/strategy/styles/BacktestGPU.scss`

The facade path stayed unchanged so the existing `BacktestGPU.vue` style import contract remains intact. `web/frontend/src/styles/artdeco-tokens.scss` remains over 500 lines, but it is the design-token source of truth and was not split in this batch.

## Compatibility Boundaries

- No Vue, TypeScript, route, store, or API files were edited.
- Selector order was preserved by importing partials in the same semantic order as the original file.
- Existing uncommitted `BacktestGPU.scss` content was treated as the local pre-batch baseline; this batch did not revert or normalize the unrelated dirty worktree.
- Function Tree scope-check reported no active source-edit authorization. This report records the governance caveat instead of expanding the batch further.

## Split Result

| File | Lines | Raw `px` Literals |
| --- | ---: | ---: |
| `BacktestGPU.scss` | 9 | 0 |
| `BacktestGPU.shell.scss` | 145 | 3 |
| `BacktestGPU.status.scss` | 103 | 1 |
| `BacktestGPU.performance-controls.scss` | 145 | 2 |
| `BacktestGPU.logs-metrics.scss` | 76 | 1 |
| `BacktestGPU.element-plus.scss` | 176 | 6 |
| `BacktestGPU.responsive.scss` | 15 | 0 |

After this split, the only remaining `web/frontend/src/**/*.scss` file over 500 lines is:

- `web/frontend/src/styles/artdeco-tokens.scss` at 692 lines

## Validation

| Gate | Command | Result |
| --- | --- | --- |
| GitNexus pre-impact | `impact(File:web/frontend/src/views/strategy/styles/BacktestGPU.scss, upstream)` | LOW risk, 0 direct callers, 0 affected processes; index stale warning present |
| Sass compile smoke | `sass.compile('src/views/strategy/styles/BacktestGPU.scss')` | Passed; facade loaded all 6 partials |
| SCSS whitespace | `git diff --check -- web/frontend/src/views/strategy/styles/BacktestGPU*.scss` | Passed |
| ArtDeco token check | `cd web/frontend && node scripts/check-artdeco-tokens.js --target-file ...BacktestGPU*.scss` | Passed |
| Frontend structural build | `cd web/frontend && npm run build:no-types` | Passed: 2583 modules transformed, built in 27.55s |
| Frontend type check | `cd web/frontend && npm run type-check` | Passed; no TypeScript error lines emitted |
| Focused E2E | `cd web/frontend && npm run test:artdeco-style -- --project=chromium` | Passed: 3 passed, 0 failed, 0 skipped |
| PM2 status | `pm2 jlist` | `mystocks-backend` online at `http://localhost:8020`; `mystocks-frontend` online at `http://localhost:3020` |

## GitNexus Detect Changes

`detect_changes(scope=all)` reported HIGH risk for the overall worktree:

- 837 changed files
- 3132 changed symbols
- 12 affected processes

This is not scoped to this batch. The worktree was already heavily dirty before the SCSS split, and the focused changed files for this batch are only:

- `web/frontend/src/views/strategy/styles/BacktestGPU.scss`
- `web/frontend/src/views/strategy/styles/BacktestGPU.shell.scss`
- `web/frontend/src/views/strategy/styles/BacktestGPU.status.scss`
- `web/frontend/src/views/strategy/styles/BacktestGPU.performance-controls.scss`
- `web/frontend/src/views/strategy/styles/BacktestGPU.logs-metrics.scss`
- `web/frontend/src/views/strategy/styles/BacktestGPU.element-plus.scss`
- `web/frontend/src/views/strategy/styles/BacktestGPU.responsive.scss`

## Quality Status

- Structural syntax errors: 0 for this batch, supported by Sass compile and `build:no-types`.
- Type inference errors: 0 observed in `npm run type-check`; baseline `reports/analysis/tech-debt-baseline.json` also records `frontend_type_errors: 0`.
- PM2 services: `mystocks-backend` and `mystocks-frontend` are online.
- E2E: focused `tests/artdeco-style.test.ts`, Chromium project, 3 passed / 0 failed / 0 skipped.

## Notes

The generated CSS was not byte-identical against `HEAD` because `HEAD` did not include the existing uncommitted BacktestGPU runtime-banner/control-note/value/responsive edits already present in the worktree. This report therefore treats the current worktree file as the pre-batch baseline and relies on Sass compile, import loading, line counts, token check, build, type check, and focused E2E for preservation evidence.
