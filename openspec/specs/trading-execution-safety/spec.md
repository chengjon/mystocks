# trading-execution-safety Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Purpose

Define the governance contract for trading execution path classification, pre-execution safety controls, deduplication policy, confirmation requirements, and minimum audit retention behavior before any trading path is described as production-grade.
## Requirements
### Requirement: Trading Domain Safety Contract
The project SHALL define an explicit safety contract for trading execution paths before they are
described as production-grade.

#### Scenario: Trading path is classified
- **WHEN** a trading execution path is documented or exposed
- **THEN** it SHALL be classified as simulated, experimental, or production-eligible
- **AND** the classification SHALL identify the safety controls that justify that state
- **AND** the classification SHALL define the minimum audit retention expectation for that state

#### Scenario: External broker-facing path is described as formally ready
- **WHEN** a trading execution path depends on a separately deployed Windows broker-facing
  `qmt` / `miniQMT` service and is presented as ready for first formal cross-project acceptance
- **THEN** the readiness claim SHALL point to a local formal acceptance sequence artifact produced
  from `WSL 上的 Ubuntu 24.04.4 LTS`
- **AND** that artifact SHALL distinguish contract-level acceptance from production broker-truth
  claims

#### Scenario: Production-eligible trading path depends on broker truth
- **WHEN** a trading execution path is proposed as production-eligible
- **THEN** it SHALL identify the canonical broker-facing execution path, broker acknowledgement
  source, and reconciliation owner
- **AND** it SHALL identify the broker acknowledgement and reconciliation evidence that justifies
  externally-aligned lifecycle claims
- **AND** absence of that contract SHALL keep the path classified as simulated or experimental

#### Scenario: Remote transport receipt is not broker acknowledgement
- **WHEN** a broker-facing execution path uses an asynchronous bridge, task worker, or remote
  transport layer that can accept delivery before broker acknowledgement is known
- **THEN** the safety contract SHALL distinguish transport acceptance from broker
  acknowledgement and external order identity binding
- **AND** the path SHALL remain experimental unless auditable runtime evidence proves the
  broker-facing acknowledgement boundary

#### Scenario: Live bridge result contract is missing or incomplete
- **WHEN** a broker-facing trading path depends on a remote live bridge or Windows agent for
  deferred broker-facing evidence
- **THEN** the safety contract SHALL identify the canonical live result retrieval path,
  timeout policy, and mismatch-handling rule
- **AND** absence of that contract SHALL keep the path classified as simulated or experimental

#### Scenario: Remote Windows agent contract is unauthenticated or unversioned
- **WHEN** a broker-facing path depends on a remote Windows `qmt` agent for execute/result
  delivery
- **THEN** the safety contract SHALL define the approved authentication, contract-version, and
  provider/method whitelist semantics for that boundary
- **AND** absence of that contract SHALL keep the path classified as simulated or experimental

### Requirement: Trading Pre-Execution Risk Gate
Safety-sensitive trading paths SHALL define pre-execution risk gates that block submissions exceeding configured capital or exposure thresholds.

#### Scenario: Capital or exposure threshold is exceeded
- **WHEN** a trading submission would exceed a configured capital, concentration, or exposure threshold
- **THEN** the execution path SHALL block the submission before order placement
- **AND** it SHALL record the blocking decision as an audit event

### Requirement: Idempotent Trading Submission
Trading execution paths SHALL define an idempotent submission policy.

#### Scenario: Trading request is retried or duplicated
- **WHEN** the same effective trading instruction is submitted more than once within the deduplication scope
- **THEN** the execution path SHALL prevent unintended duplicate order submission
- **AND** it SHALL preserve an auditable record of the deduplication decision

#### Scenario: Broker-facing replay suppression is claimed
- **WHEN** a trading path claims replay-safe suppression for broker acknowledgements or execution reports
- **THEN** it SHALL define the broker-side identity or sequencing fields that justify the suppression decision
- **AND** it SHALL NOT rely only on local quantity, price, or timing coincidence as proof of duplicate external lifecycle events

### Requirement: Trading Confirmation Policy
Safety-sensitive trading operations SHALL define a confirmation policy before execution.

#### Scenario: High-risk trading action is requested
- **WHEN** an operation crosses the configured safety threshold for capital, position change, or destructive impact
- **THEN** the system SHALL require an explicit confirmation step or approved equivalent safeguard
- **AND** the policy SHALL identify when confirmation may be bypassed and why

### Requirement: Trading Audit Minimum Fields
Trading execution paths SHALL emit a minimum audit record for each submitted action.

#### Scenario: Trading action is recorded
- **WHEN** a trading submission, rejection, confirmation, or deduplication decision occurs
- **THEN** the audit record SHALL include request identity, actor identity, execution path,
  decision outcome, and timestamp
- **AND** it SHALL be sufficient to reconstruct the basic control flow for review

#### Scenario: Audit record retention is enforced
- **WHEN** a trading audit record is created
- **THEN** the record SHALL be persisted to durable storage
- **AND** the minimum retention period SHALL be defined by the trading safety contract

#### Scenario: Broker-facing submission uses transport-stage receipt
- **WHEN** a broker-facing submission is relayed through a remote bridge or task transport and
  broker acknowledgement is not yet confirmed
- **THEN** the audit record SHALL preserve the broker channel, adapter path, and transport
  receipt identifier if one exists
