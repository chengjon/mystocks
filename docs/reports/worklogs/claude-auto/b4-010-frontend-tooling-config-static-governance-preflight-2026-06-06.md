# B4.010 frontend tooling/config/static-governance preflight

Date: 2026-06-06
Branch: `wip/root-dirty-20260403`
Mode: `no-source`

## Governance boundary

This node inventories frontend tooling, config, static runtime, local governance, local state, and residual test-governance dirty items. It does not edit, restore, stage, or commit frontend source, tests, configs, scripts, static files, generated files, or local state.

Primary references:

- `architecture/STANDARDS.md`
- `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md`
- `docs/reports/worklogs/claude-auto/b4-001-frontend-route-ui-dirty-atlas-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-002-frontend-deletion-candidate-inventory-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-003-route-header-residue-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-004-data-market-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-005-system-risk-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-006-strategy-trade-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-007-artdeco-root-legacy-route-truth-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-008-shared-ui-component-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-009-frontend-state-api-support-preflight-2026-06-06.md`

Fixed isolation list excluded from this package:

- B4.002 deletion-retirement items.
- B4.003 route-header group.
- B4.004 data/market.
- B4.005 system/risk.
- B4.006 strategy/trade, including ST-HOLD high-lock items.
- B4.007 ArtDeco/root legacy route-truth rows.
- B4.008 shared UI/component rows.
- B4.009 frontend state/API support rows.

Stale OPENDOG evidence remains non-blocking for this no-source inventory. Later source-authorized, config-authorized, tooling-authorized, or deletion-retirement work must refresh evidence or explicitly accept the stale caveat.

## Scan method

Read-only checks:

- Parse `git status --short -- web/frontend`.
- Extract archived `web/frontend/**` paths from B4.002-B4.009 reports and exclude them from this pass.
- Classify remaining dirty paths into tooling/config/static-governance buckets:
  - local `.omc` state
  - frontend-local governance docs
  - package manifest
  - Playwright config
  - public runtime static files
  - maintenance scripts
  - static governance tests
  - residual test governance

## Summary

| Bucket | Count | Status mix | Risk | Notes |
| --- | ---: | --- | --- | --- |
| `package-manifest` | 1 | modified | High | Dependency/script metadata can affect install, test, and runtime commands. |
| `playwright-config` | 2 | modified | High | E2E runner behavior and project matrix surface. |
| `public-runtime-static` | 2 | modified | High | PWA manifest and service worker can affect browser runtime behavior. |
| `maintenance-script` | 3 | modified | Medium | Tooling scripts should be handled separately from runtime source. |
| `static-governance-test` | 4 | mixed | Medium | Static/style/runtime acceptance tests; evidence only in no-source mode. |
| `residual-test-governance` | 18 | mixed | Medium | Remaining config/e2e/unit tests not owned by B4.002-B4.009 queues. |
| `frontend-local-governance-doc` | 5 | mixed | Low | Frontend-local task/worklog/catalog docs. |
| `omc-local-state` | 4 | modified | Low | Local agent/tool state; preserve or retire only after explicit policy. |

Total B4.010 candidates: 39.

Risk distribution:

| Risk | Count | Reason |
| --- | ---: | --- |
| High | 5 | Package, Playwright, manifest, and service worker paths affect test/runtime configuration. |
| Medium | 25 | Scripts and tests can encode gates or cleanup behavior but do not change runtime source directly in this pass. |
| Low | 9 | Local governance docs and local `.omc` state need archive/preserve/retire decisions. |

Status distribution:

| Status | Count |
| --- | ---: |
| modified | 27 |
| untracked | 12 |

## Candidate rows

