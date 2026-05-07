## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: AI Sentiment Workbench Route
The frontend routing system SHALL expose a dedicated AI-domain sentiment workbench route.

#### Scenario: User navigates to the AI sentiment workbench
- **WHEN** the user opens `/ai/sentiment`
- **THEN** the router SHALL load the canonical AI sentiment workbench page
- **AND** that page SHALL be the AI-domain truth source for `7.3 情感分析`

### Requirement: AI Navigation Label For Sentiment Workbench
The frontend routing system SHALL expose a visible AI navigation entry for the canonical sentiment workbench.

#### Scenario: AI navigation label is rendered
- **WHEN** the frontend renders the active navigation surfaces
- **THEN** the navigation label for `/ai/sentiment` SHALL be `情感分析`
- **AND** the AI navigation entry SHALL be treated as the canonical route-level entry for this capability

### Requirement: Risk News Wrapper Preservation
The frontend routing system SHALL keep `/risk/news` reachable as a risk-domain wrapper surface.

#### Scenario: User navigates to the risk news wrapper
- **WHEN** the user opens `/risk/news`
- **THEN** the router SHALL continue to load a risk-domain page
- **AND** that page SHALL remain reachable from risk navigation
- **AND** that page SHALL NOT replace `/ai/sentiment` as the canonical AI-domain route
