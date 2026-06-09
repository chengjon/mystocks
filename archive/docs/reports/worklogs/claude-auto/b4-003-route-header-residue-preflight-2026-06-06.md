# B4.003 route-header residue preflight

Date: 2026-06-06
Mode: `no-source`
Scope: frontend route-header handoff-sensitive dirty state

## Governance boundary

This node reconciles route-header residue only. It does not edit, restore, stage, or commit frontend source, tests, styles, or assets.

Primary references:

- `docs/reports/worklogs/claude-auto/route-header-migration-line-handoff-2026-06-05.md`
- `docs/reports/worklogs/claude-auto/b4-001-frontend-route-ui-dirty-atlas-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-002-frontend-deletion-candidate-inventory-2026-06-06.md`
- `docs/guides/frontend-structure.md`
- `web/frontend/src/router/index.ts`

Inherited handoff facts:

- Route-header migration line replaces direct `ArtDecoHeader` usage in canonical route pages with `ArtDecoRouteHeader`.
- Completed commits in that line:
  - `af23918df refactor(web): migrate market technical route header`
  - `d920e6bfa refactor(web): migrate data industry route header`
  - `bf6fcc437 refactor(web): migrate data concept route header`
- Handoff recommended next route if continuing: `/data/fund-flow`.
- Handoff explicitly deferred `/market/lhb` because the user said it must wait for later Vue slimming.
- Route-header continuation must remain separate from ordinary frontend route/UI dirty cleanup.

## Current route-header status

| Route | File | Git status | Current header state | Test id state | B4.003 decision |
| --- | --- | --- | --- | --- | --- |
| `/market/technical` | `web/frontend/src/views/market/Technical.vue` | clean | `ArtDecoRouteHeader` present; legacy `ArtDecoHeader` absent | `market-technical-header` / refresh ids present | Completed, no action in B4.003. |
| `/data/industry` | `web/frontend/src/views/data/Industry.vue` | clean | `ArtDecoRouteHeader` present; legacy `ArtDecoHeader` absent | `data-industry-header` / refresh ids present | Completed, no action in B4.003. |
| `/data/concepts` | `web/frontend/src/views/data/Concepts.vue` | clean | `ArtDecoRouteHeader` present; legacy `ArtDecoHeader` absent | `data-concept-header` / refresh ids present | Completed, no action in B4.003. |
| `/data/fund-flow` | `web/frontend/src/views/data/FundFlow.vue` | modified | legacy `ArtDecoHeader` still present; `ArtDecoRouteHeader` absent | `data-fund-flow-header` / refresh ids absent | Only valid next route-header source-authorized candidate. |
| `/market/lhb` | `web/frontend/src/views/market/LHB.vue` | modified | legacy `ArtDecoHeader` still present; `ArtDecoRouteHeader` absent | route-header ids absent | Explicitly deferred; do not include in next route-header package. |

Current reconciliation against handoff:

- `Concepts.vue` and `Industry.vue` no longer show dirty status in the current worktree.
- `market/LHB.vue` remains dirty and remains deferred.
- `data/FundFlow.vue` is still modified and still has no route-header migration hunk.
- No route-header source edit has been accepted in this B4.003 node.

## Route-header evidence residue

The following dirty test/evidence files are route-header-adjacent and should not be mixed into ordinary data/market cleanup without disposition:

| Path | Status | Relation | B4.003 disposition |
| --- | --- | --- | --- |
| `web/frontend/tests/unit/views/data-concept-refresh-fallback.spec.ts` | untracked | Completed `/data/concepts` route-header line evidence residue | Preserve for route-header evidence review or explicitly discard under a test-authorized decision. |
| `web/frontend/tests/unit/views/data-industry-refresh-fallback.spec.ts` | untracked | Completed `/data/industry` route-header line evidence residue | Preserve for route-header evidence review or explicitly discard under a test-authorized decision. |
| `web/frontend/tests/unit/views/data-fund-flow-partial-state.spec.ts` | untracked | Potential `/data/fund-flow` route support test | Keep with the future FundFlow route-header package if it is still relevant after source preflight. |
| `web/frontend/tests/e2e/market-data.spec.ts` | clean | Contains assertions for completed `market-technical`, `data-industry`, and `data-concept` route-header ids | No B4.003 action. FundFlow route-header ids are not present. |
| `web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts` | modified | Broad route matrix with route-header wording, not a focused FundFlow route-header acceptance test | Defer to route/test package preflight; do not use as FundFlow acceptance evidence without review. |

