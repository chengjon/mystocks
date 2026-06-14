# MyStocks Spec Unfinished Task Inventory

Date: 2026-06-13
Repository: `/opt/claude/mystocks_spec`
Scope: MyStocks Spec only. OpenStock is explicitly excluded from this inventory.

## Source Checks

- Git branch: `wip/root-dirty-20260403`
- HEAD observed: `c8c4048b4`
- Worktree status: dirty
- Dirty path count: 708
  - Modified: 577
  - Untracked: 121
  - Deleted: 10
- Function Tree program: `artdeco-web-design-governance`
- Function Tree active gates: 4
- OpenSpec active changes: 16
- TODO/FIXME marker scan excluding archive/build/generated-heavy paths: 0 hits

## Critical Constraint

The root worktree is not a safe place to start broad source implementation. Current governance rules require no-source inventory and explicit authorization before edits, deletion, staging, or cleanup. The immediate unfinished work is therefore governance and authorization preparation, not feature coding.

## Active Function Tree Gates

All active gates are in `decision-prepared` state. The next action is to prepare authorization; source edits are not currently authorized by these gates.

| Gate | Status | Title | Next Work |
| --- | --- | --- | --- |
| `b4-012-residual-dirty-domain-atlas` | `decision-prepared` | Residual dirty domain atlas and batch queue | Prepare authorization package. |
| `b4-012-scripts-residual-domain-audit` | `decision-prepared` | Scripts residual dirty domain no-source audit | Prepare authorization package. |
| `b4-012-scripts-deleted-untracked-disposition-audit` | `decision-prepared` | Scripts deleted and untracked disposition audit | Prepare authorization package. |
| `b4-012-scripts-market-data-opencode-disposition-audit` | `decision-prepared` | `market_data` and opencode script disposition no-source review | Prepare authorization package. |

## OpenSpec Not Started

These planned changes have `0/N` tasks complete.

| Change | Progress | First Unchecked Work |
| --- | ---: | --- |
| `implement-dirty-worktree-cleanup-governance` | `0/67` | Review and approve the change; confirm `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md`; refresh baseline counts. |
| `canonicalize-backend-route-unified-response-contracts` | `0/17` | Confirm isolated lane; reproduce `UnifiedResponse Contract Guard` blocker; run GitNexus impact per route file before editing. |
| `add-comprehensive-risk-management-system` | `0/64` | Analyze `SignalRecorder`, `MonitoredNotificationManager`, `MonitoringEventPublisher`, and GPU extension points. |
| `add-smart-quant-monitoring` | `0/137` | Create monitoring watchlist and health-score schema tasks. |

## OpenSpec In Progress

These changes have remaining planned tasks.

| Change | Progress | Next Unchecked Work |
| --- | ---: | --- |
| `enhance-api-contract-management-integration` | `43/44` | Organize contract management training session. |
| `restructure-frontend-directory` | `193/209` | Ready-for-review comment, Architecture Board approval, merge/check closeout tasks. |
| `optimize-data-source-v2` | `235/253` | Gray deploy, monitor cache/API/latency metrics, acceptance confirmation. |
| `implement-optimized-html-vue-artdeco-conversion` | `82/119` | Capture baseline screenshots, validate ArtDeco compliance, verify animation performance. |
| `implement-html5-migration-experience-optimization` | `71/119` | Remove ant-design-vue remnants, standardize on Element Plus + ArtDeco, remove unused dependencies/dead code. |
| `split-backend-core-modules-with-compatibility-wrappers` | `12/24` | Move low-risk helpers, add same-name package re-exports, introduce old-path wrapper modules. |

## Dirty Worktree Hotspots

Largest dirty areas by path count:

| Area | Dirty Paths |
| --- | ---: |
| `web/frontend` | 86 |
| `scripts/dev` | 73 |
| `web/backend` | 73 |
| `tests/unit` | 71 |
| `tests/api` | 51 |
| `reports/governance` | 45 |
| `scripts/tests` | 28 |
| `openspec/changes` | 23 |
| `tests/performance` | 19 |
| `tests/ddd` | 12 |

## Recent B4.012 Evidence Trail

Recent worklogs show B4.012 is already being decomposed into no-source audits, authorization-prep packages, and closeouts:

- `docs/reports/worklogs/claude-auto/b4-012-m2b-b2-a-market-data-package-marker-preservation-closeout-2026-06-13.md`
- `docs/reports/worklogs/claude-auto/b4-012-m2b-b2-a-market-data-package-marker-preservation-authorization-prep-2026-06-13.md`
- `docs/reports/worklogs/claude-auto/b4-012-m2b-b2-market-data-opencode-script-disposition-no-source-review-2026-06-13.md`
- `docs/reports/worklogs/claude-auto/b4-012-m2b-b1-myweb-audit-node-test-tooling-preservation-closeout-2026-06-13.md`
- `docs/reports/worklogs/claude-auto/b4-012-m2b-b-scripts-deleted-untracked-disposition-no-source-review-2026-06-13.md`
- `docs/reports/worklogs/claude-auto/b4-012-m1-residual-dirty-domain-atlas-no-source-audit-2026-06-12.md`

## Recommended Next Order

1. Continue B4.012 no-source governance, not source implementation.
   - Prepare authorization for the four active Function Tree gates.
   - Keep each package narrow: one risk class, one path family, one gate.
2. Start with `implement-dirty-worktree-cleanup-governance` only after approval.
   - It is the OpenSpec change most aligned with the current repository condition.
   - First concrete steps are baseline refresh and cleanup-guide confirmation.
3. Defer `canonicalize-backend-route-unified-response-contracts` until an isolated lane exists.
   - It requires route edits and GitNexus impact per route file.
   - Current dirty state makes this high-risk if done directly in root.
4. Close near-finished OpenSpec items separately.
   - `enhance-api-contract-management-integration` has only one task remaining.
   - `restructure-frontend-directory` and `optimize-data-source-v2` are closeout-heavy, but still require review/approval/validation.
5. Keep large not-started feature work deferred.
   - `add-smart-quant-monitoring` and `add-comprehensive-risk-management-system` should not start while root cleanup and active gates are unresolved.

## Non-Actions

- No OpenStock files were inspected or modified for this report.
- No source, test, deletion, staging, or cleanup action was performed.
- This report does not authorize implementation; it identifies the next governance and planning work.
