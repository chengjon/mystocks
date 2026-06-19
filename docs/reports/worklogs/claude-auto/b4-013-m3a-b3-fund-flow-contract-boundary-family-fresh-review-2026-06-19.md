# B4.013-M3a-B3 FUND_FLOW Contract Boundary Family Fresh Review

Date: 2026-06-19
Repository: `/opt/claude/mystocks_spec`
Baseline HEAD: `a069ceb8092da412b4cc0d6aed4af9cd44c36d2d`
Mode: no-source governance review

## Scope

This review covers the remaining B4.013 FUND_FLOW contract-boundary evidence family:

- `b4-013-m3a-b3-fund-flow-refresh-openstock-audit`
- `b4-013-m3a-b3b-fund-flow-all-market-multi-day-decision`

This package does not modify MyStocks source, tests, runtime config, OpenSpec files, frontend files, backend files, or `/opt/claude/openstock`.

## Boundary

The B4.013 boundary remains unchanged:

- OpenStock owns provider runtime, data-source adapters, provider execution, provider fallback, provider cache / circuit breaker behavior, and provider-specific normalization.
- MyStocks owns public API compatibility, frontend-facing response adaptation, persisted read models, and backend consumer integration with OpenStock.
- MyStocks must not rebuild provider acquisition, provider SDK calls, provider adapters, provider fallback, direct frontend-to-OpenStock calls, or provider-side category execution.

## Evidence Reviewed

- `docs/reports/worklogs/claude-auto/b4-013-m3a-b3-fund-flow-refresh-openstock-boundary-audit-2026-06-18.md`
  - Established the no-source boundary audit for FUND_FLOW refresh.
  - Framed the remaining question around no-symbol all-market and multi-day aggregate slices.
  - Confirmed this was a boundary audit only, not a MyStocks implementation authorization.
- `docs/reports/worklogs/claude-auto/b4-013-m3a-b3b-fund-flow-all-market-multi-day-contract-decision-2026-06-18.md`
  - Decided not to migrate `symbol=None`, `3日`, `5日`, or `10日` FUND_FLOW refresh into OpenStock under the current contract.
  - Forbade provider fallback, provider SDK calls, and new local provider adapter behavior in MyStocks.
  - Kept the temporary MyStocks legacy path only for compatibility while documenting the missing OpenStock provider contract.
- `docs/reports/worklogs/claude-auto/b4-013-runtime-mainline-bring-up-closeout-2026-06-19.md`
  - Closed the B4.013 runtime mainline cycle.
  - Recorded `b4-013-m3a-b3-fund-flow-refresh-openstock-audit` as superseded operationally by B3a plus B3b and retained only as audit evidence.
  - Recorded `b4-013-m3a-b3b-fund-flow-all-market-multi-day-decision` as the active boundary decision during B4.013 closeout, with no extra B4.013 source changes required.

## Fresh Decision

Both nodes are no longer active MyStocks implementation gates.

`b4-013-m3a-b3-fund-flow-refresh-openstock-audit` is archived because it is an upstream no-source boundary audit whose outcome has already been consumed by later B3b decision-making and the B4.013 runtime closeout. It should not stay open after the family has been converted into a decision record.

`b4-013-m3a-b3b-fund-flow-all-market-multi-day-decision` is archived as a retained boundary decision because it does not authorize any MyStocks source edits. Its main value is evidence: the unsupported stock-level all-market / multi-day FUND_FLOW slices remain an OpenStock provider-contract gap, not a MyStocks data-generation task.

The retained decision text continues to prohibit MyStocks from synthesizing `symbol=None`, `3日`, `5日`, or `10日` slices until OpenStock exposes a validated provider-backed contract. No OpenSpec change is archived or edited by this package.

## Retained Follow-Up

The retained follow-up is not a MyStocks provider-repair package. Future work should start from one of these paths:

1. OpenStock provider-contract work if stock-level all-market / multi-day FUND_FLOW support is still required.
2. A MyStocks consumer-only integration package after OpenStock exposes and validates the contract.
3. A deprecation decision if product scope decides that the legacy compatibility path should be retired instead of expanded.

## Verification Plan

Before commit, run:

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus staged verification and staged change detection
- OPENDOG verification

After commit, run GitNexus analyze and verify the staged index is empty.
