# Tasks: refactor-entry-consolidation

## Implementation Tasks

- [x] Rewrite `web/frontend/src/main-standard.ts` with all 7 production capabilities from main.js
- [x] Archive `web/frontend/src/main.js` to `_entry-archive/main.js`
- [x] Archive `web/frontend/src/main.js.backup` to `_entry-archive/main.js.backup`
- [x] Update `.planning/REQUIREMENTS.md` traceability (ENTRY-01/02/03 → Complete)
- [x] Verify: `npm run dev` starts successfully
- [x] Verify: `npm run build` succeeds
- [x] Verify: `npx vue-tsc --noEmit` passes
