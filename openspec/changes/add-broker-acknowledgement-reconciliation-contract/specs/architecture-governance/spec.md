# architecture-governance Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## ADDED Requirements

### Requirement: Broker Execution Truth Registry
The system SHALL maintain a broker execution truth registry for broker-facing execution and
lifecycle-ingestion paths.

#### Scenario: Broker-facing execution path is introduced or changed
- **WHEN** a broker-facing adapter, submission bridge, acknowledgement ingestion path, or execution-report ingestion path is introduced or materially changed
- **THEN** the registry SHALL record the canonical path owner, adapter or bridge identity, and current classification state
- **AND** it SHALL record the local-to-external order identity binding surface, lifecycle source scope, and reconciliation owner
- **AND** it SHALL identify whether the path is canonical, compatibility-retained, or still experimental

#### Scenario: Broker truth registry is reviewed during trading safety closure
- **WHEN** a trading path is reviewed for stronger lifecycle claims or production-eligible promotion
- **THEN** the broker execution truth registry SHALL be reviewed alongside the trading execution safety contract
- **AND** the recorded path SHALL be consistent with the broker acknowledgement and reconciliation contract defined for trading safety
