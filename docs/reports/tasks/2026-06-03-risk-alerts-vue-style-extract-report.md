# Risk Alerts Vue Style Extract Report

## Scope

This task reduces the large-file violation for `web/frontend/src/views/risk/Alerts.vue` by extracting only its existing scoped style block to a view-local SCSS file.

Allowed files:

- `web/frontend/src/views/risk/Alerts.vue`
- `web/frontend/src/views/risk/styles/Alerts.scss`
- Function Tree governance node files for `risk-alerts-vue-style-extract`
- This report

Non-goals:

- No router route changes.
- No backend API, OpenAPI/schema, or frontend API client changes.
- No Vue/TypeScript runtime behavior changes.
- No shared component extraction.
- No visual redesign or ArtDeco token value changes.
- No edits to other dirty `web/frontend/src/views/risk/*` files.

## Change

Before:

- `Alerts.vue`: 771 lines
- Inline `<style scoped lang="scss">...</style>` block: 287 style-body lines

After:

- `Alerts.vue`: 485 lines
- `styles/Alerts.scss`: 286 lines
- Current Vue/TS/TSX over-500 count under `web/frontend/src`: 36
- `Alerts.vue` is no longer over the 500-line threshold.

The Vue file now uses:

```vue
<style scoped lang="scss" src="./styles/Alerts.scss"></style>
```

This keeps Vue SFC scoped-style compilation semantics. A plain script-side `import './styles/Alerts.scss'` was intentionally not kept because it would make the extracted selectors global.

## Preservation Evidence

The extracted SCSS body was compared against `HEAD:web/frontend/src/views/risk/Alerts.vue` original scoped style body:

- `style_match: true`
- Inline style block removed from `Alerts.vue`
- Style `src` is present
- Script-side style import is absent

No selector, declaration, token reference, or style order was intentionally changed.

## GitNexus Impact

Target:

```text
File:web/frontend/src/views/risk/Alerts.vue
```

Impact result:

- Risk: LOW
- direct: 2
- impactedCount: 14
- affected_processes: 0
- affected_modules: 0

Local GitNexus refresh was run with the user-preferred local CLI:

```bash
gitnexus analyze --index-only --max-file-size 64 --worker-timeout 10
```

Result:

- Repository indexed successfully
- 230,698 nodes
- 316,204 edges
- 2730 clusters
- 300 flows

The GitNexus MCP impact response still reported stale metadata, but `fresh_for_staged_diff` was true after the local refresh. This matches the previously observed MCP metadata lag pattern.

## Validation

Passed:

- Function Tree scope-check: 3 changed files within active authorization
- Style preservation check: `style_match: true`
- `git diff --check` for changed files
- ArtDeco token check:
  - `node scripts/check-artdeco-tokens.js --target-file src/views/risk/Alerts.vue`
  - `node scripts/check-artdeco-tokens.js --target-file src/views/risk/styles/Alerts.scss`
- `cd web/frontend && npm run build:no-types`
  - Vite modules transformed: 2583
  - Built in 32.66s

Staged validation:

- staged allow-list check: passed, 6 files staged and all inside scope
- `.governance/programs/artdeco-web-design-governance/tree.md`: not staged
- unrelated backend risk files: not staged
- unrelated dirty risk pages/tests: not staged
- BacktestGPU work: not staged
- `docs/reports/tasks/2026-06-02-gitnexus-usage-feedback.md`: not staged
- `git diff --cached --check`: passed
- staged preservation check: `style_match: true`

GitNexus staged `detect_changes`:

- changed_files: 6
- risk_level: low
- affected_processes: 0
- fresh_for_staged_diff: true
- changed_file_classes: config 3 / documentation 1 / source 1 / style 1

Final local GitNexus refresh:

```bash
gitnexus analyze --index-only --max-file-size 64 --worker-timeout 10
```

Result:

- Repository indexed successfully
- 230,723 nodes
- 316,229 edges
- 2730 clusters
- 300 flows
- `tree-sitter-proto` optional grammar warning remains unrelated to this task.

PM2 services:

- `mystocks-backend`: online, `http://localhost:8020`
- `mystocks-frontend`: online, `http://localhost:3020`

## Function Tree

- Program: `artdeco-web-design-governance`
- Node: `risk-alerts-vue-style-extract`
- Status target: closeout then commit.
