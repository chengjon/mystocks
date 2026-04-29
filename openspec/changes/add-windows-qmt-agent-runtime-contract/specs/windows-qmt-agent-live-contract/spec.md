## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Authenticated Windows qmt Execute Contract
The repository SHALL define an authenticated and versioned execute contract for the Windows
`qmt` agent used by the `miniQMT` primary path.

#### Scenario: Linux runtime submits a primary-path order to Windows qmt agent
- **WHEN** the Linux trading runtime sends a `miniQMT` primary-path submission to the approved
  Windows agent execute endpoint
- **THEN** the request SHALL identify provider `qmt`, method `submit_order`, and the approved
  contract version
- **AND** it SHALL use the approved authentication scheme for the agent boundary
- **AND** the returned receipt SHALL remain explicit transport-stage evidence rather than broker
  acknowledgement

#### Scenario: Windows qmt agent rejects authentication or whitelist rules
- **WHEN** the execute request fails authentication, uses an unsupported contract version, or
  targets a provider/method outside the approved whitelist
- **THEN** the runtime SHALL preserve that failure as review-required live-bridge evidence
- **AND** it SHALL NOT synthesize broker-facing truth from the failed execute attempt

### Requirement: Authenticated Windows qmt Result Retrieval Contract
The repository SHALL define an authenticated and versioned result-retrieval contract for
`task_id`-keyed Windows `qmt` agent polling.

#### Scenario: Linux runtime polls a pending live bridge task
- **WHEN** a primary-path submission has a preserved `task_id` and broker-facing truth is still
  pending
- **THEN** the Linux runtime SHALL query the approved Windows agent result endpoint with the
  approved authentication and contract-version semantics
- **AND** the returned envelope SHALL distinguish pending from terminal result states
- **AND** it SHALL preserve receipt-to-result linkage by `task_id`

#### Scenario: Result retrieval fails at the agent boundary
- **WHEN** result retrieval fails because of authentication, unsupported version, unsupported
  method, timeout, or endpoint unavailability
- **THEN** the runtime SHALL preserve an explicit live-bridge failure class and any available
  reason detail
- **AND** it SHALL NOT treat the incident as synthetic broker reject, broker cancel, or implicit
  supplemental handoff

### Requirement: Windows qmt Result Identity Echo
Terminal Windows `qmt` live-result payloads SHALL echo enough submission identity before
broker-facing truth may advance.

#### Scenario: Terminal live result contains broker-facing evidence
- **WHEN** a terminal live result carries acknowledgement, reject, cancel, or execution facts
- **THEN** the payload SHALL echo the original `client_order_id` or `local_submission_id`
- **AND** it SHALL preserve `account_scope`, `result_status`, and `occurred_at`
- **AND** acknowledgement-capable results SHALL preserve `external_order_id` when that identity
  exists

#### Scenario: Live result identity does not match the active submission trail
- **WHEN** the terminal live result echoes identity that does not match the active
  channel-scoped submission trail
- **THEN** the runtime SHALL preserve a review-required mismatch incident
- **AND** it SHALL NOT auto-bind broker truth by symbol, timing, quantity, or session
  coincidence alone

### Requirement: Explicit Failure And Supplemental Boundary
The Windows `qmt` live contract SHALL preserve an explicit escalation boundary before any
Tongdaxin supplemental continuation is used.

#### Scenario: Live bridge contract fails before safe broker truth exists
- **WHEN** the Windows `qmt` agent returns invalid payload, contract mismatch, timeout,
  unavailable state, or other failure before safe broker truth is established
- **THEN** the runtime SHALL preserve the submission receipt and current live-bridge evidence
- **AND** the next action SHALL remain operator review or explicit supplemental handoff

#### Scenario: Tongdaxin supplemental path is invoked after Windows qmt bridge failure
- **WHEN** an operator explicitly invokes Tongdaxin supplemental handling after Windows `qmt`
  bridge failure
- **THEN** the handoff record SHALL retain the prior live-bridge receipt and failure evidence
- **AND** the supplemental path SHALL NOT inherit Windows `qmt` broker-truth authority by
  implication alone
