## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: Page-Level API Truth Classification
The system SHALL classify each active ArtDeco page's API dependency as `verified` or `pending` and apply page behavior accordingly.

#### Scenario: Verified API page behavior
- **WHEN** an ArtDeco page is marked `verified`
- **THEN** it SHALL use the registered real API endpoint as its primary data source
- **AND** it SHALL NOT silently fall back to mock data for the same user path
- **AND** it SHALL surface loading, error, empty, and request identifier states

#### Scenario: Pending API page behavior
- **WHEN** an ArtDeco page is marked `pending`
- **THEN** the route SHALL remain reachable
- **AND** the page SHALL render shell/loading/error/empty states without fabricating contract fields
- **AND** the unresolved API blocker SHALL be recorded in the optimization list or task report

### Requirement: Shared Adapter Consistency For Batched Pages
The system SHALL consolidate data transformation logic for active ArtDeco pages that consume the same API family.

#### Scenario: Shared signals or positions endpoints
- **WHEN** multiple pages consume `/api/v1/trade/signals` or `/api/v1/trade/positions`
- **THEN** they SHALL reuse a common transformation layer or view-model mapping
- **AND** field normalization SHALL NOT be reimplemented independently on each page

#### Scenario: Shared market data endpoint family
- **WHEN** multiple pages consume the same market or Akshare endpoint family
- **THEN** their adapter logic SHALL be centralized in shared composables or helper modules
- **AND** any endpoint-specific blocker SHALL be tracked once at the batch level instead of duplicated across pages
