# Frontend Directory Restructure Migration Progress

## Metadata
- Change ID: `restructure-frontend-directory`
- Last Updated: `2026-04-06`
- Owner: `main` (Mongo-backed mainline control plane)

## Phase Status

| Phase | Name | Status | Notes |
|---|---|---|---|
| 0 | Freeze & Planning | Completed | Pre-commit gate added, OpenSpec strict validation passed, progress tracker initialized |
| 1 | Governance & Approval | Completed | Phase 1 approvals are recorded in the change package and downstream execution proceeded under the approved scope |
| 2 | Shared Asset Extraction | Scoped follow-up | Repo-truth review found no direct `src/views/shared/*` extraction batch to perform in the current tree; only conditional helper follow-up remains |
| 3a | Market Domain Migration | Completed | Canonical market entrypoints were already landed in repo truth and preserved through wrapper-compatible migration batches |
| 3b | Data Domain Migration | Completed | Data domain canonical entrypoints and verification batches are recorded in Mongo-backed work items |
| 3c | Watchlist Domain Migration | Completed | Watchlist target entrypoints and routing retargets are already landed in repo truth |
| 3d | Strategy Domain Migration | Completed | Strategy target pages and matrix verification are preserved as verified control-plane work items |
| 3e | Trade Domain Migration | Completed | Trade canonical entrypoints, dashboard truth reconciliation, and wrapper retention are preserved as verified work items |
| 3f | Risk Domain Migration | Completed | Risk canonical entrypoints and commit-chain ledger closeout landed as verified micro-batches |
| 3g | System Domain Migration | Completed | System canonical entrypoints and system-domain ledger closeout landed as verified micro-batches |
| 4 | Routing & Layout | Completed | Closed on 2026-04-06 as repo-truth route/layout ledger verification instead of a second router rewrite |
| 5 | Testing | Completed | Closed on 2026-04-06 against the verified safe smoke chain and Playwright E2E/matrix evidence already tracked in Mongo |
| 6 | Code Review | Pending external | Formal review/sign-off workflow is still an external gate; it has not been fabricated into the ledger |
| 7 | Merge & Deploy | Pending external | Merge, CI deployment, and staging verification remain outside the current local control-plane closeout |
| 8 | Post-Deployment & Archive | Pending external | OpenSpec archive and post-deploy validation require deployment completion first |
| 9 | Cleanup & Final Verification | Pending follow-up | Final lint/route spot-check, migration-progress polish, issue closure, and project-channel reporting remain separate follow-up work |

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
- Phases 6 through 9 remain intentionally open because they depend on external review, merge, deployment, archive, and final communication gates that have not happened yet.
