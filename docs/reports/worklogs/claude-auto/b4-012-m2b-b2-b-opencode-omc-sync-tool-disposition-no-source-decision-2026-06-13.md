# B4.012-M2b-B2-B opencode OMC sync tool disposition no-source decision

Date: 2026-06-13
Branch: `wip/root-dirty-20260403`
Mode: `no-source`
Source edits authorized: `false`

## Scope

This review covers only the tracked deletion:

- `scripts/opencode/sync_omc_model_catalog.py`

This package does not restore, delete, edit, stage, or retire the target file. It records evidence for the restore-vs-retirement decision and prepares the next authorization boundary.

## Baseline

- Current HEAD at review start: `c8c4048b4 B4.012-M2b-B2-A: close market-data package marker preservation`
- Staged diff at review start: empty
- Target status at review start:
  - `D scripts/opencode/sync_omc_model_catalog.py`
- Already closed related node:
  - `b4-012-scripts-market-data-package-marker-authorization`: `closed`
- Parent decision node:
  - `b4-012-scripts-market-data-opencode-disposition-audit`: `decision-prepared`

## Target Evidence

`scripts/opencode/sync_omc_model_catalog.py` still exists in `HEAD` and is deleted only in the working tree.

HEAD shape:

- Size: 11,768 bytes
- Lines: 335
- SHA-256: `ae876eabaa2464039a83ae0ec38d565e16bf02fdc0ab1db4a88889fa7dee3b88`
- Last tracked history evidence:
  - `76f195f69 2026-03-17 security: sanitize tracked secrets and prep history rewrite`

Key constants from the deleted tool:

- `MODEL_DIR`
- `CATALOG_PATH`
- `PROJECT_OMC_PATH`
- `USER_OMC_PATH`
- `OMC_ENV_PATH`
- `CLAUDE_SETTINGS_PATH`
- `TIER_MODEL_FILES`
- `AGENT_MODEL_FILES`

Key function responsibilities unique to the deleted tool include:

- `resolve_omo_models`
- `build_omc_agent_models`
- `build_tier_models`
- `build_patch`
- `update_config`
- `write_reference_files`
- `write_env_file`
- `strip_provider_prefix`
- `normalize_claude_base_url`
- `extract_default_endpoint`
- `build_claude_env_updates`
- `update_claude_settings`
- `parse_args`

## Reference Evidence

Non-governance references still point at the deleted command:

- `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md` documents:
  - `python3 /opt/claude/mystocks_spec/scripts/opencode/sync_omc_model_catalog.py`
  - `python3 /opt/claude/mystocks_spec/scripts/opencode/sync_omc_model_catalog.py --write-user-config`

Relevant config file state:

- `.config/opencode/model/model-catalog.json`: exists, untracked local config
- `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`: exists, tracked
- `scripts/opencode/sync_opencode_model_catalog.py`: exists, tracked
- `scripts/opencode/sync_omc_model_catalog.py`: missing in worktree, tracked in `HEAD`

## Replacement Assessment

The tracked sibling `scripts/opencode/sync_opencode_model_catalog.py` is not an equivalent replacement for the deleted OMC tool.

Shared function names:

- `load_json`
- `write_json`
- `main`

Responsibilities present only in the deleted OMC tool:

- OMC project/user config paths through `PROJECT_OMC_PATH` and `USER_OMC_PATH`
- OMC environment file writing through `OMC_ENV_PATH`
- Claude settings updates through `CLAUDE_SETTINGS_PATH`
- `--write-user-config` CLI path documented by `OMC_WORKFLOW_GUIDE.md`

Responsibilities present in the sibling OpenCode tool:

- OpenCode project/global config paths
- file-ref generation for OpenCode model files
- OpenCode provider config builders
- OMO-specific OpenCode config application

Decision: the sibling tool reduces overlap but does not prove the deleted OMC tool is redundant.

## Decision

Do not accept the tracked deletion as-is.

Recommended next package:

`B4.012-M2b-B2-B-A opencode OMC sync tool restore authorization prep`

Rationale:

1. The command remains documented in a tracked operator guide.
2. The deleted script owns OMC/Claude-specific sync behavior not covered by the sibling OpenCode sync script.
3. Accepting deletion would require a separate deletion-retirement package, including `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md` changes, and that path is outside the current authorization.
4. Restoring the tracked file is the narrower reversible action, but still requires explicit source/tooling authorization before implementation.

## Alternative Path

If the operator wants to retire the OMC tool instead of restoring it, use a separate deletion-retirement package:

`B4.012-M2b-B2-B-R opencode OMC sync tool deletion-retirement authorization`

That package must explicitly authorize:

- Accepting deletion of `scripts/opencode/sync_omc_model_catalog.py`
- Updating or retiring references in `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`
- Verifying no local OMC workflow depends on `--write-user-config`

This alternative is higher risk than restore because it changes the documented operator workflow.

## Explicit Non-Goals

- Do not restore `scripts/opencode/sync_omc_model_catalog.py` in this no-source decision package.
- Do not accept or stage the deletion.
- Do not modify `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`.
- Do not touch `scripts/opencode/sync_opencode_model_catalog.py`.
- Do not touch runtime script residuals:
  - `scripts/runtime/record_graphiti_post_commit_closeout.py`
  - `scripts/runtime/trading_cash_reservations.py`
- Do not touch source, tests, API routes, OpenSpec content, ST-HOLD, `marketKlineData`, `docs/superpowers`, or external dirty files.
- Do not use broad staging.

## Required Gates For This No-Source Package

- Exact staged allowlist includes only FUNCTION_TREE artifacts and this worklog.
- No `scripts/**` paths staged.
- No `docs/guides/**` paths staged.
- `git diff --cached --check` passes.
- GitNexus staged verification reports low risk and no unexpected process impact.
- OPENDOG reports zero blockers.
- Post-commit GitNexus index refresh completes.

## Recommended Next Action

Prepare `B4.012-M2b-B2-B-A opencode OMC sync tool restore authorization prep` with a narrow allowed implementation path:

- `scripts/opencode/sync_omc_model_catalog.py`

Do not include runtime scripts or documentation changes in that restore package.
