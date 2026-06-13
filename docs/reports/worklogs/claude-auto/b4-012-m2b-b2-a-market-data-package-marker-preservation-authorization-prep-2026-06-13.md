# B4.012-M2b-B2-A market_data package marker preservation authorization prep

Date: 2026-06-13
Branch: `wip/root-dirty-20260403`
Mode: `no-source`
Source edits authorized: `false`

## Scope

This package prepares preservation authorization for one low-risk market-data script package marker:

- `scripts/market_data/__init__.py`

This worklog does not authorize staging, preserving, deleting, or editing the candidate file. It records the candidate, justification, and implementation gates for a future explicit source/test-tooling preservation approval.

## Current Evidence

- Current HEAD before this authorization prep: `c61b7c127 B4.012-M2b-B2: audit market-data opencode script disposition`
- Staged diff at review start: empty
- Candidate status: untracked
- Candidate file shape:
  - Path: `scripts/market_data/__init__.py`
  - Size: 37 bytes
  - Lines: 3
  - SHA-256: `6d9d3575c7a93e7d675d942e5538ec5d8d6a8330fa1cf9a81f79bf9788f44709`
  - Content role: package marker/docstring only
- Related tracked file in the same directory:
  - `scripts/market_data/run_miniqmt_controlled_evidence.py`

## Reference Evidence

Non-governance references show this directory is not disposable generated output:

- `tests/unit/adapters/test_miniqmt_market_data.py` imports `scripts.market_data.run_miniqmt_controlled_evidence`.
- `src/adapters/miniqmt_market_data.py` builds a command string pointing at `scripts/market_data/run_miniqmt_controlled_evidence.py`.
- `openspec/changes/add-miniqmt-market-data-controlled-evidence-consumer/` records the `scripts/market_data/` CLI path and is listed by `openspec list` as complete.

The candidate `__init__.py` is therefore a package/import compatibility support file for an existing tracked CLI path, not a standalone generated artifact.

## Decision

Prepare a preservation authorization package for `scripts/market_data/__init__.py` only.

Recommended future implementation, only after explicit approval:

1. Stage and preserve `scripts/market_data/__init__.py`.
2. Run `python -m py_compile scripts/market_data/__init__.py`.
3. Run the focused import check for `scripts.market_data.run_miniqmt_controlled_evidence`.
4. Run the focused unit test import surface if local test dependencies allow it.
5. Commit only the candidate file plus FUNCTION_TREE closeout artifacts.

## Explicit Non-Goals

- Do not stage or edit `scripts/market_data/__init__.py` in this authorization-prep commit.
- Do not touch the tracked deletion:
  - `scripts/opencode/sync_omc_model_catalog.py`
- Do not touch runtime script residuals:
  - `scripts/runtime/record_graphiti_post_commit_closeout.py`
  - `scripts/runtime/trading_cash_reservations.py`
- Do not touch source, tests, API routes, OpenSpec content, ST-HOLD, `marketKlineData`, `docs/guides`, `docs/superpowers`, or external dirty files.
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

`B4.012-M2b-B2-A market_data package marker preservation implementation`

Allowed future implementation path, if approved:

- `scripts/market_data/__init__.py`

All other paths remain out of scope unless separately authorized.
