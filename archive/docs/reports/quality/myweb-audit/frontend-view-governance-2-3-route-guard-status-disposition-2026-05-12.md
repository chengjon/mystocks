# Frontend View Governance 2.3 Route And Guard Status Disposition

Date: 2026-05-12
Change: `update-frontend-view-governance`
Task: `2.3 Assign route status and guard status for each non-canonical view.`

## Decision

Close task 2.3 as a read-only total-ledger disposition. Existing checklist records already assign route status and guard status at file or file-group level for the reviewed non-canonical view families. This record consolidates those results without changing any route, menu, guard, package script, or test.

## Route Status Ledger

| Route status | Evidence pattern | Disposition |
| --- | --- | --- |
| `canonical-active` / active route owner | Formal business-domain checklists identify active route owners under `market`, `data`, `strategy`, `trade`, `risk`, `system`, `ai`, `announcement`, blank-layout routes, and special detail routes. | Excluded from archive flow. These files are current route truth or route-local support. |
| `special-blank-active` / `special-detail-active` | Blank/error and announcement checklists identify `/login`, catch-all 404, and `/detail/news/:symbol`. | Excluded from redundant-page archive flow even when not present in the main menu. |
| `compat-retained` / `redirect` | Trading, trading-decision, and ArtDeco root wrapper checklists identify thin wrappers or compatibility shells. | Retained until compatibility contract, successor owner, and guard migration are explicitly approved. |
| `dead route` / `no active route` | Domain legacy, root demo/test/sandbox, monitoring, settings, system legacy, and demo/example checklists identify unrouted shells. | Remains `candidate-review` unless all hidden-reference, reusable-asset, successor, and guard-retirement checks pass. |
| Sidecar/non-page | Root sidecar, local test, style, composable, config, and backup checklists identify non-view assets. | Not treated as routed pages; lifecycle follows owner, tooling hygiene, or temp-backup governance. |

## Guard Status Ledger

| Guard status | Evidence pattern | Disposition |
| --- | --- | --- |
| Direct owner spec | Domain and root legacy checklists identify `*.spec.ts` owners for active pages, static shells, wrappers, and demo/test pages. | Owning view cannot be archived until the guard is migrated or retired with rationale. |
| `mainline-guarded` | Trading, trading-decision, advanced-analysis, settings, trade-management, and other checklists record mainline gate coverage. | Blocks archive movement until successor guard or explicit retirement is approved. |
| Style/token/package guard | Root demo/test/sandbox and style checklists identify style-source specs, ArtDeco lint changed-scope target files, tokenization guards, and package-script target-file guards. | Blocks archive movement for the owning page or style asset; no guard retired in this batch. |
| Inventory/docs/guard-map reference | ArtDeco, demo, and root sidecar checklists record inventory, documentation, and guard-map references. | Requires hidden-reference and successor review before archive eligibility. |
| No direct active guard found | Backup/temp artifacts and some legacy candidates may lack direct runtime guard ownership. | Still not deletion-approved by guard absence alone; `architecture/STANDARDS.md` requires code-path and function-tree disposition. |

## Evidence Inputs

- `docs/reports/quality/myweb-audit/frontend-view-governance-2b-readonly-closeout-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-root-demo-sidecars-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-non-artdeco-path-delta-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-top-level-legacy-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-trading-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-trading-decision-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-advanced-analysis-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-blank-errors-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-announcement-2026-05-10.md`

## Boundary

- This is not a new router scan and does not modify `router/index.ts` or menu configuration.
- This does not retire, move, rewrite, or delete any guard.
- This does not turn any `candidate-review`, `compat-retained`, or sidecar asset into `archive-approved`.
- File-level details remain in the referenced checklists; this document is the Section 2.3 total-ledger closeout only.
