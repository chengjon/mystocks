# ai-batch-analysis Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Purpose
Define the canonical first-batch AI batch analysis workbench, v1 aggregation routes, task evidence, and safety semantics for `7.2 批量分析`.
## Requirements
### Requirement: Canonical Batch Analysis Surface
The system SHALL provide a canonical first-batch AI-domain surface for `7.2 批量分析`.

#### Scenario: Canonical API family is used
- **WHEN** a client performs first-batch batch analysis work
- **THEN** the client SHALL use the canonical `/api/v1/strategies/batch-analysis/*` route family
- **AND** the system SHALL return `UnifiedResponse` envelopes
- **AND** existing backtest, screener, and scheduler modules SHALL remain underlying evidence or compatibility surfaces

### Requirement: Batch Runtime Readiness
The system SHALL expose machine-readable batch analysis runtime readiness.

#### Scenario: Runtime status is requested
- **WHEN** the client calls `GET /api/v1/strategies/batch-analysis/runtime-status`
- **THEN** the response SHALL include service availability, supported operations, max symbols, underlying evidence modules, warnings, and safety metadata

### Requirement: Batch Analysis Task Submission
The system SHALL allow a bounded batch analysis task to be submitted for observation.

#### Scenario: Batch analysis task succeeds
- **WHEN** a valid request includes an operation type, symbols, date range, and options
- **THEN** the system SHALL register a task
- **AND** return task identity, status, summary, per-symbol results, warnings, and generated timestamp

#### Scenario: Batch analysis request exceeds first-batch limits
- **WHEN** the request exceeds the supported symbol count
- **THEN** the system SHALL reject it with an explicit validation error
- **AND** SHALL NOT register a partial task

### Requirement: Batch Analysis Task Inspection
The system SHALL expose batch analysis task list and detail inspection.

#### Scenario: Task list is requested
- **WHEN** the client calls `GET /api/v1/strategies/batch-analysis/tasks`
- **THEN** the response SHALL include registered task summaries and total count

#### Scenario: Task detail is requested
- **WHEN** the client calls `GET /api/v1/strategies/batch-analysis/tasks/{task_id}`
- **THEN** the response SHALL include the task detail or an explicit not-found error

### Requirement: Batch Analysis Safety Semantics
The system SHALL present batch analysis results as analytical evidence only.

#### Scenario: Batch result is returned or displayed
- **WHEN** the system returns or displays batch analysis results
- **THEN** it SHALL NOT describe the output as automated trading, broker execution, or production scheduling completion
- **AND** it SHALL include wording or metadata that distinguishes analytical batch evidence from trade execution or scheduler mutation
