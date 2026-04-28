## MODIFIED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Trading Domain Safety Contract
The project SHALL define an explicit safety contract for trading execution paths before they are
described as production-grade.

#### Scenario: Trading path is classified
- **WHEN** a trading execution path is documented or exposed
- **THEN** it SHALL be classified as simulated, experimental, or production-eligible
- **AND** the classification SHALL identify the safety controls that justify that state
- **AND** the classification SHALL define the minimum audit retention expectation for that state

#### Scenario: Production-eligible trading path depends on broker truth
- **WHEN** a trading execution path is proposed as production-eligible
- **THEN** it SHALL identify the canonical broker-facing execution path, broker acknowledgement
  source, and reconciliation owner
- **AND** it SHALL identify the broker acknowledgement and reconciliation evidence that justifies
  externally-aligned lifecycle claims
- **AND** absence of that contract SHALL keep the path classified as simulated or experimental

#### Scenario: Remote transport receipt is not broker acknowledgement
- **WHEN** a broker-facing execution path uses an asynchronous bridge, task worker, or remote
  transport layer that can accept delivery before broker acknowledgement is known
- **THEN** the safety contract SHALL distinguish transport acceptance from broker
  acknowledgement and external order identity binding
- **AND** the path SHALL remain experimental unless auditable runtime evidence proves the
  broker-facing acknowledgement boundary

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
