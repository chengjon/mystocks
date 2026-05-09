## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Trade Execution Tracking Route
The frontend routing system SHALL expose a dedicated trade execution tracking route under the trade domain.

#### Scenario: User navigates to execution tracking
- **WHEN** the user opens `/trade/execution`
- **THEN** the router SHALL load the execution tracking workbench
- **AND** the trade navigation shall surface the new route as a canonical trade-domain surface

### Requirement: Execution Tracking Navigation Label
The trade navigation SHALL expose an execution tracking label for the dedicated workbench.

#### Scenario: Trade menu renders execution tracking
- **WHEN** the trade menu is rendered
- **THEN** the menu SHALL include an execution tracking entry
- **AND** the label SHALL distinguish the workbench from trade history and reconciliation
