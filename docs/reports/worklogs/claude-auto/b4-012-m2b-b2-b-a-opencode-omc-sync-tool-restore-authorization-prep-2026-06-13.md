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

## Validation Notes

Authorization-prep local checks:

- New node: `b4-012-scripts-opencode-omc-sync-restore-authorization`
- Initial new node status: `authorization-prepared`
- Initial new node `source_edits_authorized`: `false`
- New card generated: `.governance/programs/artdeco-web-design-governance/cards/b4-012-scripts-opencode-omc-sync-restore-authorization.yaml`
- Path-limited `git diff --check` for this package: passed
- Scope check for the six governance/report files in this package: no active source-edit authorization, inspected only governance/report files

Implementation approval and restore checks:

- User approval: user replied `同意，请继续` on 2026-06-13 after the restore-authorization boundary was prepared.
- Fresh evidence was appended because the prior node evidence was bound to an older `HEAD`.
- Node transition: `authorization-prepared -> approved-for-implementation`.
- Restore action: `git restore --source=HEAD -- scripts/opencode/sync_omc_model_catalog.py`.
- Restored target state: `git diff --quiet -- scripts/opencode/sync_omc_model_catalog.py` passed, so the restored script is byte-equivalent to `HEAD` and has no remaining source diff.
- Target validation: `python -m py_compile scripts/opencode/sync_omc_model_catalog.py` passed.
- CLI smoke: `python scripts/opencode/sync_omc_model_catalog.py --help` passed and printed the expected argument parser help without writing configuration.
- Import smoke: `importlib.util.spec_from_file_location(...)` loaded the script and confirmed 11 expected functions are present.
- Reference evidence: `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md` still directly references `python3 /opt/claude/mystocks_spec/scripts/opencode/sync_omc_model_catalog.py` and the `--write-user-config` form.
- GitNexus evidence: `query` found related OMC/OpenCode artifacts, but `impact` for `scripts/opencode/sync_omc_model_catalog.py` returned `not_found` / `risk=UNKNOWN`; manual reference/import evidence was used as the fallback.
- Function Tree scoped gate: `ft-governance scope-check --files ...` passed for the 7 authorized paths in this package.
- Scope caveat: paired tracked test `tests/unit/test_sync_omc_model_catalog.py` remains deleted in the worktree and is outside this node's allowed paths; it was not restored or edited in this package.
- Global `ft-governance scope-check` is not usable as a package pass/fail signal in the current root worktree because hundreds of unrelated pre-existing dirty paths are outside this node's allowed paths.
- Function Tree final node status after restore: `closed`; `source_edits_authorized=false`; closeout summary, compatibility note, and gates are recorded on the node.
- Repository-wide `git diff --check` remains blocked by unrelated pre-existing whitespace in `TASK-REPORT.md:524` and `scripts/dev/mock_market/_generate_realistic_stock_price.py:394`; path-limited `git diff --check` for this package passed.

Known repository-wide validation blocker:

- `ft-governance validate` currently fails on pre-existing closed frontend governance nodes that retain historical source `allowed_paths`, beginning with `b4-frontend-shared-ui-component-truth`.
- This blocker predates the OMC authorization-prep node and is not remediated in this package.
- Because of that blocker, this authorization-prep package should not be committed as "full Function Tree validate passed" until either the validator invariant is reconciled with historical closed nodes or a separate governance-repair package resolves the closed-node allowed-path state.
- The OMC restore node was closed by the Function Tree closeout workflow after its local gates passed. Full validation still cannot be reported as passed because the repository-wide validator currently stops at the pre-existing historical closed-node allowed-path blocker.

## Closeout Gate

- Implementation approval has been recorded and the restore implementation has completed within the narrow allowed path.
- Closeout may proceed only if the final scoped diff contains the governance state/report updates and no unexpected source/test/config/OpenSpec edits.
- Full Function Tree validation remains blocked by the pre-existing closed-node allowed-path debt described above; do not report full validation as passed for this package.

## Boundary Confirmation

This is a governance authorization-prep package only. It does not authorize source edits, test edits, deletion retirement, or cleanup outside the listed allowed paths.
