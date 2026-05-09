## MODIFIED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Execution Tracking Evidence Workbench
The system SHALL provide an execution tracking query surface that aggregates internal order or trade references, miniQMT bridge submission evidence, broker correlation state, and reconciliation status.

#### Scenario: Execution tracking list is queried
- **WHEN** the frontend queries execution tracking rows
- **THEN** the backend SHALL return execution chain rows with internal order identity, bridge task identity, broker correlation state, and reconciliation status
- **AND** miniQMT bridge submission attempts SHALL be included when available for the requested account, order id, or bridge task id
- **AND** bridge-only terminal results SHALL remain `review_required` when broker lifecycle identity is missing

#### Scenario: miniQMT bridge evidence has no broker lifecycle identity
- **WHEN** a bridge task has a terminal bridge result but no broker lifecycle identity
- **THEN** execution tracking SHALL expose the bridge result as review evidence
- **AND** execution tracking SHALL NOT mark the chain as broker acknowledged or filled

#### Scenario: Broker lifecycle identity is present
- **WHEN** miniQMT evidence includes broker lifecycle identity and acknowledgement event type
- **THEN** execution tracking MAY mark the chain as broker acknowledged
- **AND** the evidence timeline SHALL include the broker identity source used for that state transition
