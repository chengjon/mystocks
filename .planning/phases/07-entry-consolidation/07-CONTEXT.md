# Phase 7: Entry Consolidation - Context

**Gathered:** 2026-04-09
**Status:** Ready for planning (openspec proposal required before implementation)

<domain>
## Phase Boundary

Consolidate frontend entry points to a single canonical source (`main-standard.ts`). Resolve STRU-03 by handling verify-mount.js, archiving main.js, and cleaning up router artifacts. The migrated entry point becomes the full runtime boot — incorporating all production-critical startup responsibilities from main.js.

Requirements: ENTRY-01, ENTRY-02, ENTRY-03

**Scope change from original ROADMAP:** Full migration of main.js capabilities into main-standard.ts (not just archival). This is a runtime behavior change requiring openspec proposal approval before implementation.

</domain>

<decisions>
## Implementation Decisions

### Feature Migration (per-capability)

| Capability | main.js location | Decision | Rationale |
|------------|-----------------|----------|-----------|
| CSRF security init (`initializeSecurity()`) | line 138-147 | **MIGRATE** | Production-critical security |
| Contract validation error handler (`ContractValidationError`) | line 60-84 | **MIGRATE** | API contract drift detection |
| PWA / Service Worker registration | line 102-134 | **MIGRATE** | Production feature |
| Session restore (`restoreSession()`) | line 163-169 | **MIGRATE** | Session continuity |
| Element Plus icons registration | line 52-54 | **MIGRATE** | Icons not covered by auto-import |
| API version negotiation (`showVersionNotifications()`) | line 157-159 | **MIGRATE** | API compatibility |
| Global Vue instance (`window.$vue`) | line 184-186 | **MIGRATE** | Browser debugging |
| Bloomberg terminal override styles | line 37 | **DROP** | Legacy layer; ArtDeco is current design system |
| ArtDeco style imports | already in main-standard.ts | **KEEP** | Already present |
| ECharts optimization import | already in main-standard.ts | **KEEP** | Already present |
| ArtDecoCardCompact registration | already in main-standard.ts | **KEEP** | Already present |

- **D-01:** main-standard.ts gets a clean rewrite to production quality. Remove all debug console.log statements (`🏁 Standard Boot Started`, `📦 Pinia Created`, `🗺️ Router Linking`, etc.). Add proper comments organized by responsibility sections.
- **D-02:** Non-blocking async pattern from main.js is preserved: app mounts synchronously, security/PWA/session init run async after mount.

### Entry Point Disposition

- **D-03:** `main.js` → archived (moved to `_entry-archive/` or deleted). After full migration, no features are lost.
- **D-04:** `main.js.backup` → archived/deleted alongside main.js.
- **D-05:** `verify-mount.js` → **deleted**. It's a standalone Node script not in any CI/package.json script. Hardcodes `src/main.js` path. Weak validation (just checks `app.mount` text presence). Deleting it removes the only remaining consumer of main.js.

### Router Consolidation

- **D-06:** `router/index.ts` stays as-is — **no demo routes added**. Demo views are reference code; user plans to integrate their features into main pages in future work.
- **D-07:** `router/index.js` → **deleted**. Legacy router with demo routes and outdated layouts (MarketLayout, DataLayout, StrategyLayout, etc.). After demo test assertions are removed, index.js has no consumers.
- **D-08:** Router artifact cleanup — delete ALL of the following:
  - `router/index.js.backup`
  - `router/index.ts.backup`
  - `router/index.js.backup-phase2.3`
  - `router/index.js.clean`
  - `router/phase4.routes.js`

### Demo Route Tests

