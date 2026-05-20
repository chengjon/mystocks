## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Runtime Unblock Must Precede Broad Architecture Evidence
The backend SHALL restore a successful `app.main` import and the associated targeted collection smoke before route/OpenAPI closure evidence, health/status closure claims, or broad architecture batch scheduling are treated as current truth.

#### Scenario: Runtime unblock is still failing
- **WHEN** `app.main` import fails because a response-helper module in the route import chain has a missing transitive import
- **THEN** the failure SHALL be recorded as the active blocker
- **AND** route/OpenAPI closure claims SHALL remain deferred
- **AND** no broad architecture batch SHALL be treated as open for execution based on stale runtime evidence

#### Scenario: Runtime unblock is restored
- **WHEN** `app.main` import succeeds after low-risk import-time route/helper repairs
- **THEN** the evidence SHALL record the route count and targeted health route collection or test result
- **AND** route/OpenAPI evidence refresh MAY proceed from the verified checkout
- **AND** remaining non-import-chain static debt SHALL remain separate from the runtime unblock claim

### Requirement: Schema Compatibility Must Be Proved Before Directory Retirement
The backend SHALL preserve schema compatibility until canonical exports, consumer migration, and targeted validation prove that the legacy `app/schema/` path can be retired without breaking current consumers.

#### Scenario: Legacy schema consumers still exist
- **WHEN** `from app.schema` consumers remain in the codebase
- **THEN** the change SHALL preserve a compatibility path
- **AND** the retirement decision SHALL remain deferred until the consumer migration evidence is recorded

### Requirement: Singleton Lifecycle Work Must Start From Classification
The backend SHALL classify service and singleton candidates by interface depth, statefulness, and test-double suitability before selecting a lifecycle implementation pilot.

#### Scenario: No low-risk pilot exists
- **WHEN** the inventory does not contain a clean low-risk singleton pilot
- **THEN** the plan SHALL switch to interface extraction and test-double strategy instead of forcing a misleading pilot selection

### Requirement: Codebase Map Evidence Shall Distinguish Historical And Current-Head Truth
The codebase map SHALL mark each recorded artifact as historical, commit-scoped, current-head, or stale-aware so that older counts cannot be mistaken for current truth.

#### Scenario: A count changes at a later HEAD
- **WHEN** a newer HEAD contradicts an older live-count snapshot
- **THEN** the newer HEAD SHALL be recorded explicitly
- **AND** the older snapshot SHALL remain labeled as historical evidence only
