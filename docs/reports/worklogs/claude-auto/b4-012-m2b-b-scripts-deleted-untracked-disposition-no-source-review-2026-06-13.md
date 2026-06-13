# B4.012-M2b-B Scripts Deleted / Untracked Disposition No-Source Review

Date: 2026-06-13

## Scope

This is a no-source disposition review for the remaining `scripts/**` deleted and untracked entries after B4.012-M2b-A.

Included:

- remaining deleted `scripts/**` paths
- remaining untracked `scripts/**` paths
- family-level preservation / retirement recommendation

Explicitly excluded:

- preserving, deleting, restoring, moving, formatting, or editing any script
- source, tests, runtime behavior, API, routes, OpenSpec, ST-HOLD, marketKlineData, `docs/guides/**`, `docs/superpowers/**`, and external dirty files
- runtime execution of candidate scripts

## Baseline

- Branch: `wip/root-dirty-20260403`
- HEAD: `fbd575025 B4.012-M2b-A: close governance quality scripts authorization`
- Staged changes before this review: empty
- `scripts/**` dirty count after M2b-A: `175`
- Remaining deleted / untracked `scripts/**` entries: `5`
- GitNexus indexed/current commit before this review: `fbd575025f1aeaf35c741f41d6de30e200d10319`
- OPENDOG blocker count before this review: `0`

Active B4.012 gates before this review:

- `b4-012-residual-dirty-domain-atlas`
- `b4-012-scripts-residual-domain-audit`

## Deleted / Untracked Matrix

| Path | Status | Family | Shape | Disposition recommendation |
|---|---|---|---|---|
| `scripts/dev/tools/__node_tests__/` | untracked | myweb_audit_tooling | directory, 1 file: `validateMywebAuditSkill.test.mjs` | Preserve candidate, but only with a focused myweb-audit tooling/test-support authorization. |
| `scripts/market_data/__init__.py` | untracked | market_data_catalog | Python file, 37 bytes, 3 lines | Preserve candidate as package marker, but only with market-data script authorization. |
| `scripts/opencode/sync_omc_model_catalog.py` | deleted tracked | market_data_catalog | missing in worktree, tracked in HEAD, 334-line Python script | Do not silently retire. Requires explicit restore-vs-retire decision because it edits model catalog / OpenCode-adjacent configuration. |
| `scripts/runtime/record_graphiti_post_commit_closeout.py` | untracked | runtime_tooling | Python file, 11,093 bytes, 316 lines, shebang | Preserve candidate, but only with runtime tooling authorization. |
| `scripts/runtime/trading_cash_reservations.py` | untracked | runtime_tooling | Python file, 15,395 bytes, 416 lines | Preserve candidate, but only with trading/runtime authorization. |

## Additional Evidence

`scripts/opencode/sync_omc_model_catalog.py` still exists in `HEAD` and is currently deleted from the worktree.

Tracked blob summary:

- lines: `334`
- imports include `argparse`, `json`, `Path`, and `Any`
- functions include model-catalog and environment update helpers such as `resolve_omo_models`, `build_omc_agent_models`, `build_tier_models`, `update_config`, `write_reference_files`, `write_env_file`, `update_claude_settings`, and `main`
- recent tracked history includes:
  - `76f195f69 security: sanitize tracked secrets and prep history rewrite`
  - `10a2ce7a9 chore: snapshot workspace before cleanup`

This file is not safe to delete merely because the worktree currently marks it deleted.

## Risk Assessment

The remaining deleted/untracked script entries are not one implementation package.

Risk split:

- `myweb_audit_tooling`: likely coupled to the already preserved `myweb-audit` validator scripts, but should be reviewed with its test command and package expectations.
- `market_data_catalog`: includes a package marker and a deleted tracked model-catalog sync script; restore/preserve/retire decisions need explicit market-data/catalog authorization.
- `runtime_tooling`: includes scripts that may interact with Graphiti closeout and trading cash reservation logic; these are higher-risk runtime/tooling assets.

No path in this set should be preserved or retired without explicit follow-up authorization.

## Recommended Next Packages

Recommended order:

1. `B4.012-M2b-B1 myweb-audit node-test tooling preservation authorization prep`
   - Candidate: `scripts/dev/tools/__node_tests__/`
   - Authority needed before implementation: script/test-tooling preservation authorization

2. `B4.012-M2b-B2 market-data catalog script disposition authorization prep`
   - Candidates:
     - `scripts/market_data/__init__.py`
     - `scripts/opencode/sync_omc_model_catalog.py`
   - Authority needed before implementation: explicit restore-vs-retire decision for the deleted tracked script, and preservation decision for the package marker

3. `B4.012-M2b-B3 runtime tooling preservation authorization prep`
   - Candidates:
     - `scripts/runtime/record_graphiti_post_commit_closeout.py`
     - `scripts/runtime/trading_cash_reservations.py`
   - Authority needed before implementation: runtime tooling script-source authorization

## Decision

This review prepares disposition evidence only:

- no script preservation
- no script deletion or restore
- no syntax/runtime claims for the five paths
- no source/test/API/OpenSpec changes

## Required Gates For This Audit Package

- exact staged allowlist
- `git diff --cached --check`
- GitNexus staged verification
- GitNexus staged detect-changes
- OPENDOG blocker check
- post-commit GitNexus index refresh

## Current Status

`source_edits_authorized: false`

This no-source review does not authorize any deleted/untracked script implementation package.
