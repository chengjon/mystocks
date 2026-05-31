# ArtDeco Route Header Shell Modification Rules

> **Authority note**: This document is an execution guide for future Web ArtDeco route-header-shell work. Repository-wide governance still follows `architecture/STANDARDS.md`, OpenSpec governance still follows `openspec/AGENTS.md`, and Function Tree governance remains the delivery gate for scoped implementation work.

## Purpose

Use this guide when modifying routed Web pages to adopt or maintain the shared ArtDeco route header shell.

The current rollout pattern was proven on:

- `/trade/positions`
- `/trade/portfolio`
- `/risk/alerts`
- `/market/realtime`

The goal is not to beautify pages opportunistically. The goal is to standardize the route-level header grammar while preserving each page's business behavior, API contracts, runtime state, test hooks, and domain semantics.

## What The Route Header Shell Implements

`ArtDecoRouteHeader` is a visual route-header shell. It standardizes how an already-routed page renders its top-level title, subtitle, status, metadata, actions, and route-local header content.

It provides:

- a shared `artdeco-route-header` class for visual grammar, linting, and E2E assertions
- a stable `test-id` mapping so existing page-level test hooks remain addressable
- standard title, subtitle, eyebrow, status text, status type, action, and meta slots
- an optional default slot for route-local runtime strips or page-specific header content
- a reusable shell that keeps ArtDeco token usage and header layout consistent across routed pages

It does not provide:

- route registration
- route redirection
- navigation menu wiring
- API request construction
- backend response parsing
- polling, retry, stale snapshot, or business-state ownership
- table, chart, filter, risk, market, or trade-domain behavior

The intended layering is:

```text
router/index.ts -> selects the existing page component
page component -> owns API calls, stores, runtime state, and domain behavior
ArtDecoRouteHeader -> renders the page header shell only
```

## Why This Is Not Router Or API Work

Route header shell migration happens inside an existing Vue page component. The same URL still resolves to the same page file, and the page continues to use the same stores, composables, handlers, and API clients.

The migration must therefore preserve this contract:

```text
same route path
same router entry
same page component
same frontend API client
same backend API contract
same runtime state ownership
different header rendering shell
```

Do not modify `web/frontend/src/router/index.ts` for a route header shell migration. Router changes require their own approved scope because they can affect active route truth, redirects, guards, navigation, embedded modes, and canonical route ownership.

Do not modify backend API contracts for a route header shell migration. The shell accepts already-computed display props and slots; it must not require new backend fields, changed response shapes, or changed OpenAPI/Pydantic schemas.

Do not modify frontend API clients for a route header shell migration. The page may continue passing existing computed status, request id, sample count, refresh handlers, and error/loading state into the header, but the shell must not construct requests or own data-fetching behavior.

## Route Fork Prevention

The current migration pattern must reduce route grammar drift, not create a second route system.

Allowed shape:

```text
/market/realtime -> web/frontend/src/views/market/Realtime.vue -> ArtDecoRouteHeader
```

Forbidden shape:

```text
/market/realtime -> legacy page
/artdeco/market/realtime -> redesigned page
```

Do not introduce:

- parallel ArtDeco routes
- wrapper routes for migrated pages
- legacy/canonical dual entries
- route aliases to a second implementation
- menu links that point to a new route for the same business page
- feature flags that switch between two routed page implementations
- embedded ArtDeco pages that become a competing source of route truth

The correct migration keeps one URL, one router entry, one page file, one set of API calls, and one business-state owner. Only the page-header rendering shell changes.

## When This Applies

Apply these rules when a task touches any of the following:

- A canonical routed page under `web/frontend/src/views/<domain>/*.vue`.
- A page header band using `hero-shell`, `hero-rail`, `hero-meta`, `ArtDecoHeader`, or route-level title/status/action composition.
- A migration to `web/frontend/src/components/artdeco/route-shell/ArtDecoRouteHeader.vue`.
- E2E assertions for route header hooks such as `*-header`, `*-refresh`, `*-status-strip`, route metadata, or page shell visibility.
- ArtDeco page design governance using impeccable, Function Tree, GitNexus, OpenSpec, or focused Playwright validation.

Do not use this guide as permission for unrelated page redesign, component extraction, route consolidation, API changes, or visual polish outside the approved node.

## Source Of Truth

Before changing a page, confirm these sources:

