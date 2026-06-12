# B4.012-M2b Scripts Residual Domain No-Source Audit

Date: 2026-06-13

## Scope

This is a no-source audit for the `scripts/**` residual dirty domain under the B4.012 residual dirty atlas.

Included:

- `scripts/**` dirty status inventory
- family classification by purpose, risk, and likely follow-up authority
- next-package recommendation for script residual governance

Explicitly excluded:

- any script content edit, deletion, restore, rename, formatting, or migration
- source, test, runtime, API, route, OpenSpec, ST-HOLD, marketKlineData, `docs/guides/**`, `docs/superpowers/**`, and external dirty files
- executing modified scripts as behavioral verification

## Baseline

- Branch: `wip/root-dirty-20260403`
- HEAD: `abcb6bbb8 B4.012-M2a: close governance residual audit nodes`
- Staged changes before this audit package: empty
- `governance/**` and `.governance/**` residuals before this audit: `0`
- Active B4.012 gate before this audit: `b4-012-residual-dirty-domain-atlas`

## Scripts Dirty Summary

Current `scripts/**` residual count: `190`

By status:

| Status | Count |
|---|---:|
| modified | 176 |
| deleted | 1 |
| untracked | 13 |

By extension:

| Extension | Count |
|---|---:|
| `.py` | 183 |
| `.mjs` | 3 |
| `.sh` | 2 |
| `.js` | 1 |
| none | 1 |

Top dirty directories:

| Directory | Count |
|---|---:|
| `scripts/dev/tools` | 31 |
| `scripts/dev/ci` | 14 |
| `scripts/dev/quality_gate` | 12 |
| `scripts/dev/debt_analyzer` | 8 |
| `scripts/tests/legacy` | 4 |
| `scripts/tests/test_security_authentication` | 4 |
| `scripts/dev/analysis` | 3 |
| `scripts/maintenance/data_cleaning` | 3 |

## Family Matrix

| Family | Count | Modified | Deleted | Untracked | Notes |
|---|---:|---:|---:|---:|---|
| misc_tooling | 56 | 54 | 0 | 2 | Mixed AI enhancer, debt analyzer, runtime helpers, and standalone dev utilities. Needs subfamily split before implementation. |
| test_execution_support | 48 | 47 | 0 | 1 | Test runner/helper scripts, legacy test support, security auth support, and a new node-test helper directory. Requires test-support authorization before edits. |
| governance_cleanup_quality | 43 | 34 | 0 | 9 | Quality gate, cleanup, validation, audit, and baseline scripts. Highest near-term governance value, but still script-code changes, not no-source. |
| runtime_deploy_ops | 13 | 13 | 0 | 0 | CI/deploy/runtime/service scripts. High operational blast radius; do not batch with cleanup utilities. |
| market_data_ingestion | 13 | 11 | 1 | 1 | Market-data and model-catalog sync helpers. Includes the only deleted file; requires explicit disposition. |
| database_data_ops | 7 | 7 | 0 | 0 | Database optimizer, schema, SQL injection, and data-access helper scripts. Requires data/database review. |
| monitoring_observability | 7 | 7 | 0 | 0 | Monitoring repair/optimizer scripts. Should stay separate from runtime deploy scripts. |
| web_api_contract_support | 3 | 3 | 0 | 0 | API usage/reporting and websocket benchmark helpers. Likely contract-support lane. |

## Deleted And Untracked Items

Deleted item:

- `scripts/opencode/sync_omc_model_catalog.py`

Untracked items:

- `scripts/dev/quality_gate/collect_api_performance_baseline.py`
- `scripts/dev/quality_gate/collect_frontend_runtime_gate.py`
- `scripts/dev/quality_gate/validate_api_performance_drift.py`
- `scripts/dev/quality_gate/validate_backend_runtime_dependencies.py`
- `scripts/dev/quality_gate/validate_container_deployment_contract.py`
- `scripts/dev/quality_gate/validate_deployment_env_contract.py`
- `scripts/dev/tools/__node_tests__/`
- `scripts/dev/tools/generate-myweb-audit-secondary-inventory.mjs`
- `scripts/dev/tools/validate-myweb-audit-artifacts.mjs`
- `scripts/dev/tools/validate-myweb-audit-skill.mjs`
- `scripts/market_data/__init__.py`
- `scripts/runtime/record_graphiti_post_commit_closeout.py`
- `scripts/runtime/trading_cash_reservations.py`

The deleted path is not approved for retirement by this audit. The untracked paths are not approved for preservation by this audit.

## Risk Assessment

The `scripts/**` dirty domain is not a single-risk package.

Primary risks:

- many scripts are executable Python utilities, so preserving or modifying them changes repository tool behavior
- runtime/deploy and database scripts can affect operational environments
- market-data/model-catalog scripts can affect data sync or tool catalog state
- test-support scripts can alter local and CI test behavior
- untracked quality gate scripts may be valuable, but they need review before preservation
- the deleted `sync_omc_model_catalog.py` needs explicit restore/preserve/retire disposition

No script should be deleted, restored, or committed based only on this no-source inventory.

## Recommended Next Packages

Recommended order:

1. `B4.012-M2b-A governance cleanup quality scripts authorization prep`
   - Candidate scope: `scripts/dev/quality_gate/**`, quality/audit/validation helpers, and related `scripts/dev/tools/*myweb-audit*.mjs`
   - Reason: highest governance value and cohesive purpose
   - Authority needed before implementation: explicit script-source authorization

2. `B4.012-M2b-B script deletion/untracked disposition no-source review`
   - Candidate scope: the single deleted path and 13 untracked paths
   - Reason: preservation/deletion decisions need explicit separate handling
   - Authority needed before implementation: preservation or deletion-retirement authorization per path family

3. `B4.012-M2b-C test execution support scripts`
   - Candidate scope: test runner/helper scripts and `scripts/tests/**`
   - Reason: can affect test semantics and CI signal
   - Authority needed before implementation: test-support source authorization

4. `B4.012-M2b-D runtime/database/market/monitoring operational scripts`
   - Candidate scope: runtime/deploy, database, market-data, and monitoring scripts
   - Reason: higher operational blast radius
   - Authority needed before implementation: separate high-risk authorization by subdomain

5. `B4.012-M2b-E misc tooling subfamily audit`
   - Candidate scope: remaining mixed AI/debt/dev utilities
   - Reason: too broad for immediate implementation; needs a second no-source split

## Decision

`scripts/**` should remain under B4.012 but must not be implemented as a single batch.

This audit prepares the decision matrix only:

- no script edits
- no script deletion
- no script preservation
- no runtime execution claims
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

This no-source audit does not authorize any script implementation package.
