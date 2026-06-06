# miniqmt-live-bridge-runtime Specification

## Purpose
Define the `miniQMT` live bridge runtime contract between the Linux trading runtime and Windows `qmt` bridge, including submission receipts, task-keyed result retrieval, identity echo requirements, timeout/mismatch handling, and explicit supplemental escalation boundaries.
## Requirements
### Requirement: miniQMT Live Bridge Submission Receipt
The repository SHALL define a canonical live submission receipt contract for outbound `miniQMT`
primary-path bridge calls.

#### Scenario: Windows bridge accepts submission delivery
- **WHEN** the Linux trading runtime submits a primary-path order to the Windows `qmt` bridge
- **THEN** the live receipt SHALL preserve a repository-owned `task_id` or equivalent receipt
  identifier plus the `provider`, invoked method, and receipt timestamp
- **AND** it SHALL remain explicit transport-stage evidence rather than broker acknowledgement

#### Scenario: Live receipt is missing canonical fields
- **WHEN** the Windows bridge returns a receipt missing the repository-owned minimum receipt
  fields
- **THEN** the runtime SHALL preserve the incident as review-required bridge evidence
- **AND** it SHALL NOT synthesize broker acknowledgement from the incomplete receipt

### Requirement: miniQMT Live Bridge Result Retrieval
The repository SHALL define the first canonical retrieval path for live `miniQMT` bridge results.

#### Scenario: Deferred live result is retrieved by task identifier
- **WHEN** a primary-path submission is awaiting broker-facing evidence and a bridge `task_id`
  exists
- **THEN** the repository SHALL retrieve the live bridge result through the approved canonical
  retrieval contract
- **AND** it SHALL preserve the receipt-to-result linkage by `task_id`
- **AND** it SHALL route the retrieved result into the shared broker lifecycle envelope

#### Scenario: Live bridge result is unavailable within timeout
- **WHEN** the canonical retrieval path does not yield a safe result within the configured live
  bridge timeout
- **THEN** the runtime SHALL preserve a timeout incident as review-required evidence
- **AND** it SHALL NOT auto-bind broker acknowledgement or silently switch channels

### Requirement: miniQMT Live Result Identity Echo
Live bridge result payloads SHALL echo enough submission identity before broker truth may advance.

#### Scenario: Live result returns broker-facing evidence
- **WHEN** a retrieved live result contains acknowledgement, reject, cancel, or execution facts
- **THEN** the payload SHALL echo the original `client_order_id` or `local_submission_id`
- **AND** it SHALL preserve `account_scope` plus broker-facing identity such as
  `external_order_id` or explicit rejection detail
- **AND** lifecycle binding SHALL advance only after that identity can be matched explicitly

#### Scenario: Live result identity mismatches the original submission trail
- **WHEN** the retrieved live result echoes identity fields that do not match the active
  channel-scoped submission trail
- **THEN** the runtime SHALL preserve the incident as review-required mismatch evidence
- **AND** it SHALL NOT auto-match a local order by symbol, timing, or quantity coincidence alone

### Requirement: Explicit Escalation Boundary for Live Bridge Failure
The `miniQMT` live bridge contract SHALL preserve an explicit escalation boundary before any
supplemental operator-assisted continuation is used.

#### Scenario: Operator escalation is required
- **WHEN** the live bridge times out, returns mismatched identity, or becomes unavailable before
  broker-facing truth is safely established
- **THEN** the runtime SHALL preserve the live receipt and current bridge-result evidence
- **AND** it SHALL surface an explicit next action for operator review or supplemental handoff

#### Scenario: Tongdaxin supplemental continuation is invoked after live bridge failure
- **WHEN** an operator invokes Tongdaxin supplemental handling after a live `miniQMT` bridge
  failure or timeout
- **THEN** the runtime SHALL preserve the prior live bridge receipt and result evidence in the
  handoff record
- **AND** the supplemental path SHALL NOT inherit `miniQMT` live bridge authority by implication
  alone
