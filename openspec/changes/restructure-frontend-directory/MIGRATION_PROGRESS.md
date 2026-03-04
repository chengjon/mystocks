# Frontend Directory Restructure Migration Progress

## Metadata
- Change ID: `restructure-frontend-directory`
- Last Updated: `2026-03-02`
- Owner: Frontend Refactor Stream

## Phase Status

| Phase | Name | Status | Notes |
|---|---|---|---|
| 0 | Freeze & Planning | Completed | Pre-commit gate added, OpenSpec strict validation passed, progress tracker initialized |
| 1 | Governance & Approval | In Progress | Approval package prepared; waiting architecture/front-end lead sign-off |
| 2 | Shared Asset Extraction | Not Started | Pending approval |
| 3a | Market Domain Migration | Not Started | Pending approval |
| 3b | Data Domain Migration | Not Started | Pending approval |
| 3c | Watchlist Domain Migration | Not Started | Pending approval |
| 3d | Strategy Domain Migration | Not Started | Pending approval |
| 3e | Trade Domain Migration | Not Started | Pending approval |
| 3f | Risk Domain Migration | Not Started | Pending approval |
| 3g | System Domain Migration | Not Started | Pending approval |
| 4 | Routing & Layout | Not Started | Pending approval |
| 5 | Testing | Not Started | Pending approval |
| 6 | Code Review | Not Started | Pending approval |
| 7 | Merge & Deploy | Not Started | Pending approval |
| 8 | Post-Deployment & Archive | Not Started | Pending approval |
| 9 | Cleanup & Final Verification | Not Started | Pending approval |

## Phase 0 Artifacts

1. Pre-commit gate script:
   - `scripts/hooks/check-views-migration-table.py`
2. Pre-commit integration:
   - `.pre-commit-config.yaml` hook id: `views-migration-gate`
3. OpenSpec validation:
   - Command: `openspec validate restructure-frontend-directory --strict`
   - Result: `pass`

## Notes

- Phase 1+ implementation remains blocked until explicit governance approvals are recorded in PR comments.
- This file should be updated after each completed task batch and before each phase commit.
