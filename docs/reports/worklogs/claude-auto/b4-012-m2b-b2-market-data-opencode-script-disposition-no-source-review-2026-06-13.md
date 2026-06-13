# B4.012-M2b-B2 market_data/opencode script disposition no-source review

Date: 2026-06-13
Branch: `wip/root-dirty-20260403`
Mode: `no-source`
Source edits authorized: `false`

## Scope

This review covers only the two remaining script residuals from the market-data/opencode family:

- `scripts/market_data/__init__.py`
- `scripts/opencode/sync_omc_model_catalog.py`

This package does not preserve, restore, delete, stage, or edit either target file. It records disposition evidence and splits the next authorization packages.

## Baseline

- Current HEAD at review start: `5570d5873 B4.012-M2b-B1: close myweb-audit node test preservation`
- Staged diff at review start: empty
- FUNCTION_TREE active B4.012 gates at review start:
  - `b4-012-residual-dirty-domain-atlas`: `decision-prepared`
  - `b4-012-scripts-residual-domain-audit`: `decision-prepared`
  - `b4-012-scripts-deleted-untracked-disposition-audit`: `decision-prepared`
- Target statuses:
  - `?? scripts/market_data/__init__.py`
  - ` D scripts/opencode/sync_omc_model_catalog.py`

## Target Evidence

### `scripts/market_data/__init__.py`

- Git state: untracked.
- Worktree state: exists.
- Size: 37 bytes, 3 lines.
- Content shape: package marker/docstring only.
- HEAD state: not tracked in `HEAD`.
- Directory context:
  - `scripts/market_data/` exists.
  - `scripts/market_data/run_miniqmt_controlled_evidence.py` is tracked.
- Non-governance references:
  - `tests/unit/adapters/test_miniqmt_market_data.py` imports `scripts.market_data.run_miniqmt_controlled_evidence`.
  - `src/adapters/miniqmt_market_data.py` builds a command string pointing at `scripts/market_data/run_miniqmt_controlled_evidence.py`.
  - `openspec/changes/add-miniqmt-market-data-controlled-evidence-consumer/` references the `scripts/market_data/` CLI path and is listed by `openspec list` as complete.

Decision: treat this file as a low-risk package/import compatibility support candidate. Do not delete it as a generic untracked file. Prepare a separate preservation implementation authorization if the user approves.

### `scripts/opencode/sync_omc_model_catalog.py`

- Git state: tracked deletion.
- Worktree state: missing.
- HEAD state:
  - 11,768 bytes, 335 lines.
  - Python script with CLI parsing and model/environment synchronization helpers.
  - Key responsibilities from symbol scan include JSON/text writers, model map builders, env/reference-file writers, Claude env update builders, Claude settings update helpers, and `parse_args`.
- History:
  - Last tracked commit for this path: `76f195f69 2026-03-17 security: sanitize tracked secrets and prep history rewrite`.
- Non-governance references:
  - `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md` still documents:
    - `python3 /opt/claude/mystocks_spec/scripts/opencode/sync_omc_model_catalog.py`
    - `python3 /opt/claude/mystocks_spec/scripts/opencode/sync_omc_model_catalog.py --write-user-config`
- Related tracked sibling tooling:
  - `scripts/opencode/sync_opencode_model_catalog.py`
  - `scripts/opencode/migrate_opencode_assets_to_mydoc.sh`
  - `scripts/opencode/update_mydoc_opencode_guides.sh`

Decision: do not accept this deletion in the market-data package. The file is documented as an operator command and has sensitive tooling history. It requires a separate opencode/OMC tool restore-vs-retirement decision package before any implementation.

## Risk Split

| Candidate | Risk | Recommended next package | Rationale |
| --- | --- | --- | --- |
| `scripts/market_data/__init__.py` | Low | `B4.012-M2b-B2-A market_data package marker preservation implementation` | Package marker for a tracked script path that is imported by unit tests. |
| `scripts/opencode/sync_omc_model_catalog.py` | Medium/high | `B4.012-M2b-B2-B opencode OMC sync tool restore-vs-retirement no-source decision` | Tracked deletion, operator-guide references, model/env config behavior, security-history sensitivity. |

## Explicit Non-Goals

- Do not stage, preserve, restore, edit, or delete either target file in this review.
- Do not touch runtime scripts outside this pair:
  - `scripts/runtime/record_graphiti_post_commit_closeout.py`
  - `scripts/runtime/trading_cash_reservations.py`
- Do not touch source, tests, API routes, OpenSpec content, ST-HOLD, `marketKlineData`, `docs/guides`, `docs/superpowers`, or external dirty files.
- Do not run broad cleanup or broad staging.

## Required Gates For This No-Source Package

- Exact staged allowlist includes only FUNCTION_TREE artifacts and this worklog.
- No `scripts/**` paths staged.
- `git diff --cached --check` passes.
- GitNexus staged verification reports low risk and no unexpected process impact.
- OPENDOG reports zero blockers.
- Post-commit GitNexus index refresh completes.

## Recommended Next Action

Proceed with `B4.012-M2b-B2-A market_data package marker preservation authorization prep`:

- Candidate path: `scripts/market_data/__init__.py`
- Authority: source/test-tooling preservation implementation only after explicit approval.

Keep `scripts/opencode/sync_omc_model_catalog.py` out of B2-A and move it to a separate opencode/OMC decision package.
