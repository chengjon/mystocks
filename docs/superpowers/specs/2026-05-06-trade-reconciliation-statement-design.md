# Trade Reconciliation Statement Design

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Context

`FUNCTION_TREE` currently marks `5.2 对账单` as unfinished and points at `web/frontend/src/views/trade/History.vue`. The current repository truth supports a trade-history workbench, not a reconciliation statement capability. The existing frontend page renders historical trades from `/v1/trade/trades`, and the backend trade route currently exposes portfolio, positions, signals, trades, statistics, and execution flows. None of those contracts provide a dedicated statement import, broker CSV normalization, or reconciliation result surface.

The next feature should close `5.2 对账单` without collapsing it into `5.3 执行跟踪`. This batch therefore needs an independent reconciliation capability that reuses existing trade-domain truth sources, but does not claim live broker truth closure or production reconciliation proof.

## Goals

- Add an independent trade reconciliation statement capability under the existing trade domain.
- Support multi-account switching for reconciliation workflows.
- Generate internal statement rows from current trade-domain truth sources.
- Support external CSV import through two entry modes:
  - project-defined normalized template CSV
  - `miniQMT` raw CSV
- Run deterministic automatic matching and expose only these first-batch statuses:
  - `matched`
  - `mismatched`
  - `missing_broker_record`
- Support CSV export of the filtered reconciliation results.

## Non-Goals

- Do not merge reconciliation into `web/frontend/src/views/trade/History.vue`.
- Do not implement manual review, manual override, or online correction.
- Do not implement PDF export or print layouts.
- Do not implement cross-account aggregate statements.
- Do not expand this batch into live broker production reconciliation closure.
- Do not claim `5.3 执行跟踪` is complete as part of this feature.
- Do not introduce `extra_broker_record`, `ignored`, or `reviewed` statuses in this MVP.

## Chosen Scope

The approved scope is:

- layered statement design rather than full live broker closure
- CSV export only
- multi-account switching
- both normalized-template CSV import and `miniQMT` raw CSV import
- automatic matching plus read-only discrepancy display

## Capability Boundary

This capability is a new reconciliation surface inside the existing trade domain, not a parallel trading system.

### Existing surfaces that remain separate

- `web/frontend/src/views/trade/History.vue`
  - remains the trade-history workbench
- `web/backend/app/api/trade/routes.py`
  - remains the existing trade-domain entry point and should be extended, not bypassed
- execution-tracking and broker runtime flows
  - remain part of `5.3 执行跟踪`

### New surface

- `web/frontend/src/views/trade/Reconciliation.vue`
  - dedicated reconciliation page
- new reconciliation contract under the existing trade route package
  - no parallel capability or parallel route family

## Frontend Design

### Page

Add a dedicated reconciliation page at `web/frontend/src/views/trade/Reconciliation.vue`.

### Primary controls

The top section should provide four controls:

- account switcher
- date range selector
- CSV import action
- CSV export action

### Main layout

The page body should be split into three stable zones:

- internal statement summary
- external import summary
- reconciliation result table

### Result behavior

- results are read-only
- discrepancy state is display-only
- manual drawing, execution tracking, and broker runtime workflows do not belong on this page

## Backend Contract

The backend stays inside the current trade-domain route family.

### Endpoints

- `GET /api/trade/reconciliation/accounts`
  - return available account switch targets
- `GET /api/trade/reconciliation/statements`
  - return internal statement rows and summary for an account and time range
- `POST /api/trade/reconciliation/import`
  - accept one uploaded CSV and a declared source type
- `GET /api/trade/reconciliation/results`
  - return automatic reconciliation results for the selected account, time range, and imported batch
- `GET /api/trade/reconciliation/export`
  - export the current filtered reconciliation result set as CSV

All endpoints must continue using the project-standard `UnifiedResponse`.

## Data Contract

The design uses three explicit row layers.

### InternalStatementRow

This is the internal truth row derived from current trade-domain history sources. At minimum it should contain:

- `account_id`
- `trade_id`
- `order_id`
- `symbol`
- `direction`
- `trade_time`
- `price`
- `quantity`
- `amount`
- `commission`

### BrokerStatementRow

This is the normalized row derived from imported external CSV content. At minimum it should contain:

- `account_id`
- `trade_id`
- `order_id`
- `symbol`
- `direction`
- `trade_time`
- `price`
- `quantity`
- `amount`
- `commission`
- `source_type`
- `raw_row_number`

### ReconciliationResultRow

This is the deterministic result row used by the UI and export flow. At minimum it should contain:

- `match_status`
- `match_reason`
- `internal_row`
- `broker_row`

### Allowed result statuses

