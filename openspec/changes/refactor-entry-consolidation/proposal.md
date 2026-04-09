---
change_id: refactor-entry-consolidation
status: pending
created: 2026-04-09
author: Phase 07 execution
phase: 07-entry-consolidation
---

# Refactor: Entry Point Consolidation

## Summary

Migrate 7 production capabilities from `main.js` into `main-standard.ts`, making it the full production entry point. Archive `main.js` after migration. This resolves STRU-03 (duplicate entry points) by completing the consolidation that was started when `index.html` was pointed to `main-standard.ts`.

## Background

`main-standard.ts` (47 lines) is the active runtime entry point — `index.html` line 67 references it. However, it is a minimal stub missing 7 production-critical capabilities that `main.js` (187 lines) provides. The runtime behavior is degraded because these capabilities (security init, PWA, session restore, version negotiation) are not running in production.

## Capabilities Being Migrated

| # | Capability | Type | Dependency |
|---|-----------|------|------------|
| 1 | Element Plus icons registration | Sync | `@element-plus/icons-vue` |
| 2 | CSRF security init with 2s timeout race | Async | `./services/httpClient.js` |
| 3 | Contract validation error handler | Sync | `./api/unifiedApiClient.ts` |
| 4 | PWA/Service Worker registration | Async | `public/sw.js` |
| 5 | Session restore via dynamic import | Async | `./utils/sessionRestore.js` |
| 6 | API version negotiation | Async | `./services/versionNegotiator.ts` |
| 7 | Global Vue instance for debugging | Sync | None |

## Capabilities Being Dropped

| Capability | Reason |
|-----------|--------|
| Bloomberg terminal override styles | Legacy layer; ArtDeco is the current design system |

## Runtime Behavior Change

**Before:** `main-standard.ts` mounts a minimal app with styles and router, but no security init, no PWA, no session restore, no version negotiation, no icons registration, and no contract validation error handler.

**After:** `main-standard.ts` runs the full initialization chain:
1. **Synchronous mount** — app renders immediately with icons and components registered
2. **Async init chain (non-blocking, after mount):**
   - PWA/Service Worker registration (post-load event)
   - Security init with 2-second timeout race
   - API version negotiation (after security completes)
   - Session restore via dynamic import

All async operations are non-blocking — the UI renders before they complete. Failures are caught and logged, never crashing the app.

## Files Modified

| File | Change |
|------|--------|
| `web/frontend/src/main-standard.ts` | Rewrite: 47-line stub → ~100-line production entry with all 7 capabilities |
| `web/frontend/src/main.js` | Move to `_entry-archive/main.js` (archived, not deleted) |
| `web/frontend/src/main.js.backup` | Move to `_entry-archive/main.js.backup` (archived) |
| `web/frontend/index.html` | No change — already points to `main-standard.ts` |
| `.planning/REQUIREMENTS.md` | Update ENTRY-01/02/03 traceability to Complete |

## Rollback Plan

1. `main.js` is archived (not deleted) in `_entry-archive/`
2. To rollback: restore `main.js` from `_entry-archive/` and change `index.html` line 67 from `/src/main-standard.ts` to `/src/main.js`
3. The `_entry-archive/README.md` documents this procedure

## Verification

- `npm run dev` starts with hot-reload, no console errors
- `npm run build` succeeds with no broken imports
- `npx vue-tsc --noEmit` passes — no type errors
- Test suite passes (no imports from deleted/archived files)

## Design Rationale

See `.planning/phases/07-entry-consolidation/07-CONTEXT.md` decisions D-01 through D-14 for the full design rationale, including:
- D-01: Remove all debug emoji logs
- D-02: Preserve non-blocking async pattern
- D-14: OpenSpec proposal required before implementation

## Approval

This proposal requires explicit user approval before Plan 07-02 execution begins.
The CONTEXT.md decisions provide design rationale but do not constitute proposal approval.
