## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Canonical Realtime Transport Selection
The backend SHALL define a canonical transport selection policy for realtime delivery capabilities.

#### Scenario: Realtime capability is exposed
- **WHEN** a market-data, alerting, or strategy-triggered realtime capability is delivered to clients
- **THEN** the backend SHALL identify the canonical transport used for that capability
- **AND** it SHALL record any approved fallback or coexistence transport
- **AND** the selection SHALL align with the realtime delivery truth registry

#### Scenario: Competing realtime paths exist
- **WHEN** multiple realtime transports or overlapping delivery paths can serve the same capability
- **THEN** the system SHALL declare which path is canonical
- **AND** non-canonical paths SHALL remain compatibility-scoped or cleanup-scoped until retired
- **AND** the canonical designation SHALL match the registered realtime delivery truth
