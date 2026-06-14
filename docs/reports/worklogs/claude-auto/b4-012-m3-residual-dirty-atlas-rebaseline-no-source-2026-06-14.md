# B4.012-M3 residual dirty atlas rebaseline no-source audit

Date: 2026-06-14
Mode: no-source audit, no source/test/runtime/OpenSpec cleanup authorization
Branch: `wip/root-dirty-20260403`
Baseline HEAD: `c71b12597 B4.012-M2b-GOV-P4: close scripts residual parent gate`
Active gate: `b4-012-residual-dirty-domain-atlas`

## Scope

This rebaseline checks whether the top-level B4.012 residual dirty atlas can be closed after the B4.012-M2b scripts governance subline finished.

Allowed in this package:

- read-only Git/FUNCTION_TREE/GitNexus/OPENDOG checks
- status aggregation and risk grouping
- this worklog under `docs/reports/worklogs/claude-auto/`
- FUNCTION_TREE evidence refresh for the existing atlas node

Forbidden in this package:

- source, test, runtime, route, API, frontend, backend, OpenSpec, ST-HOLD, `marketKlineData`, OpenStock, or config edits
- deletion-retirement
- staging or committing any existing dirty source/test/doc/OpenSpec artifact
- broad restore/reset/clean

## Current Dirty Rebaseline

Current worktree status count: `706` dirty lines.

By Git status:

| Status | Count |
|---|---:|
| modified | 576 |
| untracked | 122 |
| deleted | 8 |

By domain:

| Domain | Count | Status mix |
|---|---:|---|
| `tests` | 231 | 218 modified, 13 untracked |
| `scripts` | 171 | 169 modified, 2 untracked |
| `web/frontend` | 86 | 64 modified, 22 untracked |
| `web/backend` | 73 | 63 modified, 4 deleted, 6 untracked |
| `reports` | 47 | 6 modified, 41 untracked |
| `src` | 43 | 41 modified, 2 untracked |
| `openspec` | 23 | 23 untracked |
| `docs` | 14 | 3 modified, 3 deleted, 8 untracked |
| root / config / task / plugin / misc | 18 | mixed modified and untracked |

## Completed Since Original Atlas

The B4.012 scripts governance subline has been resolved at the governance metadata level:

- `b4-012-scripts-governance-quality-authorization`: `closed`
- `b4-012-scripts-deleted-untracked-disposition-audit`: `archived`
- `b4-012-scripts-market-data-opencode-disposition-audit`: `archived`
- `b4-012-active-decision-gate-reconciliation`: `closed`
- `b4-012-market-data-opencode-parent-gate-closeout`: `closed`
- `b4-012-deleted-untracked-parent-gate-closeout`: `closed`
- `b4-012-scripts-residual-parent-gate-closeout`: `closed`

This does not mean every dirty `scripts/**` file has been accepted or cleaned. It only means the B4.012-M2b scripts governance queue and its parent metadata gates are closed or archived. The remaining `scripts/**` dirty paths stay external to this rebaseline unless a new scoped domain package is authorized.

## Closure Decision

The top-level `b4-012-residual-dirty-domain-atlas` must remain active.

Reason:

- the current worktree still contains 706 dirty entries across multiple domains
- several domains have deletion or untracked items that require explicit path-family authorization
- OpenSpec, backend, frontend, tests, and source domains have separate policy and runtime risk
- the original atlas was a queue controller, not a single implementation package

No top-level closeout is prepared in this package.

## Recommended Next Domain Queue

Recommended order from the current rebaseline:

1. `B4.012-M3a tests residual domain no-source audit`
   - Scope: `tests/**` modified/untracked queue.
   - Reason: largest remaining domain and directly tied to verification reliability.
   - Output: family split for adapter tests, AI/test optimizer helpers, integration/support tests, and untracked test artifacts.

2. `B4.012-M3b web/backend residual domain no-source audit`
   - Scope: `web/backend/**` modified/deleted/untracked queue.
   - Reason: includes four deletions plus API/service contract surface.
   - Output: deletion-retirement candidates separated from API/source/doc drift.

3. `B4.012-M3c OpenSpec and protected docs provenance audit`
   - Scope: `openspec/**`, protected `docs/**` deleted/untracked paths, and documented guide drift.
   - Reason: policy-sensitive; requires OpenSpec status validation before archive/delete/preserve decisions.

4. `B4.012-M3d frontend residual domain no-source audit`
   - Scope: `web/frontend/**` modified/untracked queue.
   - Reason: includes previously protected frontend dirty families and generated/component drift; requires route/UI boundary review.

5. `B4.012-M3e source/scripts remaining dirty family audit`
   - Scope: remaining `src/**` and `scripts/**` modified/untracked queues not already covered by closed governance packages.
   - Reason: executable/runtime risk; requires source authorization by subfamily before implementation.

## Boundary Statement

This package intentionally leaves all existing external dirty files untouched, including:

- `tests/**`
- `scripts/**`
- `web/**`
- `src/**`
- `openspec/**`
- `docs/**` outside this report
- `reports/**`
- root task/config/product docs
- untracked local/generated/plugin artifacts

## Gate Status

Required for this no-source report package:

- exact staged allowlist: this report plus generated FUNCTION_TREE evidence files only
- `git diff --cached --check`
- `ft-governance validate`
- GitNexus staged verification
- GitNexus staged detect-changes
- OPENDOG blocker check
- post-commit GitNexus index refresh

## Decision

`b4-012-residual-dirty-domain-atlas` remains the active queue controller.

Next safe action: request/prepare `B4.012-M3a tests residual domain no-source audit` rather than closing the top-level atlas.
