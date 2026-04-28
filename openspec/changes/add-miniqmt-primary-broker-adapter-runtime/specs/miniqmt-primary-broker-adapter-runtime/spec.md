## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: miniQMT Primary Submission Contract
The repository SHALL define a canonical runtime submission contract for the `miniQMT` primary
broker-truth path.

#### Scenario: Local order is submitted to the primary broker path
- **WHEN** a local trading order is handed from the canonical application path to the
  `miniQMT` primary runtime surface
- **THEN** the workflow SHALL preserve the local `order_id`, `local_submission_id`,
  `broker_channel`, `adapter_path`, `account_scope`, and `session_scope`
- **AND** it SHALL persist an explicit immediate submission outcome
- **AND** it SHALL NOT claim broker acknowledgement unless explicit broker identity evidence is
  present

#### Scenario: Remote bridge returns a transport receipt only
- **WHEN** the `miniQMT` primary path returns only a remote bridge or task receipt and no
  broker order identity
- **THEN** the workflow SHALL persist that transport-stage evidence separately from broker
  acknowledgement truth
- **AND** the order SHALL remain explicitly awaiting broker acknowledgement
- **AND** the system SHALL NOT synthesize `external_order_id` from the transport receipt alone

### Requirement: Primary Submission Outcome Classification
The `miniQMT` primary runtime contract SHALL classify immediate submission outcomes with
machine-readable status.

#### Scenario: Submission outcome is captured
- **WHEN** the primary runtime surface returns from an outbound submission attempt
- **THEN** the recorded outcome SHALL distinguish at least `bridge_task_accepted`,
  `broker_acknowledged`, and `submission_failed`
- **AND** a transport-stage acceptance outcome SHALL remain distinct from broker-confirmed
  acknowledgement

#### Scenario: Bridge delivery fails before broker acknowledgement
- **WHEN** the remote bridge rejects delivery or reports failure before broker acknowledgement is
  known
- **THEN** the workflow SHALL preserve that failure outcome and failure reason as durable audit
  evidence
- **AND** it SHALL NOT mutate unrelated broker lifecycle records to simulate a broker rejection

### Requirement: Deferred miniQMT Lifecycle Re-Entry
Deferred `miniQMT` bridge results, callbacks, or polled runtime evidence SHALL re-enter the
shared broker lifecycle contract through a canonical path.

#### Scenario: Deferred broker lifecycle evidence arrives
- **WHEN** acknowledgement, reject, cancel, or execution evidence is received after the initial
  submission return
- **THEN** the evidence SHALL normalize into the shared `BrokerLifecycleEvent` envelope
- **AND** it SHALL resolve through the same channel-scoped correlation surface used by the
  original primary-path submission
- **AND** acknowledgement SHALL advance broker identity binding only when correlation can be
  established explicitly

#### Scenario: Deferred evidence is missing safe identity fields
- **WHEN** deferred `miniQMT` lifecycle evidence arrives without sufficient local or external
  identity to match it safely
- **THEN** the workflow SHALL preserve the incident as review-required runtime evidence
- **AND** it SHALL NOT auto-match a local order on timing, symbol, or quantity coincidence
  alone

### Requirement: Explicit Supplemental Handoff Boundary
The primary `miniQMT` runtime path SHALL define an explicit handoff boundary before any
Tongdaxin supplemental execution or review flow is used.

#### Scenario: Primary path degrades before broker truth is confirmed
- **WHEN** the `miniQMT` primary runtime cannot confirm broker acknowledgement or returns an
  uncertain transport-stage outcome that requires operator action
- **THEN** the workflow SHALL preserve an operator-visible next action and current submission
  evidence
- **AND** any Tongdaxin supplemental continuation SHALL be recorded as an explicit handoff
  rather than a silent retry

#### Scenario: Supplemental handoff is invoked
- **WHEN** an operator invokes Tongdaxin supplemental handling for an order that first entered
  the `miniQMT` primary path
- **THEN** the handoff record SHALL preserve the prior primary-path submission evidence and the
  reason for handoff
- **AND** the supplemental path SHALL NOT inherit `miniQMT` replay-suppression or
  auto-resolution authority by implication alone