| Concern | Source |
|---|---|
| Repository governance and approval | `architecture/STANDARDS.md` |
| OpenSpec workflow | `openspec/AGENTS.md` |
| Active route truth | `web/frontend/src/router/index.ts` |
| Canonical page files | `web/frontend/src/views/<domain>/*.vue` |
| ArtDeco design context | `PRODUCT.md`, `DESIGN.md` |
| ArtDeco tokens | `web/frontend/src/styles/artdeco-tokens.scss` |
| Shared route shell | `web/frontend/src/components/artdeco/route-shell/ArtDecoRouteHeader.vue` |
| Function Tree map | `docs/FUNCTION_TREE.md` |
| Governance state | `.governance/programs/<program>/nodes.json` and `.governance/active-gates.*` |

## Required Preflight

Run this checklist before editing:

1. Confirm the user has approved implementation scope.
2. Read or query `architecture/STANDARDS.md` for current approval, route, API, and frontend gate rules.
3. If the task is planning, capability, architectural, or proposal-like work, open `openspec/AGENTS.md`.
4. Load impeccable context before design/UI mutation:

   ```text
   node /root/.agents/skills/impeccable/scripts/load-context.mjs
   ```

5. State the impeccable preflight before file edits:

   ```text
   IMPECCABLE_PREFLIGHT: context=pass product=pass command_reference=pass shape=not_required:<approved Function Tree header-shell-only migration> image_gate=skipped:no new visual asset mutation=open
   ```

6. Create or confirm an active Function Tree node when the change is implementation work.
7. Run Function Tree `scope-check` against the exact planned files.
8. Run GitNexus impact before editing a symbol. If GitNexus cannot resolve a Vue SFC, record the unknown result and add follow-up evidence with `query`, `context`, `route_map`, or staged `detect_changes`.
9. Check the worktree for unrelated dirty files. Do not stage, revert, or rewrite changes you did not make.

## Function Tree Rules

Every route header migration should be represented as a bounded node when it changes implementation.

Recommended node shape:

- Program: `artdeco-web-design-governance`
- Type: `implementation`
- Owner lane: `web-artdeco`
- Title format: `Migrate /<route> route header shell`
- Allowed paths:
  - the target page file
  - `web/frontend/src/components/artdeco/route-shell/`
  - the exact E2E file that validates the route
  - `docs/reports/tasks/`
  - `openspec/` only when the task needs spec evidence
- Non-goals:
  - no route path or router changes
  - no backend API contract changes
  - no frontend API client changes
  - no unrelated shared component extraction
  - no runtime state, table, filter, business semantic, or severity semantic changes unless explicitly approved
- Commit gates:
  - GitNexus impact or documented SFC-resolution limitation before edit
  - focused E2E for the target route
  - ArtDeco token check
  - `npx impeccable --json <file>`
  - focused ESLint
  - `npm run type-check -- --pretty false`
  - OpenSpec validation when applicable
  - Function Tree validation
- Closeout gates:
  - publish a task report under `docs/reports/tasks/`
  - confirm route/API/client/business state boundaries were preserved
  - confirm active gates are closed

Do not hand-edit generated active gate files unless a deterministic helper cannot express the required correction. Prefer `ft-governance` commands and `repair`.

## TDD Rule

Use a small E2E assertion to prove the route moved to the shared shell before changing implementation.

RED pattern:

```ts
await expect(page.getByTestId("<route-header-testid>")).toHaveClass(/artdeco-route-header/)
```

The old local shell should fail with a class similar to:

```text
hero-shell artdeco-card-shell
```

GREEN pattern:

- Replace only the page header shell.
- Keep all page copy, metadata, status props, actions, click handlers, loading state, and test IDs.
- Re-run the same focused test and then all focused route tests.

Do not weaken existing route E2E assertions to make the migration pass.

## Implementation Pattern

When migrating a page header:

1. Identify the local shell:

   ```vue
   <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell" data-testid="...">
     <div class="hero-rail">...</div>
     <ArtDecoHeader ...>
       <template #actions>...</template>
     </ArtDecoHeader>
   </section>
   ```

2. Replace it with `ArtDecoRouteHeader`:

   ```vue
   <ArtDecoRouteHeader
     v-if="!isEmbedded"
     title="..."
     subtitle="..."
     eyebrow="..."
     :show-status="true"
     :status-text="pageStatusText"
     :status-type="pageStatusType"
     test-id="..."
   >
     <template #meta>
       <span>REQ_ID: {{ displayRequestId }}</span>
       <span>...</span>
     </template>

     <template #actions>
       ...
     </template>
   </ArtDecoRouteHeader>
   ```

3. Update imports:

   ```ts
   import ArtDecoRouteHeader from '@/components/artdeco/route-shell/ArtDecoRouteHeader.vue'
   ```

