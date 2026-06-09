# Legacy Analysis Static Shell Truth Audit

## Scope
- `web/frontend/src/views/Analysis.vue`

## Defect Closed
- The legacy `Analysis.vue` page still rendered pseudo-live analysis configuration, signal summary, recent signals, and export surfaces without any router-backed or canonical truth contract.
- That violated the secondary-phase rule that a legacy surface with no verified truth source must either delegate to a matching canonical owner or degrade honestly.

## Repair
- Replaced `Analysis.vue` with an honest static legacy shell that states no reusable canonical truth currently exists for this page.
- Removed the faux live analysis configuration panel, signal summary, recent signals, and export controls.
- The shell now directs users to relevant canonical analysis routes without inventing request IDs, freshness copy, or signal semantics.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/__tests__/Analysis.spec.ts` passed `1/1`
- Style/config regression:
  - `npx vitest run tests/unit/config/root-demo-style-entrypoints.spec.ts` passed as part of the scoped regression batch
- Secondary tooling:
  - `npm run test:myweb-audit:skill` passed
  - `npm run generate:myweb-audit:secondary-inventory` passed
- Type-check:
  - `timeout 180s npm run type-check` still failed only on existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
- Runtime services:
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online

## Rule Feedback
- If an unrouted legacy analysis surface only carries local mock workbench state and has no semantically matching canonical owner, do not preserve its fake configuration, signal, or export surfaces just to keep the workbench shape alive.
- The correct repair is an honest static shell with explicit capability boundaries and no fabricated live semantics.
