# Phase 7: Entry Consolidation - Research

**Researched:** 2026-04-09
**Phase:** 07-entry-consolidation
**Status:** Research complete

---

## Summary

Phase 7 resolves STRU-03 by consolidating two frontend entry points into one. The runtime truth already points to `main-standard.ts` (via `index.html` line 67), but this file is a minimal 47-line stub missing 7 production-critical capabilities that `main.js` (187 lines) currently provides. The migration is a clean transplant — no architectural redesign, just code movement with careful async ordering.

**Key blocker:** CONTEXT.md D-14 requires an OpenSpec proposal before implementation begins, as migrating capabilities into the active boot path changes runtime behavior.

---

## 1. Current State Analysis

### Entry Point Landscape

| File | Lines | Role | Status |
|------|-------|------|--------|
| `main-standard.ts` | 47 | Active entry (index.html points here) | Minimal stub, debug-heavy |
| `main.js` | 187 | Full production entry | All capabilities, unused at runtime |
| `main.js.backup` | ~187 | Backup of main.js | Redundant, to archive/delete |
| `verify-mount.js` | 34 | Standalone Node validation script | Reads main.js, not in CI, safe to delete |

### Runtime Truth

`web/frontend/index.html:67`:
```html
<script type="module" src="/src/main-standard.ts"></script>
```

No references to `main.js`, `verify-mount.js`, or `router/index.js` in `vite.config.*`, `package.json`, or any active source file. The legacy files are fully disconnected from the build pipeline.

### Router Directory State

| File | Lines | Status |
|------|-------|--------|
| `router/index.ts` | 346 | Active — typed, auth guards, sole source of truth |
| `router/index.js` | ~300 | Legacy — deprecated layouts, demo routes |
| `router/index.js.backup` | ~300 | Artifact — delete |
| `router/index.ts.backup` | ~600 | Artifact — delete |
| `router/index.js.backup-phase2.3` | ~300 | Artifact — delete |
| `router/index.js.clean` | ~300 | Artifact — delete |
| `router/phase4.routes.js` | 20 | Artifact — references non-existent StrategyMgmtPhase4.vue, delete |

---

## 2. Capability Migration Inventory

Capabilities to transplant from `main.js` into `main-standard.ts`:

### MIGRATE (7 capabilities)

| # | Capability | main.js Location | Dependency | Async? |
|---|-----------|------------------|------------|--------|
| 1 | Element Plus icons registration | lines 51-54 | `@element-plus/icons-vue` | No (sync) |
| 2 | CSRF security init | lines 138-147 | `./services/httpClient.js` ✓ exists | Yes (race + 2s timeout) |
| 3 | Contract validation error handler | lines 60-84 | `./api/unifiedApiClient.ts` ✓ exists | No (sync config) |
| 4 | PWA/Service Worker registration | lines 102-134 | `public/sw.js` ✓ exists | Yes (post-load) |
| 5 | Session restore | lines 163-169 | `./utils/sessionRestore.js` ✓ exists | Yes (dynamic import) |
| 6 | API version negotiation | lines 157-159 | `./services/versionNegotiator.ts` ✓ exists | Yes (after security) |
| 7 | Global Vue instance | lines 184-186 | None | No (sync) |

### DROP (1 capability)

| # | Capability | Reason |
|---|-----------|--------|
| 8 | Bloomberg terminal override styles | Legacy layer; ArtDeco is current design system |

### KEEP (already in main-standard.ts)

- ArtDeco style imports (artdeco-global, artdeco-financial, fintech-design-system)
- Element Plus override styles
- Visual/pro-fintech optimization styles
- ECharts optimization import
- ArtDecoCardCompact component registration

### Dependency Verification

All dependency files confirmed to exist:
- `src/services/httpClient.js` ✓
- `src/services/versionNegotiator.ts` ✓
- `src/api/unifiedApiClient.ts` ✓
- `src/utils/sessionRestore.js` ✓
- `public/sw.js` ✓
- `@element-plus/icons-vue` (npm package) ✓

---

## 3. Async Initialization Pattern

main.js uses a critical non-blocking pattern that must be preserved:

```
1. Sync: createApp → use(pinia) → use(router) → component registrations → mount('#app')
2. Async (non-blocking, after mount):
   a. PWA: Service Worker registration (on window.load)
   b. Security: initializeSecurity() with 2-second timeout race
   c. After security completes:
      - showVersionNotifications()
      - restoreSession() (dynamic import)
```

**Why this matters:** Synchronous mount ensures the UI renders immediately. Async init runs in background without blocking render. This pattern is production-critical and must be preserved exactly.

---

## 4. Test Impact Analysis

### Files Requiring Updates

| File | Lines | Change | Risk |
|------|-------|--------|------|
| `tests/all-pages-accessibility.spec.ts` | 66-71 | Remove 5 demo page entries | Low — dead routes |
| `tests/menu-configuration.spec.js` | 121-144 | Remove entire "功能演示菜单" test block | Low — orphaned test |

### Verification Commands

After migration, these must pass:
1. `npm run dev` — dev server starts, hot-reload works
2. `npm run build` — production build succeeds
3. `npx vue-tsc --noEmit` — no type errors (main-standard.ts must be typed)
4. Test suite: the modified test files must still pass

---

## 5. OpenSpec Requirement (Blocker)

CONTEXT.md D-14 mandates an OpenSpec proposal before implementation. This is because:
- Migrating capabilities changes runtime behavior of the active entry point
- Security init, PWA, session restore are production features being added to the boot path
- `architecture/STANDARDS.md` requires approval for architecture-impacting changes

**What the proposal should cover:**
1. Capabilities being migrated (7 items above)
2. Runtime behavior change (adding async init chain to active boot)
3. Rollback plan (main.js remains as archive; revert index.html to point back)
4. Verification criteria (dev/build/test all pass)

**Recommendation:** Include the OpenSpec proposal creation as the first task in the plan, before any code changes. The proposal can be lightweight — the CONTEXT.md decisions already capture the design rationale.

---

## 6. Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Deleting verify-mount.js | LOW | Standalone script, no CI integration, no package.json reference |
| Deleting router artifacts (6 files) | LOW | No active imports from any of these files |
| Rewriting main-standard.ts | MEDIUM | Runtime entry point change; mitigate with dev/build verification |
| Removing test assertions | MEDIUM | Tests for dead routes; verify suite still passes after removal |
| OpenSpec gate | HIGH (blocker) | Must create proposal first; cannot proceed without approval |
| Missing capability during migration | MEDIUM | Inventory is complete (7 MIGRATE + 1 DROP); verify with dev server testing |

---

## 7. Implementation Approach

### Wave Structure Recommendation

**Wave 1 — OpenSpec Proposal + Cleanup (safe deletions)**
- Create OpenSpec proposal documenting the migration
- Delete verify-mount.js (ENTRY-01)
- Delete router artifacts (6 files)
- Remove dead test assertions

**Wave 2 — Entry Point Migration (core work)**
- Rewrite main-standard.ts with all 7 capabilities
- Archive main.js and main.js.backup (ENTRY-02)
- Update REQUIREMENTS.md traceability (D-12, D-13)

**Wave 3 — Verification (ENTRY-03)**
- Run `npm run dev`, `npm run build`, `vue-tsc --noEmit`
- Run modified test suite
- Confirm single entry point

---

## RESEARCH COMPLETE

Phase 7 is well-scoped with clear inventory. The main complexity is the non-blocking async init pattern preservation, not architectural discovery. The OpenSpec proposal is the only external gate.
