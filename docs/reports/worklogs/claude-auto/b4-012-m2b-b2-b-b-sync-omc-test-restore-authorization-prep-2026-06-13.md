# B4.012-M2b-B2-B-B sync OMC model catalog test restore authorization prep

## Scope

This package prepares authorization only for the tracked deletion:

- `tests/unit/test_sync_omc_model_catalog.py`

It does not restore, edit, stage, delete, or retire the test file. It records the implementation boundary for a later user-approved restore package.

## Current Evidence

- Parent no-source decision node: `b4-012-scripts-opencode-omc-sync-disposition-audit`
- Prior paired script restore node: `b4-012-scripts-opencode-omc-sync-restore-authorization`
- Prior paired script restore report: `docs/reports/worklogs/claude-auto/b4-012-m2b-b2-b-a-opencode-omc-sync-tool-restore-authorization-prep-2026-06-13.md`
- Current branch: `wip/root-dirty-20260403`
- Current observed `HEAD`: `577ee839d5`
- Current target state: `tests/unit/test_sync_omc_model_catalog.py` exists in `HEAD` and is deleted only in the dirty worktree.
- Paired script state: `scripts/opencode/sync_omc_model_catalog.py` is clean after the prior restore package.

## Test File Facts

`HEAD:tests/unit/test_sync_omc_model_catalog.py`:

- Size: 5,958 bytes
- Lines: 133
- Imports: `json`, `Path`, and `from scripts.opencode import sync_omc_model_catalog as sync`
- Helper functions: 1 (`_write_json`)
- Test functions: 1 (`test_sync_omc_models_generates_project_config_and_refs`)
- AST parse check: passed
- Runtime dry evidence: `python -m pytest <temp HEAD blob of tests/unit/test_sync_omc_model_catalog.py> -q --no-cov` passed with `1 passed in 0.06s`

## Reference And Tool Evidence

- Historical deletion split report explicitly paired `scripts/opencode/sync_omc_model_catalog.py` and `tests/unit/test_sync_omc_model_catalog.py` as likely paired script/test retirement candidates that must be evaluated together.
- The script was already restored in the prior package, preserving the documented `OMC_WORKFLOW_GUIDE.md` CLI entrypoint.
- GitNexus `query` found related `sync_omc_model_catalog.py` script symbols and adjacent OpenCode tests, but did not map the deleted test file itself to an execution flow.
- GitNexus `impact` for `tests/unit/test_sync_omc_model_catalog.py` returned `not_found` / `risk=UNKNOWN`; this package uses manual HEAD blob, reference, and temp-pytest evidence as fallback.
- OPENDOG verification is available but `aging/caution`; cleanup/refactor assessments are allowed with a caution that some historical test/build verification used pipeline commands whose exit codes may be masked.

## Decision

Prepare a restore-only authorization boundary for the deleted test file. Because the paired script has been restored and the `HEAD` test blob still passes when executed from a temporary file, silent deletion is not justified by current evidence.

This package therefore authorizes only a future test restoration path, not deletion retirement.

## Proposed Allowed Paths

