# Frontend Navigation SSOT Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor frontend navigation so `router`, `menu`, and `views` are consistently mapped, testable, and maintainable without breaking existing URLs.

**Architecture:** Keep current online paths as compatibility baseline, split routing by functional access type, and make menu config the canonical navigation metadata source with explicit hidden-route ownership semantics. Add automated consistency checks to prevent future drift between menu paths, routes, route meta, and view files.

**Tech Stack:** Vue 3, Vue Router 4, TypeScript, Pinia, Vitest, Node scripts, OpenSpec.

## Route Classification Decisions (Phase 1 Baseline)

- `sidebar.routes.ts`: all menu-domain routes, including visible menu routes and hidden-but-owned menu routes.
- `feature.routes.ts`: non-menu functional routes that still require auth (entry and detail flows), e.g. `/dealing-room`, `/detail/*`.
- `public.routes.ts`: unauthenticated routes, e.g. `/login`, `/:pathMatch(.*)*`.
- `/dealing-room` stays in `feature.routes.ts` and remains the root redirect target.
- `/detail/*` stays in `feature.routes.ts` with `meta.requiresAuth = true` and `meta.isDetail = true`.
- Hidden routes `/strategy/parameters` and `/strategy/signals` stay in `sidebar.routes.ts` with `meta.hiddenInSidebar = true` and `meta.parentMenu = '/strategy'`.

### Task 1: Create OpenSpec Change Artifacts and Approval Gate

**Files:**
- Create: `openspec/changes/refactor-frontend-navigation-ssot/proposal.md`
- Create: `openspec/changes/refactor-frontend-navigation-ssot/tasks.md`
- Create: `openspec/changes/refactor-frontend-navigation-ssot/design.md`
- Create: `openspec/changes/refactor-frontend-navigation-ssot/specs/navigation/spec.md`

**Step 1: Scaffold change folder and required files**

Run:
```bash
mkdir -p openspec/changes/refactor-frontend-navigation-ssot/specs/navigation
touch openspec/changes/refactor-frontend-navigation-ssot/{proposal.md,tasks.md,design.md}
touch openspec/changes/refactor-frontend-navigation-ssot/specs/navigation/spec.md
```

Expected: files created.

**Step 2: Draft `proposal.md` with explicit scope**

