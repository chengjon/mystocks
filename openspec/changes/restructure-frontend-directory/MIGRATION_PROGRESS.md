# Frontend Directory Restructure Migration Progress

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


## Metadata
- Change ID: `restructure-frontend-directory`
- Last Updated: `2026-04-27`
- Owner: `main` (Mongo-backed mainline control plane)

## Phase Status

| Phase | Name | Status | Notes |
|---|---|---|---|
| 0 | Freeze & Planning | Completed | Pre-commit gate added, OpenSpec strict validation passed, progress tracker initialized |
| 1 | Governance & Approval | Completed | Phase 1 approvals are recorded in the change package and downstream execution proceeded under the approved scope |
| 2 | Shared Asset Extraction | Completed | Repo-truth review confirmed no direct `src/views/shared/*` extraction batch ever existed in the current tree; the previously conditional `TradingDashboard` helper pair remains in place under task `8.5` Option C, so no executable Phase 2 extraction wave remains open |
| 3a | Market Domain Migration | Completed | Canonical market entrypoints were already landed in repo truth and preserved through wrapper-compatible migration batches |
| 3b | Data Domain Migration | Completed | Data domain canonical entrypoints and verification batches are recorded in Mongo-backed work items |
| 3c | Watchlist Domain Migration | Completed | Watchlist target entrypoints and routing retargets are already landed in repo truth |
| 3d | Strategy Domain Migration | Completed | Strategy target pages and matrix verification are preserved as verified control-plane work items |
| 3e | Trade Domain Migration | Completed | Trade canonical entrypoints, dashboard truth reconciliation, and wrapper retention are preserved as verified work items |
| 3f | Risk Domain Migration | Completed | Risk canonical entrypoints and commit-chain ledger closeout landed as verified micro-batches |
| 3g | System Domain Migration | Completed | System canonical entrypoints and system-domain ledger closeout landed as verified micro-batches |
| 4 | Routing & Layout | Completed | Closed on 2026-04-06 as repo-truth route/layout ledger verification instead of a second router rewrite |
| 5 | Testing | Completed | Closed on 2026-04-06 against the verified safe smoke chain and Playwright E2E/matrix evidence already tracked in Mongo |
| 6 | Code Review | Local review complete; external sign-off pending | Local comprehensive and security review evidence is now recorded in `REVIEW.md` and `SECURITY-REVIEW.md`; formal PR comment and Architecture Board sign-off remain external gates |
| 7 | Merge & Deploy | Pending external | Merge, CI deployment, and staging verification remain outside the current local control-plane closeout |
| 8 | Post-Deployment & Archive | Pending external | OpenSpec archive and post-deploy validation require deployment completion first |
| 9 | Cleanup & Final Verification | Partial | Final lint/route spot-check and migration-progress refresh are complete locally; GitHub issue closure and project-channel reporting remain external follow-up work |

## Phase 0 Artifacts

1. Pre-commit gate script:
   - `scripts/hooks/check-views-migration-table.py`
2. Pre-commit integration:
   - `.pre-commit-config.yaml` hook id: `views-migration-gate`
3. OpenSpec validation:
   - Command: `openspec validate restructure-frontend-directory --strict`
   - Result: `pass`

## Notes

- Mongo work items are the source of truth for execution status; this file is a projection snapshot refreshed to match that control-plane state.
- Phases 4 and 5 were closed through repo-truth ledger reconciliation batches on `2026-04-06`, replacing stale references to a second router rewrite, `npm run test:smoke`, and Cypress full-suite execution.
- Phase 6 now has local review evidence on file, but PR comment/sign-off still remain external workflow gates.
- Phases 7 and 8 remain intentionally open because they depend on external merge, deployment, staging validation, and archive timing that have not happened yet.
- Phase 9 is locally closed through migration-progress refresh except for external GitHub issue closure and project-channel reporting.
