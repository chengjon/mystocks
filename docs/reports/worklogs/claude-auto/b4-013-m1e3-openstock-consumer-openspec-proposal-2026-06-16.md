# B4.013-M1-E3 OpenStock Consumer OpenSpec Proposal

Date: 2026-06-16

Status: proposal package prepared.

## Scope

This package converts the B4.013-M1-E2 no-source boundary audit into an OpenSpec proposal.

Allowed edits in this package:

- `openspec/changes/externalize-data-source-provider-to-openstock/proposal.md`
- `openspec/changes/externalize-data-source-provider-to-openstock/design.md`
- `openspec/changes/externalize-data-source-provider-to-openstock/tasks.md`
- `openspec/changes/externalize-data-source-provider-to-openstock/specs/data-source-runtime-service/spec.md`
- `openspec/changes/externalize-data-source-provider-to-openstock/specs/data-sources/spec.md`
- FUNCTION_TREE governance state files for the M1-E3 node
- this worklog

No source, test, runtime, frontend, backend, or OpenStock files were modified.

## Baseline

- Mystocks branch: `wip/root-dirty-20260403`
- Mystocks starting HEAD: `8c43b1c30 B4.013-M1-E2: audit OpenStock consumer boundary`
- New OpenSpec change id: `externalize-data-source-provider-to-openstock`
- Existing matching change directory before creation: missing
- Relevant existing specs:
  - `data-source-runtime-service`
  - `data-sources`

External dirty items were observed and not touched:

- `architecture/STANDARDS.md`
- existing untracked FUNCTION_TREE cards
- older untracked B4.013 worklogs
- existing untracked OpenSpec archive/proposal directories

## Proposal Contents

The proposal defines:

- OpenStock as the target owner for provider adapters, upstream acquisition, provider health, route decision, cache/circuit breaker state, provider metrics, REST pull data, and market stream production.
- MyStocks as the backend compatibility and business consumer layer.
- Frontend direct OpenStock calls as out of scope for the first implementation phase.
- Quotes and K-line/OHLCV as the first ready MyStocks consumer mappings.
- Fund-flow, sector-flow, LHB, block-trade, and ETF provider refresh as OpenStock-owned contract gaps.
- Existing MyStocks provider-shaped routes/files as migration inventory, not expansion targets.

## Validation Targets

Required before commit:

- `openspec validate externalize-data-source-provider-to-openstock --strict`
- FUNCTION_TREE validation
- `git diff --cached --check`
- GitNexus staged verification and detect-changes
- OPENDOG verification

## Decision

`B4.013-M1-E3` is prepared as a proposal package only. It does not authorize implementation. Source-authorized implementation should start only after the proposal is reviewed and approved.
