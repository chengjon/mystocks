# system-resource-usage-monitoring Specification

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Purpose
Define the current-truth contract and UI capability boundaries for the dedicated single-node system resource usage workbench at `/system/resources`.
## Requirements
### Requirement: Dedicated System Resource Usage Surface
The system SHALL provide a dedicated resource usage monitoring capability for the current runtime node.

#### Scenario: User opens the resource usage page
- **WHEN** the user navigates to `/system/resources`
- **THEN** the system SHALL expose a dedicated resource usage surface
- **AND** that surface SHALL remain separate from the existing health and middleware telemetry page

### Requirement: Unified Resource Metrics Contract
The backend SHALL provide one unified contract for the system resource usage page.

#### Scenario: Resource metrics are requested
- **WHEN** the frontend requests the system resource usage payload
- **THEN** the backend SHALL return a single response envelope containing node metadata, host snapshots, process snapshots, dependency summaries, threshold definitions, and short-window trend series
- **AND** the frontend SHALL NOT be required to assemble the page by stitching multiple unrelated monitoring contracts

### Requirement: Single-Node Host Resource Observation
The capability SHALL expose current host resource snapshots and recent trends for the active runtime node only.

#### Scenario: Host resource snapshots are rendered
- **WHEN** a resource metrics response is returned
- **THEN** the payload SHALL include host CPU, memory, disk, and load information for the current runtime node
- **AND** the payload SHALL include recent trend series covering the approved short-window horizon
- **AND** the first batch SHALL NOT claim multi-node aggregation or node switching

### Requirement: Process Resource Observation
The capability SHALL expose process-level resource snapshots for the active frontend and backend processes.

#### Scenario: Runtime process metrics are returned
- **WHEN** a resource metrics response is returned
- **THEN** the payload SHALL include process snapshots for `mystocks-backend` and `mystocks-frontend`
- **AND** each process snapshot SHALL expose enough data to render current usage and threshold state in the UI

### Requirement: Dependency Resource Summaries
The capability SHALL expose first-batch dependency summaries for PostgreSQL, TDengine, and Redis.

#### Scenario: Dependency summaries are returned
- **WHEN** a resource metrics response is returned
- **THEN** the payload SHALL include PostgreSQL, TDengine, and Redis dependency entries
- **AND** each dependency entry SHALL expose status plus approved first-batch proxy resource indicators such as connection counts, memory summaries, or equivalent runtime-backed metrics
- **AND** the first batch SHALL NOT require full operating-system resource profiles for dependencies

### Requirement: Backend-Defined Threshold States
The capability SHALL derive threshold states from backend-defined warning and critical thresholds.

#### Scenario: Threshold-aware resources are rendered
- **WHEN** a resource metrics response is returned
- **THEN** each monitored resource SHALL carry server-defined threshold semantics
- **AND** each resource SHALL resolve to `normal`, `warning`, or `critical`
- **AND** the frontend SHALL render those threshold states without defining a second threshold truth source

### Requirement: Polling-Based Refresh Control
The capability SHALL refresh through polling and support operator pause/resume control.

#### Scenario: Resource polling runs by default
- **WHEN** the resource usage page is opened
- **THEN** the frontend SHALL start polling resource metrics on the approved default cadence
- **AND** the user SHALL be able to pause and resume polling
- **AND** the first batch SHALL NOT require WebSocket or SSE transport
