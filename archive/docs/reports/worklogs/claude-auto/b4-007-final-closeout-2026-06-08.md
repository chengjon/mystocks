# B4.007 Final Closeout - Frontend Route Truth and Root Legacy Governance

Date: 2026-06-08

Branch: `wip/root-dirty-20260403`

Closeout HEAD: `e92d7fab0fa518d05ccb0f14a9144a992a31cddb`

FUNCTION_TREE node: `.governance/programs/artdeco-web-design-governance/cards/b4-frontend-mainline-route-truth.yaml`

Status: `closed`

## Scope

B4.007 closed the frontend route-truth and root legacy governance line in two phases:

- Mainline route continuity: no-source audit, source-authorized route/menu/runtime repair, and full M3 validation.
- Root legacy backlog: family-based archive execution after explicit F3 authorization, replacing single-file cleanup with batched A+B, C, and D packages.

This closeout does not authorize or include any additional source movement. It records the already landed B4.007 evidence and keeps external dirty worktree items out of scope.

## Mainline Evidence

| Phase | Evidence | Result |
| --- | --- | --- |
| M1 | `docs/reports/worklogs/claude-auto/b4-007-m1-mainline-route-continuity-audit-2026-06-07.md` | Mainline route-menu-component-store/api matrix prepared. |
| M2 | `docs/reports/worklogs/claude-auto/b4-007-m2-mainline-route-breakpoint-repair-2026-06-07.md` | Route/menu/runtime breakpoints repaired under source authorization. |
| M3 | `docs/reports/worklogs/claude-auto/b4-007-m3-mainline-full-gate-validation-2026-06-07.md` | Type-check, stable unit suite, PM2 business smoke, GitNexus, and OPENDOG gates passed. |

The B4.007 mainline node was closed at M3, then kept as the governing record for F3 family backlog closure.

## F3 Family Archive Evidence

| Family | Commit | Files | Result |
| --- | --- | --- | --- |
| A+B | `b296af2e0` | `TdxMarket.vue`, `IndustryConceptAnalysis.vue`, `PortfolioManagement.vue`, `TaskManagement.vue` | Static and entry-guard root legacy files archived with README records and guard anchor updates. |
| C | `ad20a04e2` | `Analysis.vue`, `MarketData.vue`, `monitor.vue`, `TechnicalAnalysis.vue` | High-reference config/E2E files archived with E2E path anchors updated. |
| D | `e92d7fab0` | `RealTimeMonitor.vue`, `StockDetail.vue`, `Stocks.vue` | High-risk root legacy files archived with unit/E2E guard anchors updated. |

All 11 F3 family files are removed from `web/frontend/src/views/` and preserved under `archive/web/frontend/src/views/root-legacy/*/` with standard archive README files.

Earlier F3 static shell work in this line remains represented by:

- `d8782b412 B4.007-F3a: retire root TestPage shell`
- `dd29eb319 B4.007-F3b: retire root stock analysis demo shell`
- `b2a559c17 B4.007-F3c: archive root advanced analysis shell`

## Final Gate Evidence

Latest gate evidence after the final F3-D batch:

- GitNexus: post-commit analyze completed at `e92d7fab0fa518d05ccb0f14a9144a992a31cddb`; index reported fresh and staged diff empty.
- Type-check: `npm run type-check` passed.
- Focused unit: F3-D guard suite passed, 5 files and 36 tests.
- Stable unit: `npm run test:unit:stable` passed, 33 files and 415 tests.
- PM2 business smoke: `PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 npm run test:e2e:business-smoke` passed, chromium 55/55.
- OPENDOG: type-check, unit, and E2E verification evidence recorded with no new failures.
- PM2 runtime: `mystocks-backend` online at `http://localhost:8020`; `mystocks-frontend` online at `http://localhost:3020`.

## Isolation

The B4.007 closeout did not touch:

- ST-HOLD paths.
- `marketKlineData`.
- External dirty worktree files.
- Backend/API contracts.
- Non-B4.007 archive or retirement candidates.

Only B4.007-authorized route truth, test anchor, archive, worklog, and governance files were committed in the B4.007 line.

## Final State

B4.007 is closed.

Frontend mainline route truth is healthy, validated, and auditable. Root legacy handling has shifted from file-by-file cleanup to family-based governance, and the F3 backlog for this line is fully resolved.
