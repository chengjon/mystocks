# B4.012-M2a-A Catalog Preservation Authorization Prep

Date: 2026-06-12

## Scope

This package prepares authorization only. It does not preserve, stage, or commit the residual catalog edit.

Allowed review target:

- `governance/function-tree/catalog.yaml`

Explicitly out of scope:

- `governance/mainline/task-cards/g2-322.yaml`
- `governance/mainline/task-cards/g2-323.yaml`
- `governance/mainline/task-cards/g2-324.yaml`
- `governance/mainline/task-cards/g2-325.yaml`
- `governance/mainline/task-cards/g2-326.yaml`
- `governance/mainline/task-cards/g2-327.yaml`
- `governance/mainline/task-cards/g2-328.yaml`
- `governance/mainline/task-cards/g2-329.yaml`
- `governance/mainline/task-cards/pr-474.yaml`
- source, test, runtime, API, route, OpenSpec, ST-HOLD, marketKlineData, `docs/guides/**`, `docs/superpowers/**`, and any external dirty files

## Observed State

Baseline:

- Branch: `wip/root-dirty-20260403`
- HEAD: `537d0586f B4.012-M2a: audit governance task-card residuals`
- Staged changes: empty
- `governance/**` residuals: one modified tracked catalog plus nine untracked task cards

Catalog diff:

- `governance/function-tree/catalog.yaml`: `+20/-0`
- Change shape: path registration only
- Runtime/source behavior impact: none in this preparation package

Catalog path references added by the residual edit:

- `web/backend/app/api/v1/system/settings.py`
- `web/backend/app/api/data_source_config.py`
- `web/frontend/src/api/index.ts`
- `web/frontend/src/views/system/Settings.vue`
- `web/frontend/src/views/system/DataSource.vue`
- `web/backend/tests/test_system_settings_contract.py`
- `tests/api/file_tests/test_data_source_config_api.py`
- `web/frontend/src/api/__tests__/monitoringApi.spec.ts`
- `web/frontend/src/views/system/__tests__/Settings.spec.ts`
- `web/frontend/src/views/system/__tests__/DataSource.spec.ts`

The same ten path references appear in both the catalog domain path list and the nested evidence/file list, producing the observed twenty added YAML lines.

## Decision

`governance/function-tree/catalog.yaml` is a preservation candidate, not a deletion or rollback candidate, because the residual edit is a metadata/catalog registration of system settings and data-source related assets already present in the repository.

Implementation is not authorized by this worklog. A separate explicit approval is required before staging or committing `governance/function-tree/catalog.yaml`.

## Requested Follow-Up Authorization

Request `B4.012-M2a-A catalog preservation implementation` authorization with this exact implementation scope:

- Preserve the current `+20/-0` edit in `governance/function-tree/catalog.yaml`
- Update only required FUNCTION_TREE closeout/worklog artifacts for this node

Forbidden for that implementation package unless separately authorized:

- All nine `governance/mainline/task-cards/*.yaml` residuals
- Source/test/runtime/API/routes/OpenSpec/ST-HOLD/marketKlineData changes
- `docs/guides/**`
- `docs/superpowers/**`
- Any broad dirty cleanup or unrelated staged files

## Required Gates

Before any implementation commit:

- Exact staged allowlist
- `git diff --cached --check`
- GitNexus staged verification
- GitNexus staged change detection
- OPENDOG blockers check
- Post-commit GitNexus index refresh

## Current Status

`source_edits_authorized: false`

This report prepares the authorization boundary only.
