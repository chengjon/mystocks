# B4.012-M3a-E performance runtime security tests no-source split

Date: 2026-06-14
Mode: no-source split audit, no test/source/runtime cleanup authorization
Parent gate: `b4-012-m3a-tests-residual-domain-audit`

## Scope

This audit splits the performance, runtime governance, deployment, and security/compliance test dirty domain into narrower future packages.

Included:

- tracked performance/runtime governance tests under `tests/performance/**`
- tracked security/compliance scanner tests under `tests/security/**`
- tracked repository hygiene governance test under `tests/unit/scripts/**`
- untracked performance/deployment/script governance tests as provenance-only candidates

Explicitly excluded:

- API/backend overlap already routed through M3a-B
- adapter/data-source overlap already routed through M3a-C
- E2E/frontend overlap already routed through M3a-D
- contract-engine tests already routed through M3a-B4
- any source, runtime, OpenSpec, OpenStock, deletion, restore, or staging action

## Current Dirty Summary

Measured from `git status --porcelain=v1 -- tests` on 2026-06-14.

Tracked performance/runtime candidates: 12.

- `tests/performance/api_smoke_endpoints.json`
- `tests/performance/benchmark.py`
- `tests/performance/test_api_performance_baseline_governance_doc.py`
- `tests/performance/test_benchmark_cli.py`
- `tests/performance/test_build_runtime_quality_summary.py`
- `tests/performance/test_collect_runtime_observability_baseline.py`
- `tests/performance/test_metrics_snapshot_summary.py`
- `tests/performance/test_run_runtime_observability_drift_gate_script.py`
- `tests/performance/test_stress_test.py`
- `tests/performance/test_tech_debt_governance_weekly_report_runtime.py`
- `tests/performance/test_tech_debt_weekly_report_script.py`
- `tests/performance/test_validate_runtime_observability_drift.py`

Tracked security/compliance candidates: 7.

- `tests/security/test_security_compliance/compliance_test_engine_methods/part1.py`
- `tests/security/test_security_compliance/compliance_test_engine_methods/part2.py`
- `tests/security/test_security_compliance/helpers.py`
- `tests/security/test_security_compliance/utils.py`
- `tests/security/test_security_vulnerabilities/security_vulnerability_scanner_methods/part1.py`
- `tests/security/test_security_vulnerabilities/security_vulnerability_scanner_methods/part2.py`
- `tests/security/test_security_vulnerabilities/utils.py`

Tracked governance script candidate: 1.

- `tests/unit/scripts/test_repository_hygiene_paths.py`

Untracked provenance-only candidates: 10.

- `tests/performance/test_benchmark_workload_classes.py`
- `tests/performance/test_collect_api_performance_baseline.py`
- `tests/performance/test_collect_frontend_runtime_gate.py`
- `tests/performance/test_validate_api_performance_drift.py`
- `tests/performance/test_validate_backend_runtime_dependencies.py`
- `tests/performance/test_validate_container_deployment_contract.py`
- `tests/performance/test_validate_deployment_env_contract.py`
- `tests/unit/scripts/test_collect_tech_debt_baseline.py`
- `tests/unit/scripts/test_gitnexus_workflow_gate.py`
- `tests/unit/scripts/test_graphiti_post_commit_hook_integration.py`

## Boundary Findings

The broad runtime/security scan matched additional API, backend, monitoring, and unit-runtime names. Those are not accepted into this package without a narrower owner review:

- API monitoring/data quality/signal routes remain under M3a-B API packages.
- backend risk remains under M3a-B3.
- contract runtime-source test remains under M3a-B4.
- data-source runtime registry remains under M3a-C.
- frontend runtime gate remains untracked and must first pass M3a-U provenance review.

## Suggested Follow-Up Packages

1. `B4.012-M3a-E1 performance runtime tracked authorization prep`
   - Candidate scope: the 12 tracked `tests/performance/**` files.
   - Gate: runtime/performance baseline and environment assumptions review.

2. `B4.012-M3a-E2 security compliance tracked authorization prep`
   - Candidate scope: the 7 tracked `tests/security/**` files.
   - Gate: security/compliance test ownership and scanner behavior review.

3. `B4.012-M3a-E3 governance script test authorization prep`
   - Candidate scope: `tests/unit/scripts/test_repository_hygiene_paths.py`.
   - Gate: repository hygiene and governance helper behavior review.

4. `B4.012-M3a-EU performance and governance untracked provenance review`
   - Candidate scope: the 10 untracked performance/deployment/script tests.
   - Gate: provenance and preserve/delete/ignore decision before any staging.

## Non-Goals

- No test edits.
- No source, backend, API, frontend, runtime, OpenSpec, OpenStock, ST-HOLD, or marketKlineData edits.
- No test deletion, restore, or untracked staging.
- No acceptance of runtime, performance, deployment, or security behavior changes.

## Required Gates For This Audit Package

- exact staged allowlist of governance/report files only
- `git diff --cached --check`
- Function Tree validation
- GitNexus staged verification
- GitNexus staged detect-changes
- OPENDOG blocker check
- post-commit GitNexus index refresh

## Current Status

`source_edits_authorized: false`

This no-source split does not authorize performance, runtime, security, or governance test implementation.
