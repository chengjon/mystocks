# Frontend View Governance 2.7 Archive-Candidate Successor Disposition

Date: 2026-05-12
Change: `update-frontend-view-governance`
Task: `2.7 Record successor page or explicit no-successor-needed rationale for every archive-candidate.`

## Decision

Close task 2.7 as a read-only successor/no-successor ledger for the archive-candidate and archive-prep records already present in this change line. This document does not nominate new archive candidates and does not approve additional archive execution.

## Successor Ledger

| Candidate family | Successor / rationale status | Disposition |
| --- | --- | --- |
| Root OpenStock duplicate shell | Successor recorded as `web/frontend/src/views/demo/OpenStockDemo.vue` in the OpenStock decision and execution records. | Successor covered for the root duplicate shell only; child OpenStock demo components remain retain/absorb candidates. |
| Minimal root test sandboxes | `MinimalTest.vue` and `Test.vue` have `no-successor-needed` rationale recorded as local smoke/debug shells without active route, menu, package, or test ownership. | Successor requirement covered for the already executed archive batch. |
| ArtDeco visual smoke sandbox | `ArtDecoTest.vue` has `no-successor-needed` rationale recorded as a local ArtDeco component visual smoke shell after direct guard handling. | Successor requirement covered for the already executed archive batch. |
| K-line root demo shell | Successor coverage is recorded against canonical market/technical K-line surfaces and detail K-line analysis assets. | Covered for the already executed archive batch; canonical K-line assets remain in place. |
| Market data root demo shell | Successor coverage is recorded against canonical market and data-domain routes, plus honest aggregate shells where no one-to-one canonical owner exists. | Covered for the already executed paired archive batch with its local demo composable. |
| Data visualization showcase | Successor coverage is recorded against canonical chart components, market K-line pages, data-domain pages, and ArtDeco chart tabs. | Covered for the already executed archive batch; runtime visualization capability was not absorbed. |
| Smart data source test shell | Successor coverage is recorded against canonical system/data-source health and data management routes/components; page-specific style was local to the demo. | Covered for the already executed archive batch. |
| Deferred A4 candidates | Skeleton usage, stock-analysis demo, root demo parent shells, test page static shell, phase4/wencai wrappers, and top-level static shells remain deferred until successor or `no-successor-needed` rationale is approved in a separate package. | Not archive-candidate for execution in this batch. |
| Candidate-review / absorb-assets pages | Many legacy/domain/demo assets still have only handoff families, candidate successors, or absorption ideas. | Not archive-candidate until successor/no-successor proof is explicit and guards/reusable assets are handled. |

## Evidence Inputs

- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-openstock-demo-decision-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-openstock-root-duplicate-archive-execution-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-root-test-sandbox-minimal-preflight-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-root-test-sandbox-minimal-archive-execution-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-artdeco-test-target-file-archive-execution-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-kline-demo-archive-prep-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-market-data-demo-paired-archive-prep-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-data-visualization-showcase-archive-prep-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-smart-data-source-test-archive-prep-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-skeleton-usage-defer-decision-2026-05-12.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-stock-analysis-demo-defer-decision-2026-05-12.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-root-demo-parent-shells-defer-decision-2026-05-12.md`

## Boundary

- This record is a successor ledger only; it does not execute or approve archive moves.
- Deferred files remain blocked until a future package records a concrete successor or `no-successor-needed` rationale and handles guards.
- Candidate-review pages with only broad handoff families are not treated as successor-complete.
- Sidecars, tests, configs, styles, backups, and support assets are not counted as routed page archive-candidates unless an owning page decision explicitly includes them.
