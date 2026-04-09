# Phase 7: Entry Consolidation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-09
**Phase:** 07-entry-consolidation
**Areas discussed:** Feature Migration, Router Consolidation, verify-mount.js Disposition, Demo Test Disposition, Traceability

---

## Feature Migration Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Full migration | Merge ALL features from main.js into main-standard.ts | ✓ |
| Selective migration | Migrate only production-critical features, deprecate rest | |
| No migration | Archive main.js as-is, accept features not in standard boot | |

**User's choice:** Full migration with clean rewrite
**Notes:** main-standard.ts is "minimal entry" vs main.js "full entry". Migrating all capabilities ensures no features are lost. Bloomberg styles explicitly excluded (ArtDeco is current design system).

### Per-capability decisions

| Capability | Decision |
|------------|----------|
| CSRF security init | MIGRATE |
| Contract validation error handler | MIGRATE |
| PWA / Service Worker registration | MIGRATE |
| Session restore | MIGRATE |
| Element Plus icons registration | MIGRATE |
| API version negotiation | MIGRATE |
| Global Vue instance (window.$vue) | MIGRATE |
| Bloomberg terminal override styles | DROP |

---

## Entry Point Quality

| Option | Description | Selected |
|--------|-------------|----------|
| Clean rewrite | Production-quality, organized imports, remove debug logs | ✓ |
| Minimal merge | Copy-paste features as-is, minimal changes | |

**User's choice:** Clean rewrite
**Notes:** Remove verbose console.log debugging (🏁, 📦, 🗺️, 🚀, ✅ emojis). Add proper comments by responsibility sections.

---

## Router Consolidation

### Demo route URL scheme

| Option | Description | Selected |
|--------|-------------|----------|
| /demo/* (test expectations) | Matches all-pages-accessibility.spec.ts | |
| /*-demo (legacy) | Matches router/index.js paths | |
| No demo routes | Don't add demo routes — features planned for integration into main pages | ✓ |

**User's choice:** No demo routes added to index.ts
**Notes:** User's original plan is to integrate demo features into existing pages, not maintain separate demo routes. Demo views kept as reference code for future integration.

### Wencai / Phase4Dashboard

**Decision:** No routes added for Wencai or Phase4Dashboard. Consistent with "no demo routes" decision above. Both views exist in the codebase but are kept as reference code for future feature integration.

| Route | Status | Reason |
|-------|--------|--------|
| Wencai (/demo/wencai) | NOT added | Feature planned for integration into main pages, not separate demo route |
| Phase4Dashboard (/phase4-dashboard) | NOT added | phase4.routes.js references StrategyMgmtPhase4.vue which doesn't exist |

### Router artifacts

| Option | Description | Selected |
|--------|-------------|----------|
| Clean up all artifacts | Delete 3 backups, .clean, phase4.routes.js, index.js | ✓ |
| Keep backups | Historical reference | |

**User's choice:** Clean up all artifacts

---

## verify-mount.js Disposition

| Option | Description | Selected |
|--------|-------------|----------|
| Update and keep | Read main-standard.ts instead of main.js | |
| Delete it | Remove — not in CI, weak validation, hardcoded to main.js | ✓ |
| Archive it | Move to _entry-archive/ | |

**User's choice:** Delete
**Notes:** Not in any package.json script or CI. Hardcodes src/main.js path. Weak validation (just checks app.mount text). Deleting removes the only remaining consumer of main.js.

---

## Demo Test Disposition

| Option | Description | Selected |
|--------|-------------|----------|
| Remove demo assertions now | Clean up test files to match active router reality | ✓ |
| Defer test updates | Keep tests as-is, accept they may fail | |

**User's choice:** Remove demo assertions now
**Notes:** Two test files need updates:
1. `all-pages-accessibility.spec.ts` lines 66-71: Remove 5 demo page entries (OpenStock, Freqtrade, Stock Analysis, TDXPY, Smart Data)
2. `menu-configuration.spec.js` lines 121-144: Remove entire "功能演示菜单" test block — includes demoMenus array (7 items with visibility assertions) AND Wencai click/URL assertion. Entire test is orphaned.

---

## Traceability

| Option | Description | Selected |
|--------|-------------|----------|
| Update traceability | Reclassify demo/ as reference code, update REQUIREMENTS.md and Phase 6 D-08 | ✓ |
| Skip update | Leave traceability as-is | |

**User's choice:** Update traceability
**Notes:** views/demo/ reclassified from "active, not safely deletable" to "reference code, not routed." Phase 6 D-08 note updated from "unresolved" to "resolved."

---

## Approval Gate

**Decision:** Openspec proposal required before implementation. Full migration changes runtime behavior (adding security init, PWA, session restore, contract validation to active boot). Per architecture/STANDARDS.md, this requires proposal approval.

---

## Claude's Discretion

- Exact import organization in rewritten main-standard.ts
- Comment style and section headers
- Whether to keep or refactor try/catch wrapper
- Verification commands for dev server + build + hot-reload

## Deferred Ideas

- Integrating demo view features into main pages — future phase
- Type debt remediation for views/demo/ tsconfig exclusion — separate concern
- Upgrading verify-mount.js into a proper CI gate — deleted instead
