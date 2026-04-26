## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Trading Domain Safety Contract
The project SHALL define an explicit safety contract for trading execution paths before they are described as production-grade.

#### Scenario: Trading path is classified
- **WHEN** a trading execution path is documented or exposed
- **THEN** it SHALL be classified as simulated, experimental, or production-eligible
- **AND** the classification SHALL identify the safety controls that justify that state
- **AND** the classification SHALL define the minimum audit retention expectation for that state

### Requirement: Trading Pre-Execution Risk Gate
Safety-sensitive trading paths SHALL define pre-execution risk gates that block submissions exceeding configured capital or exposure thresholds.

#### Scenario: Capital or exposure threshold is exceeded
- **WHEN** a trading submission would exceed a configured capital, concentration, or exposure threshold
- **THEN** the execution path SHALL block the submission before order placement
- **AND** it SHALL record the blocking decision as an audit event

### Requirement: Idempotent Trading Submission
Trading execution paths SHALL define an idempotent submission policy.

#### Scenario: Trading request is retried or duplicated
- **WHEN** the same effective trading instruction is submitted more than once within the deduplication scope
- **THEN** the execution path SHALL prevent unintended duplicate order submission
- **AND** it SHALL preserve an auditable record of the deduplication decision

### Requirement: Trading Confirmation Policy
Safety-sensitive trading operations SHALL define a confirmation policy before execution.

#### Scenario: High-risk trading action is requested
- **WHEN** an operation crosses the configured safety threshold for capital, position change, or destructive impact
- **THEN** the system SHALL require an explicit confirmation step or approved equivalent safeguard
- **AND** the policy SHALL identify when confirmation may be bypassed and why

### Requirement: Trading Audit Minimum Fields
Trading execution paths SHALL emit a minimum audit record for each submitted action.

#### Scenario: Trading action is recorded
- **WHEN** a trading submission, rejection, confirmation, or deduplication decision occurs
- **THEN** the audit record SHALL include request identity, actor identity, execution path, decision outcome, and timestamp
- **AND** it SHALL be sufficient to reconstruct the basic control flow for review

#### Scenario: Audit record retention is enforced
- **WHEN** a trading audit record is created
- **THEN** the record SHALL be persisted to durable storage
- **AND** the minimum retention period SHALL be defined by the trading safety contract