- **AND** it SHALL distinguish transport acceptance from broker acknowledgement or external
  order identity binding

#### Scenario: Live bridge result times out or mismatches identity
- **WHEN** the live bridge result retrieval path times out, becomes unavailable, or returns
  identity fields that do not match the active channel-scoped submission trail
- **THEN** the audit or divergence evidence SHALL preserve the live receipt identifier, failure
  class, and escalation outcome
- **AND** it SHALL remain explicit review-required runtime evidence rather than synthetic broker
  truth

#### Scenario: Phase A live bridge identity fields are preserved end to end
- **WHEN** a repo-owned `miniQMT` Phase A result is normalized and re-entered into the shared
  lifecycle ledger
- **THEN** the local contract SHALL preserve the canonical v1 identity fields needed for audit and
  reconciliation review
- **AND** those fields SHALL include `account_scope`, `event_id`, `occurred_at`, `source_name`,
  and `bridge_contract_version`
- **AND** any missing or mismatched canonical identity fields SHALL keep the path in explicit
  review-required evidence rather than synthetic broker truth

#### Scenario: Remote Windows agent contract fails authentication or version checks
- **WHEN** the Windows `qmt` agent execute/result contract fails authentication, contract-version
  validation, or provider/method whitelist validation
- **THEN** the audit or divergence evidence SHALL preserve the bridge boundary, failure class,
  and any available reason code or reason detail
- **AND** it SHALL remain explicit review-required runtime evidence rather than synthetic broker
  truth

### Requirement: External Execution Tracking Canonical Trigger
The system SHALL expose a canonical external execution trigger path that records trigger intent and bridge receipt evidence without claiming broker execution truth.

#### Scenario: External trigger is submitted
- **WHEN** the frontend submits an execution trigger for the first-batch miniQMT channel
- **THEN** the backend SHALL record an external trigger request
- **AND** the response SHALL expose bridge task receipt evidence
- **AND** the response SHALL NOT claim broker acknowledgement or fill state unless broker lifecycle identity is present

### Requirement: Execution Tracking Evidence Workbench
The system SHALL provide an execution tracking query surface that aggregates internal order or trade references, miniQMT bridge submission evidence, broker correlation state, and reconciliation status.

#### Scenario: Execution tracking list is queried
- **WHEN** the frontend queries execution tracking rows
- **THEN** the backend SHALL return execution chain rows with internal order identity, bridge task identity, broker correlation state, and reconciliation status
- **AND** miniQMT bridge submission attempts SHALL be included when available for the requested account, order id, or bridge task id
- **AND** bridge-only terminal results SHALL remain `review_required` when broker lifecycle identity is missing

#### Scenario: miniQMT bridge evidence has no broker lifecycle identity
- **WHEN** a bridge task has a terminal bridge result but no broker lifecycle identity
- **THEN** execution tracking SHALL expose the bridge result as review evidence
- **AND** execution tracking SHALL NOT mark the chain as broker acknowledged or filled

#### Scenario: Broker lifecycle identity is present
- **WHEN** miniQMT evidence includes broker lifecycle identity and acknowledgement event type
- **THEN** execution tracking MAY mark the chain as broker acknowledged
- **AND** the evidence timeline SHALL include the broker identity source used for that state transition

### Requirement: Legacy Trade Execute Compatibility
The system SHALL keep legacy trade execution endpoints available as compatibility surfaces while excluding them from the new canonical external trigger workbench.

#### Scenario: New execution workbench is opened
- **WHEN** the user opens `/trade/execution`
- **THEN** the page SHALL use `/api/v1/trade/execution-tracking/trigger` for new trigger requests
- **AND** it SHALL NOT depend on `/api/v1/trade/execute` as the canonical entrypoint

### Requirement: Windows qmt Service-Ready Evidence Gate
The project SHALL require dedicated readiness evidence before a separately deployed Windows `qmt` /
`miniQMT` service is described as ready for first formal cross-project acceptance.

#### Scenario: Operator or documentation claims Windows qmt service is ready
- **WHEN** an operator-facing workflow, guide, or status artifact describes a Windows `qmt` /
  `miniQMT` service as ready for first formal acceptance from `WSL 上的 Ubuntu 24.04.4 LTS`
- **THEN** that claim SHALL be backed by a dedicated read-only readiness artifact
- **AND** a successful contract acceptance run alone SHALL not be treated as equivalent service-ready
  proof

### Requirement: Windows qmt Reference Service Fails Closed
The project SHALL keep the Windows `qmt` reference-service boundary fail-closed until live broker
evidence is explicitly available.

#### Scenario: Reference service runs in mock mode
- **WHEN** the Ubuntu / WSL trading runtime receives a receipt or result produced by the Windows
  reference service in `mock` mode
- **THEN** that evidence SHALL remain non-production by classification
- **AND** it SHALL NOT by itself justify broker acknowledgement, broker execution truth, or
  production-eligible status

#### Scenario: Live provider is unavailable or unconfigured
- **WHEN** the Windows `qmt` reference service is configured for a live `miniQMT` provider but the
  provider is unavailable, misconfigured, or missing required dependencies
- **THEN** the boundary SHALL preserve explicit failure evidence
- **AND** it SHALL NOT silently fall back to Tongdaxin or synthetic broker-facing outcomes
