# frontend-routing Specification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## ADDED Requirements

### Requirement: Trade Reconciliation Route
The frontend routing system SHALL expose a dedicated trade reconciliation statement route.

#### Scenario: User navigates to the reconciliation route
- **WHEN** the user opens `/trade/reconciliation`
- **THEN** the router SHALL load the dedicated reconciliation statement page

### Requirement: Trade Navigation Labels
The frontend routing system SHALL keep trade navigation labels aligned with the approved trade-domain surfaces.

#### Scenario: Reconciliation and history labels are rendered
- **WHEN** the frontend renders the trade navigation surfaces
- **THEN** the navigation label for `/trade/reconciliation` SHALL be `对账单`
- **AND** the navigation label for `/trade/history` SHALL be `交易历史`