## Non-route-header data/market dirty boundary

Targeted status over `web/frontend/src/views/data`, `web/frontend/src/views/market`, and related tests found `40` dirty entries. B4.003 classifies them as:

| Bucket | Count | Disposition |
| --- | ---: | --- |
| Route-header next candidate | 1 | `web/frontend/src/views/data/FundFlow.vue`; source-authorized route-header package only. |
| Explicitly deferred LHB | 1 | `web/frontend/src/views/market/LHB.vue`; wait for later Vue slimming. |
| Route-header test/evidence residue | 3 | The three unit specs listed above; keep out of ordinary route/UI package until dispositioned. |
| Ordinary data/market B4.004 queue | 26 | Data/market pages, support modules, and tests unrelated to route-header continuation. |
| Other tests outside data/market route-header scope | 7 | Defer to later test/domain preflight; do not pull into route-header continuation. |
| Deleted data/market candidates already isolated by B4.002 | 2 | `useTdx.ts`, `Tdx.scss`; remain deletion-retirement candidates, not B4.003 or B4.004 ordinary source work. |

Ordinary B4.004 queue should exclude:

- `web/frontend/src/views/data/FundFlow.vue` until the route-header decision is made.
- `web/frontend/src/views/market/LHB.vue` until the later Vue slimming task is authorized.
- `web/frontend/src/views/market/composables/useTdx.ts` and `web/frontend/src/views/market/styles/Tdx.scss` because they are B4.002 deletion-retirement candidates.
- The three route-header evidence residue unit specs until they are dispositioned.

## Recommended next package

If the user authorizes route-header continuation after this no-source preflight, the smallest coherent source-authorized package is:

- `web/frontend/src/views/data/FundFlow.vue`
- a focused unit or component test only if needed for the route shell behavior
- `web/frontend/tests/e2e/market-data.spec.ts` only if adding focused `/data/fund-flow` route-header assertions

Required gates for that future package:

- Fresh OPENDOG verification evidence or explicit stale-evidence acceptance.
- GitNexus impact before editing the Vue symbol.
- Route-specific verification plan, including focused route shell assertions and appropriate frontend checks.
- Partial staging discipline from `HEAD`, because the worktree remains broadly dirty.

Do not include:

- `web/frontend/src/views/market/LHB.vue`
- ordinary data/market route UI dirty files
- B4.002 deleted TDX files
- broad route matrix tests unless explicitly reviewed as part of the route-header package

## B4.004 handoff

B4.004 should perform data/market route package preflight / no-source after excluding the route-header items above.

Initial B4.004 focus should be:

- `web/frontend/src/views/data/Advanced.vue`
- `web/frontend/src/views/data/fundFlowPageData.ts`
- data view tests under `web/frontend/src/views/data/__tests__/`
- market pages and support files other than `LHB.vue`, `useTdx.ts`, and `Tdx.scss`
- market tests under `web/frontend/src/views/market/__tests__/` and `__node_tests__/`

## Verification performed

Read-only checks only:

- Parsed current targeted `git status --porcelain=v1 -uall`.
- Compared route-header handoff files against current working tree status.
- Counted current `ArtDecoRouteHeader`, legacy `ArtDecoHeader`, and route shell test ids in targeted files.
- Checked route-header-adjacent unit/E2E test residue.

Not run:

- Frontend build
- Frontend type check
- Vitest
- Playwright/E2E
- PM2 service checks

Reason: B4.003 is a no-source preflight and does not modify or accept route-header source changes.