The first batch only allows:

- `matched`
- `mismatched`
- `missing_broker_record`

## CSV Import Model

The feature supports two external CSV paths, both normalized into the same `BrokerStatementRow` model before matching.

### 1. Normalized template CSV

The first-batch template is a locked schema, not a fuzzy import mode. It should at minimum require:

- `account_id`
- `trade_date`
- `trade_time`
- `symbol`
- `direction`
- `price`
- `quantity`
- `amount`
- `commission`
- `order_id`
- `trade_id`

This template exists to provide a stable import truth surface for regression tests, manual verification, and future broker adapters.

### 2. `miniQMT` raw CSV

The first broker-specific parser is `miniQMT`.

Its implementation must be explicit:

- fixed header mapping
- fixed normalization rules
- fixed structured error reporting

The raw `miniQMT` file must pass through its parser first, then become the same `BrokerStatementRow` model used by the normalized template path.

## Matching Rules

The first batch uses deterministic one-to-one matching only.

### Matching priority

1. Use `order_id` when both sides provide a directly matchable order identifier.
2. Otherwise use the tuple:
   - `symbol`
   - `direction`
   - `trade_time`
   - `quantity`
   - `price`

### Time tolerance

A small normalization tolerance is allowed only to reconcile formatting differences in timestamps. It must not be used to weaken business semantics or to justify fuzzy broad matching.

### Cardinality rules

- one internal row can match at most one broker row
- one broker row can match at most one internal row

### Status semantics

- `matched`
  - critical fields align and numeric fields are within allowed tolerance
- `mismatched`
  - a candidate pair exists but critical or numeric fields do not align
- `missing_broker_record`
  - an internal row has no broker candidate

### Explicit exclusions from this batch

- no `extra_broker_record`
- no one-to-many or many-to-one grouping
- no fuzzy learning-based matching
- no operator override

## Export Rules

The first batch supports CSV export only.

### Export behavior

- export only the current filtered result set
- include internal fields, broker fields, `match_status`, and `match_reason`
- preserve enough detail for downstream review without reopening the application

## Testing Strategy

The feature should close through four validation layers.

### Backend unit tests

Cover:

- normalized-template parser
- `miniQMT` parser
- reconciliation matcher
- export serializer

Key assertions:

- valid CSV normalizes into canonical broker rows
- missing columns, bad dates, and bad numeric values return structured errors
- `matched`, `mismatched`, and `missing_broker_record` are deterministic
- one-to-one matching does not double-consume rows

### Backend route and contract tests

Lock request and response shape for:

- accounts
- statements
- import
- results
- export

Key assertions:

- `UnifiedResponse` shape
- stable field names
- correct error semantics
- empty-result semantics remain explicit

### Frontend unit tests

Cover:

- multi-account switching
- date-range filtering
- CSV import state transitions
- discrepancy summary cards
- result table rendering for all three allowed statuses

### End-to-end or smoke validation

At least one workflow must be verified:

1. open the reconciliation page
2. switch account and choose time range
3. import a normalized-template or `miniQMT` CSV
4. observe automatic reconciliation results
5. export filtered results as CSV

## Governance Closeout

### FUNCTION_TREE rule

`5.2 对账单` may only move from `🚧` to `✅` after all of the following are true:

- dedicated reconciliation page exists
- backend reconciliation contract exists
- normalized-template import works
- `miniQMT` import works
- automatic matching works
- CSV export works
- the feature has been verified through targeted tests

### OpenSpec rule

This feature should modify an existing trade-domain capability boundary rather than inventing a parallel capability.

### Documentation truth rule

This batch must describe:

- internal statement truth
- CSV import truth
- automatic discrepancy truth

It must not claim:

- live broker reconciliation closure
- operator review closure
- production broker proof

## Risks And Mitigations

### Risk: history and reconciliation collapse into one page

Mitigation:

- keep `History.vue` and `Reconciliation.vue` separate from day one

### Risk: future broker integrations force matcher rewrites

Mitigation:

- normalize every import path into the same `BrokerStatementRow` before matching

### Risk: uncontrolled import variance

Mitigation:

- lock the normalized template
- support exactly one broker-specific parser in this batch: `miniQMT`

### Risk: scope expansion into execution-tracking closure

Mitigation:

- explicitly keep live broker truth, manual review, and production reconciliation out of scope

## Acceptance Summary

This design adds a dedicated trade reconciliation statement capability that reuses current trade-domain truth sources, imports normalized-template and `miniQMT` CSV data, runs deterministic read-only matching, exposes `matched`, `mismatched`, and `missing_broker_record`, supports multi-account switching and CSV export, and stops short of manual review or production broker-truth closure.
