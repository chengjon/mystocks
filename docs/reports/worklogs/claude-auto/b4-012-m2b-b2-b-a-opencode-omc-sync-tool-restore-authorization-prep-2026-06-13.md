# B4.012-M2b-B2-B-A opencode OMC sync tool restore authorization prep

## Scope

This package prepares authorization only for restoring the tracked deletion:

- `scripts/opencode/sync_omc_model_catalog.py`

It does not restore, edit, stage, delete, or retire the script. It records the implementation boundary for a later user-approved restore package.

## Current Evidence

- Parent no-source decision: `docs/reports/worklogs/claude-auto/b4-012-m2b-b2-b-opencode-omc-sync-tool-disposition-no-source-decision-2026-06-13.md`
- Parent node: `b4-012-scripts-opencode-omc-sync-disposition-audit`
- Recommended next package from parent decision: `B4.012-M2b-B2-B-A opencode OMC sync tool restore authorization prep`
- Current target state: `scripts/opencode/sync_omc_model_catalog.py` exists in `HEAD` and is deleted only in the dirty worktree.

## Decision

Prepare a restore-only authorization boundary for the deleted OMC sync tool. The prior no-source decision found that the sibling `scripts/opencode/sync_opencode_model_catalog.py` is not an equivalent replacement and that accepting the deletion would require a separate deletion-retirement package.

This package therefore authorizes only the future restoration path, not deletion retirement.

## Proposed Allowed Paths

- `scripts/opencode/sync_omc_model_catalog.py`
- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/tree.md`
- `.governance/programs/artdeco-web-design-governance/cards/b4-012-scripts-opencode-omc-sync-restore-authorization.yaml`
- `docs/reports/worklogs/claude-auto/b4-012-m2b-b2-b-a-opencode-omc-sync-tool-restore-authorization-prep-2026-06-13.md`

## Explicit Non-Goals

- Do not restore, edit, stage, delete, or retire `scripts/opencode/sync_omc_model_catalog.py` during authorization prep.
- Do not modify `scripts/opencode/sync_opencode_model_catalog.py`.
- Do not modify `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`.
- Do not touch market-data scripts, runtime scripts, source code, tests, API routes, OpenSpec changes, ST-HOLD, marketKlineData, docs/guides, docs/superpowers, or unrelated dirty paths.
- Do not treat this prep package as approval to implement restore.

## Commit Gate

- Exact staged allowlist only.
- No target script staged during authorization prep.
- `git diff --cached --check` passes.
- Function Tree validation passes.
- GitNexus staged-change review is run before commit.

## Closeout Gate

- Node remains `authorization-prepared` until explicit implementation approval.
- A later restore implementation must prove the restored script is byte-equivalent or intentionally updated from `HEAD`, must pass `python -m py_compile scripts/opencode/sync_omc_model_catalog.py`, and must include focused reference/import evidence before closeout.

## Boundary Confirmation

This is a governance authorization-prep package only. It does not authorize source edits, test edits, deletion retirement, or cleanup outside the listed allowed paths.
