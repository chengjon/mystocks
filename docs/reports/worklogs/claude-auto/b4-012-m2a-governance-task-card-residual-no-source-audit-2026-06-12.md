# B4.012-M2a Governance Task-Card Residual No-Source Audit

Date: 2026-06-12

Mode: no-source audit, no deletion-retirement authorization, no source/test/runtime edits

## Scope

This audit covers only the `governance/**` residual dirty bucket identified by B4.012-M1.

Current baseline:

- Branch: `wip/root-dirty-20260403`
- HEAD: `fd44d61a2 B4.012-M1: audit residual dirty domain atlas`
- Parent node: `b4-012-residual-dirty-domain-atlas`

Explicitly out of scope:

- source, tests, runtime, route, API, OpenSpec, ST-HOLD, `marketKlineData`
- `web/**`, `src/**`, `scripts/**`, `tests/**`, `openspec/**`
- `docs/guides/**`, `docs/superpowers/**`
- deletion-retirement, archive moves, broad restore/reset/clean
- staging or committing the audited dirty governance files

## Current Governance Residuals

Total governance residual entries: `10`

| Status | Count | Meaning |
| --- | ---: | --- |
| `M` | 1 | tracked catalog update |
| `??` | 9 | untracked governance mainline task-card artifacts |

## Modified Tracked Catalog

| File | Lines | Diff | SHA-256 | Decision class |
| --- | ---: | --- | --- | --- |
| `governance/function-tree/catalog.yaml` | 770 | `+20 / -0` | `d97b0a585be06221a0920c31a11337a8e555635119a3f414ce981c1096cede7a` | tracked governance catalog update; needs separate preservation authorization |

The catalog diff appends path references for system settings and data source configuration surfaces:

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

No catalog change should be accepted or reverted without confirming the corresponding governance lane and whether this is a valid catalog preservation update.

## Untracked Task Cards

| File | Lines | SHA-256 | Task id | Status | Decision class |
| --- | ---: | --- | --- | --- | --- |
| `governance/mainline/task-cards/g2-322.yaml` | 117 | `154a483985d0d30550fabefa730bf898f5e4ee0e6d3d5f3c36ffd90816eb14e8` | `g2-322` | `accepted_merged` | preserve-candidate governance history |
| `governance/mainline/task-cards/g2-323.yaml` | 114 | `efedd5cfa2919aadff430124934be93a82858dcba91a85dce85a42ead11ba4a9` | `g2-323` | `accepted_merged` | preserve-candidate governance history |
| `governance/mainline/task-cards/g2-324.yaml` | 115 | `8cb5e26c24732dfe5f1c891922e78d17ff9e9afc747ec297b127fc10bf0867ea` | `g2-324` | `accepted_merged` | preserve-candidate governance history |
| `governance/mainline/task-cards/g2-325.yaml` | 116 | `61de8cba0fd1a930c58dd1bde4b0f7dd7df64d8c674877b6a4ba5e071a648b4e` | `g2-325` | `accepted_merged` | preserve-candidate governance history |
| `governance/mainline/task-cards/g2-326.yaml` | 124 | `8967326b6bd068d7ed2914da616a4f35467b3dcd5fa88fa9667ddeb0ed59f4a1` | `g2-326` | `accepted_merged` | preserve-candidate governance history |
| `governance/mainline/task-cards/g2-327.yaml` | 111 | `2aa4773289519adbe99be57f023ee3fb825dcf0cca55af05df586fd4eef2ed4e` | `g2-327` | `source_implementation_review_required` | high-risk source-lane evidence; do not preserve/delete without lane decision |
| `governance/mainline/task-cards/g2-328.yaml` | 86 | `6406323d1b63bad38a9a09f9ca2d8793bb8144bfa708673135ce5d68755373d4` | `g2-328` | `accepted_reviewed_no_source` | preserve-candidate governance history |
| `governance/mainline/task-cards/g2-329.yaml` | 85 | `abc99154a18e5270dde286bcef190437c811d4648f50162a848feed07852ec5a` | `g2-329` | `accepted_reviewed_no_source` | preserve-candidate governance history |
| `governance/mainline/task-cards/pr-474.yaml` | 137 | `fed77c8fde2692e0bae957b0f73fbb2d614e5440addfd1cc7ba2af74e2cf050e` | `pr-474` | `accepted_merged` | preserve-candidate governance history |

## Interpretation

- This is not source cleanup.
- This is not deletion-retirement by default.
- The nine task-card files look like governance evidence for G2 service lifecycle / DataSourceFactory lanes.
- Most cards are already marked accepted or reviewed, but `g2-327.yaml` explicitly references source implementation review and should be treated as higher risk.
- The catalog update appears to bind system settings and data-source config paths into the governance function-tree catalog. That may be valuable, but it is a tracked catalog modification and should be authorized separately from untracked task-card preservation.

## Recommended Split

### B4.012-M2a-A Catalog Preservation Review

Allowed scope:

- `governance/function-tree/catalog.yaml`

Recommended action:

- no-source verify the catalog insertion against the related system settings / data source config governance lane
- then request preservation authorization if the update is valid

### B4.012-M2a-B Task-Card Preservation Review

Allowed scope:

- `governance/mainline/task-cards/g2-322.yaml`
- `governance/mainline/task-cards/g2-323.yaml`
- `governance/mainline/task-cards/g2-324.yaml`
- `governance/mainline/task-cards/g2-325.yaml`
- `governance/mainline/task-cards/g2-326.yaml`
- `governance/mainline/task-cards/g2-327.yaml`
- `governance/mainline/task-cards/g2-328.yaml`
- `governance/mainline/task-cards/g2-329.yaml`
- `governance/mainline/task-cards/pr-474.yaml`

Recommended action:

- no-source map each card to its G2/PR lane and related commits
- preserve accepted governance-history cards only after authorization
- treat `g2-327.yaml` as a separate higher-risk card if its source implementation lane has not been closed

## Required Gates For Any Follow-Up

- exact staged allowlist
- `git diff --cached --check`
- GitNexus `verify-staged`
- GitNexus staged change detection
- OPENDOG verification blockers `[]`
- no source/test/runtime/API/route/OpenSpec/ST-HOLD/marketKlineData changes unless explicitly authorized in a separate node

## Decision

B4.012-M2a is decision-prepared as a no-source audit. The next safe action is not implementation; it is an explicit authorization choice between catalog preservation review, task-card preservation review, or deferral.
