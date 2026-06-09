# System Config Health Summary Fallback Audit

## Scope
- `/system/config`

## Routed Defect Closed
- The monitor-tab fallback from detailed health metrics to summary health status would discard a successful plain `/api/health` payload because the generic wrapper expected `success/data`, which meant a summary-capable route could degrade all the way to `UNAVAILABLE`.

## Repair
- Reused the system-family `healthProbeContract` adapter in `web/frontend/src/views/system/Settings.vue`.
- Added a faithful wrapper-contract regression in `web/frontend/src/views/system/__tests__/Settings.spec.ts` proving that a detailed-health failure plus a live plain health summary now yields `DATA: SUMMARY` and `/api/health` instead of `DATA: UNAVAILABLE`.

## Verification Evidence
- Regression:
  - `npx vitest run src/views/system/__tests__/Settings.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` passed
- Code-path evidence:
  - `normalizeSystemSettingsMonitorRows` already accepted plain health summary payloads
  - the real gap was the wrapper-envelope mismatch before the payload reached that normalizer

## Rule Feedback
- This page-family fallback defect is covered by the new `v1.33` probe-envelope truth rule.
