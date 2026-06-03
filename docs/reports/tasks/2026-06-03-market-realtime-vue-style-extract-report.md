# Market Realtime Vue Style Extract Report (2026-06-03)

## Scope

Function Tree node: `artdeco-web-design-governance/market-realtime-vue-style-extract`

This task mechanically externalized the scoped SCSS block from `web/frontend/src/views/market/Realtime.vue` into a view-local stylesheet.

Committed files:

- `web/frontend/src/views/market/Realtime.vue`
- `web/frontend/src/views/market/styles/RealtimePage.scss`
- `.governance/active-gates.json`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/cards/market-realtime-vue-style-extract.yaml`
- `docs/reports/tasks/2026-06-03-market-realtime-vue-style-extract-report.md`

`.governance/active-gates.md` was synchronized by the Function Tree helper but had no net final diff.

## Rationale

`Realtime.vue` was a frontend large-file offender because its scoped SCSS was embedded in the SFC. The page had 654 lines before this task, including a 263-line scoped SCSS body. Moving that style body into a view-local SCSS file reduces the Vue SFC below the 500-line threshold without changing runtime behavior.

The new file is named `RealtimePage.scss` instead of reusing `styles/Realtime.scss` because `styles/Realtime.scss` already exists, has different legacy content, and is not an exact copy of the current inline scoped style. This task deliberately avoids overwriting or repurposing that existing asset.

## Non-Goals Preserved

- No router route, alias, navigation, or canonical route truth changes.
- No backend API contract, OpenAPI/schema, or frontend API client changes.
- No Vue/TypeScript runtime logic, data fetching, computed state, template structure, props, or emitted-event changes.
- No shared component extraction.
- No visual redesign, ArtDeco token value changes, or style reinterpretation.
- No touch to unrelated `web/frontend/src/views/market/styles/Tdx.scss` deletion or BacktestGPU worktree changes.

## Implementation

`Realtime.vue` now references the extracted style through SFC style `src` syntax:

```vue
<style scoped lang="scss" src="./styles/RealtimePage.scss"></style>
```

This preserves Vue SFC scoped-style semantics. The SCSS file content is an exact byte-for-byte match to the original inline scoped style body from `HEAD:web/frontend/src/views/market/Realtime.vue`.

## Measurements

Line-count method: split files by LF in the current worktree.

- `Realtime.vue`: 654 lines -> 390 lines.
- Extracted style body: 263 lines.
- `web/frontend/src` Vue/TS/TSX files over 500 lines: 35 -> 34.

## GitNexus Evidence

- Ran local `gitnexus analyze --index-only --max-file-size 64 --worker-timeout 10` before implementation, per user preference. Did not use `npx`.
- Refreshed index state reported `stale=false` and `fresh_for_staged_diff=true` before source edits.
- GitNexus could not resolve `web/frontend/src/views/market/Realtime.vue` or `Realtime` as an impact target, so symbol impact remained `UNKNOWN`. This is recorded as a tool limitation for this SFC style-only task.
- Ran local `gitnexus analyze --index-only --max-file-size 64 --worker-timeout 10` again after implementation. It completed successfully with 230,734 nodes, 316,240 edges, 2,730 clusters, and 300 flows.

## Validation

Passed:

- Function Tree scope-check: changed files within active authorization.
- Exact style preservation check: `RealtimePage.scss === HEAD inline scoped style body`.
- `git diff --check` for authorized changed files.
- ArtDeco changed-file token check for `src/views/market/Realtime.vue`.
- ArtDeco changed-file token check for `src/views/market/styles/RealtimePage.scss`.
- `web/frontend`: `npm run build:no-types` passed with Vite build completion.
- PM2 status confirmed:
  - `mystocks-backend` online, PID 945, `http://localhost:8020`
  - `mystocks-frontend` online, PID 946, `http://localhost:3020`

Not run:

- `vue-tsc`: not run because this task did not change TypeScript, props, template bindings, runtime logic, API clients, or schemas.
- E2E: not run because this task did not change router, layout behavior, API contracts, frontend API client behavior, or user workflow logic. The build and exact style-preservation checks are the relevant gates for this mechanical scoped-style extraction.

## Quality Status Confirmation

- Structural syntax errors: 0 observed in `npm run build:no-types`.
- Type inference errors: not measured in this task; no TypeScript/runtime files were changed beyond replacing the SFC style block with `style src`.
- PM2 services: online at the required service addresses listed above.
- E2E status: not executed for this style-only extraction; no fixed historical pass-count wording used.

## Result

This task removes one Vue large-file violation while preserving scoped style behavior and avoiding route/API/client/component/design changes.
