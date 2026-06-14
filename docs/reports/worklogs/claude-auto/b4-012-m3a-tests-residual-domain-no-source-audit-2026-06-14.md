# B4.012-M3a tests residual domain no-source audit

Date: 2026-06-14
Mode: no-source audit, no test/source/runtime cleanup authorization
Node: `b4-012-m3a-tests-residual-domain-audit`
Parent gate: `b4-012-m3-residual-dirty-atlas-rebaseline`
Legacy duplicate node: `b4-012-tests-residual-domain-audit` (superseded by the parent-linked node above)
Baseline HEAD: `acf58d95a B4.012-M3: keep residual atlas rebaseline active`

## Scope

This audit inventories the remaining `tests/**` dirty domain under the active B4.012-M3 residual atlas rebaseline.

Included:

- `tests/**` dirty status classification
- family grouping by test purpose and risk
- untracked test artifact disposition boundaries
- recommended next authorization packages

Explicitly excluded:

- editing, deleting, restoring, moving, formatting, or staging any `tests/**` file
- modifying source, API, frontend, backend, runtime, OpenSpec, ST-HOLD, `marketKlineData`, config, or external dirty files
- claiming any test behavior has been accepted or validated
- running broad test suites against unreviewed dirty tests as an acceptance signal

## Current Tests Dirty Summary

Current `tests/**` dirty count: `231`.

By status:

| Status | Count |
|---|---:|
| modified | 218 |
| untracked | 13 |
| deleted | 0 |

By extension:

| Extension | Count |
|---|---:|
| `.py` | 224 |
| `.ts` | 4 |
| `.json` | 1 |
| no extension / directory entries | 2 |

## Family Matrix

| Family | Count | Primary risk | Notes |
|---|---:|---|---|
| misc unit/support tests | 64 | test behavior signal | Broad unit/support drift across base test helpers, DDD tests, dashboard helpers, and core behavior checks. Needs smaller source-domain alignment before any preservation. |
| API/backend contract tests | 62 | contract/security signal | API route/file tests and backend contract coverage. Must be paired with backend/API truth before accepting changes. |
| adapter tests | 25 | data-source contract signal | Akshare/TDX/financial/data adapter tests. Must align with adapter behavior and data-source contracts. |
| fixtures/helpers | 21 | test infrastructure contract | Includes helpers, fixtures, assertions, SSE helper TypeScript, pipeline/data helper tests. High blast radius for later test runs. |
| AI/test tooling | 17 | generated/tooling signal | AI-assisted testing, analyzer, optimizer, and related test tooling. Should not be mixed with business test contracts. |
| performance/runtime governance tests | 15 | runtime gate signal | Runtime observability, benchmark, tech-debt governance, deployment/runtime dependency checks. Needs runtime/governance gate review. |
| integration/acceptance tests | 10 | environment-dependent signal | PostgreSQL, TDengine, realtime integration, acceptance/CI checks. Needs environment assumptions before preservation. |
| security tests | 9 | security/compliance signal | Security compliance and vulnerability scanner tests. Keep isolated from ordinary unit cleanup. |
| frontend/E2E/component tests | 8 | E2E/UI signal | Playwright/route/UI/login/risk/fund-flow coverage. Needs frontend route/runtime gate alignment. |

Risk lens:

| Risk bucket | Count |
|---|---:|
| test behavior signal | 140 |
| contract/security signal | 61 |
| test infrastructure contract | 16 |
| E2E/UI signal | 10 |
| high-review untracked test support | 4 |

## Untracked Test Artifacts

The 13 untracked `tests/**` paths are not automatically accepted. They require separate preservation or deletion/ignore authorization.

Untracked paths:

