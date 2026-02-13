# Tech Debt Governance Rollup (2026Q1)

## Week Window
- Start: ____-__-__
- End: ____-__-__
- Owner: ____

## Summary
- Completed: 0 / 10
- In Progress: 3
- Blocked: 0
- Overdue: 0

## Task Snapshot
| ID | Status | Progress This Week | Risks/Blockers | Next Action |
| --- | --- | --- | --- | --- |
| T01 | doing | Drafted SoT doc | Review pending | Assign owner + review |
| T02 | doing | Seeded conflict matrix | Owners missing | Assign owners |
| T03 | doing | Seeded debt register | Owners/DDL missing | Assign owners + DDL |
| T04 | doing | Added deprecation timeline | Implementation pending | Route registry reads via shared loader |
| T05 | doing | Dispatched to CLI-api (gov-t05) | Awaiting baseline selection | Confirm OpenAPI source |
| T06 | todo | Testing dispatched to CLI-6 (gov-t06-test) | Awaiting routing rules | Document routing rules |
| T07 | todo | Not started | N/A | Define SLO baselines |
| T08 | todo | Not started | N/A | Inventory tool entry points |
| T09 | todo | Not started | N/A | Draft PR gate policy |
| T10 | todo | Not started | N/A | Define report automation |

## Metrics
- Debt items with owners: __%
- Conflicts triaged: __
- Overdue items: __

## Decisions Needed
1. Assign owners for T01-T04.
2. Confirm DDLs for P0 tasks.

---

## Worktree Delivery Report: `update-artdeco-design-governance` (2026-02-13)

### Scope
- Completed governance plan Batch 1 (Task 1-3) and Batch 2 (Task 4-5).
- Integrated selected items from `docs/reports/ARTDECO_UI_UX_OPTIMIZATION_RECOMMENDATIONS.md`.

### Implemented
- Governance baseline and tests:
  - `web/frontend/src/styles/artdeco-governance-manifest.json`
  - `web/frontend/tests/unit/styles/artdeco-governance-manifest.spec.ts`
- Doc consistency and governance docs:
  - `docs/guides/ARTDECO_MASTER_INDEX.md`
  - `docs/guides/ARTDECO_COMPONENT_GUIDE.md`
  - `web/frontend/tests/unit/styles/artdeco-docs-consistency.spec.ts`
- Token checker hardening:
  - `web/frontend/scripts/check-artdeco-tokens.js`
  - `web/frontend/tests/unit/scripts/check-artdeco-tokens.spec.ts`
  - `web/frontend/package.json` (`lint:artdeco:strict`)
- Report recommendation integration:
  - Removed conflicting color source import in `web/frontend/src/styles/artdeco-main.css`
  - Added trust-blue and compatibility aliases in `web/frontend/src/styles/artdeco-variables.css`
  - Added reduced-motion fallback in `web/frontend/src/styles/artdeco-animations.css`
  - Added tests:
    - `web/frontend/tests/unit/styles/artdeco-governance-cli.spec.ts`
    - `web/frontend/tests/unit/styles/artdeco-report-recommendations.spec.ts`

### Validation
- Passed:
  - `openspec validate update-artdeco-design-governance --strict`
  - `cd web/frontend && npm run test -- tests/unit/styles/artdeco-governance-manifest.spec.ts`
  - `cd web/frontend && npm run test -- tests/unit/styles/artdeco-docs-consistency.spec.ts`
  - `cd web/frontend && npm run test -- tests/unit/scripts/check-artdeco-tokens.spec.ts`
  - `cd web/frontend && npm run test -- tests/unit/styles/artdeco-governance-cli.spec.ts`
  - `cd web/frontend && npm run test -- tests/unit/styles/artdeco-report-recommendations.spec.ts`
  - Combined unit scope run: 5 files / 10 tests passed
- Expected non-zero (governance enforcement confirmed):
  - `cd web/frontend && npm run lint:artdeco:strict` (reports legacy hardcoded literals)

### Known Blockers (pre-existing)
- Design regression scripts currently not runnable as-is:
  - `npm run test:design-token`
  - `npm run test:bloomberg`
  - Root causes: Playwright config mismatch + dev server startup failures in existing project state.
- Type check currently fails on existing syntax errors:
  - `src/views/TradingDecisionCenter.vue:500+`
