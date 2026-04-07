# Pitfalls Research: v1.1 Final Polish

**Researched:** 2026-04-08
**Focus:** What breaks and how to prevent it

## F821 Resolution Pitfalls

### P1: Fixing Dead Code Instead of Deleting
**Sign:** F821 in a function that references deleted modules.
**Prevention:** Check if containing function is used before fixing. Delete dead code instead.
**Phase:** F821 resolution — "dead or alive" check before each fix.

### P2: Wrong Import Path
**Sign:** Multiple modules with similar names (e.g., financial/stock_daily vs akshare/stock_daily).
**Prevention:** Verify correct module by checking what the undefined name is and which module exports it.

### P3: Circular Imports
**Sign:** Adding import creates circular dependency.
**Prevention:** After batch fixes, run `python -c "import src.module"` to verify.

### P4: GPU/Optional Code
**Sign:** 34 F821s in src/gpu/ may have conditional imports.
**Prevention:** Don't blindly add imports for GPU code — check if module is meant to work without GPU.

## Frontend Entry Pitfalls

### P5: verify-mount.js Already Archived
**Sign:** File is in _entry-archive/ already.
**Prevention:** Verify actual status before starting — may just need confirmation.

### P6: Breaking Hot-Reload
**Sign:** Vite HMR fails after entry changes.
**Prevention:** Run `npm run dev` and verify hot-reload after changes.

## Composables Migration Pitfalls

### P7: Name Collisions in Target
**Sign:** src/composables/ already has ~30 files — possible name collisions.
**Prevention:** Pre-migration audit: check each name against existing entries.

### P8: Relative Import Chains
**Sign:** Composables import from relative paths (`../api/`, `../stores/`).
**Prevention:** Read each composable's imports before moving.

### P9: Test Files Left Behind
**Sign:** 2 test files reference old location.
**Prevention:** Move/update tests alongside their composables.

### P10: TypeScript Path Aliases
**Sign:** `@/composables/` resolves differently after move.
**Prevention:** Run `vue-tsc --noEmit` after each batch.

## Archive Removal Pitfalls

### P11: Test Files Referencing Archive
**Sign:** Tests import from converted.archive.
**Prevention:** Grep test files for archive references before deletion.

### P12: Router References
**Sign:** Vue Router lazy-loads archived views.
**Prevention:** Check router config for converted.archive references.

## Prevention Strategy

| Phase | Verification | Tool |
|-------|-------------|------|
| F821 batch | Error count drops, no circular imports | ruff + python import |
| Entry | Dev server + HMR works | npm run dev |
| Composables | TS compiles + build succeeds | vue-tsc --noEmit + npm run build |
| Archive | No dangling refs + tests pass | grep + pytest |
| Every phase | Full build + tests | CI commands |

---
*Pitfalls research complete: 2026-04-08*
