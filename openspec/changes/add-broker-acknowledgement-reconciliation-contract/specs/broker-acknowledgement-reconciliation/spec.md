# broker-acknowledgement-reconciliation Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## ADDED Requirements

### Requirement: Local-To-External Order Identity Binding
Broker-facing execution paths SHALL define how a local order submission is bound to external
broker or counterparty identity.

#### Scenario: Submission is accepted before broker order identity is finalized
- **WHEN** a local order submission is handed to a broker-facing adapter and an external order id is not yet available
- **THEN** the system SHALL persist a correlation record that binds the local order id to the broker-facing submission attempt
- **AND** the record SHALL identify the adapter path, account or session scope, and acknowledgement status
- **AND** the path SHALL remain explicitly awaiting broker acknowledgement rather than silently claiming external order truth

#### Scenario: Broker acknowledgement assigns external identity
- **WHEN** a broker or counterparty acknowledgement provides an external order identity for a known local submission
- **THEN** the system SHALL bind the local order id and external order identity within the same canonical correlation surface
- **AND** subsequent broker lifecycle events SHALL resolve through that binding instead of free-text or heuristic matching alone

### Requirement: Broker Lifecycle Event Identity Contract
Broker-facing lifecycle ingestion SHALL define the minimum identity and sequencing metadata
required for acknowledgement, rejection, cancel, and execution events.

#### Scenario: Broker lifecycle event is ingested
- **WHEN** a broker-facing adapter emits an acknowledgement, reject, cancel, or execution event
- **THEN** the event SHALL preserve the external order identity or correlation token used for matching
- **AND** it SHALL preserve event type, source timestamp, and any event identity or sequencing metadata that the adapter can provide
- **AND** missing identity or sequencing fields SHALL be classified explicitly instead of being treated as replay-safe by default

#### Scenario: Replay suppression is claimed for broker lifecycle events
- **WHEN** a trading path claims to suppress duplicate broker lifecycle events
- **THEN** the suppression contract SHALL identify which external identity or sequencing fields justify the suppression decision
- **AND** the system SHALL preserve an auditable record of that suppression decision

### Requirement: Reconciliation Divergence Classification
The system SHALL classify local-versus-broker lifecycle mismatches through stable divergence
categories before automatic resolution is attempted.

#### Scenario: Local and broker lifecycle states diverge
- **WHEN** a broker-facing acknowledgement, reject, cancel, or execution fact disagrees with current local order evidence
- **THEN** the divergence SHALL be classified through a stable machine-readable category
- **AND** the category SHALL distinguish at least awaiting-broker-acknowledgement, unmatched-external-order, locally-terminal-externally-open, externally-terminal-locally-open, and quantity-or-fill divergence

#### Scenario: Execution event cannot be matched safely
- **WHEN** an execution event arrives without sufficient identity to match it safely to a local order
- **THEN** the system SHALL classify it as an unmatched external execution incident
- **AND** it SHALL NOT auto-mutate an unrelated local order on quantity or price coincidence alone

### Requirement: Reconciliation Resolution Boundary
Broker acknowledgement and reconciliation workflows SHALL define explicit boundaries for
automatic resolution, operator review, and unresolved incident retention.

#### Scenario: Divergence policy requires operator review
- **WHEN** a reconciliation divergence does not satisfy the configured automatic resolution contract
- **THEN** the workflow SHALL preserve the divergence as an auditable review-required state
- **AND** it SHALL identify the owner, next action, and evidence needed for closure

#### Scenario: Divergence is auto-resolved
- **WHEN** the reconciliation policy allows automatic resolution for a divergence class
- **THEN** the policy SHALL identify which external facts authorize the local state update
- **AND** the system SHALL preserve an audit record of the automatic resolution decision and its justification
