# B4.012-M2b-A Governance Quality Scripts Authorization Prep

Date: 2026-06-13

## Scope

This package prepares authorization only for the governance cleanup quality script subfamily identified by the B4.012-M2b scripts residual no-source audit.

Candidate future implementation scope:

- `scripts/dev/quality_gate/**` dirty entries
- related `scripts/dev/tools/*myweb-audit*.mjs` dirty entries

This package does not modify, preserve, delete, restore, rename, format, execute, or validate any script file.

Explicitly excluded:

- all `scripts/**` paths outside the candidate list below
- source, tests, runtime behavior, API, routes, OpenSpec, ST-HOLD, marketKlineData, `docs/guides/**`, `docs/superpowers/**`, and external dirty files
- the deleted market-data/model-catalog script `scripts/opencode/sync_omc_model_catalog.py`
- all runtime/deploy, database, market-data, monitoring, test-execution, and misc tooling script families

## Baseline

- Branch: `wip/root-dirty-20260403`
- HEAD: `8af24adeb B4.012-M2b: audit scripts residual dirty domain`
- Staged changes before this authorization-prep package: empty
- Active B4.012 gates before this package:
  - `b4-012-residual-dirty-domain-atlas`
  - `b4-012-scripts-residual-domain-audit`
- `scripts/**` dirty count: `190`
- Candidate M2b-A dirty count: `15`
- GitNexus indexed/current commit before this package: `8af24adeb8a4b16ce5d1f160fa6e1bcd33eec9c9`
- OPENDOG blocker count before this package: `0`

## Candidate Path List

Modified tracked paths:

- `scripts/dev/quality_gate/build_runtime_quality_summary.py`
- `scripts/dev/quality_gate/collect_runtime_observability_baseline.py`
- `scripts/dev/quality_gate/collect_tech_debt_baseline.py`
- `scripts/dev/quality_gate/summarize_metrics_snapshot.py`
- `scripts/dev/quality_gate/tech_debt_governance_gate.py`
- `scripts/dev/quality_gate/validate_runtime_observability_drift.py`

Untracked paths:

- `scripts/dev/quality_gate/collect_api_performance_baseline.py`
- `scripts/dev/quality_gate/collect_frontend_runtime_gate.py`
- `scripts/dev/quality_gate/validate_api_performance_drift.py`
- `scripts/dev/quality_gate/validate_backend_runtime_dependencies.py`
- `scripts/dev/quality_gate/validate_container_deployment_contract.py`
- `scripts/dev/quality_gate/validate_deployment_env_contract.py`
- `scripts/dev/tools/generate-myweb-audit-secondary-inventory.mjs`
- `scripts/dev/tools/validate-myweb-audit-artifacts.mjs`
- `scripts/dev/tools/validate-myweb-audit-skill.mjs`

By status:

| Status | Count |
|---|---:|
| modified | 6 |
| untracked | 9 |
| deleted | 0 |

## Authorization Decision Prepared

Recommended next implementation package:

- `B4.012-M2b-A governance cleanup quality scripts implementation`

Recommended implementation authority:

- explicit script-source authorization limited to the 15 candidate paths above
- preservation review for the 9 untracked paths
- delta review for the 6 modified tracked paths
- no broad formatting or unrelated import cleanup
- no deletion-retirement

Recommended non-goals:

- do not touch any `scripts/**` path outside the 15-path candidate list
- do not touch source, tests, runtime behavior, API, routes, OpenSpec, ST-HOLD, marketKlineData, `docs/guides/**`, `docs/superpowers/**`, or external dirty files
- do not execute modified scripts as proof of runtime correctness unless the implementation authorization explicitly includes focused verification commands
- do not preserve untracked scripts without first confirming they belong to the governance quality gate lane
- do not batch this package with the deleted `sync_omc_model_catalog.py` path or the broader script families

## Required Gates For Future Implementation

Any future implementation must pass:

- exact staged allowlist containing only the 15 candidate script paths plus required FUNCTION_TREE/worklog artifacts
- `git diff --cached --check`
- GitNexus staged verification
- GitNexus staged detect-changes
- focused syntax checks for changed Python and MJS scripts, selected after implementation scope is approved
- OPENDOG blocker check
- post-commit GitNexus index refresh

If implementation changes script behavior rather than simply preserving untracked files, add focused runtime or unit verification for the affected script family.

## Current Status

`source_edits_authorized: false`

This authorization-prep package does not authorize staging or modifying any script file.
