# B4.012-M2b-B1 myweb-audit node-test tooling preservation authorization prep

Date: 2026-06-13
Branch: `wip/root-dirty-20260403`
Mode: `no-source`
Source edits authorized: `false`

## Scope

This package prepares authorization only for the myweb-audit Node test tooling residual found during `B4.012-M2b-B`.

Candidate path:

- `scripts/dev/tools/__node_tests__/validateMywebAuditSkill.test.mjs`

This worklog does not authorize staging, preserving, deleting, or editing the candidate file. It records the candidate, risk boundary, and proposed implementation gate for human approval.

## Current Evidence

- Current HEAD before this authorization prep: `07590ca68 B4.012-M2b-B: audit scripts deleted untracked disposition`
- Staged diff at review start: empty
- Candidate status: untracked directory `scripts/dev/tools/__node_tests__/`
- Candidate file count in the directory: 1
- Candidate file shape:
  - File: `scripts/dev/tools/__node_tests__/validateMywebAuditSkill.test.mjs`
  - Size: 6,758 bytes
  - Lines: 165
  - Runtime: Node built-ins (`node:test`, `node:assert/strict`, `node:child_process`, `node:fs`, `node:os`, `node:path`)
  - Focused test blocks:
    - `validate-myweb-audit-skill emits structured success checks for the current repo`
    - `validate-myweb-audit-skill fails when a fixture breaks the operations linkage contract`
    - `validate-myweb-audit-skill fails when a fixture breaks the workflow or package tool linkage`

## Relationship To Closed Work

`B4.012-M2b-A` preserved the myweb-audit validation scripts:

- `scripts/dev/tools/generate-myweb-audit-secondary-inventory.mjs`
- `scripts/dev/tools/validate-myweb-audit-artifacts.mjs`
- `scripts/dev/tools/validate-myweb-audit-skill.mjs`

The untracked Node test file appears to be a direct focused test companion for `scripts/dev/tools/validate-myweb-audit-skill.mjs`. It should not be handled as generic generated output or deletion-retirement without explicit review.

## Decision

Prepare a preservation authorization package for the single myweb-audit node-test tooling path.

Recommended future implementation, only after explicit approval:

1. Stage and preserve `scripts/dev/tools/__node_tests__/validateMywebAuditSkill.test.mjs`.
2. Run a syntax check with `node --check scripts/dev/tools/__node_tests__/validateMywebAuditSkill.test.mjs`.
3. Run the focused Node test command if local dependencies and runtime assumptions allow it.
4. Keep the implementation commit limited to the candidate file plus FUNCTION_TREE closeout artifacts.

## Explicit Non-Goals

- Do not stage or edit `scripts/dev/tools/__node_tests__/validateMywebAuditSkill.test.mjs` in this authorization-prep commit.
- Do not touch other script residuals:
  - `scripts/market_data/__init__.py`
  - `scripts/opencode/sync_omc_model_catalog.py`
  - `scripts/runtime/record_graphiti_post_commit_closeout.py`
  - `scripts/runtime/trading_cash_reservations.py`
- Do not touch source, tests outside this candidate, runtime behavior, API routes, OpenSpec, ST-HOLD, `marketKlineData`, `docs/guides`, `docs/superpowers`, or external dirty files.
- Do not delete or retire any file.
- Do not use broad staging such as `git add -A`.

## Required Gates For This Authorization Prep

- Exact staged allowlist contains only FUNCTION_TREE artifacts and this worklog.
- No `scripts/**` paths staged.
- `git diff --cached --check` passes.
- GitNexus staged verification reports low risk and no unexpected process impact.
- OPENDOG reports zero blockers.
- Post-commit GitNexus index refresh completes.

## Requested Follow-Up Authorization

`B4.012-M2b-B1 myweb-audit node-test tooling preservation implementation`

Allowed future implementation path, if approved:

- `scripts/dev/tools/__node_tests__/validateMywebAuditSkill.test.mjs`

All other paths remain out of scope unless separately authorized.
