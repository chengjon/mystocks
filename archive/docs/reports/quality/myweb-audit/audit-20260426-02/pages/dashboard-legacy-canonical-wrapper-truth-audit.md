# Legacy Dashboard Canonical Wrapper Truth Audit

## Scope
- `web/frontend/src/views/Dashboard.vue`

## Defect Closed
- The legacy `Dashboard.vue` page still rendered hardcoded pseudo-live market summary, heat, flow, and table surfaces even though a semantically matching canonical dashboard owner already exists.
- That violated the secondary-phase rule that a legacy surface with a matching canonical owner should delegate truth, not preserve a forked pseudo-live dashboard shell.

## Repair
- Replaced `Dashboard.vue` with a thin orchestration wrapper over the canonical `ArtDecoDashboard.vue` owner.
- Removed the hardcoded faux live summary cards, market heat shell, industry flow shell, and sector table shell from the legacy file.
- Preserved the legacy file only as a compatibility wrapper while delegating all real dashboard truth to the canonical owner.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/__tests__/Dashboard.spec.ts` passed `1/1`
- Secondary tooling:
  - `npm run test:myweb-audit:skill` passed
  - `npm run generate:myweb-audit:secondary-inventory` passed
- Type-check:
  - `timeout 180s npm run type-check` still failed only on existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
- Runtime services:
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online

## Rule Feedback
- If an unrouted legacy surface has a semantically matching canonical owner, keep the legacy file as a thin orchestration wrapper over the canonical owner rather than preserving a forked pseudo-live shell.
- Only degrade to a static shell when there is no matching canonical truth to delegate to.