| Path | Status | Bucket | Risk | Notes |
| --- | --- | --- | --- | --- |
| `web/frontend/package.json` | modified | `package-manifest` | High | Package metadata/scripts/dependencies; requires dedicated tooling authorization. |
| `web/frontend/playwright.config.js` | modified | `playwright-config` | High | JS Playwright config; coordinate with TS config before acceptance. |
| `web/frontend/playwright.config.ts` | modified | `playwright-config` | High | TS Playwright config; coordinate with JS config before acceptance. |
| `web/frontend/public/manifest.json` | modified | `public-runtime-static` | High | PWA manifest runtime surface. |
| `web/frontend/public/sw.js` | modified | `public-runtime-static` | High | Service worker runtime/cache surface. |
| `web/frontend/scripts/audit-type-extension-quality.js` | modified | `maintenance-script` | Medium | Tooling audit script. |
| `web/frontend/scripts/fix-incomplete-tags.py` | modified | `maintenance-script` | Medium | Mechanical repair script; do not run/accept without separate authorization. |
| `web/frontend/scripts/fix-multiple-templates.py` | modified | `maintenance-script` | Medium | Mechanical repair script; do not run/accept without separate authorization. |
| `web/frontend/tests/design-token.test.ts` | modified | `static-governance-test` | Medium | Design token governance evidence. |
| `web/frontend/tests/stock-colors.test.ts` | modified | `static-governance-test` | Medium | Stock color governance evidence. |
| `web/frontend/tests/artdeco-style.test.ts` | untracked | `static-governance-test` | Medium | ArtDeco style governance evidence. |
| `web/frontend/tests/html5-runtime-acceptance.test.ts` | untracked | `static-governance-test` | Medium | HTML5 runtime acceptance evidence. |
| `web/frontend/tests/e2e/accessibility-smoke.spec.ts` | modified | `residual-test-governance` | Medium | E2E accessibility evidence; keep separate from Playwright config changes. |
| `web/frontend/tests/e2e/auth-login.spec.ts` | modified | `residual-test-governance` | Medium | E2E auth evidence; do not mix with API/state package. |
| `web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts` | modified | `residual-test-governance` | Medium | Mainline matrix evidence not owned by prior B4 domain queues. |
| `web/frontend/tests/e2e/blank-layout-smoke.spec.ts` | untracked | `residual-test-governance` | Medium | Blank layout smoke evidence; route-truth follow-up only. |
| `web/frontend/tests/unit/config/dashboard-route-canonical-truth.spec.ts` | modified | `residual-test-governance` | Medium | Dashboard route-truth config evidence. |
| `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts` | modified | `residual-test-governance` | Medium | Root demo/static entrypoint evidence. |
| `web/frontend/tests/unit/config/settings-style-normalization.spec.ts` | modified | `residual-test-governance` | Medium | Settings style normalization evidence. |
| `web/frontend/tests/unit/config/skeleton-usage-tokenization.spec.ts` | modified | `residual-test-governance` | Medium | Skeleton/token usage evidence. |
| `web/frontend/tests/unit/config/technical-web3-style-support.spec.ts` | modified | `residual-test-governance` | Medium | Technical/Web3 static style evidence. |
| `web/frontend/tests/unit/port-config-consistency.spec.ts` | modified | `residual-test-governance` | Medium | Port config consistency evidence. |
| `web/frontend/tests/unit/useHeaderSummary.spec.ts` | modified | `residual-test-governance` | Medium | Header summary test evidence; consider pairing back to B4.008 support work. |
| `web/frontend/tests/unit/components/ArtDecoLanguageSwitcher.accessibility.spec.ts` | untracked | `residual-test-governance` | Medium | Component accessibility evidence; route/component package decision needed. |
| `web/frontend/tests/unit/config/artdeco-technical-analysis-static-shell.spec.ts` | untracked | `residual-test-governance` | Medium | Static shell evidence. |
| `web/frontend/tests/unit/config/pwa-manifest-assets.spec.ts` | untracked | `residual-test-governance` | Medium | PWA manifest asset evidence; pair with manifest decision if accepted. |
| `web/frontend/tests/unit/config/risk-orphan-static-shells.spec.ts` | untracked | `residual-test-governance` | Medium | Risk static shell evidence; keep separate from B4.005 route package. |
| `web/frontend/tests/unit/config/shell-route-runtime-guardrails.spec.ts` | untracked | `residual-test-governance` | Medium | Shell route runtime guardrail evidence. |
| `web/frontend/tests/unit/config/stocks-orphan-static-shells.spec.ts` | untracked | `residual-test-governance` | Medium | Stocks static shell evidence. |
| `web/frontend/tests/unit/config/stocks-portfolio-static-shell.spec.ts` | untracked | `residual-test-governance` | Medium | Stocks portfolio static shell evidence. |
| `web/frontend/ARTDECO_COMPONENTS_CATALOG.md` | modified | `frontend-local-governance-doc` | Low | Frontend-local catalog doc. |
| `web/frontend/TASK-REPORT.md` | modified | `frontend-local-governance-doc` | Low | Worktree-local task report. |
| `web/frontend/TASK.md` | modified | `frontend-local-governance-doc` | Low | Worktree-local task file. |
| `web/frontend/docs/worklogs/claude-auto/2026-05-10.md` | untracked | `frontend-local-governance-doc` | Low | Frontend-local historical worklog. |
| `web/frontend/docs/worklogs/claude-auto/2026-05-11.md` | untracked | `frontend-local-governance-doc` | Low | Frontend-local historical worklog. |
| `web/frontend/.omc/project-memory.json` | modified | `omc-local-state` | Low | Local tool memory state. |
| `web/frontend/.omc/state/idle-notif-cooldown.json` | modified | `omc-local-state` | Low | Local tool state. |
| `web/frontend/.omc/state/last-tool-error.json` | modified | `omc-local-state` | Low | Local tool state. |
| `web/frontend/.omc/state/subagent-tracking.json` | modified | `omc-local-state` | Low | Local tool state. |