- **D-09:** Remove demo page assertions from `tests/all-pages-accessibility.spec.ts` (lines 66-71: 5 demo page entries). These test routes that don't exist in the active router.
- **D-10:** Remove entire "功能演示菜单" test block from `tests/menu-configuration.spec.js` (lines 121-144). This includes: the demoMenus array (OpenStock, PyProfiling, Freqtrade, Stock-Analysis, pytdx, Phase 4 Dashboard, Wencai visibility assertions at lines 126-138), plus the Wencai click + URL assertion (lines 141-143). The entire test is orphaned — it asserts a demo submenu and /demo/* URLs that don't exist in the active router.
- **D-11:** Demo views (`views/demo/`) reclassified from "active, not safely deletable" to "reference code, not routed." Traceability update required in REQUIREMENTS.md. Phase 6 D-08 ("route truth unresolved") is resolved by this phase — add resolution note in Phase 7 documents, do NOT modify Phase 6's historical context.

### Traceability Updates

- **D-12:** Update REQUIREMENTS.md traceability for ARCH-03: add note that demo/ views are reclassified as reference code (not routed in index.ts, features planned for future integration into main pages).
- **D-13:** Add resolution note in Phase 7 documents: Phase 6 D-08 ("route truth unresolved") is resolved — demo views kept as reference code, not routed in canonical router. Do NOT modify Phase 6's historical context file (it is a phase snapshot).

### Approval Gate

- **D-14:** Full migration changes runtime behavior (adding security init, PWA, session restore, contract validation to active boot). Per `architecture/STANDARDS.md`, this requires an openspec proposal before implementation begins. The openspec proposal should document: capabilities being migrated, runtime behavior changes, and rollback plan.

### Claude's Discretion

- Exact organization of imports in the rewritten main-standard.ts (grouping, ordering)
- Comment style and section headers in the rewritten entry
- Whether to keep or refactor the try/catch wrapper from current main-standard.ts
- Verification commands for dev server + build + hot-reload testing

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Entry point files
- `web/frontend/src/main-standard.ts` — Active entry point (target of migration). 47 lines, minimal, needs full rewrite.
- `web/frontend/src/main.js` — Full entry point (source of migration). 187 lines with all production capabilities.
- `web/frontend/index.html` — Runtime truth: `<script type="module" src="/src/main-standard.ts">` (line 67)
- `web/frontend/verify-mount.js` — Standalone Node script reading main.js. To be deleted.

### Router files
- `web/frontend/src/router/index.ts` — Active router (sole source of truth after cleanup). 346 lines, typed, auth guards.
- `web/frontend/src/router/index.js` — Legacy router. To be deleted along with all backup artifacts.
- `web/frontend/src/router/phase4.routes.js` — Phase 4 route definitions. References StrategyMgmtPhase4.vue which doesn't exist. To be deleted.

### Test files needing updates
- `web/frontend/tests/all-pages-accessibility.spec.ts` §66-71 — Demo page assertions to remove
- `web/frontend/tests/menu-configuration.spec.js` §126-143 — Demo menu + Wencai assertions to remove

### Planning artifacts
- `.planning/ROADMAP.md` §Phase 7 — Phase scope, requirements, success criteria
- `.planning/REQUIREMENTS.md` — ENTRY-01, ENTRY-02, ENTRY-03 + traceability update needed
- `.planning/STATE.md` — Current project state

### Prior phase context
- `.planning/phases/03-structural-consolidation/03-CONTEXT.md` §D-07 through D-10 — Original entry point audit decisions
- `.planning/phases/06-archive-cleanup/06-CONTEXT.md` §D-08 — Deferred route truth (now resolved in D-06/D-11 above)

### Project governance
- `architecture/STANDARDS.md` — Architecture change approval requirements (openspec proposal needed)

</canonical_refs>

<code_context>
## Existing Code Insights

### main.js capabilities inventory
- Element Plus icons: globally registered via `for...of Object.entries(ElementPlusIconsVue)` — NOT covered by auto-import (comment at line 51)
- Security: `initializeSecurity()` with 2-second timeout race pattern — non-blocking
- Contract validation: `app.config.errorHandler` catches `ContractValidationError` with dev/prod behavior split
- PWA: Service Worker registration with update detection + controller change auto-reload
- Session restore: dynamic `import('./utils/sessionRestore.js')` — non-blocking
- Version negotiation: `showVersionNotifications()` called after security init completes
- Debug: `window.$vue = app` for browser console access

### main-standard.ts current state
- 47 lines, minimal: createApp, createPinia, App.vue, router, style imports, ArtDecoCardCompact
- Has verbose debug console.log on every step
- Wrapped in try/catch that catches but doesn't handle errors well
- Already imports: ArtDeco styles, fintech styles, element-plus overrides, visual/pro-fintech optimization, echarts

### Router directory state
- `index.ts`: 346 lines, fully typed, uses `authGuard`, `homeRoute` constants, lazy-loaded components
- `index.js`: Legacy, uses deprecated layouts (MarketLayout, DataLayout, etc.), has 6 demo routes
- 5 artifact files (backups, .clean, phase4 routes) to delete
- No active consumer of index.js (main-standard.ts imports index.ts)

### Integration Points
- `index.html` line 67 → `main-standard.ts` — the runtime entry contract
- `main-standard.ts` line 4 → `router/index.ts` — the routing contract
- `vite.config.js` → build pipeline (no reference to main.js or index.js)
- `package.json` → no script references verify-mount.js

</code_context>

<specifics>
## Specific Ideas

- Non-blocking async pattern from main.js is worth preserving: app mounts synchronously first, then security/PWA/session init run async. This ensures UI renders fast.
- The clean rewrite should organize imports by category: framework → styles → components → services → async init
- Debug console.log should be replaced with a single boot-time log in dev mode only (`import.meta.env.DEV`)

</specifics>

<deferred>
## Deferred Ideas

- Integrating demo view features into main pages — future phase, not Phase 7
- Type debt remediation for views/demo/ tsconfig exclusion — separate concern
- Wencai route in index.ts — defer until feature integration phase
- Phase4Dashboard route — defer (StrategyMgmtPhase4.vue doesn't exist)
- Upgrading verify-mount.js into a proper CI gate — not planned; delete instead

</deferred>

---
*Phase: 07-entry-consolidation*
*Context gathered: 2026-04-09*
