## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: External Execution Tracking Canonical Trigger
The system SHALL expose a canonical external execution trigger path that records trigger intent and bridge receipt evidence without claiming broker execution truth.

#### Scenario: External trigger is submitted
- **WHEN** the frontend submits an execution trigger for the first-batch miniQMT channel
- **THEN** the backend SHALL record an external trigger request
- **AND** the response SHALL expose bridge task receipt evidence
- **AND** the response SHALL NOT claim broker acknowledgement or fill state unless broker lifecycle identity is present

### Requirement: Execution Tracking Evidence Workbench
The system SHALL provide an execution tracking query surface that aggregates internal order or trade references, bridge evidence, broker correlation state, and reconciliation status.

#### Scenario: Execution tracking list is queried
- **WHEN** the frontend queries execution tracking rows
- **THEN** the backend SHALL return execution chain rows with internal order identity, bridge task identity, broker correlation state, and reconciliation status
- **AND** bridge-only terminal results SHALL remain `review_required` when broker lifecycle identity is missing

### Requirement: Legacy Trade Execute Compatibility
The system SHALL keep legacy trade execution endpoints available as compatibility surfaces while excluding them from the new canonical external trigger workbench.

#### Scenario: New execution workbench is opened
- **WHEN** the user opens `/trade/execution`
- **THEN** the page SHALL use `/api/v1/trade/execution-tracking/trigger` for new trigger requests
- **AND** it SHALL NOT depend on `/api/v1/trade/execute` as the canonical entrypoint
