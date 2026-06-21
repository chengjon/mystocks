# B4.012-M3a-E1 Performance Runtime Tracked Authorization Prep

Date: 2026-06-21

## Scope

This is an authorization-preparation package for the first executable sub-batch under:

- Parent: `b4-012-m3a-e-performance-runtime-security-tests-split`
- Child: `b4-012-m3a-e1-performance-runtime-tracked-authorization`

No test/source/runtime/OpenSpec/OpenStock files are modified by this prep package.

## Allowed Implementation Paths

E1 is limited to the 12 tracked performance/runtime governance files below:

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

The eventual implementation package may also create its own closeout worklog under:

- `docs/reports/worklogs/claude-auto/b4-012-m3a-e1-performance-runtime-tracked-closeout-2026-06-21.md`

## Non-Goals

- Do not touch untracked `tests/performance/**` provenance candidates.
- Do not touch `tests/security/**`.
- Do not touch `tests/e2e/**` or the closed D1 browser-smoke files.
- Do not touch `tests/unit/**`, `scripts/tests/**`, `web/backend/tests/**`, or `web/frontend/**`.
- Do not touch application source/runtime, OpenSpec, OpenStock provider/data-source runtime, ST-HOLD, or marketKlineData.
- Do not weaken performance, security, deployment, runtime-observability, or tech-debt gate semantics.
- Do not silently skip environment-dependent tests; any skip or xfail must be explicit, justified, and bounded to this package.

## Risk Assessment

- Runtime/performance tests may encode local machine state, PM2 availability, generated report paths, or benchmark timing assumptions.
- `api_smoke_endpoints.json` is configuration-like test data; edits must preserve endpoint intent and avoid broad API contract changes.
- Governance and tech-debt performance tests can hide real quality regressions if assertions are relaxed. Implementation must prefer fixture isolation, path normalization, deterministic inputs, and explicit environment guards over assertion weakening.

## Required Gates For E1 Implementation

- `git diff --cached --check`
- FUNCTION_TREE scope check for the exact allowed E1 paths
- GitNexus staged verification and staged change detection
- OPENDOG verification
- `python -m py_compile` for all allowed Python files
- `ruff check` for allowed Python files, or document repo-config blocker if ruff cannot run on the narrow file set
- Focused `pytest` for the allowed E1 tests with `--no-cov`, recording any environment-only blockers separately from code failures
- Staged index must contain only E1 allowed files, E1 closeout worklog, and generated governance state files

## Decision

Prepare E1 as the next source-authorized candidate, but do not start implementation until the user explicitly approves the E1 authorization.
