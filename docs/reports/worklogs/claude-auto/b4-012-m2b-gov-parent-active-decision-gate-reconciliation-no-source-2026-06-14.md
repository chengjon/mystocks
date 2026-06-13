# B4.012-M2b-GOV-PARENT active decision gate reconciliation no-source audit

Date: 2026-06-14
Mode: no-source audit
Current HEAD: `c96aff53d B4.012-M2b-B2-C-B-A: close OpenCode model catalog contract fix`

## Scope

This audit reconciles the active B4.012 decision gates left after the OpenCode model catalog restore and contract-standardization packages closed.

No source, test, runtime config, OpenSpec, frontend, API, ST-HOLD, marketKlineData, or external dirty files were modified for this audit.

## Current Git Boundary

Observed with `git status --porcelain=v1`:

- Staged files: none.
- Repository dirty counts: `577` unstaged modified, `8` unstaged deleted, `122` untracked.
- Top dirty directories: `tests` 232, `scripts` 171, `web` 159, `reports` 47, `src` 43, `openspec` 23, `docs` 15.
- `scripts/` scoped dirty state: `168` unstaged modified files and `2` untracked files.
- `scripts/` untracked files:
  - `scripts/runtime/record_graphiti_post_commit_closeout.py`
  - `scripts/runtime/trading_cash_reservations.py`

These are external dirty items for this reconciliation and must not be staged into parent-gate cleanup commits without separate authorization.

## Active Gate Reconciliation

| Active gate | Current status | Descendant status | Reconciliation |
| --- | --- | --- | --- |
| `b4-012-residual-dirty-domain-atlas` | `decision-prepared` | 19 descendants, 13 closed, 6 active | Keep active as the top-level B4.012 atlas until all residual dirty domains close. |
| `b4-012-scripts-residual-domain-audit` | `decision-prepared` | 12 descendants, 7 closed, 5 active | Keep active until the scripts residual family is fully reconciled. Current scripts dirty state is still broad. |
| `b4-012-scripts-deleted-untracked-disposition-audit` | `decision-prepared` | 10 descendants, 6 closed, 4 active | Keep active or refresh later; it covers deleted/untracked scripts beyond the already-closed OpenCode packages. |
| `b4-012-scripts-market-data-opencode-disposition-audit` | `decision-prepared` | 8 descendants, 5 closed, 3 active | Candidate for later parent cleanup after the OMC and OpenCode model catalog disposition gates are reconciled. |
| `b4-012-scripts-opencode-omc-sync-disposition-audit` | `decision-prepared` | 2 descendants, both closed | Candidate for governance-only parent closure. Its restore and paired test child packages are closed. |
| `b4-012-scripts-sync-opencode-model-catalog-disposition-audit` | `decision-prepared` | 3 descendants, 2 closed, 1 active child audit | Candidate for governance-only parent closure after the contract drift audit is closed. |
| `b4-012-sync-opencode-model-catalog-contract-drift-audit` | `decision-prepared` | 1 descendant, closed | Candidate for governance-only parent closure. The dedicated C-B-A standardization authorization node is closed. |

## Interpretation

The OpenCode model catalog work is now complete at implementation level:

- `b4-012-sync-opencode-model-catalog-restore-authorization` is closed.
- `b4-012-sync-opencode-model-catalog-contract-standardization-authorization` is closed.
- Focused contract verification is green: `tests/unit/test_sync_opencode_model_catalog.py` passed 4/4 in the closeout package.

The remaining active gates are not evidence of a failing source package. They are parent/atlas decision gates that still represent queue structure.

## Recommended Next Authorization

Prepare a small governance-only cleanup batch:

`B4.012-M2b-GOV-P1 active parent gate reconciliation metadata closeout`

Allowed intent:

- Close or archive only completed parent decision gates whose child packages are already closed.
- Keep broad atlas and broad scripts residual gates active.
- Do not touch source, tests, runtime configs, OpenSpec, frontend, API, ST-HOLD, marketKlineData, or external dirty paths.

Recommended candidate nodes for the first parent cleanup batch:

- `b4-012-sync-opencode-model-catalog-contract-drift-audit`
- `b4-012-scripts-sync-opencode-model-catalog-disposition-audit`
- `b4-012-scripts-opencode-omc-sync-disposition-audit`

Do not include:

- `b4-012-residual-dirty-domain-atlas`
- `b4-012-scripts-residual-domain-audit`
- `b4-012-scripts-deleted-untracked-disposition-audit`

`b4-012-scripts-market-data-opencode-disposition-audit` should be reviewed after the two OpenCode sibling parent gates above are closed, because it is their shared parent.

## Gates For Any Follow-Up Metadata Cleanup

- Exact staging only; no source/test/runtime/config files.
- `git diff --cached --name-status` must show only governance metadata and closeout worklogs for the selected parent-gate batch.
- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs validate --root /opt/claude/mystocks_spec` must pass.
- `node .gitnexus/run.cjs verify-staged --repo mystocks --cwd /opt/claude/mystocks_spec --json` must pass with low or no risk.
- OPENDOG verification must show no cleanup/refactor blockers.

## Disposition

This no-source audit does not itself close parent gates. It prepares the next governance-only authorization decision and preserves the boundary between completed OpenCode model catalog source work and broader scripts residual cleanup.