## Proposed package order

| Package | Rows | Authority needed later | Recommendation |
| --- | ---: | --- | --- |
| TC-1 runtime tooling/config | 5 | tooling/config-authorized | Package manifest, Playwright configs, manifest, and service worker must be verified with build/test evidence before acceptance. |
| TC-2 maintenance scripts | 3 | tooling-authorized | Review scripts separately; do not run mechanical repair scripts from this no-source pass. |
| TC-3 static governance tests | 4 | source-authorized test package | Accept only after naming the static/style/runtime governance contract. |
| TC-4 residual test governance | 18 | source-authorized test package | Split by concern before accepting: e2e smoke/auth, route config guardrails, static shell guardrails, component accessibility. |
| TC-5 frontend-local governance docs | 5 | docs/worklog-authorized | Decide preserve/archive/relocate policy for frontend-local task/worklog/catalog docs. |
| TC-6 local tool state | 4 | local-state cleanup authorization | Decide preserve/ignore/delete policy for `.omc` local state; do not mix with source commits. |

Do not stage these rows directly from B4.010. This report is a classification artifact, not acceptance of config, tooling, tests, static runtime files, docs, or local state.

## B4.011 handoff

After B4.010, the next no-source step should be a residual reconciliation pass:

- Re-run current frontend dirty status.
- Union all archived B4.002-B4.010 frontend paths.
- Verify whether every current `web/frontend/**` dirty row has a B4 bucket.
- Produce a gap table for any path still unclassified.
- Keep deletion-retirement and source-authorized decisions separate.

## Verification performed

Read-only checks only:

- Frontend dirty status parse.
- Fixed B4.002-B4.009 exclusion filtering.
- Tooling/config/static-governance pattern classification.
- Risk and package classification.

Not run:

- Frontend build
- Frontend type check
- Vitest
- Playwright/E2E
- PM2 service checks

Reason: B4.010 is a no-source preflight and does not modify or accept frontend source/test/config/tooling/static/local-state changes.
