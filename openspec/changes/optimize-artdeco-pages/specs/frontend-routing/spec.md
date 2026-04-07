## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: ArtDeco Route Metadata SSOT
The system SHALL keep active ArtDeco page metadata aligned across the router, page configuration, and optimization status tracking.

#### Scenario: P0/P1 page metadata alignment
- **WHEN** a P0/P1 ArtDeco page is prepared for optimization
- **THEN** `web/frontend/src/router/index.ts`, `web/frontend/src/config/pageConfig.ts`, and `docs/plans/frontend-page-optimization-list.md` SHALL identify the same route path, page component, and API truth classification
- **AND** the route title and functional domain grouping SHALL remain consistent across those sources

#### Scenario: Executable route batching
- **WHEN** multiple active ArtDeco pages share the same parent container, reusable domain block, or API family
- **THEN** they SHALL be grouped into the same executable optimization batch
- **AND** that batch SHALL declare its primary verification entrypoints before implementation starts

### Requirement: Route And Layout Regression Gate
The system SHALL validate ArtDeco route or layout changes with PM2 smoke and page-level E2E evidence.

#### Scenario: Route or layout change verification
- **WHEN** a change modifies an ArtDeco route, layout shell, or parent container
- **THEN** `scripts/run_e2e_pm2.sh` SHALL be executed against the PM2 environment
- **AND** the change report SHALL record the actual browser project, executed suite names, and pass/fail counts

#### Scenario: Service availability reporting
- **WHEN** route or layout verification results are reported
- **THEN** the report SHALL include `http://localhost:3020` and `http://localhost:8020`
- **AND** it SHALL distinguish newly introduced regressions from pre-existing technical debt
