## MODIFIED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Trading Audit Minimum Fields
Trading execution paths SHALL emit a minimum audit record for each submitted action.

#### Scenario: Trading action is recorded
- **WHEN** a trading submission, rejection, confirmation, or deduplication decision occurs
- **THEN** the audit record SHALL include request identity, actor identity, execution path,
  decision outcome, and timestamp
- **AND** it SHALL be sufficient to reconstruct the basic control flow for review

#### Scenario: Audit record retention is enforced
- **WHEN** a trading audit record is created
- **THEN** the record SHALL be persisted to durable storage
- **AND** the minimum retention period SHALL be defined by the trading safety contract

#### Scenario: Broker-facing submission uses transport-stage receipt
- **WHEN** a broker-facing submission is relayed through a remote bridge or task transport and
  broker acknowledgement is not yet confirmed
- **THEN** the audit record SHALL preserve the broker channel, adapter path, and transport
  receipt identifier if one exists
- **AND** it SHALL distinguish transport acceptance from broker acknowledgement or external
  order identity binding

#### Scenario: Live bridge result times out or mismatches identity
- **WHEN** the live bridge result retrieval path times out, becomes unavailable, or returns
  identity fields that do not match the active channel-scoped submission trail
- **THEN** the audit or divergence evidence SHALL preserve the live receipt identifier, failure
  class, and escalation outcome
- **AND** it SHALL remain explicit review-required runtime evidence rather than synthetic broker
  truth

#### Scenario: Phase A live bridge identity fields are preserved end to end
- **WHEN** a repo-owned `miniQMT` Phase A result is normalized and re-entered into the shared
  lifecycle ledger
- **THEN** the local contract SHALL preserve the canonical v1 identity fields needed for audit and
  reconciliation review
- **AND** those fields SHALL include `account_scope`, `event_id`, `occurred_at`, `source_name`,
  and `bridge_contract_version`
- **AND** any missing or mismatched canonical identity fields SHALL keep the path in explicit
  review-required evidence rather than synthetic broker truth