4. Remove `ArtDecoHeader` from the page import only if it is no longer used.
5. Preserve the old `data-testid` through the `test-id` prop.
6. Preserve legacy `data-test` through `legacy-test` if the route has one.
7. Preserve `hero-meta` content and ordering.
8. Preserve embedded mode behavior such as `v-if="!isEmbedded"` or equivalent.
9. If the legacy header shell contains a route-local runtime strip, keep it as the `ArtDecoRouteHeader` default slot so the strip remains inside the same page header shell:

   ```vue
   <ArtDecoRouteHeader
     title="..."
     test-id="..."
     shell-class="route-header-shell artdeco-card-shell"
   >
     <template #actions>
       ...
     </template>

     <div class="status-strip" data-testid="...">
       ...
     </div>
   </ArtDecoRouteHeader>
   ```

## What Must Not Change Without Explicit Approval

Route header shell migrations must not change:

- `web/frontend/src/router/index.ts`
- route paths, aliases, guards, or navigation behavior
- backend routes, schemas, OpenAPI contract, or generated frontend types
- frontend API clients or request URLs
- page stores, composables, polling, retry, or stale snapshot behavior
- filter state, sort state, table columns, row semantics, or chart semantics
- A-share red/green financial conventions
- risk severity labels, priority ranking, alert triage semantics, or unread semantics
- runtime status strips, empty states, error states, degraded backend copy, or mock-data labels unless the approved node explicitly targets them
- unrelated ArtDeco polish such as borders, spacing, shadows, icons, decorative motion, or typography tweaks

## Dirty Worktree Rules

This repository often has unrelated uncommitted work. Follow these rules:

1. Treat existing dirty files as user or parallel-agent work.
2. Before editing, record relevant `git status --short` for the files you intend to touch.
3. If a file already has unrelated changes, stage only your hunks.
4. Use `git diff --cached` to prove the staged E2E diff contains only your intended assertion.
5. Never run destructive cleanup commands to make the worktree look clean.
6. Do not include unrelated documentation, generated files, reports, or test rewrites in the commit.
7. State any remaining unrelated dirty file in the final report.

## Verification Gate

For a route header shell migration, run at minimum:

```bash
cd web/frontend
npx playwright test tests/e2e/<matrix>.spec.ts -g "<RouteName>" --project=chromium
npm run test -- <route unit test if present>
npx eslint <route file> <e2e file> --quiet
node scripts/check-artdeco-tokens.js --target-file <route file relative to web/frontend>
npx impeccable --json <route file>
npm run type-check -- --pretty false
```

From the repo root, also run:

```bash
openspec validate --all --strict
node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs validate --steward
node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs gate --verbose
pm2 list
```

Before commit:

```bash
git diff --cached --check
```

Then run GitNexus staged scope detection. If GitNexus reports stale metadata, run:

```bash
npx gitnexus analyze
```

If the CLI analyze succeeds but MCP metadata still reports the old indexed commit, record it as a tool metadata warning and keep the staged risk result visible. Do not loop indefinitely.

## Commit And Closeout Rules

Use two commits when the Function Tree node requires closeout after implementation:

1. Implementation commit:

   ```text
   feat(web): migrate <route name> route header shell
   ```

2. Closeout commit:

   ```text
   docs(web): close <route name> route header gate
   ```

The implementation commit should include:

- target Vue page
- exact E2E assertion hunk
- Function Tree node/card/gate files needed to authorize the work
- task report under `docs/reports/tasks/`

The closeout commit should include only Function Tree closeout state files.

After closeout, `ft-governance gate --verbose` must show:

```text
active gates: none
```

## Final Response Checklist

When reporting completion, include:

- commits created
- files changed
- route migrated
- explicit non-changes: no route changes, no API contract changes, no frontend API client changes, no shared state or semantic changes
- RED and GREEN evidence
- focused E2E count, browser project, and pass count
- unit/lint/token/impeccable/type/OpenSpec/Function Tree/PM2/GitNexus results
- PM2 URLs:
  - backend: `http://localhost:8020`
  - frontend: `http://localhost:3020`
- structural syntax error count
- type-check result
- active gate state
- any unrelated dirty files left untouched

Do not claim completion until the verification commands have actually run and their outputs have been read.

## Current Route Header Shell Migration Ledger

| Route | Page file | Status |
|---|---|---|
| `/trade/positions` | `web/frontend/src/views/trade/Center.vue` | migrated |
| `/trade/portfolio` | `web/frontend/src/views/trade/Portfolio.vue` | migrated |
| `/risk/alerts` | `web/frontend/src/views/risk/Alerts.vue` | migrated |
| `/market/realtime` | `web/frontend/src/views/market/Realtime.vue` | migrated |
| `/trade/execution` | `web/frontend/src/views/trade/Execution.vue` | migrated |
| `/trade/reconciliation` | `web/frontend/src/views/trade/Reconciliation.vue` | migrated |

Future migrations should append to this ledger only after implementation and closeout are complete.
