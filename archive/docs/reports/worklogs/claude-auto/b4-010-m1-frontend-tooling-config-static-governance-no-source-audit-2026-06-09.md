# B4.010-M1 frontend tooling/config/static governance no-source audit

Generated at: 2026-06-09T13:02:00+08:00

## Scope

Mode: `no-source`

This audit refreshes the B4.010 frontend tooling/config/static governance boundary after B4.007, B4.008, and B4.009 were closed. It inventories current dirty assets that belong to frontend tooling, local governance, static governance tests, and local agent/tool state. It does not edit, restore, delete, stage, or commit source, tests, configs, static files, generated files, or local state.

Current baseline:

- Branch: `wip/root-dirty-20260403`
- HEAD: `25024d08c B4.009-M3: close frontend state API support governance`
- Prior B4 closed nodes:
  - `b4-frontend-mainline-route-truth`
  - `b4-frontend-shared-ui-component-truth`
  - `b4-frontend-state-api-support-truth`

## Drift From 2026-06-06 Preflight

The older B4.010 preflight listed high-risk rows such as `web/frontend/package.json`, Playwright config, public runtime static files, and maintenance scripts. Those rows are not dirty in the current scoped status and must not be carried forward as active B4.010 implementation targets without fresh evidence.

Current active B4.010 surface is smaller:

| Family | Current count | Risk | Disposition |
|---|---:|---|---|
| `omc-local-state` | 4 | Low | Preserve as local state unless a local-state policy batch is authorized. |
| `frontend-local-governance-doc` | 5 | Low | Candidate for documentation/worklog disposition, not runtime source. |
| `repo-worklog-backlog` | 29 | Low | Candidate for worklog inventory/disposition batch, not runtime source. |
| `governance-card-backlog` | 1 | Low | Candidate for governance card reconciliation. |
| `static-governance-test` | 1 | Medium | Requires test/source authorization before any edit. |
| `advanced-style-residual` | 5 | Medium external | Not B4.010; forward to residual/UI styling governance. |
| `app-shell-external` | 1 | Medium external | Not B4.010; app shell work requires separate authorization. |
| `view-residual-external` | 75 | External | Not B4.010; belongs to residual view/UI cleanup. |
| `residual-test-governance` | 2 | External | Not B4.010; belongs to residual view/data test cleanup. |
| `BaseLayout` archive residue | 1 | External hold | Preserve; already known external dirty item. |

## Current B4.010 Candidate Rows

### `omc-local-state`

| Status | Path | Risk | Notes |
|---|---|---|---|
| `M` | `web/frontend/.omc/project-memory.json` | Low | Local agent/tool memory state. Do not commit without explicit local-state policy. |
| `M` | `web/frontend/.omc/state/idle-notif-cooldown.json` | Low | Local agent/tool state. |
| `M` | `web/frontend/.omc/state/last-tool-error.json` | Low | Local agent/tool state. |
| `M` | `web/frontend/.omc/state/subagent-tracking.json` | Low | Local agent/tool state. |

### `frontend-local-governance-doc`

| Status | Path | Risk | Notes |
|---|---|---|---|
| `M` | `web/frontend/ARTDECO_COMPONENTS_CATALOG.md` | Low | Frontend-local component catalog; documentation disposition only. |
| `M` | `web/frontend/TASK-REPORT.md` | Low | Frontend-local worker report artifact. |
| `M` | `web/frontend/TASK.md` | Low | Frontend-local worker task artifact. |
| `??` | `web/frontend/docs/worklogs/claude-auto/2026-05-10.md` | Low | Frontend-local auto worklog; should be reconciled with repo worklog policy. |
| `??` | `web/frontend/docs/worklogs/claude-auto/2026-05-11.md` | Low | Frontend-local auto worklog; should be reconciled with repo worklog policy. |

### `repo-worklog-backlog`

The current repo-level worklog backlog contains 29 untracked reports under `docs/reports/worklogs/claude-auto/`. This includes B4 preflights, B4.009 SA-4 audit reports, and G2/OpenSpec residual inventories. These are documentation/disposition assets, not runtime source.

Representative rows:

- `docs/reports/worklogs/claude-auto/b4-001-frontend-route-ui-dirty-atlas-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-010-frontend-tooling-config-static-governance-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-011-frontend-residual-reconciliation-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-012-frontend-deletion-pre-authorization-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-412-sequence-backend-architecture-unblocks-disposition-2026-06-06.md`

### `governance-card-backlog`

| Status | Path | Risk | Notes |
|---|---|---|---|
| `??` | `.governance/programs/artdeco-web-design-governance/cards/ai-batch-shape-readiness.yaml` | Low | Governance card backlog; reconcile separately from runtime code. |

### `static-governance-test`

| Status | Path | Risk | Notes |
|---|---|---|---|
| `M` | `web/frontend/tests/unit/config/trading-style-normalization.spec.ts` | Medium | Static/trading style governance test. Do not edit or accept without source/test authorization. |

## Explicit Exclusions

The following dirty groups are visible in the current frontend status but are not B4.010 implementation targets:

- `web/frontend/src/views/**` modified/untracked rows: residual view/UI cleanup, likely B4.011 or later.
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoTradingSignals.active*.scss`: advanced style residual, not tooling/config static governance.
- `web/frontend/src/App.vue`: app shell change, requires independent app-shell authorization.
- `web/frontend/tests/unit/views/**`: residual view/data tests, not B4.010.
- `web/frontend/src/layouts/archive/BaseLayout.vue`: known external archive/layout dirty item, preserve.
- `marketKlineData`: remains excluded from this governance line.
- ST-HOLD and B4.006: remain fully excluded.
- B4.007, B4.008, B4.009: closed domains; do not reopen from B4.010.

## Proposed Package Order

1. `B4.010-M2a local-state disposition`
   - Scope: `.omc` state only.
   - Recommended action: decide whether to preserve locally, ignore, or document as non-committable local state.
   - Risk: Low, but do not commit generated local state by default.

2. `B4.010-M2b frontend governance documentation/worklog disposition`
   - Scope: frontend-local governance docs, repo-level B4/G2 worklog backlog, governance card backlog.
   - Recommended action: batch inventory and either commit selected durable worklogs or classify as backlog artifacts.
   - Risk: Low, documentation-only.

3. `B4.010-M2c static governance test review`
   - Scope: `web/frontend/tests/unit/config/trading-style-normalization.spec.ts`.
   - Recommended action: test/source authorization required before any edit. Validate whether the test reflects current style contract or stale acceptance logic.
   - Risk: Medium because it can change style-normalization acceptance.

4. Forward external residuals to B4.011+
   - Scope: views, app shell, advanced style residuals, view test residuals.
   - Recommended action: no B4.010 changes. Start a separate residual/UI no-source audit before any source/test edit.

## M1 Decision

B4.010 should not start with code changes. The current high-risk tooling/config items from the old preflight are no longer active dirty rows. The only medium-risk current B4.010 test row is `trading-style-normalization.spec.ts`; it should receive a separate M2c source/test authorization if it is still relevant.

Recommended next step:

- Create FUNCTION_TREE node `b4-frontend-tooling-config-static-governance`.
- Record this report as `evidence-prepared`.
- Request explicit authorization for either M2a local-state disposition or M2b documentation/worklog disposition before making any additional changes.

## Verification

No source validation was run because M1 is no-source. The current working tree was inspected with:

- `git status --porcelain=v1 -z -- web/frontend .governance/programs/artdeco-web-design-governance docs/reports/worklogs/claude-auto`
- `git log -1 --oneline`

Staging state at audit time:

- No staged changes before this report was created.
