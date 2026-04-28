# trading-execution-safety Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## MODIFIED Requirements

### Requirement: Trading Domain Safety Contract
The project SHALL define an explicit safety contract for trading execution paths before they are described as production-grade.

#### Scenario: Trading path is classified
- **WHEN** a trading execution path is documented or exposed
- **THEN** it SHALL be classified as simulated, experimental, or production-eligible
- **AND** the classification SHALL identify the safety controls that justify that state
- **AND** the classification SHALL define the minimum audit retention expectation for that state

#### Scenario: Production-eligible trading path depends on broker truth
- **WHEN** a trading execution path is proposed as production-eligible
- **THEN** it SHALL identify the canonical broker-facing execution path, broker acknowledgement source, and reconciliation owner
- **AND** it SHALL identify the broker acknowledgement and reconciliation evidence that justifies externally-aligned lifecycle claims
- **AND** absence of that contract SHALL keep the path classified as simulated or experimental

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
