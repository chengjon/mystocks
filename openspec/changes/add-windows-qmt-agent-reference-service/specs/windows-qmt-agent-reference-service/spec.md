## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Dedicated Windows qmt Reference Service
The repository SHALL provide a dedicated Windows `qmt` reference agent/service instead of treating
the generic task-node template as the canonical broker-truth agent surface.

#### Scenario: Reference service is used as the canonical Windows boundary
- **WHEN** project documentation or runtime instructions point to the Windows `qmt` agent
- **THEN** they SHALL identify a dedicated reference service for the approved `miniQMT` boundary
- **AND** that service SHALL be narrower than the generic multi-provider task-node template

### Requirement: Authenticated And Versioned Execute/Result Surface
The Windows `qmt` reference service SHALL expose the approved authenticated and versioned
execute/result surface for the `miniQMT` primary path.

#### Scenario: Linux runtime submits a qmt order to the reference service
- **WHEN** the Linux trading runtime submits a primary-path order to the Windows reference service
- **THEN** the service SHALL accept only provider `qmt` and method `submit_order`
- **AND** it SHALL require the approved authentication and contract-version headers
- **AND** it SHALL return a transport-stage receipt rather than broker acknowledgement

#### Scenario: Auth, version, or whitelist validation fails
- **WHEN** the request is unauthenticated, uses the wrong contract version, or targets an
  unapproved provider/method
- **THEN** the reference service SHALL reject the request with explicit failure semantics
- **AND** it SHALL NOT fabricate a task receipt that appears broker-valid

### Requirement: Task Registry And Result Retrieval
The Windows `qmt` reference service SHALL preserve task results by `task_id` and expose pending
and terminal result retrieval through the approved polling contract.

#### Scenario: Reference service returns a pending result
- **WHEN** the Linux runtime polls a `task_id` whose provider execution is not terminal yet
- **THEN** the service SHALL return a pending-compatible result envelope
- **AND** it SHALL preserve the original `task_id` and contract version

#### Scenario: Reference service returns a terminal result
- **WHEN** provider execution reaches a terminal state
- **THEN** the service SHALL return a canonical terminal result envelope
- **AND** the envelope SHALL distinguish broker-facing evidence from provider or transport failure

### Requirement: Explicit Provider Modes
The Windows `qmt` reference service SHALL expose explicit provider modes rather than hiding whether
the result came from a mock path or a live `miniQMT` SDK path.

#### Scenario: Mock provider mode is enabled
- **WHEN** the reference service runs in `mock` mode
- **THEN** receipts and results SHALL disclose that mode explicitly
- **AND** the service SHALL keep the same contract shape as the live-oriented path for testing

#### Scenario: miniQMT SDK mode is unavailable or unconfigured
- **WHEN** the reference service runs in `miniqmt_sdk` mode but the live provider is unavailable,
  misconfigured, or missing dependencies
- **THEN** the service SHALL fail closed with explicit reason fields
- **AND** it SHALL NOT synthesize broker acknowledgement or terminal execution facts

### Requirement: Terminal Result Identity Echo
Terminal Windows `qmt` reference-service results SHALL preserve the identity echo and failure
detail required by the Linux broker-truth runtime.

#### Scenario: Terminal result carries broker-facing evidence
- **WHEN** the reference service returns acknowledgement, rejection, cancellation, or execution
  evidence
- **THEN** the result SHALL preserve `client_order_id` or `local_submission_id`,
  `account_scope`, `occurred_at`, `result_status`, and `bridge_contract_version`
- **AND** acknowledgement-capable results SHALL preserve `external_order_id` when that identity
  exists

#### Scenario: Terminal result is provider or contract failure
- **WHEN** the reference service returns a terminal failure rather than broker-facing evidence
- **THEN** the result SHALL preserve explicit `reason_code` and `reason_detail`
- **AND** it SHALL remain distinguishable from broker reject/cancel semantics
