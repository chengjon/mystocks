# Frontend View Governance 2.6 Archive-Candidate Eligibility Disposition

Date: 2026-05-12
Change: `update-frontend-view-governance`
Task: `2.6 Mark pages eligible for archive-candidate only after hidden-reference checks and strict redundant-page eligibility checks.`

## Decision

Close task 2.6 as a read-only archive-candidate eligibility ledger. The Section 2 rule is:

1. A page may only become `archive-candidate` after route/menu, hidden-reference, guard, reusable-asset, function-tree, compatibility, and successor/no-successor checks are complete.
2. `archive-candidate` is not `archive-approved`.
3. Any actual move still requires a separate approved mutation batch.

The existing 2b evidence records no `archive-approved` page. Most reviewed files remain blocked as `canonical-active`, `canonical-support-asset`, `compat-retained`, `absorb-assets`, `candidate-review`, guard assets, sidecars, or temp-backup candidates.

## Eligibility Ledger

| Eligibility result | Evidence pattern | Disposition |
| --- | --- | --- |
| Not archive scope | Active route owners, special route owners, active support assets, direct router wrappers, and canonical helper modules. | Excluded from archive-candidate flow. |
| Blocked by compatibility retention | Thin wrappers, legacy compatibility shells, wrapper targets, and compatibility support assets. | Cannot become archive-candidate until compatibility consumers and wrapper-retention guards are retired. |
| Blocked by reusable asset review | Pages or components carrying reusable UI, composables, KPI/stat logic, table/filter schemas, or domain calculation rules. | Must be absorbed or explicitly rejected with rationale before archive-candidate status. |
| Blocked by guard or hidden references | Direct specs, mainline gates, package target-file guards, style-source specs, documentation references, guard-map references, or function-tree references. | Must migrate or retire guards/references before archive-candidate status. |
| Conditional archive-prep only | A4 preparation records identify a few demo/test/sandbox or duplicate-shell candidates only after final hidden-reference sweeps and guard decisions. | Remains preparation evidence, not archive execution approval. |
| Sidecar/temp/non-page | Tests, `.claude` sidecars, `TASK.md`, styles, configs, helpers, and backup files. | Not redundant routed pages; govern through owner lifecycle, tooling hygiene, or temp-backup rules. |

## Evidence Inputs

- `docs/reports/quality/myweb-audit/frontend-view-governance-2b-readonly-closeout-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-artdeco-coverage-rollup-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-non-artdeco-path-delta-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-root-demo-sidecars-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-advanced-analysis-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-technical-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-stocks-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-top-level-legacy-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-openstock-demo-decision-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-smart-data-source-test-archive-prep-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-artdeco-test-target-file-archive-prep-2026-05-11.md`

## Boundary

- This record does not add any new `archive-candidate` beyond previously recorded conditional preparation evidence.
- This record does not convert conditional `archive-candidate` or `archive-prep` notes into `archive-approved`.
- This record does not perform hidden-reference sweeps for new paths; it consolidates the already recorded eligibility rule.
- Files already deferred by later A4 decisions remain deferred.
