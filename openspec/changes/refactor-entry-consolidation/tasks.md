# Tasks: refactor-entry-consolidation

## Implementation Tasks

- [ ] Rewrite `web/frontend/src/main-standard.ts` with all 7 production capabilities from main.js
- [ ] Archive `web/frontend/src/main.js` to `_entry-archive/main.js`
- [ ] Archive `web/frontend/src/main.js.backup` to `_entry-archive/main.js.backup`
- [ ] Update `.planning/REQUIREMENTS.md` traceability (ENTRY-01/02/03 → Complete)
- [ ] Verify: `npm run dev` starts successfully
- [ ] Verify: `npm run build` succeeds
- [ ] Verify: `npx vue-tsc --noEmit` passes
