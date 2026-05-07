## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Canonical AI Sentiment Workbench Page
The system SHALL provide a canonical AI-domain sentiment workbench page that combines sentiment analysis and announcement/news monitoring into a single dual-column surface.

#### Scenario: Canonical workbench renders the approved structure
- **WHEN** the user opens the AI sentiment workbench
- **THEN** the page SHALL present a left monitoring column for announcement/news flow
- **AND** the page SHALL present a right analysis column for text sentiment analysis, stock sentiment trend, and market sentiment overview

### Requirement: Shared Frontend Orchestration
The system SHALL use one shared frontend orchestration layer as the truth source for the sentiment workbench.

#### Scenario: Canonical workbench owns orchestration truth
- **WHEN** the frontend loads sentiment workbench data
- **THEN** announcement/news flow and sentiment API calls SHALL be coordinated by a shared workbench orchestration layer
- **AND** the canonical AI page SHALL consume that orchestration as the primary truth source

### Requirement: Risk Wrapper Reuse Boundary
The system SHALL keep the risk-domain news surface as a wrapper over shared workbench logic instead of a parallel orchestration owner.

#### Scenario: Risk wrapper reuses shared workbench logic
- **WHEN** the frontend renders `/risk/news`
- **THEN** the page SHALL reuse the shared sentiment/news workbench logic
- **AND** the page MAY apply risk-domain framing or filtered presentation
- **AND** the page SHALL provide a jump path into the canonical AI workbench
- **AND** the page SHALL NOT own a separate fetch orchestration for the same capability
