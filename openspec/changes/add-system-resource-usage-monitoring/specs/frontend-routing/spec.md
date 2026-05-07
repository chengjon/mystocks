# frontend-routing Specification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## ADDED Requirements

### Requirement: System Resource Usage Route
The frontend routing system SHALL expose a dedicated system resource usage route.

#### Scenario: User navigates to the resource usage route
- **WHEN** the user opens `/system/resources`
- **THEN** the router SHALL load the dedicated system resource usage page

### Requirement: System Navigation Labels For Resource Usage
The frontend routing system SHALL keep system navigation labels aligned with the approved resource usage surface.

#### Scenario: Resource usage label is rendered
- **WHEN** the frontend renders the active system navigation surfaces
- **THEN** the navigation label for `/system/resources` SHALL be `资源使用`
