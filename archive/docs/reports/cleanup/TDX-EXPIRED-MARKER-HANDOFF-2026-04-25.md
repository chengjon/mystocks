# TDX Expired Marker Handoff

## Scope

This handoff records the remaining `techdebt-expired-markers` items after the non-TDX governance cleanup line was closed on 2026-04-25.

This document is intentionally limited to TDX-owned files. It does not authorize non-TDX follow-up edits.

## Stable Baseline

- Weekly report: `/tmp/tech-debt-weekly-report-expired-pass28/tech-debt-weekly-report-20260425-013343.md`
- `ttl_expired_items`: `9`
- `new_debt_violations`: `0`
- `no-new-debt`: `PASS`
- `baseline-non-increase`: `PASS`
- `frontend_type_errors`: `0`

## Remaining TDX-Owned Items

### 1. Unit test gate markers

File: `tests/unit/adapters/test_tdx_adapter_basic.py`

- Line 20
  `pytest.skip(f"无法导入TDXDataSource: {e}", allow_module_level=True)`
- Line 204
  `pytest.skip("TDXDataSource不可用")`

Expected remediation style:
- Keep test behavior unchanged.
- Add inline metadata on the same line:
  `owner=... issue=techdebt-expired-markers ttl=2026-06-30`

### 2. Shared TDX test fixture markers

File: `tests/utils/tdx_test_helpers.py`

- Line 33
  `pytest.skip(f"TDX test day file not found: {file_path}")`
- Line 42
  `pytest.skip(f"TDX test minute file not found: {file_path}")`

Expected remediation style:
- Keep skip semantics unchanged.
- Add inline metadata on the same line.

### 3. Frontend TDX placeholder TODO markers

File: `web/frontend/src/views/market/composables/useTdx.ts`

- Line 69
  `// TODO: Replace with actual TDX connection check API`
- Line 92
  `// TODO: Replace with actual TDX quote API`
- Line 128
  `// TODO: Update chart with new period`
- Line 133
  `// TODO: Update chart with new date range`
- Line 142
  `// TODO: Implement chart data loading`

Expected remediation style:
- Keep current placeholder flow unchanged unless the TDX workstream is ready to implement real APIs.
- If only doing governance cleanup, add inline metadata to each TODO.
- If implementing real TDX behavior, update tests/contracts in the same batch and rerun runtime gate checks.

## Boundaries

- Do not rewrite TDX business logic in the governance-only line.
- Do not replace mock/simulated flows in `useTdx.ts` unless the TDX delivery line is actively implementing real endpoints.
- Do not treat these 9 items as non-TDX debt; they are intentionally deferred.

## Recommended Order For TDX Workstream

1. Patch the 4 `pytest.skip(...)` lines first.
2. Patch the 5 `useTdx.ts` TODO lines if the line is still governance-only.
3. Rerun:
   `TECH_DEBT_WEEKLY_REPORT_DIR=/tmp/tech-debt-weekly-report-expired-pass-tdx bash scripts/run_tech_debt_weekly_report.sh`
4. If `useTdx.ts` is functionally upgraded instead of metadata-only patched, also rerun:
   `npm --prefix web/frontend run type-check`

## Notes

- Governance tooling false positives for generated `components.d.ts` and `autoDownsample` have already been fixed in `scripts/dev/quality_gate/tech_debt_governance_gate.py`.
- Remaining count should drop from `9` to `0` once the TDX line applies metadata or real implementation changes and reruns the weekly report.
