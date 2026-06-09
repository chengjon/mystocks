# Legacy Monitoring Dashboard Static Shell Truth Audit

## Scope
- `web/frontend/src/views/monitoring/MonitoringDashboard.vue`

## Defect Closed
- The legacy `MonitoringDashboard.vue` page still rendered hardcoded pseudo-live monitoring summary, alerts, and dragon-tiger records without any router-backed or canonical truth contract.
- That violated the secondary-phase rule that a legacy surface with no verified truth source must either delegate to a matching canonical owner or degrade honestly.

## Repair
- Replaced `MonitoringDashboard.vue` with an honest static legacy shell that states no reusable canonical monitoring truth currently exists for this page.
- Removed the hardcoded faux live summary cards, pseudo alert sections, pseudo realtime list, and pseudo dragon-tiger records.
- The shell now directs users to relevant canonical routes without inventing request IDs, freshness copy, sync banners, or live metrics.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/monitoring/__tests__/MonitoringDashboard.spec.ts` passed `1/1`
- Secondary tooling:
  - `npm run test:myweb-audit:skill` passed
  - `npm run generate:myweb-audit:secondary-inventory` passed
- Type-check:
  - `timeout 180s npm run type-check` still failed only on existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
- Runtime services:
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online

## Rule Feedback
- If an unrouted legacy surface only carries hardcoded pseudo-live data and has no canonical truth contract, do not preserve its fake summary, alert, or table content just to keep the old dashboard shape alive.
- The correct repair is an honest static legacy shell with explicit capability boundaries and no fabricated live semantics.
