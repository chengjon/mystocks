## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: ArtDeco Container-Tab Boundary
The frontend SHALL keep ArtDeco parent containers, page tabs, and reusable domain components separated according to the governance baseline.

#### Scenario: Parent container responsibilities
- **WHEN** implementing an ArtDeco parent container under `web/frontend/src/views/artdeco-pages/`
- **THEN** it SHALL own route integration, tab state, and API configuration handoff
- **AND** it SHALL avoid duplicating reusable domain rendering logic across sibling pages

#### Scenario: Tab-only block responsibilities
- **WHEN** implementing a file under `web/frontend/src/views/artdeco-pages/*-tabs/`
- **THEN** it SHALL contain page-specific block logic only
- **AND** it SHALL NOT be imported by unrelated pages outside its owning container

#### Scenario: Shared domain component extraction
- **WHEN** the same interaction or presentation block is needed by multiple P0/P1 ArtDeco pages
- **THEN** that block SHALL be extracted to `web/frontend/src/views/artdeco-pages/components/` or `web/frontend/src/components/artdeco/`
- **AND** the pages SHALL consume the extracted component instead of duplicating logic in multiple tabs
