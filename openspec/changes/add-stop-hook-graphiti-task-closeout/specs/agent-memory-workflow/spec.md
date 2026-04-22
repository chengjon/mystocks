## ADDED Requirements
### Requirement: Stop Hook Task Closeout Reporting
The project SHALL support a Stop-hook-driven Graphiti closeout report for clearly completed tasks.

#### Scenario: Final assistant message indicates completion
- **WHEN** the Stop hook inspects the final assistant message for a session
- **AND** that message matches an approved completion phrase such as `收尾已完成`, `任务完成`, `已完成`, `done`, or `finished`
- **AND** the message does not match a configured negative phrase such as `未完成`, `尚未完成`, or `not completed`
- **THEN** the hook SHALL build a standardized closeout summary
- **AND** it SHALL submit the closeout through the shared Graphiti CLI contract

#### Scenario: Final assistant message does not indicate completion
- **WHEN** the Stop hook inspects the final assistant message for a session
- **AND** the message does not match an approved completion phrase
- **THEN** the hook SHALL NOT submit a Graphiti closeout report

### Requirement: Stop Hook Graphiti Closeout Payload Must Be Auditable
The project SHALL record auditable metadata for Stop-hook-driven Graphiti closeout writes.

#### Scenario: Closeout report is written
- **WHEN** the Stop hook writes a Graphiti closeout report
- **THEN** the payload SHALL include a bounded summary of the completed work
- **AND** it SHALL include changed file evidence or an explicit empty marker
- **AND** it SHALL include available verification evidence
- **AND** the result SHALL retain durable metadata including `episode_uuid` and `group_id`

#### Scenario: Duplicate Stop events occur for same final assistant message
- **WHEN** the Stop hook is invoked more than once for the same `session_id` and final assistant message identifier
- **THEN** the project SHALL deduplicate the Graphiti closeout write
- **AND** it SHALL ensure at most one closeout episode is recorded for that final message

### Requirement: Stop Hook Graphiti Reporting Must Remain Non-Blocking
The project SHALL keep completion-triggered Graphiti reporting non-blocking with respect to Stop completion.

#### Scenario: Graphiti write fails during closeout reporting
- **WHEN** the Stop hook detects completion but the Graphiti write cannot be completed
- **THEN** the hook SHALL emit warning or audit context
- **AND** it SHALL NOT block Stop solely because the Graphiti write failed
- **AND** it SHALL preserve enough local evidence to troubleshoot the failed write later
