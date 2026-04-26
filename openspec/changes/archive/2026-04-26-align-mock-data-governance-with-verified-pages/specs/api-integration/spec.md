## MODIFIED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Page-Level API Truth Classification
The system SHALL classify each active ArtDeco page's API dependency as `verified` or `pending` and apply page behavior accordingly.

#### Scenario: Verified API page behavior
- **WHEN** an ArtDeco page is marked `verified`
- **THEN** it SHALL use the registered real API endpoint as its primary data source
- **AND** it SHALL NOT silently fall back to mock data for the same user path
- **AND** it SHALL surface loading, error, empty, and request identifier states
- **AND** any explicit mock behavior for that page SHALL require an explicit mock-mode or approved automation-isolation path rather than implicit runtime substitution

#### Scenario: Pending API page behavior
- **WHEN** an ArtDeco page is marked `pending`
- **THEN** the route SHALL remain reachable
- **AND** the page SHALL render shell/loading/error/empty states without fabricating contract fields
- **AND** the unresolved API blocker SHALL be recorded in the optimization list or task report

## ADDED Requirements

### Requirement: Frontend Mock Mode Execution Truth
The frontend SHALL use `VITE_USE_MOCK_DATA` through the shared `apiClient` as the single active execution truth for explicit mock-mode switching and SHALL NOT use `VITE_APP_MODE` or any service-level mock/real endpoint switching in current verified-page runtime behavior.

#### Scenario: Explicit mock mode is enabled
- **WHEN** the frontend is started in explicit mock mode
- **THEN** the shared frontend execution path SHALL use the approved mock-mode switch as the current truth
- **AND** mock-backed behavior SHALL be described and tested as explicit mock acceptance rather than real-path verification

#### Scenario: Legacy service-level switching exists in code or docs
- **WHEN** `VITE_APP_MODE` or service-level endpoint branching remains in code or implementation-facing docs
- **THEN** it SHALL be removed from active runtime behavior
- **AND** any remaining documentation reference SHALL be marked as historical or legacy guidance
- **AND** current implementation and execution-facing docs SHALL identify `VITE_USE_MOCK_DATA` through the shared `apiClient` as the active switching truth unambiguously