- `tests/fixtures/miniqmt_promotion_bundle/`
- `tests/integration/contract/test_contract_validation_e2e.py`
- `tests/performance/test_benchmark_workload_classes.py`
- `tests/performance/test_collect_api_performance_baseline.py`
- `tests/performance/test_collect_frontend_runtime_gate.py`
- `tests/performance/test_validate_api_performance_drift.py`
- `tests/performance/test_validate_backend_runtime_dependencies.py`
- `tests/performance/test_validate_container_deployment_contract.py`
- `tests/performance/test_validate_deployment_env_contract.py`
- `tests/unit/data_source/`
- `tests/unit/scripts/test_collect_tech_debt_baseline.py`
- `tests/unit/scripts/test_gitnexus_workflow_gate.py`
- `tests/unit/scripts/test_graphiti_post_commit_hook_integration.py`

Recommended disposition:

- preserve as candidates only; do not delete, add, or ignore yet
- split runtime/performance gate tests from script/governance tests
- inspect fixture bundle provenance before any commit or cleanup
- require explicit path-family authorization before staging untracked tests

## Boundary Findings

There are no deleted `tests/**` paths in the current baseline, so no tests deletion-retirement package is needed for this subdomain at this moment.

The high-risk pieces are not from deletion; they are from contract authority:

- `tests/conftest.py`, helper/fixture files, and runner utilities can change broad pytest behavior
- API/backend contract tests can mask or expose backend route regressions
- Playwright/E2E tests can change frontend acceptance signal
- performance/runtime tests can alter governance and deployment gate semantics
- untracked tests may be valuable but have no tracked provenance in the current baseline

## Recommended Next Packages

Recommended order:

1. `B4.012-M3a-A tests infrastructure and helper boundary authorization prep`
   - Candidate scope: `tests/conftest.py`, `tests/base*.py`, `tests/helpers/**`, `tests/file_level/**`, test runners, fixtures, pipeline helpers.
   - Reason: these files affect later test behavior and should be stabilized before accepting large behavioral test diffs.
   - Authority needed: explicit test-support authorization.

2. `B4.012-M3a-B API/backend contract tests no-source split`
   - Candidate scope: `tests/api/**`, `tests/backend/**`, contract/auth/security-adjacent backend tests.
   - Reason: must be reviewed with backend/API route truth and contract shape.
   - Authority needed before implementation: test-authorized plus relevant backend/API source boundary review if behavior drift is found.

3. `B4.012-M3a-C adapter and data-source tests no-source split`
   - Candidate scope: `tests/adapters/**`, adapter-related API tests, `tests/unit/data_source/**`.
   - Reason: data-source tests need alignment with adapter contracts and external data assumptions.

4. `B4.012-M3a-D E2E/frontend tests no-source split`
   - Candidate scope: `tests/e2e/**`, frontend/runtime gate tests, Playwright specs, UI route smoke tests.
   - Reason: must stay isolated from frontend source dirty work and current route/UI governance.

5. `B4.012-M3a-E performance/runtime/security governance tests no-source split`
   - Candidate scope: `tests/performance/**`, runtime observability, deployment contract, security/compliance tests.
   - Reason: high operational/gate sensitivity; do not mix with ordinary unit test cleanup.

6. `B4.012-M3a-U untracked tests provenance review`
   - Candidate scope: the 13 untracked paths listed above.
   - Reason: untracked tests require explicit preserve/delete/ignore decision after provenance review.

## Decision

`tests/**` should remain under B4.012-M3 but must not be implemented as a single batch.

This audit prepares the decision matrix only:

- no test edits
- no test deletion
- no test preservation
- no untracked test staging
- no source/runtime/API/frontend/OpenSpec changes

## Required Gates For This Audit Package

- exact staged allowlist
- `git diff --cached --check`
- `ft-governance validate`
- GitNexus staged verification
- GitNexus staged detect-changes
- OPENDOG blocker check
- post-commit GitNexus index refresh

## Current Status

`source_edits_authorized: false`

This no-source audit does not authorize any test implementation package.

Governance metadata correction on 2026-06-14:

- canonical node is `b4-012-m3a-tests-residual-domain-audit`, parented by `b4-012-m3-residual-dirty-atlas-rebaseline`
- legacy duplicate node `b4-012-tests-residual-domain-audit` is a superseded orphan and should not drive follow-up packages
- correction remains no-source: no `tests/**`, source, runtime, OpenSpec, deletion, restore, or staging authorization is granted
