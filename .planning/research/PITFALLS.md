# Pitfalls Research: v1.1 Final Polish (Corrected)

**Researched:** 2026-04-08
**Corrected:** 2026-04-08 — aligned with v1.0 Phase 3 VERIFICATION.md

## Critical Pitfall: Getting v1.0 Facts Wrong

The biggest pitfall is re-building conclusions that v1.0 already resolved with evidence:
- **Entry**: canonical is main-standard.ts, NOT main.js
- **Composables**: 15/17 are view-local, bulk migration is harmful
- **Archive**: demo/ is active code, only converted.archive/ is removable (with test deps)

## F821 Pitfalls

### P1: Fixing Dead Code Instead of Deleting
**Prevention:** Check if function is used before adding imports.

### P2: Wrong Import Path
**Sign:** financial/stock_daily vs akshare/stock_daily confusion.
**Prevention:** Verify correct module for each undefined name.

### P3: GPU Conditional Imports
**Prevention:** Don't blindly add imports for GPU code — check conditional patterns.

## Entry Consolidation Pitfalls

### P4: Deleting the Wrong Entry
**CRITICAL:** main.js is NOT the target entry. main-standard.ts is canonical.
Deleting main.js without resolving verify-mount.js will break the dev workflow.

### P5: verify-mount.js Still Active
**Fact:** verify-mount.js is at web/frontend/verify-mount.js (NOT archived).
**Prevention:** Read verify-mount.js, understand its role, then decide update vs remove.

## Composables Pitfalls

### P6: Bulk Migration
**CRITICAL:** Do NOT bulk-move 17 files. 15/17 are correctly view-local.
**Prevention:** Accept view-local pattern or extract only the 2 candidates.

### P7: Name Collisions
**Prevention:** Pre-check against existing src/composables/ names for the 2 extraction candidates.

## Archive Removal Pitfalls

### P8: Deleting Without Test Resolution
**Fact:** 5 test consumers exist for converted.archive/.
**Prevention:** Update or remove those tests BEFORE deleting archive directory.

### P9: Accidentally Removing demo/
**CRITICAL:** demo/ is active code with routes, views, and tests.
**Prevention:** STRU-05 demo portion = "not applicable". Only touch converted.archive/.

---
*Pitfalls research corrected: 2026-04-08*
