## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

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
