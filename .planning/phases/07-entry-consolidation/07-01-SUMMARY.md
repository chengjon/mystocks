---
plan: 07-01
phase: 07-entry-consolidation
status: complete
completed: 2026-04-09
---

# Plan 07-01: Safe Deletions + OpenSpec Proposal — Summary

## What was built

Removed all dead entry-point and router artifacts with zero active consumers. Created the OpenSpec proposal required before the main-standard.ts migration (Plan 07-02).

## Tasks Completed

| Task | Description | Status |
|------|-------------|--------|
| 1 | Delete verify-mount.js | ✓ Complete |
| 2 | Delete 6 router artifact files | ✓ Complete |
| 3 | Remove dead demo test assertions | ✓ Complete |
| 4 | Create OpenSpec proposal for entry point migration | ✓ Complete |

## Key Decisions

- verify-mount.js deleted (standalone script, not in CI, no package.json reference)
- 6 router files deleted: index.js (legacy), index.js.backup, index.ts.backup, index.js.backup-phase2.3, index.js.clean, phase4.routes.js
- Demo route assertions removed from 2 test files (routes don't exist in active router/index.ts)
- OpenSpec proposal created with status `pending` — Plan 07-02 blocked until user approves

## Files Modified

### key-files.deleted
- `web/frontend/verify-mount.js`
- `web/frontend/src/router/index.js`
- `web/frontend/src/router/index.js.backup`
- `web/frontend/src/router/index.ts.backup`
- `web/frontend/src/router/index.js.backup-phase2.3`
- `web/frontend/src/router/index.js.clean`
- `web/frontend/src/router/phase4.routes.js`

### key-files.modified
- `web/frontend/tests/all-pages-accessibility.spec.ts` (removed 5 demo page entries)
- `web/frontend/tests/menu-configuration.spec.js` (removed 功能演示菜单 test block)

### key-files.created
- `openspec/changes/refactor-entry-consolidation/proposal.md`

## Issues Encountered

None. All deletions verified — zero active consumers for all removed files.

## Self-Check: PASSED

- [x] verify-mount.js deleted
- [x] All 6 router artifact files deleted
- [x] Dead demo test assertions removed from both test files
- [x] OpenSpec proposal created with status `pending`
- [x] No broken imports — router dir contains only expected files
