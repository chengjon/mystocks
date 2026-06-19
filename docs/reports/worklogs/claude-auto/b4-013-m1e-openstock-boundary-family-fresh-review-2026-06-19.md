# B4.013-M1E OpenStock Boundary Family Fresh Review

Date: 2026-06-19
Mode: no-source governance review
Source edits authorized: false

## Scope

This review covers the OpenStock boundary evidence family:

- `b4-013-m1e-openstock-data-source-boundary-audit`
- `b4-013-m1e2-openstock-consumer-boundary-audit`
- `b4-013-m1e3-openstock-consumer-openspec-proposal`

The goal is to decide whether these nodes still need active FUNCTION_TREE authorization gates after the B4.013 runtime-mainline parent has closed.

This review does not modify:

- source code
- tests
- OpenSpec files
- OpenStock repository files
- frontend/backend runtime implementation
- routes, API models, or configs
- ST-HOLD / marketKlineData / external dirty files

## Existing Evidence

M1E established the corrected boundary:

- OpenStock owns data-source provider functionality.
- MyStocks must not expand or repair provider behavior as if it were the provider system.
- MyStocks is responsible for integration, request/response adaptation, compatibility shapes, and business workflows that consume data.

M1E2 mapped the consumer boundary:

- MyStocks should consume provider-backed data through a backend OpenStock consumer client.
- Local provider adapters and factories are migration inventory, not expansion points.
- Consumer-side timeout, retry, cache-read, and degradation behavior are valid MyStocks responsibilities.

M1E3 prepared the OpenSpec proposal:

- Change id: `externalize-data-source-provider-to-openstock`
- Current OpenSpec state: active change exists.
- Validation: `openspec validate externalize-data-source-provider-to-openstock --strict` passed.
- Task state observed by `openspec list`: `0/19 tasks`.

## Fresh Runtime / Governance Context

B4.013 parent closeout has already recorded:

- OpenStock consumer boundary was documented and enforced.
- MyStocks-side OpenStock backend consumer contracts were expanded and tested for the market categories used by the runtime path.
- Refresh/runtime paths were migrated where OpenStock had provider-backed contracts:
  - `ETF_SPOT`
  - `BLOCK_TRADE`
  - `DRAGON_TIGER`
  - symbol-scoped `FUND_FLOW` for `今日`
  - supported `SECTOR_FUND_FLOW` slices
- Unsupported provider gaps remain backlog/provider-contract concerns, not MyStocks data synthesis work.

Fresh PM2 business smoke evidence from the M1C/M1E cleanup pass:

- PM2 backend: online at `http://localhost:8020`
- PM2 frontend: online at `http://localhost:3020`
- PM2 external frontend business smoke: `55 passed (2.9m)`
- Failure count: `0`

## Decision

The three M1E-family FUNCTION_TREE nodes should not remain active authorization gates.

Reasoning:

- They are boundary/proposal evidence nodes, not current implementation packages.
- The B4.013 parent node has already closed the mainline runtime cycle that consumed this evidence.
- Keeping them in active gates as `decision-prepared -> prepare authorization` creates false pressure to authorize MyStocks source edits in a provider-boundary area.
- The OpenSpec change itself remains active and valid; this review does not archive or edit OpenSpec.

Therefore:

- Archive `b4-013-m1e-openstock-data-source-boundary-audit`.
- Archive `b4-013-m1e2-openstock-consumer-boundary-audit`.
- Archive `b4-013-m1e3-openstock-consumer-openspec-proposal`.

## Remaining Work

OpenSpec follow-up is separate from this FUNCTION_TREE cleanup.

The active OpenSpec proposal may be updated or archived only under a dedicated OpenSpec-authorized package. Because `openspec list` reports `0/19 tasks`, this review intentionally does not mark OpenSpec implementation complete.

Next practical queue after this family cleanup:

1. Review `b4-013-m2e3-openstock-category-coverage-audit` and `b4-013-m2e4-openstock-contract-gap-handoff` as the next OpenStock contract evidence family.
2. Preserve the critical `FUND_FLOW` all-market/multi-day boundary decision until OpenStock exposes a provider-backed contract.
3. Start a new P0 runtime cycle only if a fresh PM2 route/API/data-flow regression is observed.

MyStocks remains consumer-only for OpenStock data.
