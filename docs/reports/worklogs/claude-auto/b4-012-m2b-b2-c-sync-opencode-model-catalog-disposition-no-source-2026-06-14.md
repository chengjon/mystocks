# B4.012-M2b-B2-C sync OpenCode model catalog disposition no-source review

Date: 2026-06-14
Branch: `wip/root-dirty-20260403`
Mode: `no-source`
Node: `b4-012-scripts-sync-opencode-model-catalog-disposition-audit`
Parent: `b4-012-scripts-market-data-opencode-disposition-audit`

## Scope

This review covers the remaining modified OpenCode sibling tool:

- `scripts/opencode/sync_opencode_model_catalog.py`

Read-only comparison paths:

- `scripts/opencode/sync_omc_model_catalog.py`
- `tests/unit/test_sync_opencode_model_catalog.py`
- `tests/unit/test_sync_omc_model_catalog.py`

## Boundary

No source, test, config, OpenSpec, frontend, ST-HOLD, marketKlineData, or external dirty paths are modified by this package.

The review is disposition-only. It does not authorize accepting, restoring, editing, deleting, or retiring the dirty script.

## Current Git Evidence

- Current HEAD when reviewed: `95d990a6d B4.012-M2b-B2-B-B: close sync OMC test restore`
- Staged files at review start: none
- Target status: `M scripts/opencode/sync_opencode_model_catalog.py`
- Target diff size: `25` insertions, `92` deletions
- `scripts/opencode/sync_omc_model_catalog.py`: tracked and clean
- `tests/unit/test_sync_omc_model_catalog.py`: tracked and clean after the prior B2-B-B restore package

## Structural Findings

`sync_opencode_model_catalog.py` and `sync_omc_model_catalog.py` are sibling tools, not replacements for each other.

`sync_opencode_model_catalog.py` current dirty version:

- 271 lines, 10,232 bytes
- Main constants include `PROJECT_OPENCODE_PATH`, `GLOBAL_OPENCODE_PATH`, `OMO_PATH`, `ASXS_BASE_URL_FILE_REF`, and `ASXS_API_KEY_FILE_REF`
- Main functions include `sync_catalog_to_env_file`, `sync_catalog_to_ref_files`, `build_provider_configs`, `apply_common`, and `apply_omo_specific`
- Mentions `OPENCODE` and `OMO`; does not mention `OMC`, `CLAUDE_SETTINGS_PATH`, or `--write-user-config`

`sync_omc_model_catalog.py` clean restored version:

- 335 lines, 11,768 bytes
- Main constants include `PROJECT_OMC_PATH`, `USER_OMC_PATH`, `OMC_ENV_PATH`, and `CLAUDE_SETTINGS_PATH`
- Main functions include `build_omc_agent_models`, `build_tier_models`, `build_claude_env_updates`, `update_claude_settings`, `parse_args`, and `main`
- Owns the documented OMC/Claude settings workflow and `--write-user-config` behavior

Conclusion: the modified OpenCode script must be evaluated on its own OpenCode/OMO/provider contract. It should not be merged into, replaced by, or judged through the OMC restore package.

## Dirty Diff Character

The dirty diff is a behavior/config-generation change, not a formatting cleanup.

Observed changes include:

- Removes `GMN_BASE_URL_FILE_REF` and `GMN_API_KEY_FILE_REF`
- Adds `ASXS_BASE_URL_FILE_REF` and `ASXS_API_KEY_FILE_REF`
- Removes `GMN_MODEL_DEFS` entries and OMO xhigh constants
- Adds `ASXS_MODEL_DEFS`
- Changes provider model building from `gmn/glm` to `glm/asxs`
- Changes provider config package mapping from `gmn` to `asxs`
- Removes `desired_omo_variant` and xhigh variant assignment logic
- Changes OMO provider concurrency from `gmn` paths to `asxs` paths
- Changes accepted model prefixes from `gmn/glm/opencode` to `glm/opencode/asxs`

## Test Evidence

Existing paired test:

- `tests/unit/test_sync_opencode_model_catalog.py`
- 166 lines
- 4 test functions
- Mentions `gmn` 21 times and `glm` 33 times
- Mentions `asxs` 0 times
- Imports `from scripts.opencode import sync_opencode_model_catalog as sync`

The focused paired test was run against the current dirty script with bytecode and pytest cache disabled:

```bash
env PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/unit/test_sync_opencode_model_catalog.py -q --no-cov -p no:cacheprovider
```

Result:

- `4 failed in 0.44s`
- Failure class 1: `apply_common` raises `KeyError: 'enabled_providers'` against the existing minimal catalog fixture
- Failure class 2: `test_main_updates_model_files_from_catalog` expects `GMN_BASE_URL_FILE_REF`, which the dirty script removed

Conclusion: the dirty script is not compatible with the currently tracked paired test contract.

## GitNexus Evidence

GitNexus query found the OpenCode script, paired test, OMC sibling script, and OMO documentation anchors.

Impact checks:

- `sync_catalog_to_env_file` upstream impact: risk `LOW`, direct `1`, affected processes `0`
- `apply_omo_specific` upstream impact: risk `LOW`, direct `1`, affected processes `0`

Interpretation:

GitNexus reports low graph blast radius because this is a script/config-generation surface with limited indexed callers. That does not make the dirty diff safe to accept, because the paired unit test currently fails 4/4 and the provider contract changes from `gmn` to `asxs`.

## Decision

Do not accept the current dirty diff as-is.

Recommended next authorization:

1. Preferred short package: restore `scripts/opencode/sync_opencode_model_catalog.py` to `HEAD`, clearing the dirty provider-change diff and preserving the existing `gmn/glm` paired test contract.
2. If the `asxs` migration is desired, split it into a separate source/test implementation package that explicitly authorizes:
   - `scripts/opencode/sync_opencode_model_catalog.py`
   - `tests/unit/test_sync_opencode_model_catalog.py`
   - any directly bound OpenCode/OMO docs or config fixtures discovered during that package

## Proposed Next Node

Suggested authorization node if the short restore path is approved:

- Node: `b4-012-sync-opencode-model-catalog-restore-authorization`
- Ref: `B4.012-M2b-B2-C-A`
- Allowed source path: `scripts/opencode/sync_opencode_model_catalog.py`
- Allowed governance/report paths: generated task card, active gates, nodes, tree, and a restore authorization worklog
- Non-goals:
  - Do not modify `scripts/opencode/sync_omc_model_catalog.py`
  - Do not modify either paired test in the restore package
  - Do not introduce or validate the `asxs` migration in the restore package
  - Do not touch docs/guides, OpenSpec, frontend, API, ST-HOLD, marketKlineData, or unrelated dirty paths

## Closeout Gate For This No-Source Review

- Path-limited report/governance diff only
- Exact staging only
- `git diff --cached --check` passes
- GitNexus staged verification reports low or no process impact
- OPENDOG verification reports no cleanup/refactor blockers
