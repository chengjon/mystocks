## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Primary And Supplemental Broker Channel Roles
The project SHALL define explicit roles when multiple broker-facing trading channels coexist.

#### Scenario: Multi-channel broker topology is published
- **WHEN** the repository defines more than one broker-facing trading channel
- **THEN** it SHALL identify exactly one primary broker-truth candidate for the preferred automated execution path
- **AND** it SHALL classify any remaining channels as supplemental, operator-assisted, compatibility-retained, or otherwise non-equivalent to the primary path
- **AND** upstream orchestration surfaces SHALL remain explicitly non-truth unless they also provide the required broker-facing identity contract

#### Scenario: Current repository channel topology is classified
- **WHEN** the project publishes its first concrete broker channel topology
- **THEN** `miniQMT` SHALL be identified as the first primary broker-truth candidate
- **AND** Tongdaxin semi-manual trading SHALL be identified as a supplemental operator-assisted path unless it can later prove equivalent external identity and sequencing evidence

### Requirement: Channel-Scoped Correlation Identity
Broker-facing submissions SHALL preserve channel-scoped identity when multiple execution
channels coexist.

#### Scenario: Broker-facing submission is persisted
- **WHEN** a local order submission is recorded for a broker-facing channel
- **THEN** the correlation record SHALL preserve `broker_channel`, `adapter_path`, `account_scope`, and `session_scope`
- **AND** it SHALL preserve a sufficient source label to distinguish `miniQMT`, Tongdaxin, and any later broker-facing path without ambiguous cross-channel matching

#### Scenario: External identity is bound later
- **WHEN** an external order identity arrives for a known local submission
- **THEN** the external identity binding SHALL resolve within the same channel-scoped correlation surface
- **AND** it SHALL NOT silently reuse an unrelated correlation record from a different broker channel

### Requirement: Channel-Specific Reconciliation Authority
Replay suppression, auto-resolution, and review policy SHALL remain channel-specific when
broker-facing paths have different truth strength.

#### Scenario: Supplemental channel emits lifecycle evidence
- **WHEN** a supplemental or operator-assisted broker channel emits acknowledgement, reject, cancel, or execution evidence
- **THEN** the workflow SHALL preserve that evidence through the shared lifecycle and divergence ledgers
- **AND** the default reconciliation outcome SHALL remain `review_required` unless that channel has an explicit stronger identity contract

#### Scenario: Primary channel claims stronger automated authority
- **WHEN** the primary broker-truth candidate claims replay suppression or bounded auto-resolution
- **THEN** the policy SHALL identify the channel-specific external identity or sequencing basis that authorizes that stronger behavior
- **AND** unsupported channels SHALL NOT inherit the same authority by implication alone
