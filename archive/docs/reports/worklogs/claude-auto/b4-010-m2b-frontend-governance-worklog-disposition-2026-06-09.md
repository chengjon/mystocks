# B4.010-M2b frontend governance documentation/worklog disposition

Generated at: 2026-06-09T13:43:00+08:00

## Scope

Mode: documentation/governance disposition

This package resolves the repo-level worklog backlog identified by B4.010-M1. It does not modify runtime source, tests, frontend configs, local `.omc` state, route/view files, app shell files, ST-HOLD, B4.006, BaseLayout, or `marketKlineData`.

Governance node:

- Program: `.governance/programs/artdeco-web-design-governance`
- Node: `b4-frontend-tooling-config-static-governance`
- Current state before this package: `evidence-prepared`

## Commit Decision

Commit the repo-level governance/worklog reports under `docs/reports/worklogs/claude-auto/` because they are in the repository-standard worklog location and contain durable audit evidence for B4/G2 decisions already used by later governance work.

Do not commit frontend-local worker state or parallel worklog paths in this package.

## Committed Worklog Backlog

The following untracked repo-level worklogs are accepted as durable evidence:

| Family | Count | Paths |
|---|---:|---|
| B4 frontend governance preflights | 13 | `b4-001` through `b4-012`, including B4.009 M2d no-source audits |
| G2/OpenSpec dirty-worktree inventories | 16 | `g2-381`, `g2-382`, `g2-383`, `g2-385`, `g2-387`, `g2-388`, `g2-389`, `g2-391`, `g2-393`, `g2-395`, `g2-398`, `g2-402`, `g2-406`, `g2-412`, plus related residual inventories |

Detailed accepted paths:

- `docs/reports/worklogs/claude-auto/b4-001-frontend-route-ui-dirty-atlas-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-002-frontend-deletion-candidate-inventory-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-003-route-header-residue-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-004-data-market-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-005-system-risk-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-006-st5-artdeco-strategy-trading-support-preflight-2026-06-07.md`
- `docs/reports/worklogs/claude-auto/b4-006-strategy-trade-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-007-artdeco-root-legacy-route-truth-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-008-shared-ui-component-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-009-frontend-state-api-support-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-009-m2d-c-asnumber-numeric-string-no-source-audit-2026-06-09.md`
- `docs/reports/worklogs/claude-auto/b4-009-m2d-sa4-strategy-trade-adapter-boundary-no-source-audit-2026-06-09.md`
- `docs/reports/worklogs/claude-auto/b4-010-frontend-tooling-config-static-governance-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-011-frontend-residual-reconciliation-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-012-frontend-deletion-pre-authorization-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-381-deletion-retirement-domain-split-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-382-openspec-deletion-retirement-active-change-inventory-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-383-openspec-strong-archive-deletion-retirement-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-385-openspec-content-drift-deletion-retirement-reconciliation-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-387-openspec-residual-m-untracked-inventory-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-388-openspec-active-change-residual-inventory-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-389-openspec-dirty-worktree-governance-change-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-391-openspec-backend-core-split-change-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-393-openspec-frontend-active-change-package-split-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-395-openspec-html5-migration-experience-active-change-review-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-398-openspec-active-spec-residual-inventory-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-402-openspec-broker-qmt-active-spec-safety-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-406-openspec-independent-active-spec-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/g2-412-sequence-backend-architecture-unblocks-disposition-2026-06-06.md`

## Deferred Rows

The following B4.010-M1 documentation/governance candidates are not committed in M2b:

| Path group | Reason |
|---|---|
| `web/frontend/.omc/**` | Local agent/tool state. Requires a local-state policy decision; default is not to commit. |
| `web/frontend/TASK.md` and `web/frontend/TASK-REPORT.md` | Frontend-local worker artifacts. Keep deferred until a worker-artifact policy is approved. |
| `web/frontend/docs/worklogs/claude-auto/2026-05-10.md` and `2026-05-11.md` | Parallel frontend-local worklog path. Repository policy prefers `docs/reports/worklogs/claude-auto/`; do not commit or move without separate disposition authorization. |
| `web/frontend/ARTDECO_COMPONENTS_CATALOG.md` | Durable catalog candidate, but it touches ArtDeco component truth from a sealed domain. Defer to a catalog-specific documentation batch. |
| `.governance/programs/artdeco-web-design-governance/cards/ai-batch-shape-readiness.yaml` | Valid-looking governance card backlog, but it references a separate `/ai/batch` readiness task and old evidence head. Defer to a card reconciliation batch. |

## Validation

Because M2b is documentation-only, no frontend type-check, unit, or E2E suite was required for behavioral safety. Commit gates are:

- staged files limited to accepted repo-level worklogs, this M2b disposition report, and governance metadata produced by `ft-governance observe`
- `git diff --cached --check`
- GitNexus `verify-staged`
- GitNexus `detect_changes --scope staged`
- OPENDOG verification freshness check

## Next Recommendation

Next B4.010 batch should be either:

1. `B4.010-M2a local-state disposition` for `.omc` state, preferably deciding ignore/preserve policy rather than committing local state; or
2. `B4.010-M2c static-governance-test review` for `web/frontend/tests/unit/config/trading-style-normalization.spec.ts`, requiring explicit test/source authorization.