- `tests/unit/test_sync_omc_model_catalog.py`
- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/tree.md`
- `.governance/programs/artdeco-web-design-governance/cards/b4-012-sync-omc-test-restore-authorization.yaml`
- `docs/reports/worklogs/claude-auto/b4-012-m2b-b2-b-b-sync-omc-test-restore-authorization-prep-2026-06-13.md`

## Explicit Non-Goals

- Do not restore, edit, stage, delete, or retire `tests/unit/test_sync_omc_model_catalog.py` during authorization prep.
- Do not modify `scripts/opencode/sync_omc_model_catalog.py`.
- Do not modify `tests/unit/test_sync_opencode_model_catalog.py`.
- Do not modify `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`.
- Do not touch source code, unrelated tests, API routes, frontend, OpenSpec changes, ST-HOLD, marketKlineData, docs/guides, docs/superpowers, or unrelated dirty paths.
- Do not treat this prep package as approval to implement restore.

## Commit Gate

- Exact staged allowlist only.
- No target test staged during authorization prep.
- `git diff --check -- <authorized paths>` passes.
- Function Tree scoped `scope-check --files ...` passes for this package.
- GitNexus result and manual fallback evidence are recorded.

## Validation Notes

Authorization-prep local checks:

- New node: `b4-012-sync-omc-test-restore-authorization`
- New node status: `authorization-prepared`
- New node `source_edits_authorized`: `false`
- New card generated: `.governance/programs/artdeco-web-design-governance/cards/b4-012-sync-omc-test-restore-authorization.yaml`
- Allowed paths count: 7
- Path-limited `git diff --check` for this package: passed
- Function Tree scoped `scope-check --files ...`: passed with no active source-edit authorization, inspected 7 changed files
- At authorization-prep time, the target test was deleted in the worktree and was not restored during the prep-only phase.

Implementation local checks:

- User approval: user replied `同意，请继续` on 2026-06-13 after the restore-authorization boundary was prepared.
- Node transition: `authorization-prepared -> approved-for-implementation`.
- Restore action: `git restore --source=HEAD -- tests/unit/test_sync_omc_model_catalog.py`.
- Restored target state: `tests/unit/test_sync_omc_model_catalog.py` is byte-equivalent to `HEAD`, and the target-path dirty deletion is cleared.
- Runtime validation: `python -m pytest tests/unit/test_sync_omc_model_catalog.py -q --no-cov` passed with `1 passed in 0.29s`.
- Function Tree scoped gate during implementation: `ft-governance scope-check --files ...` passed for the 7 authorized paths in this package.
- Node transition after restore: `approved-for-implementation -> implementation-ready -> implementation-landed`.
- Function Tree final node status after closeout: `closed`; `source_edits_authorized=false`; closeout summary, compatibility note, and gates are recorded on the node.
- No sibling script, sibling OpenCode test, docs guide, source, API, frontend, OpenSpec, OpenStock, or unrelated dirty paths were modified by this implementation package.

Known repository-wide validation blocker:

- `ft-governance validate` currently fails on pre-existing closed frontend governance node `artdeco-web-design-governance.nodes[45]`, which retains historical source `allowed_paths`.
- This blocker predates the sync OMC test restore authorization node and is not remediated in this package.
- Because of that blocker, this package should not be reported as "full Function Tree validate passed" until a separate governance-repair package resolves the historical closed-node allowed-path state or the validator invariant is updated.

## Closeout Gate

- User approval was recorded on 2026-06-13 and the node reached `approved-for-implementation` with source/test edits authorized only for the listed target test and governance/report paths.
- Restore action: `git restore --source=HEAD -- tests/unit/test_sync_omc_model_catalog.py`.
- Restored test state: `git diff --quiet HEAD -- tests/unit/test_sync_omc_model_catalog.py` passed; the test is byte-equivalent to `HEAD` and the dirty deletion is cleared.
- Target script state: `scripts/opencode/sync_omc_model_catalog.py` remains tracked, clean, and byte-equivalent to `HEAD`.
- Focused test gate: `python -m pytest tests/unit/test_sync_omc_model_catalog.py -q --no-cov` passed with `1 passed in 0.28s`.
- Isolation gate: `scripts/opencode/sync_opencode_model_catalog.py`, `scripts/opencode/sync_omc_model_catalog.py`, `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`, source code, unrelated tests, OpenSpec, ST-HOLD, marketKlineData, and external dirty paths were not modified.
- GitNexus impact remains `not_found` / `risk=UNKNOWN` for the restored test function, so this package relies on the manual HEAD blob, reference, and focused pytest fallback already recorded above.
- Full Function Tree validation remains blocked by the pre-existing historical closed-node `allowed_paths` invariant. Do not report repository-wide Function Tree validation as passed for this package.

## Boundary Confirmation

This report began as the restore authorization-prep package and now records the approved restore closeout. It authorizes and records only the restoration of `tests/unit/test_sync_omc_model_catalog.py` to the `HEAD` version plus the listed governance/report files. It does not authorize source edits, deletion retirement, or cleanup outside the listed allowed paths.