```markdown
# Change: Refactor frontend navigation SSOT

## Why
Current route/menu/page definitions are split across multiple files with partial drift and no enforced consistency checks.

## What Changes
- Split router into `sidebar.routes.ts`, `feature.routes.ts`, `public.routes.ts`.
- Normalize menu metadata for hidden route ownership.
- Add route/menu/view consistency guard and CI-friendly report.
- Introduce phased compatibility shims for view path migration.

## Impact
- Affected specs: navigation
- Affected code: `web/frontend/src/router/*`, `web/frontend/src/layouts/MenuConfig.ts`, sidebar components, validation scripts/tests
- Breaking change: none in Phase 1 (URL compatible)
```

**Step 3: Draft `design.md` with architecture decisions**

```markdown
## Context
Navigation responsibilities are currently mixed between route files, layout config, and historical page directories.

## Goals / Non-Goals
- Goals: clear route layering, explicit ownership, machine-checkable consistency.
- Non-Goals: filesystem auto-route generation, mass deletion of historical views in Phase 1.

## Decisions
- Decision 1: Route layering by access/usage type (`sidebar`/`feature`/`public`).
- Decision 2: Hidden menu-owned routes remain in sidebar domain module, but are filtered from sidebar UI.
- Decision 3: `/dealing-room` and `/detail/*` are non-menu feature routes with auth.
- Decision 4: Keep URLs unchanged in Phase 1; use compatibility shims for moved view files.

## Risks / Trade-offs
- Risk: mixed old/new view paths during migration.
- Mitigation: compatibility shims + navigation consistency checker.

## Migration Plan
- Phase 1: structural split + checks + selective view moves.
- Phase 2: cleanup/archive of validated unused pages.
```

**Step 4: Draft `specs/navigation/spec.md` full framework**

```markdown
## ADDED Requirements

### Requirement: Route Layer Partitioning
The system SHALL partition frontend routes into sidebar routes, feature routes, and public routes.

#### Scenario: Classify route modules
- **WHEN** the router is assembled
- **THEN** routes are imported from `sidebar.routes.ts`, `feature.routes.ts`, and `public.routes.ts`
- **AND** each route belongs to exactly one module.

### Requirement: Hidden Route Ownership
The system SHALL support hidden routes that are owned by a menu domain.

#### Scenario: Hidden strategy routes
- **WHEN** `/strategy/parameters` and `/strategy/signals` are configured
- **THEN** they are reachable routes
- **AND** they are marked `hiddenInSidebar=true`
- **AND** ownership maps to `/strategy`.

### Requirement: Navigation Consistency Validation
The system SHALL provide an automated consistency checker for menu-route-view relationships.

#### Scenario: Detect mismatches
- **WHEN** consistency script runs
- **THEN** it reports `menuOnly`, `routeOnly`, `missingViews`, `orphanViews`, `ownershipErrors`, `metaGroupErrors`.

### Requirement: Compatibility Migration
The system SHALL keep existing URLs stable during Phase 1 view file migration.

#### Scenario: Move login page path
- **WHEN** login view moves from old path to new domain folder
- **THEN** route behavior remains unchanged
- **AND** compatibility shim remains until scheduled removal.
```

**Step 5: Draft `tasks.md` checklist and validate**

Run:
```bash
openspec validate refactor-frontend-navigation-ssot --strict
```

Expected: PASS.

**Step 6: Approval gate**

Do not implement code changes until explicit user approval.

### Task 2: Split Router by Type and Clarify Hidden Route Placement (No URL Change)

**Files:**
- Create: `web/frontend/src/router/routes/sidebar.routes.ts`
- Create: `web/frontend/src/router/routes/feature.routes.ts`
- Create: `web/frontend/src/router/routes/public.routes.ts`
- Modify: `web/frontend/src/router/index.ts`
- Test: `web/frontend/src/router/__tests__/route-structure.spec.ts`

**Step 1: Write failing route structure test**

```ts
it('classifies hidden menu-domain routes under sidebar module', () => {
  const report = inspectRouteModules()
  expect(report.sidebarPaths).toContain('/strategy/parameters')
  expect(report.sidebarPaths).toContain('/strategy/signals')
  expect(report.featurePaths).toContain('/dealing-room')
  expect(report.publicPaths).toContain('/login')
})
```

**Step 2: Run test to verify failure**

Run:
```bash
cd web/frontend && npm run test -- src/router/__tests__/route-structure.spec.ts
```

Expected: FAIL.

**Step 3: Implement modular route files**

- `sidebar.routes.ts`
  - includes all current menu-domain routes `/market`..`/system`
  - includes hidden menu-owned routes `/strategy/parameters`, `/strategy/signals`
  - hidden route meta: `{ hiddenInSidebar: true, parentMenu: '/strategy', group: 'strategy' }`
- `feature.routes.ts`
  - includes `/dealing-room` with `requiresAuth: true`
  - includes `/detail/graphics/:symbol`, `/detail/news/:symbol` with `requiresAuth: true`, `isDetail: true`
- `public.routes.ts`
  - includes `/login`, `/:pathMatch(.*)*` with `requiresAuth: false`
- `index.ts` composes all modules and keeps current guard/title behavior.

**Step 4: Quick validation (mandatory)**

Run:
```bash
cd web/frontend && npm run type-check
cd web/frontend && npm run test -- src/router/__tests__/route-structure.spec.ts
cd web/frontend && npm run check:navigation || true
```

Expected: type-check PASS; route test PASS; navigation check may fail before Task 4 exists.

**Step 5: Commit**

```bash
git add web/frontend/src/router web/frontend/src/router/__tests__/route-structure.spec.ts
git commit -m "refactor(frontend): split router by type and classify hidden menu-domain routes"
```

### Task 3: Define Menu Hidden Semantics and Ownership Metadata

**Files:**
- Modify: `web/frontend/src/layouts/MenuConfig.ts`
- Create: `web/frontend/src/layouts/menuHelpers.ts`
- Modify: `web/frontend/src/components/artdeco/trading/ArtDecoCollapsibleSidebar.vue`
- Test: `web/frontend/src/layouts/__tests__/menu-visibility.spec.ts`

**Step 1: Add menu types and failing tests**

```ts
interface MenuItem {
  path: string
  label: string
  icon: string
  businessKey: string
  children?: MenuItem[]
  meta?: {
    hidden?: boolean
    parentMenu?: string
    ownedRoutes?: string[]
  }
}
```

```ts
it('hides hidden children and preserves ownership metadata', () => {
  const sidebar = getSidebarMenu(ARTDECO_MENU_ITEMS)
  const strategy = sidebar.find(m => m.path === '/strategy')
  expect(strategy?.children?.some(c => c.path === '/strategy/parameters')).toBe(false)
  expect(strategy?.meta?.ownedRoutes).toContain('/strategy/parameters')
})
```

**Step 2: Run test to verify failure**

Run:
```bash
cd web/frontend && npm run test -- src/layouts/__tests__/menu-visibility.spec.ts
```

Expected: FAIL.

**Step 3: Implement semantics**

- `MenuConfig.ts`: for `strategy` domain, declare hidden child items or owned route list.
- `menuHelpers.ts`: implement `getSidebarMenu()` that filters hidden entries.
- Sidebar component consumes `getSidebarMenu()` result.

**Step 4: Quick validation (mandatory)**

Run:
```bash
cd web/frontend && npm run type-check
cd web/frontend && npm run test -- src/layouts/__tests__/menu-visibility.spec.ts
cd web/frontend && npm run check:navigation || true
```

Expected: type-check PASS; menu test PASS.

**Step 5: Commit**

```bash
git add web/frontend/src/layouts web/frontend/src/components/artdeco/trading/ArtDecoCollapsibleSidebar.vue
git commit -m "feat(frontend): define hidden menu semantics and route ownership metadata"
```

### Task 4: Expand Navigation Consistency Checker Scope

**Files:**
- Create: `web/frontend/scripts/check-navigation-consistency.mjs`
- Modify: `web/frontend/package.json`
- Test: `web/frontend/src/router/__tests__/navigation-consistency.spec.ts`

**Step 1: Write failing consistency tests**

```ts
it('validates menu-route-view ownership and group consistency', async () => {
  const report = await runConsistencyCheck()
  expect(report.menuOnly.length).toBe(0)
  expect(report.missingViews.length).toBe(0)
  expect(report.ownershipErrors.length).toBe(0)
  expect(report.metaGroupErrors.length).toBe(0)
})

it('reports orphan views for manual triage', async () => {
  const report = await runConsistencyCheck()
  expect(Array.isArray(report.orphanViews)).toBe(true)
})
```

**Step 2: Run test to verify failure**

Run:
```bash
cd web/frontend && npm run test -- src/router/__tests__/navigation-consistency.spec.ts
```

Expected: FAIL.

**Step 3: Implement checker with full scope**

Checker must validate:
1. menu path -> route existence
2. route -> view file existence
3. hidden route declaration in menu `ownedRoutes` or hidden child entry
4. view file referenced by at least one route (`orphanViews` output)
5. route `meta.group` aligns with menu `businessKey` domain mapping

Expected output fields:
- `menuOnly`
- `routeOnly`
- `missingViews`
- `orphanViews`
- `ownershipErrors`
- `metaGroupErrors`

Add script:
```json
"check:navigation": "node scripts/check-navigation-consistency.mjs"
```

**Step 4: Quick validation (mandatory)**

Run:
```bash
cd web/frontend && npm run check:navigation
cd web/frontend && npm run type-check
cd web/frontend && npm run test -- src/router/__tests__/navigation-consistency.spec.ts
```

Expected: PASS.

**Step 5: Commit**

```bash
git add web/frontend/scripts/check-navigation-consistency.mjs web/frontend/package.json web/frontend/src/router/__tests__/navigation-consistency.spec.ts
git commit -m "test(frontend): expand navigation consistency guard with ownership and group checks"
```

### Task 5: Migrate View File Structure with Compatibility Shim Lifecycle

**Files:**
- Create: `web/frontend/src/views/auth/Login.vue`
- Create: `web/frontend/src/views/404/NotFound.vue` (or reuse `views/errors/NotFound.vue` with clear convention)
- Create: `web/frontend/src/views/dealing-room/DealingRoom.vue`
- Modify: `web/frontend/src/router/routes/*.ts`
- Optional wrappers: `web/frontend/src/views/Login.vue`, `web/frontend/src/views/NotFound.vue`, legacy dealing-room view path
- Test: routing/unit/e2e smoke as below

**Step 1: Phase 1 move (new canonical files)**

- Create canonical files in target folders.
- Route imports switch to canonical files.

**Step 2: Phase 2 compatibility shims (same release)**

- Keep legacy files as thin wrappers to canonical component for compatibility and incremental cleanup.

Example shim:
```vue
<script setup lang="ts">
import LoginPage from '@/views/auth/Login.vue'
</script>
<template><LoginPage /></template>
```

**Step 3: Phase 3 shim removal (next version)**

- Remove legacy shim files only after consistency checker and usage scan confirm no references.
- Record removal plan in changelog/release notes.

**Step 4: Quick validation (mandatory)**

Run:
```bash
cd web/frontend && npm run type-check
cd web/frontend && npm run check:navigation
scripts/run_e2e_pm2.sh
```

Expected: PASS.

**Step 5: Commit**

```bash
git add web/frontend/src/views web/frontend/src/router
git commit -m "refactor(frontend): migrate core views with phased compatibility shims"
```

### Task 6: Inventory and Automated Governance for Unrouted Views

**Files:**
- Create: `web/frontend/scripts/inventory-unrouted-views.mjs`
- Create: `reports/analysis/unrouted-views-2026-03-02.json`
- Create: `docs/guides/frontend-navigation-cleanup-governance.md`

**Step 1: Implement inventory script with automated signals**

Per view file include:
- `hasRouteRef` (router reference)
- `isImported` (found by `rg` import/use)
- `lastCommitDate` (from `git log -1 --format=%cs -- <file>`)
- `isInDemoOrArchivePath` (path heuristic)
- `directoryCategory`

**Step 2: Define classification rules in governance doc**

- `active`: has route or strong runtime import evidence.
- `candidate`: no route now, but recently modified and referenced by active module.
- `archive`: demo/archive path or no route/import and stale by commit history.

**Step 3: Generate report**

Run:
```bash
cd web/frontend && node scripts/inventory-unrouted-views.mjs
```

Expected: JSON report with classification and evidence fields.

**Step 4: Quick validation (mandatory)**

Run:
```bash
cd web/frontend && npm run check:navigation
```

Expected: report generation and checker both runnable.

**Step 5: Commit**

```bash
git add web/frontend/scripts/inventory-unrouted-views.mjs reports/analysis/unrouted-views-2026-03-02.json docs/guides/frontend-navigation-cleanup-governance.md
git commit -m "docs(frontend): add evidence-based unrouted view inventory and governance"
```

### Task 7: Final Verification and Quality Gate

**Files:**
- Modify: `TASK-REPORT.md` (if worktree workflow requires)

**Step 1: Run frontend quality checks**

Run:
```bash
cd web/frontend && npm run lint
cd web/frontend && npm run type-check
cd web/frontend && npm run test
```

Expected: no new regressions.

**Step 2: Run PM2/E2E runtime gate**

Run:
```bash
scripts/run_e2e_pm2.sh
pm2 list
```

Expected:
- syntax errors: 0
- type errors: not above baseline `reports/analysis/tech-debt-baseline.json`
- PM2 services alive: `mystocks-backend` (`http://localhost:8000`), `mystocks-frontend` (`http://localhost:3020`)
- E2E baseline maintained

**Step 3: Publish verification summary**

- Separate newly introduced issues vs pre-existing technical debt.
- Include command output evidence for each gate.

## Rollback Plan

If consistency checks fail after Task 4:
1. Revert Task 4 commit.
2. Re-run `npm run check:navigation` and capture failure category.
3. If failure originates from Task 2-3 classification, revert Task 3 then Task 2 commits.
4. Re-analyze ownership and `meta.group` mappings, patch tests first, then re-apply incrementally.

## Known Limitations (Phase 1)

- Hidden routes must be explicitly declared in menu config ownership metadata.
- No filesystem auto-route discovery.
- Manual review still required for unrouted view categorization.
- Phase 2 can add automated prioritization/remediation workflows.
