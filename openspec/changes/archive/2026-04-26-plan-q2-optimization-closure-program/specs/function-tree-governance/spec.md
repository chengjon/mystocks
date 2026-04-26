## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Criteria-Backed Completion Semantics
The function tree SHALL use criteria-backed completion semantics instead of subjective completion percentages alone.

#### Scenario: Function-tree status is updated
- **WHEN** a function domain or capability is marked with a completion state or percentage
- **THEN** the recorded status SHALL identify the criteria behind that claim
- **AND** the criteria SHALL include applicable implementation, verification, documentation, and runtime-readiness evidence

#### Scenario: Safety-sensitive capability is reported
- **WHEN** a trading, risk, or similarly safety-sensitive capability is reported as partially or substantially complete
- **THEN** the status SHALL identify the missing controls or evidence that prevent higher completion status
- **AND** it SHALL NOT imply production-grade readiness without matching safety proof

#### Scenario: Safety-sensitive classification is determined
- **WHEN** the function tree classifies whether a capability is safety-sensitive
- **THEN** capabilities involving funds movement, position change, or pre-execution risk decisions SHALL be treated as safety-sensitive
- **AND** capabilities governed by a production-eligible trading execution path SHALL inherit that safety-sensitive classification
