# Frontend View Governance 2.2 Reusable Asset Class Disposition

Date: 2026-05-12
Change: `update-frontend-view-governance`
Task: `2.2 Mark reusable assets by the approved five asset classes.`

## Decision

Close task 2.2 as a read-only ledger disposition. The approved reusable asset classes are the five classes in the OpenSpec delta for `Reusable Asset Review Before Frontend View Archive`:

1. Reusable components
2. Composables
3. KPI/stat logic
4. Table/filter schemas
5. Domain calculation rules

This record does not extract, merge, archive, or move any asset. It only normalizes the existing 2b checklist evidence into the five reusable-asset review classes so later mutation batches cannot treat a non-canonical view as archive-ready before reusable assets are absorbed or explicitly rejected.

## Five-Class Ledger

| Approved class | Current evidence pattern | Disposition |
| --- | --- | --- |
| Reusable components | ArtDeco component, demo component, risk/strategy/trade tab, and view-local component checklists contain active support assets and candidate-review assets. | Active route-owned components remain support assets. Candidate components remain `candidate-review/*` until owner, successor, and absorption value are decided. |
| Composables | `views/composables`, domain-local composables, and demo composables are split between active support and legacy/demo support. | Active composables remain paired with their owning route or view. Legacy/demo composables are not archive-approved until owning shell and successor decisions are complete. |
| KPI/stat logic | Monitoring, dashboard, trade/risk, strategy, and root legacy checklists identify metric cards, summaries, and static-stat shells. | KPI/stat logic is treated as absorb-or-reject evidence. Pages carrying such logic cannot move beyond candidate-review without explicit absorption or rejection rationale. |
| Table/filter schemas | Trade-management, trading-decision, market/data, and config/helper checklists identify table rows, filters, configs, and schemas. | Table/filter assets inherit their owner lifecycle. They are not bulk-archived and must be migrated or rejected with rationale before any owning page archive. |
| Domain calculation rules | Market/data helper modules, system data normalizers, strategy/risk helpers, and technical helper sets carry domain normalization or calculation semantics. | Domain rules remain canonical support when imported by active owners. Legacy rule sets stay candidate-review until compared with canonical successors and explicitly absorbed or rejected. |

## Evidence Inputs

- `docs/reports/quality/myweb-audit/frontend-view-governance-2b-readonly-closeout-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-non-artdeco-path-delta-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-view-composables-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-artdeco-components-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-market-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-data-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-monitoring-2026-05-10.md`

## Boundary

- No file is marked `archive-approved` by this record.
- No reusable asset is extracted to a shared module by this record.
- No guard, spec, package target, route, menu, or style entrypoint is retired by this record.
- Task 2.2 is closed only as five-class reusable-asset ledger coverage; successor mapping, hidden-reference checks, compatibility retention, and redundant-page eligibility remain governed by their own Section 2 tasks.

## Next Valid Step

For any future mutation batch, re-check the selected file against these five classes before marking it `archive-candidate`. If any approved reusable asset class is present, the batch must either absorb the asset into the canonical owner or record an explicit rejection rationale before archive execution is considered.
