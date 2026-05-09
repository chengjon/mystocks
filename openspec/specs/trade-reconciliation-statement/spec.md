# trade-reconciliation-statement Specification

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Purpose
Define the canonical first-batch trade reconciliation statement capability, including account-aware internal statement projection, approved CSV import modes, deterministic read-only matching, and filtered CSV export.
## Requirements
### Requirement: Dedicated Trade Reconciliation Statement Surface
The system SHALL provide a dedicated trade reconciliation statement capability under the trade domain.

#### Scenario: User opens the reconciliation statement page
- **WHEN** the user navigates to `/trade/reconciliation`
- **THEN** the system SHALL expose a read-only reconciliation statement surface
- **AND** the surface SHALL provide account switching, date-range filtering, CSV import, CSV export, and discrepancy results
- **AND** the surface SHALL remain separate from the trade history workbench

### Requirement: Reconciliation Account Descriptor Contract
The system SHALL expose explicit reconciliation account descriptors for account switching.

#### Scenario: Available statement accounts are listed
- **WHEN** the frontend requests available reconciliation accounts
- **THEN** the backend SHALL return a list of account descriptors
- **AND** each descriptor SHALL include a stable `account_id`, a display label, and an account type
- **AND** the account descriptor contract SHALL be explicit rather than inferred from the trade history endpoint

### Requirement: Internal Statement Projection
The system SHALL project internal reconciliation statement rows from persisted trade-domain history sources through a dedicated account-aware query path.

#### Scenario: Internal rows are queried for a time range
- **WHEN** a reconciliation statement query is executed for an account and date range
- **THEN** the system SHALL return internal statement rows derived from persisted trade-domain records
- **AND** each row SHALL include the account identity, trade identity, symbol, direction, trade time, price, quantity, amount, and commission
- **AND** the statement projection SHALL not be described as a direct reuse of the trade history workbench contract

### Requirement: Supported CSV Import Modes
The system SHALL accept only the approved first-batch CSV import modes for trade reconciliation and SHALL normalize both modes into the same broker-statement row shape.

#### Scenario: A normalized template CSV is uploaded
- **WHEN** the user imports a CSV declared as `normalized_template`
- **THEN** the system SHALL require the normalized template columns `account_id`, `trade_date`, `trade_time`, `symbol`, `direction`, `price`, `quantity`, `amount`, `commission`, `order_id`, and `trade_id`
- **AND** the system SHALL treat `account_id` as an explicit source field from the uploaded template
- **AND** the system SHALL normalize the imported rows into the shared broker-statement shape
- **AND** the normalized broker-statement row SHALL preserve the imported `account_id`

#### Scenario: A miniQMT raw CSV is uploaded
- **WHEN** the user imports a CSV declared as `miniqmt`
- **THEN** the system SHALL require the supported `miniQMT` raw CSV header set `证券代码`, `买卖方向`, `成交价格`, `成交数量`, `成交金额`, `手续费`, `委托编号`, `成交编号`, and `成交时间`
- **AND** the system SHALL bind the imported rows to the selected reconciliation account instead of inferring account identity from the raw CSV
- **AND** the system SHALL normalize the imported rows into the shared broker-statement shape
- **AND** the normalized broker-statement row SHALL preserve the selected reconciliation account as `account_id`

### Requirement: Deterministic Reconciliation Matching
The system SHALL perform deterministic one-to-one reconciliation matching and expose only the approved first-batch statuses.

#### Scenario: Imported broker rows are matched against internal rows
- **WHEN** the reconciliation engine compares imported broker rows with internal statement rows
- **THEN** the system SHALL classify each result as `matched`, `mismatched`, or `missing_broker_record`
- **AND** the system SHALL use deterministic matching rules rather than manual override or heuristic repair

### Requirement: Read-Only Reconciliation Export
The system SHALL support CSV export of the currently filtered reconciliation results.

#### Scenario: A filtered result set is exported
- **WHEN** the user requests export for the current account, date range, import batch, and status filter
- **THEN** the system SHALL return a CSV download of the filtered reconciliation result set
- **AND** the export SHALL preserve the same reconciliation statuses and row pairing used by the UI

### Requirement: Execution Tracking to Reconciliation Link
The system SHALL support navigation from execution tracking evidence to the trade reconciliation statement surface using account and order context.

#### Scenario: User jumps from execution evidence to reconciliation
- **WHEN** the user opens an execution tracking detail and chooses the reconciliation link
- **THEN** the system SHALL navigate to `/trade/reconciliation`
- **AND** the navigation SHALL preserve account identity, order identity, and bridge task identity as query context

### Requirement: Reconciliation Reverse Context Link
The system SHALL expose a reverse reconciliation context link back to the execution tracking surface when reconciliation is opened with execution context.

#### Scenario: Reconciliation page receives execution context
- **WHEN** `/trade/reconciliation` is opened with execution-related query context
- **THEN** the surface SHALL expose a link back to the execution tracking surface
- **AND** the link SHALL preserve the incoming query context for order and bridge task lookup
